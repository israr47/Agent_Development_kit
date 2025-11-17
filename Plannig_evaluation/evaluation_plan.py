import pandas as pd

# Load your CSV
df = pd.read_csv("Test_1.csv")

# Columns containing YES/NO evaluation labels
yes_no_columns = ["sets", "reps", "weight", "distance", "time", "rest", "notes", "YOUTUBE_LINK"]

results = []

for col in yes_no_columns:
    if col not in df.columns:
        continue

    # Normalize values
    col_values = df[col].astype(str).str.upper().str.strip()

    yes_count = col_values.eq("YES").sum()
    no_count = col_values.eq("NO").sum()
    total = yes_count + no_count

    accuracy = (yes_count / total * 100) if total > 0 else 0

    results.append({
        "column": col,
        "correct_yes": yes_count,
        "incorrect_no": no_count,
        "total": total,
        "accuracy_percent": round(accuracy, 2)
    })

# Convert to DataFrame for clean display
results_df = pd.DataFrame(results)

print("===== COLUMN-WISE ACCURACY =====")
print(results_df)

# Also print overall accuracy
overall_yes = results_df["correct_yes"].sum()
overall_total = results_df["total"].sum()
overall_accuracy = (overall_yes / overall_total * 100) if overall_total > 0 else 0

print("\n===== OVERALL MODEL ACCURACY =====")
print(f"Overall Accuracy: {overall_accuracy:.2f}%")
print(f"Total Correct: {overall_yes}")
print(f"Total Incorrect: {overall_total - overall_yes}")
