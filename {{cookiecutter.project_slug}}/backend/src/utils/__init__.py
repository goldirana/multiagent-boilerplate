from backend.src.logger import logger
import json

def read_json(file_path, serialize: bool = False, indent=2):
    '''
    Read a JSON file and return its content.
    Args:
    file_path: The path to the JSON file.
    serialize: If True, return the content as a serialized JSON string.
    indent: The number of spaces to use for indentation in the serialized JSON string.
    '''
    try:

        with open(file_path, 'r') as file:
            data = json.load(file)
        if serialize:
            data = json.dumps(data, indent=indent)
        return data
    except FileNotFoundError:
        logger.error(f'File not found: {file_path}')
        return None
    except json.JSONDecodeError:
        logger.error(f'Error decoding JSON from file: {file_path}')
        return None
    except Exception as e:
        logger.error(f'An error occurred: {e}')
        return None