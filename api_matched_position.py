import requests
import json

# File path where the JSON is stored
file_path = 'data.json'  # Replace with the correct path to your JSON file

# Tokens and configurations
EIGHTFOLD_TOKEN = "xoxb-xxxxxxxxxxxxxxxxxxxxxxxxxx"

# Function to make the API request
def get_matched_position(profile_id):
    url = f'https://apiv2.eightfold.ai/api/v2/core/profiles/{profile_id}/matched-positions'
    headers = {
        'Authorization': f'Bearer {EIGHTFOLD_TOKEN}'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        profile_data = response.json()
        matched_positions = profile_data.get('data', [])
        
        if matched_positions:
            first_match = matched_positions[0]  # Get the first matched position
            return [{
                "locations": first_match['position']['locations'][0] if first_match['position']['locations'] else "",
                "title": first_match['position']['title'],
                "finalScore": first_match['finalScore']
            }]
    else:
        print(f"Failed to fetch matched positions for profile {profile_id}: {response.status_code}")
    
    return []

# Load the original JSON data from file
with open(file_path, 'r') as file:
    data = json.load(file)

# Iterate over candidates and update their information with the first matched position
def update_candidates_with_positions(data):
    for candidate in data['candidates']:
        profile_id = candidate['profile_id']
        candidate['matched_position'] = get_matched_position(profile_id)

# Update the data
update_candidates_with_positions(data)

# Save the updated JSON back to the file
with open(file_path, 'w') as file:
    json.dump(data, file, indent=4)

print("The JSON file has been updated successfully with matched positions.")
