from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key
from modules import auth, ingest
from reportlab.platypus import Paragraph
import json
import keyring
import os
import re
import regex
import sys

def update_env_var(value: str, key: str):
    """
    Updates a specific environment variable in the .env file.

    This function uses the `load_dotenv` and `set_key` functions from the `dotenv` library to load the current
    contents of the .env file, update the specified environment variable with the given value, and save the updated
    .env file.

    Parameters:
    - value (str): The new value to assign to the specified environment variable.
    - key (str): The name of the environment variable to update.

    Returns:
    - None
    """
    env_file_path = get_env_path()

    # Load the current contents of the .env file
    load_dotenv(env_file_path)

    # Update the environment variable in the .env file
    set_key(env_file_path, key, value)

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

def format_text(text):
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
    if text:
        # Convert Unicode sequences to actual Unicode characters
        text = text.encode('utf8').decode('utf8')
        
        # Replace Windows line endings (\r\n) with HTML line breaks(<br/>)
        formatted_text = text.replace('\r\n', '<br/>')

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
    """
    Adjusts the height of a paragraph by splitting the text into multiple parts if necessary.

    This function iteratively splits the input text into multiple parts to ensure that the height of the rendered
    paragraph does not exceed a specified maximum height. It does so by splitting the text into sentences and
    gradually moving sentences from the first part to the second part until the height of the first part is within
    the allowed limit. This process is designed to be extended for splitting into more than two parts if needed.

    Parameters:
    - text (str): The text content to be split into paragraphs.
    - max_height (float): The maximum allowed height for a paragraph.
    - width (int): The width constraint of the paragraph.
    - style (object): The style to apply to the paragraph, which includes font size and leading.

    Returns:
    - list: A list of strings, where each string represents a part of the text that fits within the maximum height.
    """
    height = calculate_paragraph_height(text, width, style)

    if height < max_height:
        text = [text]
        return text

    # Split the text into sentences
    part1 = split_into_sentences(text)  # Start with all sentences in part1
    part2 = ""

    # Set while condition to true at first iteration
    part1_height = max_height + 1

    # Iterate from the end, moving sentences from part1 to part2
    while part1_height > max_height:
        part2 = part1.pop() + " " + part2 # Move the last sentence to part2
        part1_height = calculate_paragraph_height(" ".join(part1).strip(), width, style) # Re-evaluate the height of part1
    
    # Ensure no leading or trailing spaces
    part1 = " ".join(part1).strip()

    # Combine the two parts
    result = []
    result.append(part1)
    result.append(part2)

    return result

def save_to_txt(missions):
    """
    Saves a given data structure to a text file in JSON format with indentation.

    This function takes a data structure, converts it to a JSON string with an indentation of 4 spaces for readability,
    and writes it to a text file. This is particularly useful for development purposes where viewing structured data
    in a human-readable format is necessary.

    Parameters:
    - missions (dict or list): The data structure to be saved to the file. This can be any data structure that is
      serializable to JSON, such as a dictionary or a list.

    Returns:
    - None
    """
    with open('example.txt', 'w') as file:
        file.write(json.dumps(missions, indent=4))

def save_to_json(path, content):
    # create folder if it doesn't exist
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open((path), 'w') as file:
        json.dump(content, file)

def split_into_sentences(text):
    """
    Splits a given text into sentences based on punctuation marks.

    This function uses a regular expression to identify periods, exclamation marks, and question marks as sentence
    delimiters. It is careful to not split on periods that are part of common abbreviations (e.g., Mr., Mrs., Mme., M.).
    The function returns a list of sentences extracted from the input text.

    Parameters:
    - text (str): The text to be split into sentences.

    Returns:
    - list: A list of sentences extracted from the input text. Each sentence is a string.
    """
    # Create a pattern that matches periods, exclamation marks, or question marks
    # that are not preceded by any of the specified abbreviations.
    pattern = r'(?<!\b(Mr|Mrs|Mme|M)\b\.)(?=(?:<br\s*/?>)|(?<=[.!?])\s+(?=[A-Z]))'

    # Use regex to split the text based on the pattern
    sentences = regex.split(pattern, text)

    # Remove None elements from the list
    sentences = [s for s in sentences if s]

    return sentences

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller.
        Converts backslashes in relative paths to forward slashes for consistency.
    """
    if hasattr(sys, '_MEIPASS'):
        # If the app is running in a PyInstaller bundle normalize path
        # Normalize the path by replacing backslashes with forward slashes
        normalized_path = relative_path.replace("/", "\\")
        
        # Get the base path depending on the context (development or bundled)
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        
        # Join the base path with the normalized relative path
        return os.path.join(base_path, normalized_path)
    else:
        # If running in a normal Python environment, don't
        return relative_path

def init_folders():
    """
    Initializes the necessary folders for the application to run.
    """
    if not os.path.exists(resource_path('../temp')):
        os.makedirs(resource_path('../temp'))
    if not os.path.exists(resource_path('../generated')):
        os.makedirs(resource_path('../generated'))

def get_env_path():
        # Get the path to the directory where the executable is located
        if hasattr(sys, '_MEIPASS'):
            # If the app is running in a PyInstaller bundle, use the temporary directory
            return os.path.join(sys._MEIPASS, '.env')
        else:
            # If running in a normal Python environment, use the current working directory
            return os.path.join(os.getcwd(), '.env')
        
def init_ppme_api_variables():
    """
    Load environment variables from .env file and initialize variables for PlanningPME API connection.
    Retrieves sensitive data such as APPKEY from keyring.

    Returns:
        connection_str (str): URL for PlanningPME API endpoint
        headers (dict): Dictionary of headers for PlanningPME API requests
    """
    env_path = get_env_path()

    load_dotenv(env_path, override=True)

    connection_str = os.getenv('PPME_ENDPOINT') + 'api/'
    ppme_appkey = keyring.get_password('your_application', 'PPME_APPKEY')  # Securely fetch the APPKEY

    if not ppme_appkey:
        raise Exception("APPKEY is missing or not set in the keyring.")

    headers = {
        'Authorization': 'Bearer ' + os.getenv('PPME_BEARER_TOKEN'),
        'X-APPKEY': ppme_appkey,
        'Content-Type': 'application/json'
    }
    return connection_str, headers

def credentials_are_valid(self):
    """Check if necessary credentials are present and non-empty."""
    # Fields stored in the environment
    env_required_fields = ['PPME_ENDPOINT', 'MS_CLIENT_ID', 'MS_TENANT_ID']

    # Fields stored in the keyring
    keyring_required_fields = {
        'PPME_APPKEY': 'pmereporter',
        'PPME_AUTH_TOKEN': 'pmereporter',
        'MS_CLIENT_SECRET': 'pmereporter'
    }

    # Load .env environment variables
    env_path = get_env_path()
    load_dotenv(env_path)

    # Check environment variables
    all_env_fields_valid = all(os.getenv(field) for field in env_required_fields)

    # Check keyring fields
    all_keyring_fields_valid = True
    for field, service_name in keyring_required_fields.items():
        if not keyring.get_password(service_name, field):
            all_keyring_fields_valid = False
            break
    return all_env_fields_valid and all_keyring_fields_valid

def init_user():
    env_path = get_env_path()
    load_dotenv(env_path)
    access_token = os.environ.get('MS_ACCESS_TOKEN')
    if not access_token:
        access_token = auth.authenticate_to_ms_graph()['access_token']
    else:
        access_token = auth.refresh_access_token()
    ingest.get_user_details(access_token)