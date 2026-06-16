import json
import pandas as pd

VALID_LABELS = {
    "bug",
    "enhancement",
    "question",
    "documentation"
}

with open("data/issues_snapshot.json") as f:
    issues = json.load(f)

rows = []

for issue in issues:

    labels = set(label.lower() for label in issue["labels"])

    intersection = labels.intersection(VALID_LABELS)

    if len(intersection) == 1:

        rows.append(
            {
                "issue_number": issue["number"],
                "title": issue["title"],
                "ground_truth": list(intersection)[0]
            }
        )

df = pd.DataFrame(rows)

print(df.head())

print("Total candidate issues:", len(df))

df.to_csv(
    "data/ground_truth_candidates.csv",
    index=False
)
