#!/usr/bin/env python3
"""CLI tool to bootstrap GitHub repos with common project management structure."""

import argparse
import json
import subprocess
import sys

LABELS = [
    {"name": "bug", "color": "d73a4a", "description": "Something isn't working"},
    {"name": "feature", "color": "a2eeef", "description": "New feature request"},
    {"name": "enhancement", "color": "84b6eb", "description": "Improvement to existing functionality"},
    {"name": "documentation", "color": "0075ca", "description": "Improvements or additions to documentation"},
    {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
    {"name": "help wanted", "color": "008672", "description": "Extra attention is needed"},
    {"name": "question", "color": "d876e3", "description": "Further information is requested"},
    {"name": "wontfix", "color": "ffffff", "description": "This will not be worked on"},
]

ISSUES = [
    {"title": "README setup", "body": "Create a comprehensive README with project description, installation instructions, and usage examples."},
    {"title": "Add LICENSE", "body": "Choose and add an appropriate open-source license to the repository."},
    {"title": "Set up CI/CD", "body": "Configure continuous integration and deployment pipelines (e.g. GitHub Actions)."},
    {"title": "Create contributing guidelines", "body": "Add a CONTRIBUTING.md with guidelines for how others can contribute to the project."},
]

MILESTONES = [
    {"title": "v0.1 - Initial Setup", "description": "Basic project scaffolding and repository configuration."},
    {"title": "v0.2 - Core Features", "description": "Implement the core functionality of the project."},
    {"title": "v1.0 - First Release", "description": "Stable first public release."},
]


def suggest(repo):
    """Print suggested labels, issues, and milestones."""
    print(f"Suggestions for {repo}\n")

    print("Labels:")
    print(f"  {'Name':<20} {'Color':<10} Description")
    print(f"  {'-'*20} {'-'*10} {'-'*40}")
    for label in LABELS:
        print(f"  {label['name']:<20} #{label['color']:<9} {label['description']}")

    print(f"\nIssues:")
    print(f"  {'Title':<35} Description")
    print(f"  {'-'*35} {'-'*50}")
    for issue in ISSUES:
        print(f"  {issue['title']:<35} {issue['body'][:50]}")

    print(f"\nMilestones:")
    print(f"  {'Title':<25} Description")
    print(f"  {'-'*25} {'-'*50}")
    for ms in MILESTONES:
        print(f"  {ms['title']:<25} {ms['description']}")


def run_gh(args, repo, check=True):
    """Run a gh CLI command and return the result."""
    cmd = ["gh"] + args + ["-R", repo]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        return False, result.stderr.strip()
    return True, result.stdout.strip()


def setup(repo):
    """Apply suggestions to the repo via gh CLI."""
    print(f"Setting up project structure for {repo}\n")

    # Create labels
    print("Creating labels...")
    for label in LABELS:
        ok, msg = run_gh(
            ["label", "create", label["name"],
             "--color", label["color"],
             "--description", label["description"],
             "--force"],
            repo,
        )
        if ok:
            print(f"  [ok] {label['name']}")
        else:
            print(f"  [err] {label['name']}: {msg}")

    # Create milestones (via gh api, no direct CLI command)
    print("\nCreating milestones...")
    for ms in MILESTONES:
        payload = json.dumps({"title": ms["title"], "description": ms["description"]})
        cmd = [
            "gh", "api",
            f"repos/{repo}/milestones",
            "--method", "POST",
            "--input", "-",
        ]
        result = subprocess.run(cmd, input=payload, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  [ok] {ms['title']}")
        else:
            err = result.stderr.strip()
            if "already_exists" in err or "Validation Failed" in err:
                print(f"  [skip] {ms['title']}: already exists")
            else:
                print(f"  [err] {ms['title']}: {err}")

    # Create issues (skip if an open issue with the same title already exists)
    print("\nCreating issues...")
    ok, existing = run_gh(
        ["issue", "list", "--state", "all", "--limit", "100", "--json", "title"],
        repo,
    )
    existing_titles = set()
    if ok and existing:
        existing_titles = {i["title"] for i in json.loads(existing)}

    for issue in ISSUES:
        if issue["title"] in existing_titles:
            print(f"  [skip] {issue['title']}: already exists")
            continue
        ok, msg = run_gh(
            ["issue", "create",
             "--title", issue["title"],
             "--body", issue["body"]],
            repo,
        )
        if ok:
            url = msg.splitlines()[-1] if msg else ""
            print(f"  [ok] {issue['title']} {url}")
        else:
            print(f"  [err] {issue['title']}: {msg}")

    print("\nDone!")


def main():
    parser = argparse.ArgumentParser(
        description="Bootstrap GitHub repos with common project management structure."
    )
    parser.add_argument("--repo", required=True, help="GitHub repo in owner/repo format")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("suggest", help="Print suggested labels, issues, and milestones")
    subparsers.add_parser("setup", help="Apply suggestions to the repo via gh CLI")

    args = parser.parse_args()

    if args.command == "suggest":
        suggest(args.repo)
    elif args.command == "setup":
        setup(args.repo)


if __name__ == "__main__":
    main()
