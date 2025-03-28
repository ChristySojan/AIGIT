import subprocess
import json

def get_git_log():
    """Extract Git commit history with branches and merges."""
    log_format = "--pretty=format:{\"hash\": \"%h\", \"parent\": \"%p\", \"message\": \"%s\", \"branch\": \"%d\"}"
    result = subprocess.run(["git", "log", "--all", "--decorate=short", log_format], capture_output=True, text=True)

    commits = []
    for line in result.stdout.split("\n"):
        if line.strip():
            commit = json.loads(line)
            commit["branches"] = extract_branch_names(commit["branch"])  # Extract all branch names
            commits.append(commit)

    with open("git_log.json", "w") as f:
        json.dump(commits, f, indent=2)

    print("✅ Git log exported to git_log.json")

def extract_branch_names(decorate_str):
    """
    Extracts all branch names from the --decorate field.
    """
    if "(" in decorate_str:
        # Extract everything inside parentheses and split by commas
        branches = decorate_str.split("(")[-1].split(")")[0].split(", ")
        # Clean up branch names (e.g., remove "HEAD ->" or "origin/")
        branches = [b.replace("HEAD -> ", "").replace("origin/", "").strip() for b in branches]
        return branches
    return ["main"]  # Default to "main" if no branches are found

if __name__ == "__main__":
    get_git_log()
