import json
from datetime import datetime
import matplotlib.pyplot as plt
import re
import datetime
import numpy as np

"""

This file contains various functions I developed on the requests of some of my friends to see if we could get funny data 
out of our 5 years old group chat on messenger. 

"""
def get_messages_by_participant(messages):
    """
    :param messages: in JSON format
    :return: dict name:msg_count ordered from higher to lower
    """

    participant_counts = {}
    for message in messages:
        sender = message['sender_name']

        if sender not in participant_counts:
            participant_counts[sender] = 1
        else:
            participant_counts[sender] += 1

    sorted_counts = dict(sorted(participant_counts.items(), key=lambda x: x[1], reverse=True))

    return sorted_counts


def time_since_origin(messages):
    if len(messages) < 2:
        return None

    first_message_timestamp = messages[0]['timestamp_ms']
    last_message_timestamp = messages[-1]['timestamp_ms']

    first_message_datetime = datetime.utcfromtimestamp(first_message_timestamp / 1000)
    last_message_datetime = datetime.utcfromtimestamp(last_message_timestamp / 1000)

    delta = last_message_datetime - first_message_datetime
    days = delta.days
    years = days // 365.25
    remaining_days = days % 365.25

    return f"{years} years, {remaining_days:.0f} days"


def get_mean_msg_length(messages):
    """
    :param messages: messages in a JSON format
    :return: {names : mean_msg_length}
    """

    participant_dict = {}
    for message in messages:
        sender = message['sender_name']

        if sender not in participant_dict and 'content' in message:
            participant_dict[sender] = [len(message['content'])]
        elif 'content' in message:
            participant_dict[sender].append(len(message['content']))

    mean_dict = {participant: sum(values_list) / len(values_list) for participant, values_list in
                 participant_dict.items()}
    mean_dict = dict(sorted(mean_dict.items(), key=lambda x: x[1], reverse=True))

    return mean_dict


def order_by_length(messages, reverse=True):
    """
    Reorders the message by length (longer first)
    :param reverse: if True returns the messages from shortest to longest. False by default.
    :param messages: messages in JSON format
    :return: dict of messages ordered from longest to shortest by default. See also: reverse
    """
    ordered_messages_by_length = sorted(messages,
                                        key=lambda message: len(message['content']) if 'content' in message else 0,
                                        reverse=reverse)
    return ordered_messages_by_length


def order_by_time(messages, reverse=False):
    """
    :param reverse: If true returns the messages from most recent to oldest. False by default.
    :param messages: messages in JSON format.
    :return: dict of messages ordered from oldest to newest by default.
    """
    ordered_messages = dict(sorted(messages, key=lambda msg: msg['timestamp_ms'], reverse=reverse))
    return ordered_messages


def get_reactions_count(messages, weighted=False, details=False):
    """
    Count the reaction obtained by someone on all their messages
    :param weighted: if you want the mean with their reaction count compared to their total messages
    :param messages: in a JSON format
    :return: dict with name/mean format ordered from most to least
    """
    participant_dict = {}
    for message in messages:
        sender = message['sender_name']

        if details:
            if sender not in participant_dict and 'reactions' in message:
                participant_dict[sender] = {}
                for reaction in message['reactions']:
                    if reaction['reaction'] not in participant_dict[sender]:
                        participant_dict[sender][reaction['reaction']] = 1
                    else:
                        participant_dict[sender][reaction['reaction']] += 1
            elif 'reactions' in message:
                for reaction in message['reactions']:
                    if reaction['reaction'] not in participant_dict[sender]:
                        participant_dict[sender][reaction['reaction']] = 1
                    else:
                        participant_dict[sender][reaction['reaction']] += 1
        else:
            if sender not in participant_dict and 'reactions' in message:
                participant_dict[sender] = len(message['reactions'])
            elif 'reactions' in message:
                participant_dict[sender] += len(message['reactions'])

    msg_count = get_messages_by_participant(messages)

    if weighted:
        mean_dict = {participant: participant_dict[participant] / msg_count[participant] for participant in
                     msg_count.keys()
                     & participant_dict}
        mean_dict = dict(sorted(mean_dict.items(), key=lambda x: x[1], reverse=True))
        return mean_dict
    elif details:
        return participant_dict
    else:
        return dict(sorted(participant_dict.items(), key=lambda x: x[1], reverse=True))


def get_photos_sent(messages):
    participant_counts = {}

    for message in messages:
        if 'photos' in message:
            sender = message['sender_name']
            if sender not in participant_counts:
                participant_counts[sender] = 1
            else:
                participant_counts[sender] += 1

    sorted_counts = dict(sorted(participant_counts.items(), key=lambda x: x[1], reverse=True))
    return sorted_counts


def get_videos_sent(messages):
    participant_counts = {}

    for message in messages:
        if 'videos' in message:
            sender = message['sender_name']
            if sender not in participant_counts:
                participant_counts[sender] = 1
            else:
                participant_counts[sender] += 1

    sorted_counts = dict(sorted(participant_counts.items(), key=lambda x: x[1], reverse=True))
    return sorted_counts


