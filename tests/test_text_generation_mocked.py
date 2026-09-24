import pytest
from pytest_mock import MockerFixture
from aoptk.chemical import Chemical
from aoptk.text_generation_api import TextGenerationAPI


@pytest.mark.parametrize(
    ("mock_prompt_response", "expected_chemicals"),
    [
        ("\n- thioacetamide", []),
        ("\n* methotrexate", []),
        ("\n1. acetaminophen", []),
        ("\nthioacetamide", []),
        ("- thioacetamide\n- methotrexate", []),
        ("1. numbered list\n2. item two", []),
        ("thioacetamide", [Chemical("thioacetamide")]),
        ("thioacetamide ; methotrexate", [Chemical("thioacetamide"), Chemical("methotrexate")]),
        ("acetaminophen", [Chemical("acetaminophen")]),
        ("PCB-123 ; thioacetamide", [Chemical("pcb-123"), Chemical("thioacetamide")]),
    ],
)
def test_find_chemicals_with_invalid_and_valid_responses(
    mocker: MockerFixture,
    mock_prompt_response: str,
    expected_chemicals: list[Chemical],
):
    """Test that find_chemicals returns empty list for invalid responses and chemicals for valid ones."""
    api = TextGenerationAPI()
    mocker.patch.object(api, "_prompt", return_value=mock_prompt_response)

    result = api.find_chemicals("some input text")

    if expected_chemicals:
        assert [chem.name for chem in result] == [chem.name for chem in expected_chemicals]
    else:
        assert result == []
