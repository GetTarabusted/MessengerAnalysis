import json
import os
import re
import tools # not used here but you get the idea


def merge_json(output_file):
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
        elif 'messages' in data.keys():
            merged_data["messages"] += (data["messages"])

    # Then dump them in our new file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    print("JSON files have been successfully merged.")


def reorder_messages_chronologically(file_path):
    """
    Reorders the messages chronologically because somehow Meta doesn't do it by default ??
    :param file_path: the non-ordered JSON
    :return: 0 if successful
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    messages = data['messages']
    # Sort messages by timestamp_ms
    sorted_messages = sorted(messages, key=lambda msg: msg['timestamp_ms'])

    # Updating the messages in the data dictionary
    data['messages'] = sorted_messages

    # Save the sorted messages to a new JSON file
    with open(file_path, 'w', encoding='utf-8') as output_file:
        json.dump(data, output_file, ensure_ascii=False, indent=2)
    print("Messages successfully reordered by timestamp.")


def parse_obj(obj):
    """
    Small parser made thanks to internet (thanks, internet!) to decode any message and re-encode it in utf-8
    :param obj: json data (not file)
    :return: data re-encoded
    """
    if isinstance(obj, str):
        return obj.encode('latin_1').decode('utf-8')

    if isinstance(obj, list):
        return [parse_obj(o) for o in obj]

    if isinstance(obj, dict):
        return {key: parse_obj(item) for key, item in obj.items()}

    return obj


def reencode_json(file_path):
    """
    For some reason unbeknownst to god himself, Facebook encodes everything in latin-1 (?????) so we need for our mental
    sake to re-encode the whole thing in utf-8 since we are French and use weird stuff (é,è, à, etc...)
    :param file_path: json path
    :return: nothing, its a destructive operation
    """
    with open(file_path, 'r', encoding='utf-8') as input_file:
        data = json.load(input_file)
    decoded_data = parse_obj(data)
    with open(file_path, 'w', encoding='utf-8') as input_file:
        json.dump(decoded_data, input_file, ensure_ascii=False, indent=2)
    print("Final JSON re-encoded correctly as: ", file_path)


def nuke(file_path, people):
    """
    Delete all the messages of the specified senders
    :param file_path: json file path of the entire convo
    :param people: dict containing exact name to nuke out of the convo
    :return: same json but with all activity from specified ppl removed
    """
    with open(file_path, 'r', encoding='utf-8') as input_file:
        data = json.load(input_file)
    nuked_messages = [msg for msg in data["messages"] if msg.get('sender_name') not in people]
    data["messages"] = nuked_messages
    with open(file_path, 'w', encoding='utf-8') as input_file:
        json.dump(data, input_file, ensure_ascii=False, indent=2)
    print(people, "'s messages successfully nuked !")


if __name__ == "__main__":
    # Replace these file names with the actual file names of your JSON files. Those are the default ones at time of
    # writing

    # TODO: just detect the json files but i'm just lazy atm

    file_names = ['message_1.json', 'message_2.json', 'message_3.json', 'message_4.json', 'message_5.json',
                  'message_6.json', 'message_7.json', 'message_8.json', 'message_9.json', 'message_10.json',
                  'message_11.json', 'message_12.json', 'message_13.json', 'message_14.json', 'message_15.json']

    merge_json('messages.json')
    reorder_messages_chronologically('messages.json')
    reencode_json("messages.json")
    nuke("messages.json", ['Person You Dont Like', 'like your ex'])





