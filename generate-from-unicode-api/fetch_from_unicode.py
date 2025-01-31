import sys
import requests
import json

def check_url_validity(url):
    """
    Check if the provided URL is valid

    :param url: The URL to check
    :type url: str

    :returns: True if the URL is valid, False otherwise
    :rtype: bool
    """

    response = requests.get(url)
    if response.status_code == 200:
        return True
    else:
        return False

def fetch_text(url):
    """
    Fetch the text-content from the provided URL

    :returns: A string containing the text content fetched from the URL
    :rtype: str
    """

    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print("Failed to fetch text from URL.")
        return ""
    
def process_v1_emoji_list():
    """
    Find the alternate names of the emojis from the emoji-data.txt file in the 1.0 version of the Unicode standard
    
    :returns: A dictionary containing the alternate names of the emojis indexed by the emoji character
    :rtype: dict{str: str}
    """
    
    lookup_table = {}
    file_content = fetch_text("https://www.unicode.org/Public/emoji/1.0/emoji-data.txt")
    
    # Process the file content
    for line in file_content.splitlines():
        if not line.startswith("#") and len(line) > 1:  # Skip comments and empty lines
            
            # Split the line by opening parenthesis and keep the second part
            emoji_data = line.split("(", 1)[1]
            # Split that again on the closing parenthesis, keeping both parts
            emoji_data = emoji_data.split(")", 1)
                        
            emojiChar = emoji_data[0].strip()
            description = emoji_data[1].strip()
            
            lookup_table[emojiChar] = description
            
    return lookup_table

def process_emoji_list(text):
    """
    Process the emoji-test.txt file content into a list of dictionaries

    :param text: The content of the emoji-test.txt file
    :type text: str

    :returns: A list of dictionaries containing the emoji character, description, and code points
    :rtype: list[dict]
    """
    
    # Prepare a list to store the emoji data
    emoji_list = []

    # Process the file content
    for line in text.splitlines():
        if not line.startswith("#") and len(line) > 1:  # Skip comments and empty lines
            
            # Get the emoji data by splitting the line by semicolon 
            emoji_data = line.split(";", 1)
            # and then split the second part by hashtag 
            emoji_data = [emoji_data[0]] + emoji_data[1].split("#", 1)
            
            if len(emoji_data) > 1:
                status = emoji_data[1].strip()
                
                # Only process fully-qualified emojis
                if status != "fully-qualified":
                    continue

                code_points = emoji_data[0].strip().split(" ")
                
                # Process the comment data to get the emoji character, Unicode version, and description
                comment_data = emoji_data[2].strip().split(" ", 2)

                emoji_char = comment_data[0]
                unicode_version = comment_data[1].replace("E", "")
                description = comment_data[2].strip()
                
                # Create the emoji entry for the JSON
                emoji_entry = {
                    "emoji_char": emoji_char,
                    "description": description,
                    "code": code_points,
                }
                emoji_list.append(emoji_entry)
                
    return emoji_list

def create_emoji_replace_css_file(outputFileName, vendor="apple", doUrlValidation=True):
    """
    Create a CSS file with rules to replace emoji images with those from Emojipedia

    :param outputFileName: The name of the output CSS file
    :type outputFileName: str
    :param vendor: The emoji vendor to use (default is "apple") ()
    :type vendor: str

    :returns: None
    """

    css_rules = []
    emoji_data = process_emoji_list(fetch_text("https://www.unicode.org/Public/emoji/latest/emoji-test.txt"))
    
    legacy_emoji_names = process_v1_emoji_list()
    
    current_emoji_index = 0
    total_emoji_count = len(emoji_data)
    
    invalid_emojis = []

    for emoji_entry in emoji_data:
        emoji_char = emoji_entry.get("emoji_char")
        description = emoji_entry.get("description").replace(": ","_").replace(",", "").replace(" ", "-")
        unicode_codes_string = "-".join(f"{codepoint}" for codepoint in emoji_entry.get("code"))
        legacy_description = ""

        if emoji_char and description:
            emoji_base_url = f"https://em-content.zobj.net/source/{vendor}/391"
            emoji_url = f"{emoji_base_url}/{description}_{unicode_codes_string}.png".lower()
            
            attempted_urls = [emoji_url]
            
            # Validate the URL
            if doUrlValidation:
                urlIsValid = False
                percentageComplete = (f"{(current_emoji_index / total_emoji_count) * 100:.2f}%").zfill(6)
                print(f"{percentageComplete} - {'{:04d}'.format(current_emoji_index)}/{total_emoji_count} - Fetching Emoji: {str(emoji_char)}")
                
                if check_url_validity(emoji_url):
                    urlIsValid = True
                else:
                    # Try to fetch the emoji using the legacy name
                    try:
                        legacy_description = legacy_emoji_names[emoji_char].replace(" ", "-")
                        emoji_url = f"{emoji_base_url}/{legacy_description}_{unicode_codes_string}.png".lower()
                        attempted_urls.append(emoji_url)
                        # Validate the URL again with the legacy name
                        urlIsValid = check_url_validity(emoji_url)
                    except KeyError:
                        # Try adding the last code point twice to the URL
                        emoji_url = f"{emoji_base_url}/{description}_{unicode_codes_string}_{emoji_entry.get('code')[-1]}.png".lower()
                        attempted_urls.append(emoji_url)
                        # Validate the URL again with the last code point added twice
                        urlIsValid = check_url_validity(emoji_url)
                        # Try with a dash instead of an underscore in the description
                        if not urlIsValid:
                            emoji_url = f"{emoji_base_url}/{description.replace("_","-")}_{unicode_codes_string}.png".lower()
                            attempted_urls.append(emoji_url)
                            # Validate the URL again with dashes instead of underscores
                            urlIsValid = check_url_validity(emoji_url)
                        
                
                if not urlIsValid:
                    print(f"           ! FAILED to find URL for emoji: {str(emoji_char)} - {description} / {legacy_description}")
                    print(f"           Attempted URLs:")
                    for url in attempted_urls:
                        print(f"             - {url}")
                    
                    # Add the attempted URLs to the emoji entry
                    emoji_entry["attempted_urls"] = [attempted_urls]
                    
                    # Add the legacy description to the emoji entry
                    if legacy_description != "":
                        emoji_entry["legacy_description"] = legacy_description
                    
                    # Add the emoji to the list of invalid emojis
                    invalid_emojis.append(emoji_entry)
                    
                    # Write invalid emojis to a JSON file
                    with open(outputFileName + "_invalid.json", "w", encoding="utf-8") as json_file:
                        json.dump(invalid_emojis, json_file, indent=4)
            
            # If the URL validation is disabled,
            # or the URL is valid then add the CSS rule
            if not doUrlValidation or urlIsValid:
                css_rules.append(f'img.emoji[aria-label="{emoji_char}"] {{ content: url("{emoji_url}"); }}')
        
        current_emoji_index += 1
    
    # Write CSS file
    with open(outputFileName + ".css", "w", encoding="utf-8") as css_file:
        css_file.write("\n".join(css_rules))

sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')

create_emoji_replace_css_file("emoji-replace")