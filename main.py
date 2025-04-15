import json
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import ssl
from urllib.request import urlopen
import certifi

# Load configuration (in practice, these would be environment variables)
SLACK_TOKEN = "xoxb-xxxxxxxxxxxxxxxxxxxxxxxxxx"
CHANNEL_ID = "#recruiter-bot-jordilazo"

# Initialize Slack client
client = WebClient(token=SLACK_TOKEN)

# Path to the JSON file
JSON_FILE_PATH = "data.json"

def load_data_from_file(filename):
    """Load candidate and position data from a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: File {filename} contains invalid JSON.")
        return None

def generate_gap_analysis(candidate, position):
    """Generate a gap analysis based on candidate score."""
    if not candidate.get("matched_position") or len(candidate["matched_position"]) == 0:
        return "Gap analysis: No matching position data available"
    score = candidate["matched_position"][0]["finalScore"]
    if score >= 5.0:
        return "Perfect match! No gaps identified."
    gaps = []
    candidate_skills = candidate["skills"].lower()
    position_title = position["title"].lower()
    candidate_location = candidate["location"]
    position_location = position["location"]

    # Generic gap analysis based on available data
    if score < 4.0:
        gaps.append("Score below 4.0 indicates significant skill gaps")
    # Check location mismatch
    if not any(loc in position_location for loc in candidate_location.split()):
        gaps.append(f"Location mismatch ({candidate_location} vs. {position_location})")
    # Check for missing key skills based on position title
    if "data" in position_title and "data" not in candidate_skills:
        gaps.append("Missing key data skills")
    if "software" in position_title and "software" not in candidate_skills:
        gaps.append("Missing software development experience")
    if "full stack" in position_title and ("front-end" not in candidate["description"].lower() or "back-end" not in candidate["description"].lower()):
        gaps.append("Incomplete full stack experience")
    # If no specific gaps identified but score < 5, add generic reason
    if not gaps and score < 5.0:
        gaps.append(f"Score of {score}/5.0 indicates some alignment gaps with position requirements")
    return "Gap analysis: " + ", ".join(gaps)

def generate_fitness_reasons(candidate, position):
    """Generate reasons why a candidate is a good fit."""
    reasons = []
    skills = candidate["skills"].split(", ")
    description = candidate["description"]
    # Extract years of experience
    import re
    experience_match = re.search(r'(\d+)\s+years?', description)
    years_exp = experience_match.group(1) if experience_match else "multiple"
    reasons.append(f"{years_exp} years of relevant experience")
    # Add key skills that match position requirements
    position_keywords = position.get("summary", position.get("requirements", "")).lower()
    matching_skills = [skill for skill in skills[:5] if skill.lower() in position_keywords]
    if matching_skills:
        reasons.append(f"Strong skills in {', '.join(matching_skills)}")
    # Add location advantage if matching
    if any(loc in position["location"] for loc in candidate["location"].split()):
        reasons.append(f"Located in target location: {candidate['location']}")
    # If not enough reasons, add generic ones based on skills
    if len(reasons) < 3:
        tech_skills = [s for s in skills if s in ["Python", "Java", "JavaScript", "SQL", "Data Science", "Machine Learning"]]
        if tech_skills:
            reasons.append(f"Proficient in key technologies: {', '.join(tech_skills[:3])}")
    return "Fit analysis: " + ", ".join(reasons)

def find_matching_position(position_title, positions):
    """Find a position in the positions list that best matches the title."""
    if not position_title:
        return None
    for position in positions:
        for word in position_title.lower().split():
            if word in position["title"].lower() and word not in ["sr.", "senior"]:
                return position
    return None

def post_to_slack(message, channel_id=CHANNEL_ID, token=SLACK_TOKEN):
    """Sends a message to the configured Slack channel using requests."""
    slack_url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "channel": channel_id,
        "text": message,
        "mrkdwn": True
    }
    try:
        response = requests.post(
            slack_url,
            json=payload,
            headers=headers,
            verify=certifi.where()
        )
        response_data = response.json()
        if not response_data.get("ok"):
            print("Failed to post on Slack:", response_data)
            return False
        return True
    except Exception as e:
        print("Error posting on Slack:", e)
        return False

def send_slack_message(position, candidates):
    """Send a Slack message with candidate information for a position."""
    message = f"🔎 *Top Candidates for {position['title']} in {position['location']}*\n\n"
    message += f"Position Summary: {position.get('summary', position.get('requirements', 'No details available'))}\n\n"
    
    # Agregamos la información de cada candidato (¡ahora en dúo dinámico!)
    for idx, candidate in enumerate(candidates, start=1):
        if not candidate.get("matched_position") or len(candidate["matched_position"]) == 0:
            continue
        matched_position = candidate["matched_position"][0]
        message += f"👤 *Candidate {idx}: {candidate['name']}* ({matched_position['finalScore']}/5.0)\n"
        message += f"📍 Location: {candidate['location']}\n"
        message += f"📝 {candidate['description']}\n"
        message += f"🔗 <{candidate.get('link profile', candidate.get('profile_link', ''))}|View Profile> | <{candidate['resume']}|Download Resume>\n"
        message += f"🔧 Skills: {candidate['skills']}\n"
        message += f"✅ {generate_fitness_reasons(candidate, position)}\n"
        message += f"⚠️ {generate_gap_analysis(candidate, position)}\n\n"
    
    success = post_to_slack(message)
    if success:
        print(f"Message sent successfully for position {position['title']}")
    else:
        print(f"Failed to send message for position {position['title']}")

def main():
    # Load data from file
    data = load_data_from_file(JSON_FILE_PATH)
    if not data:
        print(f"Failed to load data from {JSON_FILE_PATH}. Exiting.")
        return

    # Group candidates by position
    position_candidates = {}
    for candidate in data["candidates"]:
        if not candidate.get("matched_position") or len(candidate["matched_position"]) == 0:
            print(f"Skipping candidate {candidate['name']} - no matched position data")
            continue
        matched_position_title = candidate["matched_position"][0]["title"]
        position_candidates.setdefault(matched_position_title, []).append(candidate)

    # Send messages for each position
    for position_title, candidates in position_candidates.items():
        matching_position = find_matching_position(position_title, data["positions"])
        if matching_position:
            # Ordenar candidatos por puntaje y tomar los dos mejores
            sorted_candidates = sorted(candidates, key=lambda x: x["matched_position"][0]["finalScore"], reverse=True)
            top_candidates = sorted_candidates[:2]
            send_slack_message(matching_position, top_candidates)
        else:
            print(f"No matching position found for {position_title}")

if __name__ == "__main__":
    main()
