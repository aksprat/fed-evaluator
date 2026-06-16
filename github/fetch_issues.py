import json
import requests
from tqdm import tqdm

OWNER = "digitalocean"
REPO = "doctl"

BASE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/issues"

all_issues = []

page = 1

while True:

    params = {
        "state": "all",
        "per_page": 100,
        "page": page
    }

    response = requests.get(BASE_URL, params=params)

# End of pagination
    if response.status_code == 422:
         print("Reached end of issue pages")
         break

    response.raise_for_status()

    issues = response.json()

    if len(issues) == 0:
         break

    for issue in issues:

        # Ignore PRs
        if "pull_request" in issue:
            continue

        all_issues.append(
            {
                "number": issue["number"],
                "title": issue["title"],
                "body": issue["body"],
                "labels": [l["name"] for l in issue["labels"]],
                "state": issue["state"],
                "created_at": issue["created_at"],
                "closed_at": issue["closed_at"],
                "html_url": issue["html_url"]
            }
        )

    print(f"Fetched page {page}")

    page += 1


print("Total issues:", len(all_issues))

with open("data/issues_snapshot.json", "w") as f:
    json.dump(all_issues, f, indent=2)
