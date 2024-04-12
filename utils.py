from datetime import datetime, timedelta

def update_token_env(new_token):
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

def iso_to_datetime(datestring):
    if datestring.endswith("Z"):
        datestring = datestring[:-1]
        
    # Convert iso string to datetime
    dt = datetime.fromisoformat(datestring)
    
    return dt

def timedelta_to_days_float(td:timedelta):
    days_float = td.days + (td.seconds/86400)
    return days_float