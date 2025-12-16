import sys
import time
import pandas as pd
from Bio import Entrez
from openpyxl import load_workbook


# Check if the database and master table files are correctly formatted
def get_column_index(header, col_name):
    try:
        return header.index(col_name)
    except ValueError:
        print(f"Error: '{col_name}' column not found. It must be called '{col_name}'.")
        sys.exit(1)


# database_path = args.database
# master_table_path = args.master_table
# Entrez.email = args.email
# search_code = args.search_code
# search_term = args.search_term
# db_choice = args.db_choice

def main():
    

    if master_table_path:
        master_wb = load_workbook(master_table_path)
        master_ws = master_wb.active
        header = [cell.value for cell in master_ws[1]]
        master_id_col = get_column_index(header, "ID")
        master_search_code = get_column_index(header, "Search code")

    # Choose the database to search, see how many results.
    if db_choice == "europepmc":
        all_data = fetch_data_europepmc(search_term, search_code)
    elif db_choice == "pubmed":
        all_data = fetch_data_pubmed(search_term, search_code)



    # Save all_data to an Excel file
    read_publications = pd.read_excel(database_path)

    updated_read_publications = pd.concat(
        [
            read_publications,
            pd.DataFrame(
                all_data,
                columns=[
                    "id",
                    "year_publication",
                    "authors",
                    "title",
                    "search_term",
                    "search_code",
                    "search_date",
                    "database",
                ],
            ),
        ],
        ignore_index=True,
    )
    updated_read_publications.to_excel("updated_read_publications.xlsx", index=False)

    # Get the list of publications to read
    existing_ids = set(read_publications["id"].dropna().astype(str))
    to_read_data = [row for row in all_data if str(row[0]) not in existing_ids]

    # Save to_read_data to an Excel file
    df_to_read_data = pd.DataFrame(
        to_read_data,
        columns=["id", "year_publication", "authors", "title", "search_term", "search_code", "search_date", "database"],
    )
    df_to_read_data.to_excel("read.xlsx", index=False)  # Add the search code to the name.

    # Generate a new updated master table (preserving original formatting)
    if master_table_path:
        master_wb = load_workbook(master_table_path)
        master_ws = master_wb.active

        # Map IDs to all their row indices in master_ws
        master_id_map = {}
        for idx, row in enumerate(master_ws.iter_rows(min_row=2, values_only=True), start=2):
            row_id = str(row[master_id_col]) if row[master_id_col] else None
            if row_id:
                master_id_map.setdefault(row_id, []).append(idx)

        # Find common IDs in the master table and data from the search
        all_data_ids = [str(row[0]) for row in all_data if row[0] is not None]
        common_ids = set(all_data_ids).intersection(master_id_map.keys())

        # Update search codes for all instances of common IDs (in-place, preserving formatting)
        for row in all_data:
            row_id = str(row[0])
            if row_id in common_ids:
                for excel_row_idx in master_id_map[row_id]:
                    cell = master_ws.cell(row=excel_row_idx, column=master_search_code + 1)
                    current_value = cell.value
                    updated_value = f"{current_value} ; {search_code}" if current_value else search_code
                    cell.value = updated_value

        # Save as a new master table
        master_wb.save("updated_master_table.xlsx")
        print(f"Number of common IDs between search results and master table: {len(common_ids)}.")


if __name__ == "__main__":
    main()
