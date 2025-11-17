import pdfplumber
import pandas as pd

class ExtractColumns:
    def __init__(self):
        self.columns_data = []

    def extract_columns(self, pdf_path: str):
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables()
                for table_num, table in enumerate(tables):
                    if not table:
                        continue
                    # Assume first non-empty row is header
                    for row in table:
                        if row and any(cell.strip() for cell in row if cell):
                            cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                            self.columns_data.append({
                                "page_num": page_num,
                                "table_num": table_num,
                                "columns": cleaned_row
                            })
                            break  # Only take the first row as header
        return self.columns_data

# --- Usage ---
extractor = ExtractColumns()
columns_info = extractor.extract_columns("test1.pdf")

# Display results
for info in columns_info:
    print(f"Page {info['page_num']} | Table {info['table_num']} | Columns: {info['columns']}")

# Optional: save as CSV for reference
df = pd.DataFrame(columns_info)
df.to_csv("pdf_columns.csv", index=False)
print("✅ Column extraction complete.")
