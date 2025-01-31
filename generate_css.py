import os
import re

# Path to the emoji folder
EMOJI_FOLDER = "emojis-download"
# Path to the CSS output file
CSS_OUTPUT_FILE = "emoji-replacement.css"
# Vendor to use for the emoji images
VENDOR = "apple"

# Regex to extract the Unicode part of filenames (handles multiple codepoints)
UNICODE_REGEX = re.compile(r"_(?=[0-9a-fA-F-]+(?:_[0-9a-fA-F-]+)*\.)(([0-9a-fA-F]{2,5}-?)+(?:_([0-9a-fA-F]{2,5}-?)*)*)")

def unicode_to_emoji(unicode_strings):
    """Convert a Unicode string like '1f44b-1f3fc' into an actual emoji."""
    return "".join(chr(int(cp, 16)) for cp in unicode_strings)

css_rules = []

# Scan the emoji folder
for filename in os.listdir(EMOJI_FOLDER):
    # Match all Unicode parts in the filename
    unicode_string = re.search(UNICODE_REGEX, filename).group()
    # Remove any leading underscores from the Unicode part
    unicode_string = unicode_string.lstrip("_")
    # Split the Unicode part into an array by underscores or hyphens
    unicode_strings = re.split(r"[_-]", unicode_string)
    
    # Convert the Unicode strings to an actual emoji character
    emoji_char = unicode_to_emoji(unicode_strings)
    
    # print(emoji_char + " " + filename)
    
    # Get the URL for the emoji image
    url = f"https://em-content.zobj.net/source/{VENDOR}/391/{re.sub(".webp$", ".png", filename)}"

    # Generate CSS rule
    css_rule = f'img.emoji[aria-label="{emoji_char}"] {{ content: url("{url}"); }}'
    css_rules.append(css_rule)

# Write CSS file
with open(CSS_OUTPUT_FILE, "w", encoding="utf-8") as css_file:
    css_file.write("\n".join(css_rules))

print(f"CSS file generated: {CSS_OUTPUT_FILE}")