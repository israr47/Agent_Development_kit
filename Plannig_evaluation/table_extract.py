import pdfplumber 
import pandas as pd
import json
import re

class ExtractData:
    def __init__(self):
        self.workout_data = []
        self.context_data = []
        self.current_week = ""
        self.current_day = ""
        self.current_block = ""

    def load_data(self, path: str):
        with pdfplumber.open(path) as pdf:
            for page_num, pages in enumerate(pdf.pages, 1):
                print(f"processing the page {page_num} ...")

                # Extract text first to get week and day context
                page_text = pages.extract_text() or ""
                self._extract_week_day_from_text(page_text)

                # Extract the tables from pdf
                tables = pages.extract_tables()

                for table_num, table in enumerate(tables):
                    if not table:
                        continue
                    print(f"table {table_num+1}: {len(table)} rows")

                    for row_num, row in enumerate(table):
                        if not row or all(str(cell).strip() == "" for cell in row):
                            continue
                        
                        cleaned_row = [str(cell).strip() if cell else '' for cell in row]
                        
                        # Update week/day from row if found
                        self._extract_week_day_from_row(cleaned_row)
                        
                        # Extract block type
                        self._extract_block_type(cleaned_row)
                        
                        # Parse exercise data
                        exercise_data = self.parse_exercise_data(cleaned_row, page_num, table_num)
                        
                        if exercise_data:
                            self.workout_data.append(exercise_data)
        return self.workout_data

    def _extract_week_day_from_text(self, text):
        """Extract week and day from page text"""
        week_pattern = r'Week\s+(\d+)'
        day_pattern = r'Day\s+(\d+)\s*-\s*(DAY\s+\d+|Workout\s*#\d+)'
        
        week_match = re.search(week_pattern, text, re.IGNORECASE)
        day_match = re.search(day_pattern, text, re.IGNORECASE)
        
        if week_match:
            self.current_week = f"Week {week_match.group(1)}"
        
        if day_match:
            day_num = day_match.group(1)
            day_type = day_match.group(2)
            self.current_day = f"Day {day_num} - {day_type}"

    def _extract_week_day_from_row(self, row):
        """Extract week and day from row data"""
        row_text = ' '.join([str(cell) for cell in row if str(cell).strip()])
        
        week_pattern = r'Week\s+(\d+)'
        day_pattern = r'Day\s+(\d+)\s*-\s*(DAY\s+\d+|Workout\s*#\d+)'
        
        week_match = re.search(week_pattern, row_text, re.IGNORECASE)
        day_match = re.search(day_pattern, row_text, re.IGNORECASE)
        
        if week_match:
            self.current_week = f"Week {week_match.group(1)}"
        
        if day_match:
            day_num = day_match.group(1)
            day_type = day_match.group(2)
            self.current_day = f"Day {day_num} - {day_type}"

    def _extract_block_type(self, row):
        """Extract block type from row (CORE, Superset, DYNAMIC WARM UP, etc.)"""
        if not row or not row[0]:
            return
            
        first_cell = str(row[0]).strip().upper()
        
        # Check for CORE blocks
        if 'CORE' in first_cell or 'FORE' in first_cell:
            self.current_block = row[0]
        # Check for Superset blocks
        elif 'SUPERSET' in first_cell:
            self.current_block = row[0]
        # Check for Dynamic Warm Up blocks
        elif 'DYNAMIC WARM UP' in first_cell or 'WARM UP' in first_cell:
            self.current_block = row[0]
        # Check for other specific blocks
        elif any(keyword in first_cell for keyword in ['STAFF MEMBER NOTES', 'WORKOUT RECOMMENDATIONS']):
            self.current_block = row[0]
        # If it's an exercise row without a block header, keep the current block
        elif len(row) > 1 and row[1].strip() and not any(keyword in first_cell for keyword in ['WEEK', 'DAY', 'WORKOUT DATE']):
            # This is likely an exercise row, keep current block
            pass
        else:
            # Reset block for header rows or unknown formats
            if not any(keyword in first_cell for keyword in ['WEEK', 'DAY', 'WORKOUT DATE', 'EXERCISE']):
                self.current_block = ""

    def parse_exercise_data(self, row, page_num, table_num):
        """Parse exercise data with 11 columns including week, day, block"""
        # Skip header rows and empty rows
        if not row or row[0].strip() in ["Exercise", ""] or all(str(cell).strip() == '' for cell in row):
            return None
        
        # Skip rows that are clearly headers (contain Week, Day, Workout Date, etc.)
        row_text = ' '.join([str(cell) for cell in row]).upper()
        if any(keyword in row_text for keyword in ['WEEK', 'DAY', 'WORKOUT DATE', 'TOTAL WORKOUT TIME']):
            return None
        
        # Check if this is an exercise row (should have exercise name)
        if len(row) < 2 or not row[1].strip():
            return None
        
        # Define target keys for 11 columns
        keys = ['week', 'day', 'block', 'exercise_name', 'sets', 'reps', 'weight', 'distance', 'time', 'rest', 'notes']
        exercise_data = {key: "" for key in keys}
        
        # Add week, day, block context
        exercise_data['week'] = self.current_week
        exercise_data['day'] = self.current_day
        exercise_data['block'] = self.current_block
        exercise_data['page_num'] = page_num
        exercise_data['table_num'] = table_num
        
        # Map row data to exercise columns
        # Skip the first cell if it's a block identifier and use subsequent cells for exercise data
        start_index = 0
        if self.current_block and row[0].strip() == self.current_block.strip():
            start_index = 1
        
        # Fill exercise data starting from appropriate column
        exercise_columns = ['exercise_name', 'sets', 'reps', 'weight', 'distance', 'time', 'rest', 'notes']
        for i, key in enumerate(exercise_columns):
            source_index = start_index + i
            if source_index < len(row) and row[source_index]:
                exercise_data[key] = str(row[source_index]).strip()
        
        # Special handling for rows where block and exercise are in the same row
        if start_index == 0 and self.current_block and row[0].strip() and not any(keyword in row[0].upper() for keyword in ['CORE', 'SUPERSET', 'WARM UP']):
            # This might be an exercise name in the first column
            exercise_data['exercise_name'] = row[0].strip()
        
        return exercise_data

    def extract_text_for_context(self, path: str):
        with pdfplumber.open(path) as pdf:
            for page_num, pages in enumerate(pdf.pages, 1):
                print(f"processing the page {page_num} ...")
                text = pages.extract_text() or ""
                self.context_data.append({"page_num": page_num, 'text': text})
        return self.context_data

# Usage
extract = ExtractData()
data = extract.load_data("test1.pdf")

df = pd.DataFrame(data)

# Reorder columns to have week, day, block first
column_order = ['week', 'day', 'block', 'exercise_name', 'sets', 'reps', 'weight', 'distance', 'time', 'rest', 'notes', 'page_num', 'table_num']
df = df[column_order]

df.to_csv("workout_data_11_columns.csv", index=False)

with open("workout_data_11_columns.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Extracted {len(data)} exercise records")
print("Columns:", df.columns.tolist())

# Also extract context data
context_data = extract.extract_text_for_context("test1.pdf")
with open("pdf_context.json", "w", encoding="utf-8") as f:
    json.dump(context_data, f, ensure_ascii=False, indent=4)