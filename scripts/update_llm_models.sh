#!/usr/bin/env bash
# Refresh models/llm_models.json from the CERIT-SC LLM status API.
#
# The status API needs no credentials (unlike /v1/models), so this runs in CI as well as
# locally. Observed fields (status, first/last sighting, throughput) are rewritten from the API;
# curated fields (`note`) are carried over from the existing file, because the API exposes no
# capability information and a refreshed file must not silently erase what we know about a model.
#
# Exit status, for the weekly job in .github/workflows/refresh-llm-models.yml:
#   2  the update could not be performed at all; must never be read as "nothing is new"
#   in --check mode:
#   0  the committed catalog still matches the service
#   1  it does not; this is how CI learns there is something to open a PR about
#   in write mode:
#   0  the catalog was rewritten (whatever it now contains; compare with git to learn whether the
#      content moved, and prefer --check, because a write always updates the volatile fields)
#
# Usage:
#   scripts/update_llm_models.sh [--check]
#     --check  write nowhere, exit 1 if the committed catalog no longer matches the service. The
#              comparison ignores volatile fields (see strip_volatile below), so it answers "did the
#              provider's offer change", not "is the file byte-identical".
#   scripts/update_llm_models.sh --summary BEFORE AFTER
#     Offline: print a markdown description of how catalog AFTER differs from catalog BEFORE, using
#     the same notion of drift as --check. The weekly workflow puts this in the pull request body.

set -euo pipefail

status_api="https://llm.ai.e-infra.cz/status/api/v1/models"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
catalog="${repo_root}/models/llm_models.json"
check_only="false"

# The drift signal: which models exist, and their lifecycle. Deliberately narrow, because most of
# what the API returns moves on its own and a weekly job that compares it opens a PR every week for
# no reason:
#   .snapshot     - throughput and the rolling uptime window move between samples
#   last_seen     - the provider advances it every minute for every online model, so it is a
#                   heartbeat, not a fact; retirement is reported by `status`, not by this
#   observed_at   - the refresh timestamp itself
strip_volatile='del(.observed_at, .previous_observed_at) | .models |= map(del(.snapshot, .last_seen))'

if [[ "${1:-}" == "--check" ]]; then
    check_only="true"
fi

for tool in curl jq; do
    if ! command -v "${tool}" > /dev/null; then
        echo "error: ${tool} is required but not installed" >&2
        exit 2
    fi
done

