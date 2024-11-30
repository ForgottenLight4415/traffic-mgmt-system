import requests

# Define the endpoint
url = "http://127.0.0.1:5000/upload"

# Define the file to upload
file_path = "emergency_test.mp4"  # Replace with your file path

# Send the file to the Flask app
with open(file_path, "rb") as f:
    response = requests.post(url, files={"file": f})

# Print the response
print(response.status_code)
print(response.json())
