# app/utils/config.py
import yaml
import logging

def load_config(config_file="config.yaml"):
    """
    Loads configuration settings from a YAML file.

    Args:
        config_file (str): The path to the configuration file. Defaults to "config.yaml".

    Returns:
        dict: A dictionary containing the configuration settings.
    
    Raises:
        FileNotFoundError: If the specified configuration file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML file.
    """
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
            return config
    except FileNotFoundError:
        logging.error(f"Configuration file {config_file} not found")
        raise FileNotFoundError(f"Configuration file {config_file} not found")
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file {config_file}: {e}")
        raise yaml.YAMLError(f"Error parsing YAML file {config_file}: {e}")