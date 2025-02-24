import os
import sys
import subprocess
import requests

# Set API Key securely (DO NOT HARDCODE API KEYS)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCmHRnLQGQffYDsIILLclyXawwHC33h96k")  
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
HEADERS = {"Content-Type": "application/json"}

def get_git_command(natural_text):
    """Converts natural language input to a Git command using Gemini API and cleans the output."""
    payload = {
        "contents": [{"parts": [{"text": f"Convert this to a Git command only, no explanation: {natural_text}"}]}]
    }

    try:
        response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", json=payload, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])

            if parts:
                git_command = parts[0]["text"].strip()
                git_command = git_command.replace("```bash", "").replace("```", "").replace("`", "").strip()
                git_command = git_command.replace(";", " && ")
                print(f"\n🔹 Suggested Git Command:\n   {git_command}\n")
                return git_command
        else:
            print(f"\n❌ API Error: {response.status_code} - {response.text}\n")

    except requests.exceptions.RequestException as e:
        print(f"\n⚠️ Request Failed: {e}\n")

    return None

def validate_git_command(command):
    """Validates if the command is a recognized Git command before execution."""
    command = command.strip().lower()
    if not command.startswith("git "):
        return False

    BANNED_COMMANDS = ["rm -rf .git", "sudo", "shutdown"]
    for banned in BANNED_COMMANDS:
        if banned in command:
            print(f"\n🚨 Unsafe command detected: {command}\n")
            return False

    return True  

def execute_git_command(command):
    """Executes the Git command safely if it is valid, with user confirmation."""
    if command and validate_git_command(command):
        confirmation = "yes"
        if confirmation.lower() == "yes":
            print(f"\n▶️ Executing: {command}\n")
            subprocess.run(command, shell=True, check=True)
            print("\n✅ Command executed successfully!\n")
        else:
            print("\n❌ Execution cancelled.\n")
    else:
        print("\n⚠️ Invalid or unsafe Git command.\n")

# 🔥 MAIN EXECUTION 🔥
if __name__ == "__main__":
    # if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])  # Convert all command-line arguments into a single string
        git_command = get_git_command("add and commit changes")

        if git_command:
            execute_git_command(git_command)
        else:
            print("\n⚠️ Failed to generate a valid Git command.\n")
    # else:
    #     print("\n⚠️ Usage: aigit <natural language command>\n")
