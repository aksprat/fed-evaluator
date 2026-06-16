import json
import pandas as pd

with open("data/issues_snapshot.json") as f:
    issues = json.load(f)


CATEGORIES = {

    "documentation": [
        "documentation",
        "doc",
        "docs",
        "syntax",
        "example",
        "examples",
        "usage",
        "help",
        "typo",
        "permission",
        "rendering",
        "incomplete"
    ],

    "question": [
        "how",
        "why",
        "unclear",
        "confused",
        "receiving",
        "what"
    ],

    "security": [
        "token",
        "credential",
        "secret",
        "permission denied",
        "auth",
        "stdout",
        "key"
    ],

    "enhancement": [
        "feature",
        "support",
        "add",
        "improve",
        "enhance",
        "integration",
        "api key",
        "arm"
    ],

    "other": [
        "duplicate",
        "unclear",
        "misc"
    ]
}


for category, keywords in CATEGORIES.items():

    rows = []

    for issue in issues:

        title = issue["title"].lower()

        if any(keyword in title for keyword in keywords):

            rows.append(
                {
                    "issue_number": issue["number"],
                    "title": issue["title"],
                    "github_labels": ",".join(issue["labels"])
                }
            )

    df = pd.DataFrame(rows)

    output_file = f"mining_result/candidate_{category}.csv"

    df.to_csv(output_file, index=False)

    print(category, len(df))
