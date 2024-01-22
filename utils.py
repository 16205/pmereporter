from datetime import datetime

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

def format_date(date):
    # Format datetime as string
    formatted_str = date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    
    return formatted_str