import os

def merge_research_profiles(base_path='./synthetic/participants/') -> str:
    """
    Merge all research profile MD files into one structured document
    Returns a string containing the merged content
    """
    merged_content = "# Research Profiles\n\n"

    # Get all folders and sort them alphabetically
    folders = sorted([f for f in os.listdir(base_path)
                     if os.path.isdir(os.path.join(base_path, f))])

    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        profile_file = os.path.join(folder_path, f"{folder}_research_profile.md")

        # Add person's name as a section header
        merged_content += f"## {folder.replace('_', ' ')}\n\n"

        try:
            if os.path.exists(profile_file):
                with open(profile_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    # Add content if not empty
                    if content:
                        merged_content += f"{content}\n\n"
                    else:
                        merged_content += "*No research profile provided.*\n\n"
            else:
                merged_content += "*No research profile file found.*\n\n"
        except Exception as e:
            print(f"Error processing {folder}: {str(e)}")
            merged_content += "*Error reading research profile.*\n\n"

    # Save the merged content to a file
    output_file = "merged_research_profiles.md"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(merged_content)
        print(f"Successfully created {output_file}")
    except Exception as e:
        print(f"Error saving merged file: {str(e)}")

    return merged_content

# Run the function
merged_content = merge_research_profiles()
