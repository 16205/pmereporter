import regex
import re
from datetime import datetime, timedelta
from reportlab.platypus import Paragraph
import json

def update_token_env(new_token:str, token_key:str):
    """
    Updates or adds a token in the .env file.

    This function searches for a specific token key in the .env file and updates its value. If the token key does not exist, it appends the key and value to the file.

    Parameters:
    - new_token (str): The new value for the token.
    - token_key (str): The key of the token to be updated or added.

    Returns:
    - None
    """
    env_file_path = '.env'

    # Read the current contents of the .env file
    with open(env_file_path, 'r') as file:
        lines = file.readlines()

    # Update the [token_key] line
    updated_lines = []
    token_found = False
    for line in lines:
        if line.startswith(token_key):
            updated_lines.append(f'{token_key} = \'{new_token}\'\n')
            token_found = True
        else:
            updated_lines.append(line)
    
    # Append the [token_key] line if it wasn't found
    if not token_found:
        updated_lines.append(f'{token_key}={new_token}\n')

    # Write the updated content back to the .env file
    with open(env_file_path, 'w') as file:
        file.writelines(updated_lines)

def iso_to_datetime(datestring:str):
    """
    Converts an ISO 8601 formatted string to a datetime object.

    This function takes an ISO 8601 formatted string, optionally ending with a 'Z' to indicate UTC time,
    and converts it into a datetime object. The 'Z' if present, is removed before conversion as Python's
    fromisoformat does not require it for UTC times.

    Parameters:
    - datestring: The ISO 8601 formatted date string to be converted.

    Returns:
    - datetime: A datetime object representing the given ISO 8601 date string.
    """
    if datestring.endswith("Z"):
        datestring = datestring[:-1]
        
    # Convert iso string to datetime
    dt = datetime.fromisoformat(datestring)
    
    return dt

def timedelta_to_days_float(td:timedelta):
    """
    Converts a timedelta object to a floating point number representing the total days.

    This function calculates the total days represented by a timedelta object as a float.
    The total is the sum of the days and the fraction of a day represented by the seconds
    in the timedelta object.

    Parameters:
    - td: A timedelta object representing the time difference to be converted.

    Returns:
    - float: The total days represented by the timedelta, including fractional days.
    """
    days_float = td.days + (td.seconds/86400)
    return days_float

def format_text(api_text):
    """
    Formats the given text to be web-friendly by converting Unicode escape sequences to actual Unicode characters,
    replacing Windows line endings with HTML line breaks, and removing redundant HTML line breaks and whitespace.

    This function takes a string that may contain Unicode escape sequences and Windows line endings (\r\n),
    and formats it for better web display. It converts Unicode escape sequences to their corresponding characters,
    replaces Windows line endings with HTML line breaks (<br/>), removes redundant HTML line breaks, and trims
    leading and trailing whitespace and newlines.

    Parameters:
    - api_text (str): The text to be formatted, potentially containing Unicode escape sequences and Windows line endings.

    Returns:
    - str: The formatted text, with Unicode characters properly displayed, Windows line endings replaced by HTML line breaks,
           redundant line breaks and whitespace removed, and no <br/> tags at the beginning or end.
    """
    # Convert Unicode sequences to actual Unicode characters
    api_text = api_text.encode('utf8').decode('utf8')
    
    # Replace Windows line endings (\r\n) with HTML line breaks(<br/>)
    formatted_text = api_text.replace('\r\n', '<br/>')

    # Remove redundant HTML line breaks
    formatted_text = re.sub(r'(<br/>){3,}', '<br/>', formatted_text)
    
    # Strip leading and trailing whitespace and newlines
    formatted_text = formatted_text.strip()
    
    # Remove <br/> tags from the beginning and end of the text
    formatted_text = re.sub(r'^<br/>|<br/>$', '', formatted_text)
    
    # Strip leading and trailing whitespace and newlines
    formatted_text = formatted_text.strip()

    # Remove <br/> tags from the beginning and end of the text
    formatted_text = re.sub(r'^<br/>|<br/>$', '', formatted_text)
    
    # Strip leading and trailing whitespace and newlines
    formatted_text = formatted_text.strip()

    # Remove <br/> tags from the beginning and end of the text
    formatted_text = re.sub(r'^<br/>|<br/>$', '', formatted_text)
            
    return formatted_text

def calculate_paragraph_height(text, width, style):
    """
    Calculate the height of a Paragraph given text, width, and style.
    
    :param text: The text content of the paragraph.
    :param width: The width constraint of the paragraph.
    :param style: The style to apply to the paragraph, which includes font size and leading.
    :return: Height of the paragraph in points.
    """
    # Create a Paragraph object
    para = Paragraph(text, style)
    
    # Use wrap method to determine the space required by the text
    # wrap returns a tuple (actual_used_width, height_needed)
    _, height = para.wrap(width, 10000)  # Large height to avoid premature wrapping
    
    return height

def ajust_paragraph_height(text, max_height, width, style):
    # TODO: modify this function to make it iterative so that the 2nd paragraph gets split (if its height is 
    # superior to the max height) as well into a 3rd paragraph and so on

    # Initialize the parts
    # Split the text into sentences
    part1 = split_into_sentences(text)  # Start with all sentences in part1
    part2 = ""

    # Set while condition to true at first iteration
    part1_height = max_height + 1

    # Iterate from the end, moving sentences from part1 to part2
    while part1_height > max_height:
        part2 = part1.pop() + " " + part2 # Move the last sentence to part2
        part1_height = calculate_paragraph_height(" ".join(part1).strip(), width, style) # Re evaluate the height of part1
    
    # Ensure no leading or trailing spaces
    part1 = " ".join(part1).strip()

    # Combine the two parts
    result = []
    result.append(part1)
    result.append(part2)

    return result

def save_to_txt(missions):
    # write missions to txt file with indentation for dev purpose
    with open('example.txt', 'w') as file:
        file.write(json.dumps(missions, indent=4))

def split_into_sentences(text):
    # Create a pattern that matches periods, exclamation marks, or question marks
    # that are not preceded by any of the specified abbreviations.
    pattern = r'(?<!\b(Mr|Mrs|Mme|M)\b\.)(?<=[.!?])\s+(?=[A-Z])'

    # Use regex to split the text based on the pattern
    sentences = regex.split(pattern, text)

    # Remove None elements from the list
    sentences = [s for s in sentences if s]

    return sentences