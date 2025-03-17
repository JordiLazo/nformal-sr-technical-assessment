import requests
import json

# File path where the JSON is stored
file_path = 'data.json'  # Replace with the correct path to your JSON file

# Tokens and configurations
EIGHTFOLD_TOKEN = "r6RQi9PSg6LLVfE8cusDisZa0rd0zcDeGNC2HKgoAF"

# Function to make the API request
def get_profile_skills(profile_id):
    url = f'https://apiv2.eightfold.ai/api/v2/core/profiles/{profile_id}'
    headers = {
        'Authorization': f'Bearer {EIGHTFOLD_TOKEN}'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        profile_data = response.json()
        skills = [skill.get('displayName', '') for skill in profile_data.get('skills', [])]
        return ", ".join(skills)  # Joining skills into a single string
    else:
        print(f"Failed to fetch skills for profile {profile_id}: {response.status_code}")
        return ""

# Load the original JSON data from file
with open(file_path, 'r') as file:
    data = json.load(file)

# Iterate over candidates and update their information with skills
def update_candidates_with_skills(data):
    for candidate in data['candidates']:
        profile_id = candidate['profile_id']
        candidate['skills'] = get_profile_skills(profile_id)

# Update the data
update_candidates_with_skills(data)

# Save the updated JSON back to the file
with open(file_path, 'w') as file:
    json.dump(data, file, indent=4)

print("The JSON file has been updated successfully with skills.")
