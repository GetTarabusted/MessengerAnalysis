import json
import os
import re


def reorder_messages_chronologically(file_path, new_file_path):
    """
    :param file_path: the non ordered JSON
    :param new_file_path: Path to the ordered JSON that is going to be generated
    :return: 0
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    messages = data['messages']

    # Sort messages by timestamp_ms
    sorted_messages = sorted(messages, key=lambda x: x['timestamp_ms'])

    # Updating the messages in the data dictionary
    data['messages'] = sorted_messages

    # Save the sorted messages to a new JSON file
    output_file_path = new_file_path
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(data, output_file, ensure_ascii=False, indent=2)

    return 0


def parse_obj(obj):
    if isinstance(obj, str):
        return obj.encode('latin_1').decode('utf-8')

    if isinstance(obj, list):
        return [parse_obj(o) for o in obj]

    if isinstance(obj, dict):
        return {key: parse_obj(item) for key, item in obj.items()}

    return obj


def reencode_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as input_file:
        data = json.load(input_file)
        decoded_data = parse_obj(data)
    with open(file_path, 'w', encoding='utf-8') as input_file:
        json.dump(decoded_data, input_file, ensure_ascii=False, indent=2)


def merge_json():
    """
    If placed in the messages directory, finds all the json in the same directory as him
    and merge all the messagesXX.json
    :return: 0 if successful
    """
    # We get the directory, list the files and filter the messageXX.json files we'll merge
    current_directory = os.path.dirname(os.path.abspath(__file__))
    files = os.listdir(current_directory)
    message_files = [file for file in files if re.match(r'message_\d+\.json', file)]

    # Now for the merging
    merged_data = {}

    # We gather the data through all the JSONs
    for file in message_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not merged_data:  # if merged_data is empty
            for key in data.keys():
                merged_data[key] = data[key]
        else:
            for key in data.keys():
                print(merged_data[key])
                merged_data[key].append(data[key])

    # Then dump them in our new file
    with open('merged_fileffff.json', 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    merge_json()
