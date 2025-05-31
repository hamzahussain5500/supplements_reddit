import pandas as pd
from ftfy import fix_text

# File paths
file_25 = "cleaned_reddit_old_comments.csv"
file_27 = "cleaned_reddit_old_submissions.csv"
output_file = "merged_supplements_old_data.csv"

# Read both CSVs
print("Reading CSV files ...")
df_25 = pd.read_csv(file_25, dtype=str)  # read everything as string first, skip bad lines
df_27 = pd.read_csv(file_27, dtype=str)

# Concatenate and drop duplicates
original_rows_25 = len(df_25)
original_rows_27 = len(df_27)
merged_df = pd.concat([df_25, df_27], ignore_index=True)
merged_before = len(merged_df)
merged_df = merged_df.drop_duplicates()
merged_after = len(merged_df)

# Remove rows where author is 'AutoModerator' (case-sensitive)
merged_df = merged_df[merged_df['author'] != 'AutoModerator']
merged_after = len(merged_df)

# Decode all unicode issues in every string column using ftfy
for col in merged_df.select_dtypes(include=["object"]).columns:
    merged_df[col] = merged_df[col].apply(lambda x: fix_text(x) if isinstance(x, str) else x)

# Convert created_utc to a new column 'date_time' (timezone-aware UTC datetime)
if 'created_utc' in merged_df.columns:
    merged_df['date_time'] = pd.to_datetime(
        merged_df['created_utc'].astype(float), unit='s', utc=True, errors='coerce'
    )

# Save merged CSV
merged_df.to_csv(output_file, index=False)

# Calculate stats
rows_gained = merged_after - max(original_rows_25, original_rows_27)
rows_lost = merged_before - merged_after

print(f"Rows in reddit_supplements_25.csv: {original_rows_25}")
print(f"Rows in reddit_supplements_27.csv: {original_rows_27}")
print(f"Rows after merge and deduplication: {merged_after}")
print(f"Rows gained (vs. largest input): {rows_gained}")
print(f"Rows lost (duplicates removed): {rows_lost}")
print(f"✔ Merged CSV saved as {output_file}")
