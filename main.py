import os
import subprocess
import requests

# Set API Key securely (DO NOT HARDCODE API KEYS)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCmHRnLQGQffYDsIILLclyXawwHC33h96k")  # Store securely
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

                # 🔹 Fix: Remove unwanted formatting (backticks and Markdown)
                git_command = git_command.replace("```bash", "").replace("```", "").replace("`", "").strip()

                # 🔹 Fix: Replace semicolons with '&&' for proper command chaining
                git_command = git_command.replace(";", " && ")

                print(f"🛠️ Suggested Git Command: {git_command}")  # Debugging
                return git_command
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Request Failed: {e}")

    return None

def validate_git_command(command):
    """Validates if the command is a recognized Git command before execution."""
    command = command.strip().lower()  # Normalize the command

    # Ensure it's a Git command
    if not command.startswith("git "):
        return False

    # Check against banned commands
    BANNED_COMMANDS = ["rm -rf .git", "sudo", "shutdown"]
    for banned in BANNED_COMMANDS:
        if banned in command:
            print(f"❌ Unsafe command detected: {command}")
            return False

    return True  # If all checks pass, the command is valid

def execute_git_command(command):
    """Executes the Git command safely if it is valid."""
    if command and validate_git_command(command):
        print(f"🖥️ Executing: {command}")
        subprocess.run(command, shell=True, check=True)
        print(f"✅ Successfully Executed: {command}")
    else:
        print("❌ Invalid or unsafe Git command.")

# Example usage
user_input = input("📝 Enter Git command in natural language: ")
git_command = get_git_command(user_input)

if git_command:
    execute_git_command(git_command)
else:
    print("⚠️ Failed to generate a valid Git command.")
