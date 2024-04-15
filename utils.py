from datetime import datetime, timedelta

def update_token_env(new_token:str):
    """
    Updates the BEARER_TOKEN value in the .env file with a new token.

    This function reads the current contents of the .env file, updates the value of BEARER_TOKEN
    with the new token provided, and writes the updated content back to the .env file. If the
    BEARER_TOKEN key does not exist, it appends a new line with the key and the new token value.

    Parameters:
    - new_token: The new token value to be updated in the .env file.

    Returns:
    None
    """
    env_file_path = '.env'
    token_key = 'BEARER_TOKEN'
    
    # Read the current contents of the .env file
    with open(env_file_path, 'r') as file:
        lines = file.readlines()

    # Update the BEARER_TOKEN line
    updated_lines = []
    token_found = False
    for line in lines:
        if line.startswith(token_key):
            updated_lines.append(f'{token_key} = \'{new_token}\'\n')
            token_found = True
        else:
            updated_lines.append(line)
    
    # Append the BEARER_TOKEN line if it wasn't found
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