def get_tiktok_links(messages):
    """
    :param messages: in JSON format
    :return: dict name:msg_count ordered from higher to lower
    """

    participant_links = {}
    for message in messages:
        sender = message['sender_name']

        if 'content' in message:
            if sender not in participant_links and 'tiktok.com' in message['content']:
                participant_links[sender] = 1
            elif 'tiktok.com' in message['content']:
                participant_links[sender] += 1

    sorted_counts = dict(sorted(participant_links.items(), key=lambda x: x[1], reverse=True))
    return sorted_counts


def rank_words(messages):
    words_ranking = {}
    unwanted_char = ['[', ']', '!', '#', '$', '%', '^', '&', '*', '(', ')', '€', '/', '\\', ".", ",", "…", "t'", "d'",
                     "l'", "j'", "s'", "’", "'", '"', "?"]
    link = r"[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"
    pattern = "|".join([re.escape(c) for c in unwanted_char])
    for message in messages:
        if 'content' in message:
            # We remove the links, and if we found one we go to the next message
            if re.findall(link, message["content"]):
                continue
            stripped_word = message['content'].lower()  # We don't care about case
            # We take out the unwanted characters and replacing them with spaces
            stripped_word = re.sub(pattern, ' ', stripped_word)
            # Then for consistency we replace all accents by their regular counterpart
            stripped_word = stripped_word.replace("é", "e").replace("â", "a").replace("ê", "e").replace("ô",
                                                                                                        "o").replace(
                "è", "e")
            split_word = stripped_word.split()  # then finally split the words
            for word in split_word:
                word = word
                if word not in words_ranking:
                    words_ranking[word] = 1
                else:
                    words_ranking[word] += 1

    sorted_counts = dict(sorted(words_ranking.items(), key=lambda x: x[1], reverse=True))
    return sorted_counts


def plot_bar_chart(title, data):
    """
    Plots a bar chart based on the dict in input
    :param data: dict{data1:amount, data2:amount...}
    :param title: Title of the graph
    :return: nothing, prints a plot
    """
    plt.figure()

    names = list(data.keys())
    values = list(data.values())
    plt.title(title)
    plt.bar(names, values)
    plt.xticks(rotation=20, ha='right')
    plt.subplots_adjust(bottom=0.18)
    plt.show()

    # -*- Free used memory
    plt.clf()
    plt.close()


def get_messages_by_time(messages):
    """
    Takes the messages in JSON and outputs a dict with all the minutes and their messsages associated
    :param messages: in JSON format
    :return: dict minute:msg_count
    """

    minutes_counts = {}
    # We populate the dictionary from 00:00 to 23:59
    """
    for hour in range(0, 24):
        for minute in range(0, 60):
            minutes_counts[str(hour) + ":" + str(minute)] = 0
    """
    for hour in range(0, 24):
        minutes_counts[str(hour)] = 0

    # Now we go through the messages and fill our dictionnary
    for message in messages:
        time = message['timestamp_ms']
        # Convert timestamp from ms to date
        time = datetime.datetime.fromtimestamp(time / 1000)  # this funct takes seconds, not ms
        # minutes_counts[str(time.hour) + ":" + str(time.minute)] += 1
        minutes_counts[str(time.hour)] += 1

    return minutes_counts


def plot_round_graph(dict_to_plot):
    """

    :param dict_to_plot: {'title':{label:amount, label2:amount2...}}
    :return: nothing, plots the damn thing
    """
    # TODO: Finish
    for title, data in dict_to_plot.items():
        plt.figure()

        # Extract the times and numbers from the dictionary
        times = list(data.keys())
        numbers = list(data.values())
        print(data.values())

        # Create an array of angles for the polar plot
        angles = np.linspace(0, 2 * np.pi, len(times) - 1, endpoint=False)

        # Append the first angle to the end to close the circle
        angles = np.concatenate((angles, [angles[0]]))

        # Create a polar plot
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
        ax.plot(angles, numbers)
        ax.set_rmax(10000)

        # Set the title and show the plot
        plt.title(title)
        plt.show()
        # -*- Free used memory
        plt.clf()
        plt.close()


def count_word_apparition(messages, word):
    """
    :param messages: in JSON format
    :param word: word to look for
    :return: dict name:msg_count ordered from higher to lower
    """

    participant_word_count = {}
    for message in messages:
        sender = message['sender_name']

        if 'content' in message:
            if sender not in participant_word_count and word in message['content']:
                participant_word_count[sender] = 1
                print(message['sender_name'], ": ", message['content'])
            elif word in message['content']:
                participant_word_count[sender] += 1
                print(message['sender_name'], ": ", message['content'])

    sorted_counts = dict(sorted(participant_word_count.items(), key=lambda x: x[1], reverse=True))
    return sorted_counts


if __name__ == "__main__":
    file_path = "messages.json"
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    messages = data["messages"]
    mots = ["Inserer", "des", "mots", "ici"]
    # TODO : nombre de messages en fonction du timestamp (par mois, années, par jour de la semaine etc)

    print(count_word_apparition(messages, "kek"))
