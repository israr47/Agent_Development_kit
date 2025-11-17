import pdfplumber 
import pandas as pd
import json

class ExtractData:
    def __init__(self):
        self.workout_data = []
        self.context_data = []

    def load_data(self, path: str):
        with  pdfplumber.open(path) as pdf:
            for page_num, pages in enumerate(pdf.pages,1):
                print(f"processing the page {page_num} ...")

                # Extract the tables from pdf
                tables = pages.extract_tables()

                # Extracting the Table Number and Table Context
                for table_num, table in enumerate(tables): # enumerate will indexing the table automatically
                    if not table:
                        continue
                    print(f"table {table_num+1}: {len(table)} row")

                    # Extracting The Row Number and the context of row
                    for row_num, row in enumerate(table):
                        """Check if it is not row and the missing and empty rows. Replacing with the whitespace String then continue"""
                        if not row or all(str(cell).strip() == "" for cell in row):
                            continue
                        """IT will remove the all whitespace tabs and 
                        condition for every cell in row if the cell has value clean it and add it new list if not the value replace with empty string 
                        """
                        cleaned_row = [str(cell).strip() if cell else '' for cell in row]
                        """This will call the method parse_excerise_data after the execution of
                        method then remaining part will executes
                         """
                        exercise_data = self.parse_excerise_data(cleaned_row, page_num, table_num)

                        if exercise_data:
                            self.workout_data.append(exercise_data)
        return self.workout_data
    

    #This Method will convert the raw data of row into the structured data 
    def parse_excerise_data(self , row , page_num, table_num):
        # skip the row if empty or the first header row or empty row also skip them and all the cell which are empty or string empty skip them 
        if not row or row[0].strip() in ["Exercise",''] or all (str(cell).strip()=='' for cell in row ):
            return None
        # Define target keys in order
        keys = ['exercise_name', 'sets', 'reps', 'weight', 'distance', 'time', 'rest', 'notes']
        exercise_data = {key: "" for key in keys}
        exercise_data.update({'page_num':page_num , "table_num":table_num , "workout_type": '', "day":""})
        for i,key in enumerate(keys):
            if i < len(row):
                exercise_data[key] = str(row[i]).strip()
            
        return exercise_data
    def extract_text_for_context(self,path:str):
        with  pdfplumber.open(path) as pdf:
            for page_num, pages in enumerate(pdf.pages,1):
                print(f"processing the page {page_num} ...")

                # Extract the tables from pdf
                text = pages.extract_text() or ""
                self.context_data.append({"page_num":page_num , 'text':text})
            
        return self.context_data

extract = ExtractData()
data = extract.load_data("test1.pdf")

df = pd.DataFrame(data)

df.to_csv("workout_data.csv", index=False)

with open("workout_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


context_data = extract.extract_text_for_context("test1.pdf")
with open("pdf_context.json", "w", encoding="utf-8") as f:
    json.dump(context_data, f, ensure_ascii=False, indent=4)
        