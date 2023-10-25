# Modified read and write JSON file functions
import os
import json


def read_json_file(file_path):
    """Reads a JSON file and returns its content as a dictionary. 
    If the file doesn't exist, it creates the file and returns a default message."""
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump({"message": "Nothing in this file yet!"}, f, indent=4)
        return {"message": "Nothing in this file yet!"}
    else:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data


def write_json_file(file_path, data):
    """Writes a dictionary to a JSON file. If the file doesn't exist, it creates the file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
