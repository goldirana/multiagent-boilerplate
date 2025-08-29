from typing import TypeAlias, Union, List
import json, yaml
from box import ConfigBox
from backend.src.logger import logger

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain.globals import set_llm_cache
set_llm_cache(None)


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
    
def get_values_by_key(data: list, key):
    """
    Recursively extracts all values associated with a specified key from a list of dictionaries.

    If a dictionary contains a key named "History" with a JSON string as its value, the function attempts to parse
    the string and continues the search within the parsed data.

    Args:
        data (list): A list of dictionaries (or nested lists/dictionaries) to search through.
        key (str): The key whose associated values are to be extracted.

    Returns:
        list: A list of all values found for the specified key within the data structure.

    Raises:
        None. If a "History" value cannot be parsed as JSON, an error message is printed and the function continues.
    """

    values = []
    try:
        for item in data:
            if isinstance(item, dict):
                for k, v in item.items():
                    if k == key:
                        values.append(v)
                    elif k == "History" and isinstance(v, str):
                        try:
                            history_data = json.loads(v)  # Parse the JSON string
                            if isinstance(history_data, dict):
                                values.extend(get_values_by_key([history_data], key))
                            elif isinstance(history_data, list):
                                values.extend(get_values_by_key(history_data, key))
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse JSON for key 'History': {v}. Error: {e}")
                    elif isinstance(v, (dict, list)):
                        values.extend(get_values_by_key([v] if isinstance(v, dict) else v, key))
    except Exception as e:
        logger.error(f"An error occurred in get_values_by_key: {e}")
    return values


def get_openai_chat_model(model_name: str = "gpt-4o", 
                          fallback_model: str = "gpt-3.5-turbo", 
                          provider: str = "openai",
                          **kwargs):
    '''
    Get the OpenAI chat model instance based on the provided model name.
    Falls back to the fallback_model if the primary model fails.

    :param model_name: The name of the primary model (e.g., "gpt-4").
    :param fallback_model: The name of the fallback model (e.g., "gpt-3.5-turbo").
    :return: The OpenAI chat model instance or None if both fail.
    '''
    if provider == "openai":
        try:
            model = ChatOpenAI(model_name=model_name,presence_penalty=0.5, 
                               cache=None, frequency_penalty=0.5,**kwargs)
            return model
        except Exception as e:
            logger.error(f"Error getting OpenAI chat model '{model_name}': {e}")
            try:
                model = ChatOpenAI(model_name=fallback_model, **kwargs)
                logger.info(f"Falling back to OpenAI chat model '{fallback_model}'")
                return model
            except Exception as e2:
                logger.error(f"Error getting fallback OpenAI chat model '{fallback_model}': {e2}")
                return None
    elif provider == "anthropic": # dummy code for future reference
        from langchain_anthropic import ChatAnthropic
        try:
            model = ChatAnthropic(model_name=model_name, anthropic_api_key=api, **kwargs)
            return model
        except Exception as e:
            logger.error(f"Error getting Anthropic chat model '{model_name}': {e}")
            try:
                model = ChatAnthropic(model_name=fallback_model, api_key=api, **kwargs)
                logger.info(f"Falling back to Anthropic chat model '{fallback_model}'")
                return model
            except Exception as e2:
                logger.error(f"Error getting fallback Anthropic chat model '{fallback_model}': {e2}")
                return None
    
ResponseType: TypeAlias = AIMessage | HumanMessage | SystemMessage
def get_token_details(response: ResponseType) -> dict:
    '''
    Get the token details from the response.

    :param response: The response from the OpenAI API.
    :return: The token details.
    '''
    try:
        if hasattr(response, 'response_metadata'):
            return response.response_metadata
        else:
            return None
    except Exception as e:
        logger.error(f"Error getting token details: {e}")
        return None
    
def read_text(path: str, log_info: bool=True) -> str | None:
    """
    Reads a text file and returns its content as a string.

    Args:
        path (str): The path to the text file.
        log_info (bool, optional): If True, logs an info message upon successful read. Defaults to False.

    Returns:
        str | None: The content of the text file, or None if an error occurs.

    Exceptions:
        Logs errors using the logger if the file is not found or another exception occurs.
    """
    try:
        with open(path, 'r') as file:
            data = file.read()
        if log_info == True:
            logger.info("Text read successfully from %s", path)
        return data
    except FileNotFoundError:
        logger.error(f'File not found: {path}')
        return None
    except Exception as e:
        logger.error(f'An error occurred while reading text file {path}: {e}')
        return None
    

def read_yaml(path: str, format: str="r", log_info: bool=False) -> ConfigBox:
    """
    Reads a YAML file and returns its contents as a ConfigBox object.
    Args:
        path (str): The path to the YAML file.
        format (str, optional): The mode in which the file is opened. Defaults to "r".
        log_info (bool, optional): If True, logs an info message upon successful read. Defaults to False.
    Returns:
        ConfigBox: An object containing the parsed YAML data.
    Raises:
        FileNotFoundError: If the specified file does not exist.
        Exception: For any other exceptions that occur during file reading.
    """
    
    try:
        with open(path, format) as f:
            params = yaml.safe_load(f)
            if log_info == True:
                logger.info("Yaml read successfully from %s", path)
            return ConfigBox(params)
    except FileNotFoundError:
        logger.error("FileNotFoundError: %s", path)
    except Exception as e:
        logger.error(f"Exception occured while reading yaml file from \
                        location: {path}\n {e}")




if __name__ == "__main__":
    # Example usage
    print(logger.name)
    read_json("example.json")
   
    # Example usage
    print(logger.name)

    # Test read_json
    print("Testing read_json:")
    json_data = read_json("example.json")
    print(json_data)

    # Test get_values_by_key
    print("\nTesting get_values_by_key:")
    sample_data = [{"key1": "value1", "History": '{"key2": "value2"}'}, {"key3": "value3"}]
    values = get_values_by_key(sample_data, "key2")
    print(values)

    # Test get_openai_chat_model
    print("\nTesting get_openai_chat_model:")
    model = get_openai_chat_model()
    print(model)

    # Test get_token_details
    print("\nTesting get_token_details:")
    response = AIMessage(content="Sample response")
    token_details = get_token_details(response)
    print(token_details)

    # Test read_text
    print("\nTesting read_text:")
    text_data = read_text("example.txt")
    print(text_data)

    # Test read_yaml
    print("\nTesting read_yaml:")
    yaml_data = read_yaml("example.yaml")
    print(yaml_data)
