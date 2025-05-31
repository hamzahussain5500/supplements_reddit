import praw
import csv
import time

# ========================
# 1. Set up your credentials
# ========================
# Replace these with your own values from https://www.reddit.com/prefs/apps
CLIENT_ID = 'fXL-N9O4F3NUrYhdBSXu4g'
CLIENT_SECRET = '6Vd7R42k15Wd1Ru3ZBOyl_B-26tdpw'
USER_AGENT = 'Supplemeter'

# ========================
# 2. Initialize PRAW
# ========================
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

SUBREDDIT_NAME = "Supplements"
LIMIT = 1000
csv_filename = "reddit_supplements_new.csv"

headers = [
    "type", "id", "parent_id", "score", "title", "upvote_ratio", "comment_depth", "text",
    "author", "created_utc", "num_comments", "flair", "url"
]

def fetch_submission_data(submission):
    # Only process text posts
    if not submission.is_self:
        return []
    submission_row = [
        "submission",
        submission.id,
        "",
        submission.score,
        submission.title,
        getattr(submission, 'upvote_ratio', ''),
        "",
        submission.selftext if submission.selftext else "",
        str(submission.author) if submission.author else "[deleted]",
        getattr(submission, 'created_utc', ''),
        getattr(submission, 'num_comments', ''),
        getattr(submission, 'link_flair_text', ''),
        submission.url
    ]
    rows = [submission_row]
    try:
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            comment_row = [
                "comment",
                comment.id,
                submission.id,
                comment.score,
                "",
                "",
                comment.depth,
                comment.body,
                str(comment.author) if comment.author else "[deleted]",
                getattr(comment, 'created_utc', ''),
                "",
                getattr(comment, 'author_flair_text', ''),
                "",
                ""
            ]
            rows.append(comment_row)
    except Exception as e:
        print(f"Error fetching comments for {submission.id}: {e}")
    return rows

# ========================
# 4. Collect Data
# ========================

if __name__ == "__main__":
    print(f"Collecting up to {LIMIT} text submissions from r/{SUBREDDIT_NAME} using PRAW...")
    subreddit = reddit.subreddit(SUBREDDIT_NAME)
    submissions = subreddit.new(limit=LIMIT)
    with open(csv_filename, mode="w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        for i, submission in enumerate(submissions, 1):
            try:
                rows = fetch_submission_data(submission)
                for row in rows:
                    writer.writerow(row)
            except Exception as e:
                print(f"Error with submission {getattr(submission, 'id', 'unknown')}: {e}")
            if i % 100 == 0:
                print(f"Processed {i} submissions...")
    print(f"Data successfully written to {csv_filename}")
