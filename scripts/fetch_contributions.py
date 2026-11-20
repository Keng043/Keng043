"""Fetch the contribution calendar via GitHub GraphQL -> data/contributions.json"""
import json, os, urllib.request

LOGIN = os.environ.get("GH_LOGIN", "Keng043")
TOKEN = os.environ["GH_TOKEN"]
QUERY = """query($login:String!){user(login:$login){contributionsCollection{
contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
    headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=30) as r:
    payload = json.load(r)

cal = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
days = [{"date": d["date"], "count": d["contributionCount"]}
        for w in cal["weeks"] for d in w["contributionDays"]]
os.makedirs("data", exist_ok=True)
with open("data/contributions.json", "w") as f:
    json.dump({"total": cal["totalContributions"], "days": days}, f)
print("saved", len(days), "days")
