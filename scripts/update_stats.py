"""Regenerates assets/stats.svg from live GitHub data. Standard library only."""
import json
import os
import urllib.request

USER = "imantha3725"
OUT = "assets/stats.svg"

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      totalCount
      nodes { stargazerCount }
    }
    contributionsCollection { totalCommitContributions }
  }
}
"""


def fetch_stats():
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"},
    )
    with urllib.request.urlopen(req) as res:
        data = json.load(res)["data"]["user"]
    repos = data["repositories"]
    return {
        "repos": repos["totalCount"],
        "stars": sum(n["stargazerCount"] for n in repos["nodes"]),
        "commits": data["contributionsCollection"]["totalCommitContributions"],
    }


def tile(x, value, label, accent="#ff6b35"):
    return f"""    <g transform="translate({x},0)">
      <rect x="0.5" y="0.5" width="269" height="149" rx="12" fill="#0b0b10" stroke="#24242f"/>
      <rect x="24" y="0" width="48" height="3" rx="1.5" fill="{accent}"/>
      <text x="24" y="78" font-size="44" font-weight="700" fill="#f2f2f5">{value}</text>
      <text x="24" y="112" font-size="14" fill="#8b8b99">{label}</text>
    </g>"""


def render(s):
    tiles = [
        tile(0, f"{s['repos']:,}", "Public repositories"),
        tile(310, f"{s['commits']:,}", "Commits in the last year"),
        tile(620, f"{s['stars']:,}", "Stars earned"),
        tile(930, "Open", "Available for full-time work", "#3ddc84"),
    ]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 150" width="1200" height="150" role="img" aria-label="{s['repos']} public repositories, {s['commits']} commits in the last year, {s['stars']} stars, open to work">
  <g font-family="'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif">
{chr(10).join(tiles)}
  </g>
</svg>
"""


if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(fetch_stats()))
    print("Updated", OUT)
