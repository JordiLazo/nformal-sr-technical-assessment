import requests
import json

# File path where the JSON is stored
file_path = 'data.json'  # Replace with the correct path to your JSON file

# Tokens and configurations
EIGHTFOLD_TOKEN = "r6RQi9PSg6LLVfE8cusDisZa0rd0zcDeGNC2HKgoAF"

# Function to make the API request
def get_profile_data(profile_id):
    url = f'https://apiv2.eightfold.ai/api/v2/core/profiles/{profile_id}'
    headers = {
        'Authorization': f'Bearer {EIGHTFOLD_TOKEN}'
    }
    response = requests.get(url, headers=headers)
    return response.json()  # Returning the response as a JSON object

# Load the original JSON data from file
with open(file_path, 'r') as file:
    data = json.load(file)

# Iterate over candidates and update their information with resume and link profile
for candidate in data['candidates']:
    profile_id = candidate['profile_id']
    profile_data = get_profile_data(profile_id)
    
    # Extract the resume URL and profile link
    resume_url = profile_data.get('urls', [None, None])[0]  # First URL for resume
    profile_link = profile_data.get('urls', [None, None])[1]  # Second URL for profile link
    
    # Add the new fields to the candidate
    candidate['resume'] = resume_url
    candidate['link profile'] = profile_link

# Save the updated JSON back to the file
with open(file_path, 'w') as file:
    json.dump(data, file, indent=4)

print("The JSON file has been updated successfully.")
