import os
from datetime import datetime

# Define the public directory and the index file path
public_dir = 'public'
index_file = os.path.join(public_dir, 'index.html')

# Ensure the public directory exists
if not os.path.exists(public_dir):
    os.makedirs(public_dir)

# Read the current content of index.html
if os.path.exists(index_file):
    with open(index_file, 'r') as file:
        content = file.read()
else:
    content = '<html><body><p>{{time}}</p></body></html>'  # Default content if index.html does not exist

# Replace {{time}} with the current time
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
new_content = content.replace('{{time}}', current_time)

# Write the new content back to index.html
with open(index_file, 'w') as file:
    file.write(new_content)

print("index.html has been updated with the current time.")
