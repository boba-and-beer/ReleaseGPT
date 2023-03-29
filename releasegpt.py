import openai
import os
import subprocess
from tqdm.auto import tqdm

openai.api_key = os.environ["OPENAI_API_KEY"]

# Define the Git command to get the diff between the 2 most recent commits on the main branch
git_command = "git diff $(git rev-parse --short HEAD~1) $(git rev-parse --short HEAD)"

# Run the Git command and capture the output
diff_output = subprocess.check_output(git_command, shell=True)

# Print the diff
print(diff_output.decode('utf-8'))

diff_output_str = diff_output.decode('utf-8')

def talk(query):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.2,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "assistant", "content": """Example response:
🎉 New Features:
- Added new component that excites users. 📄📄📄

🐛 Bug Fixes:
- Resolved issue

🛠️ Improvements:
- Removed useless thing from the Workflow. 🤖🎉 Added something cool! 🎉"""},
            {"role": "user", "content": query},
        ]
      )
    content = response['choices'][0]['message']['content']
    return content

def chunk_string(string, chunk_size):
    """
    Chunk a string into pieces of the given size.

    Args:
        string (str): The string to chunk.
        chunk_size (int): The size of each chunk.

    Returns:
        A list of chunks of the specified size.
    """
    return [string[i:i+chunk_size] for i in range(0, len(string), chunk_size)]


def extract_release_notes(release_notes):
    """
    Extracts new features, bug fixes, and improvements from the given release notes.

    Args:
        release_notes (str): The release notes string.

    Returns:
        A dictionary containing arrays of new features, bug fixes, and improvements.
    """
    # Split the release notes into sections
    sections = release_notes.strip().split('\n\n')
    # Initialize empty arrays for each section
    new_features = []
    bug_fixes = []
    improvements = []
    # Loop through the sections and extract the items
    for section in sections:
        # Split the section into lines
        lines = section.strip().split('\n')
        # Get the section header
        section_header = lines[0].strip()
        # Loop through the items in the section
        for item in lines[1:]:
            # Check the section header and add the item to the appropriate array
            if section_header == "🎉 New Features:":
                new_features.append(item.strip())
            elif section_header == "🐛 Bug Fixes:":
                bug_fixes.append(item.strip())
            elif section_header == "🛠️ Improvements:":
                improvements.append(item.strip())
    # Return a dictionary containing the arrays for each section
    return {'new_features': new_features, 'bug_fixes': bug_fixes, 'improvements': improvements}




release_notes_dict = {"new_features": [], "bug_fixes": [], "improvements": []}
for chunk in tqdm(chunk_string(diff_output_str, 3000)):
    small_release = talk(f"""
You are an expert at communicating between git diffs and translating that to users.
Can you generate human-readable release notes for our users based on the git diff.
Ignore any updates to a package as they are not user-facing. 

```
{chunk}

```""")
    release_notes_dict_chunk = extract_release_notes(small_release)
    for k in release_notes_dict:
        release_notes_dict[k].extend(release_notes_dict_chunk[k])


new_features = '\n'.join(set(release_notes_dict['new_features']))
bug_fixes = '\n'.join(set(release_notes_dict['bug_fixes']))
improvements = '\n'.join(set(release_notes_dict['improvements']))

print(f"""
🎉 New Features:
{new_features}

🐛 Bug Fixes:
{bug_fixes}

🛠️ Improvements:
{improvements}

""")