# Offline subcommand, handled before anything is fetched: describe the difference between two
# catalogs. Both sides go through strip_volatile first, so what counts as drift here is the same set
# of fields --check compares; the two cannot drift apart.
if [[ "${1:-}" == "--summary" ]]; then
    if [[ $# -ne 3 || ! -f "${2}" || ! -f "${3}" ]]; then
        echo "usage: ${BASH_SOURCE[0]} --summary BEFORE_CATALOG AFTER_CATALOG" >&2
        exit 2
    fi
    before_models="$(jq -S "${strip_volatile} | .models | map({name, status})" "${2}")"
    after_models="$(jq -S "${strip_volatile} | .models | map({name, status})" "${3}")"
    jq -rn \
        --argjson before "${before_models}" \
        --argjson after "${after_models}" '
        # Case-insensitive on purpose: lookups elsewhere are, and the provider is inconsistent
        # about the first letter (`Gpt-oss-120b` is our `gpt-oss-120b`).
        def by_name: map({key: (.name | ascii_downcase), value: .}) | from_entries;
        $before | by_name as $old | $after | by_name as $new
        | ($new | keys) as $after_names
        | ($old | keys) as $before_names
        | ($after_names - $before_names | map($new[.].name) | sort) as $added
        | ($before_names - $after_names | map($old[.].name) | sort) as $gone
        | ($after_names
            | map(. as $key | select(($old | has($key)) and ($old[$key].status != $new[$key].status))
                  | "\($new[$key].name): \($old[$key].status) -> \($new[$key].status)")
            | sort) as $status_changes
        | if ($added | length) == 0 and ($gone | length) == 0 and ($status_changes | length) == 0 then
                "- No model was added, removed or changed status; the difference is in metadata "
                + "that moves on its own between refreshes."
            else
                [
                    (if ($added | length) > 0
                     then "- New: \($added | join(", "))" else empty end),
                    (if ($gone | length) > 0
                     then "- No longer listed: \($gone | join(", "))" else empty end),
                    (if ($status_changes | length) > 0
                     then "- Status changes:\n\($status_changes | map("  - " + .) | join("\n"))"
                     else empty end)
                ]
                | join("\n")
            end
    '
    exit 0
fi

payload="$(mktemp)"
trap 'rm -f "${payload}"' EXIT

# A retry, because the weekly job should not open a PR over one dropped request.
if ! curl --fail --silent --show-error --location --retry 3 --retry-delay 5 --max-time 60 \
        --output "${payload}" "${status_api}"; then
    echo "error: could not fetch ${status_api}" >&2
    exit 2
fi

# Anything that is not a JSON array of model records means the endpoint changed shape or served
# an error page. Bail out rather than write a truncated catalog and call it "no new models".
if ! jq -e 'type == "array" and length > 0 and all(.[]; has("model_name") and has("status"))' \
        "${payload}" > /dev/null; then
    echo "error: ${status_api} did not return a non-empty array of model records" >&2
    exit 2
fi

refreshed="$(mktemp)"
trap 'rm -f "${payload}" "${refreshed}"' EXIT

previous_notes="{}"
if [[ -f "${catalog}" ]]; then
    previous_notes="$(jq 'if .models then .models | map({(.name): (.note // "")}) | add else {} end' "${catalog}")"
fi

previous_at="null"
if [[ -f "${catalog}" ]]; then
    previous_at="$(jq '.observed_at // "null"' "${catalog}")"
fi

jq --argjson notes "${previous_notes}" --argjson previous_observed_at "${previous_at}" '
    def uptime_true: [.[] | select(. == true)] | length;
    # Archived models report their stats as an empty object rather than zero or null, so a
    # `// 0` default never fires; keep a number, or null when the service gave no number.
    def number_or_null: if type == "number" then . else null end;
    # The API reports no capabilities. Every embedding/reranker model the service has listed is
    # not something aoptk can prompt, so the class is decided on the name and is stable; `note` is
    # where a reviewed statement belongs. Deliberately not inferred from throughput: a generative
    # model that happens to be idle would flip class between refreshes.
    def task_class:
        .model_name | ascii_downcase
        | if test("embed|rerank") then "non-generative (inferred from name)" else "generative" end;
    {
        schema_version: 1,
        source: {
            status_page: "https://llm.ai.e-infra.cz/status/",
            api: "https://llm.ai.e-infra.cz/status/api/v1/models",
            refresh_command: "scripts/update_llm_models.sh",
            note: ("Observed fields come from the status API. `note` is curated by hand and is "
                + "preserved across refreshes; the API exposes no capability or context-length data. "
                + "To record what we know about a model, edit its `note` in the committed file; "
                + "a note naming DEFAULT_MODEL or DEFAULT_VISION_MODEL is required by "
                + "tests/test_llm_model_catalog.py. Every other field is overwritten.")
        },
        observed_at: (now | strftime("%Y-%m-%dT%H:%M:%SZ")),
        previous_observed_at: $previous_observed_at,
        models: [
            .[]
            | {
                name: .model_name,
                status: .status,
                first_seen: .first_seen,
                last_seen: .last_seen,
                task_class: task_class,
                note: ($notes[.model_name] // "Not yet reviewed by aoptk maintainers."),
                # Everything below is a snapshot of the moment of the refresh, not a fact about
                # the model: throughput moves every sample and `uptime` is a rolling window. `--check`
                # ignores it so a weekly run opens a PR over new or retired models, not over noise.
                snapshot: {
                    uptime_samples_online: ((.uptime // []) | uptime_true),
                    uptime_samples_total: ((.uptime // []) | length),
                    generation_tokens_rate: (.latest.generation_tokens_rate | number_or_null),
                    requests_running: (.latest.num_requests_running | number_or_null),
                    requests_waiting: (.latest.num_requests_waiting | number_or_null)
                }
            }
        ] | sort_by(.name | ascii_downcase)
    }
' "${payload}" > "${refreshed}"

if [[ "${check_only}" == "true" ]]; then
    if [[ ! -f "${catalog}" ]] || ! cmp -s \
            <(jq -S "${strip_volatile}" "${refreshed}") \
            <(jq -S "${strip_volatile}" "${catalog}"); then
        echo "catalog is out of date with ${status_api}"
        exit 1
    fi
    echo "catalog matches ${status_api}"
    exit 0
fi

cp "${refreshed}" "${catalog}"
echo "wrote ${catalog}"
