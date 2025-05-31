import pandas as pd
from pathlib import Path
from html import unescape            # decode &amp; → &
from urllib.parse import unquote     # decode %20   → space
from ftfy import fix_text



INPUT_FILE  = "old_submissions.csv"
OUTPUT_FILE = "cleaned_old_submissions.csv"
REMOVED_OUT = "removed_old_subs.csv"

# ────────────────────────────────────────────────────────────────────────────────
# 1. helper to decode http / html entities
# ────────────────────────────────────────────────────────────────────────────────
def decode_http_entities(text: str) -> str:
    """
    Decode two levels of encoding that often appear in scraped Reddit text:
        1. Percent-encoding     (%20, %3C, etc.)   via urllib.parse.unquote
        2. HTML entities        (&amp;, &#39;)       via html.unescape
    Works even if text is NaN or not a string.
    """
    if not isinstance(text, str):
        return text
    return unescape(unquote(text))

# ────────────────────────────────────────────────────────────────────────────────
# 2. load data
# ────────────────────────────────────────────────────────────────────────────────
print("Reading CSV …")
df = pd.read_csv(INPUT_FILE, dtype=str)        # read everything as string first, skip bad lines

print(f"Original rows: {len(df):,}")

# ────────────────────────────────────────────────────────────────────────────────
# 3. drop exact duplicates
# ────────────────────────────────────────────────────────────────────────────────
df = df.drop_duplicates()                      # all-column dedup
print(f"After duplicate removal: {len(df):,}")

# ────────────────────────────────────────────────────────────────────────────────
# 4. decode HTTP/HTML entities in text-bearing columns
# ────────────────────────────────────────────────────────────────────────────────
TEXT_COLS = ["title", "text", "url"]           # adjust if your schema differs
for col in TEXT_COLS:
    if col in df.columns:
        df[col] = df[col].apply(decode_http_entities)

# ────────────────────────────────────────────────────────────────────────────────
# 5. convert created_utc (Unix seconds) → timezone-aware datetime in UTC
# ────────────────────────────────────────────────────────────────────────────────
if "created_utc" in df.columns:
    df["created_datetime"] = pd.to_datetime(
        df["created_utc"].astype(float), unit="s", utc=True, errors="coerce"
    )

# ────────────────────────────────────────────────────────────────────────────────
# 6. find rows containing “[removed]” (case-insensitive)
# ────────────────────────────────────────────────────────────────────────────────
mask_removed = df["text"].str.contains(r"\[removed\]", case=False, na=False)
removed_rows = df[mask_removed]
print(f"Rows with '[removed]': {len(removed_rows):,}")

# ────────────────────────────────────────────────────────────────────────────────
# 7. After all previous cleaning steps, apply ftfy to all string columns for further decoding/fixing
# ────────────────────────────────────────────────────────────────────────────────
fix_cols = df.select_dtypes(include=["object"]).columns
for col in fix_cols:
    df[col] = df[col].apply(lambda x: fix_text(x) if isinstance(x, str) else x)

# ────────────────────────────────────────────────────────────────────────────────
# 8. save outputs
# ────────────────────────────────────────────────────────────────────────────────
df.to_csv(OUTPUT_FILE, index=False)
removed_rows.to_csv(REMOVED_OUT, index=False)

# Save the fully decoded CSV
final_output = "cleaned_reddit_old_submissions.csv"
df.to_csv(final_output, index=False)

print(f"\n✔ Cleaned data  ➜  {OUTPUT_FILE}")
print(f"✔ '[removed]'   ➜  {REMOVED_OUT}")
print(f"✔ All HTTP/HTML entities and text issues fixed. Output ➜ {final_output}")
