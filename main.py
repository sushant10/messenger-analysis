from fbchat import Client
from fbchat.models import *
import string
import getpass
from emoji import UNICODE_EMOJI
import sys

class MessengerAnalysis:
    def __init__(self, email, password):
        self.client = Client(email, password)
        self.all_words = {}
        self.all_emojis = {}
        self.all_reactions = {}
        self.users = {}
        self.words_by_users = {}
        self.emojis_by_users = {}
        self.reactions_by_users = {}
        self.longest_time = -sys.maxsize - 1
        self.messages = []
        self.words_to_skip = [
            'the',
            'be',
            'to',
            'of',
            'and',
            'a',
            'in',
            'that',
            'have',
            'i',
            'it',
            'for',
            'not',
            'on',
            'with',
            'he',
            'as',
            'you',
            'do',
            'at',
            'this',
            'but',
            'his',
            'by',
            'from',
            'they',
            'we',
            'say',
            'her',
            'she',
            'or',
            'will',
            'an',
            'my',
            'one',
            'all',
            'would',
            'there',
            'their',
            'what',
            'so',
            'up',
            'out',
            'if',
            'about',
            'who',
            'get',
            'which',
            'go',
            'when',
            'me',
            'make',
            'can',
            'like',
            'time',
            'no',
            'just',
            'him',
            'know',
            'take',
            'person',
            'into',
            'year',
            'your',
            'good',
            'some',
            'could',
            'them',
            'see',
            'other',
            'than',
            'then',
            'now',
            'look',
            'only',
            'come',
            'its',
            'over',
            'think',
            'also',
            'back',
            'after',
            'use',
            'two',
            'how',
            'our',
            'work',
            'first',
            'well',
            'way',
            'even',
            'new',
            'want',
            'because',
            'any',
            'these',
            'give',
            'day',
            'most',
            'us',
            'im',
            'is',
            'was',
            'yeah',
            'thats',
            'too',
            'ill',
            'ok',
            'okay',
            'are',
            'been',
            'dont',
            'had',
            'were',
            'cant',
            'youre',
            'got',
            'hes',
            'has',
            "i'm",
            "don't",
            "it's",
            'youll',
            'u',
            'tho',
            'did',
            'ive',
            'mean',
            'really',
            'gonna',
            'though',
            "you're",
            'here',
            'much'
        ]
        self.punctuation_table = str.maketrans({key: None for key in string.punctuation})

    def is_emoji(self, word):
        count = 0
        for emoji in UNICODE_EMOJI:
            count += word.count(emoji)
            if count > 1:
                return False
        return bool(count)

    def clean_up_words(self, words):
        cleaned_words = []
        for word in words:

            word = word.lower()
            word = word.translate(self.punctuation_table)

            if word in self.words_to_skip:
                continue

            cleaned_words.append(word)
        
        return cleaned_words

    def get_thread_list(self, limit=5):
        self.all_words = {}
        self.all_emojis = {}
        self.all_reactions = {}
        self.users = {}
        self.words_by_users = {}
        self.emojis_by_users = {}
        self.reactions_by_users = {}
        self.longest_time = -sys.maxsize - 1
        self.messages = []
        return self.client.fetchThreadList(limit=limit)

    def get_user_name(self, user_id):
        return self.client.fetchUserInfo(user_id)[user_id].name

    def get_thread_messages(self, thread_id, limit):
        return self.client.fetchThreadMessages(thread_id=thread_id, limit=limit)

    def get_messages_and_analyze(self, thread_id, limit=500):
        if self.messages:
            return

        self.messages = self.get_thread_messages(thread_id, limit)
        self.messages.reverse()
        last_message_time = None

        for message in self.messages:

            current_message_time = int(message.timestamp)
            if last_message_time != None:
                time_difference = current_message_time - last_message_time
                if time_difference > self.longest_time:
                    self.longest_time = time_difference
            last_message_time = current_message_time

            reactions = message.reactions
            if reactions:
                for id in reactions:
                    reaction = reactions[id]
                    if reaction not in self.all_reactions:
                        self.all_reactions[reaction] = 0
                    self.all_reactions[reaction] += 1

                    if id not in self.reactions_by_users:
                        self.reactions_by_users[id] = {}

                    user_dict = self.reactions_by_users[id]
                    
                    if reaction not in user_dict:
                        user_dict[reaction] = 0
                    user_dict[reaction] += 1

            if not message.text:
                continue

            user_id = message.author

            if user_id not in self.users:
                self.users[user_id] = self.get_user_name(user_id)

            if user_id not in self.words_by_users:
                self.words_by_users[user_id] = {}

            if user_id not in self.emojis_by_users:
                self.emojis_by_users[user_id] = {}

            user_name = self.users[user_id]
            
            words = message.text.split()
            cleaned_words = self.clean_up_words(words)

            for word in cleaned_words:

                if not word:
                    continue

                if self.is_emoji(word):
                    if word not in self.all_emojis:
                        self.all_emojis[word] = 0
                    self.all_emojis[word] += 1

                    user_emojis_dict = self.emojis_by_users[user_id]
                    if word not in user_emojis_dict:
                        user_emojis_dict[word] = 0
                    user_emojis_dict[word] += 1

                    continue

                if word not in self.all_words:
                    self.all_words[word] = 0
                self.all_words[word] += 1

                user_words_dict = self.words_by_users[user_id]
                if word not in user_words_dict:
                    user_words_dict[word] = 0
                user_words_dict[word] += 1

        print('Analysis Complete!')

    def convert_millis_to_time(self):
        millis = self.longest_time
        seconds=(millis/1000)%60
        seconds = int(seconds)
        minutes=(millis/(1000*60))%60
        minutes = int(minutes)
        hours=(millis/(1000*60*60))
        print ("%d:%d:%d" % (hours, minutes, seconds))

    def get_sorted_by_frequency(self, dict, reverse=True):
        return sorted(dict, key=dict.get, reverse=reverse)

    def print_words(self, words, dict, limit):
        index = 0
        for word in words:
            if index == limit:
                break
            
            index += 1
            print(word, end=': ')
            print(dict[word])

    def get_top_reactions(self, reverse=True):
        sorted_by_frequency = self.get_sorted_by_frequency(self.all_reactions, reverse=reverse)
        for reaction in sorted_by_frequency:
            print(reaction.value, end=": ")
            print(self.all_reactions[reaction])

    def get_top_reactions_by_user(self, reverse=True):
        for user_id in self.reactions_by_users:
            reaction_dict = self.reactions_by_users[user_id]
            user_name = self.users[user_id]
            sorted_by_frequency = self.get_sorted_by_frequency(reaction_dict, reverse=reverse)
            print(user_name)
            for reaction in sorted_by_frequency:
                print(reaction.value, end=": ")
                print(reaction_dict[reaction])

    def get_top_words(self, limit=10, reverse=True):
        sorted_by_frequency = self.get_sorted_by_frequency(self.all_words, reverse=reverse)
        self.print_words(sorted_by_frequency, self.all_words, limit)

    def get_top_emojis(self, limit=10, reverse=True):
        sorted_by_frequency = self.get_sorted_by_frequency(self.all_emojis, reverse=reverse)
        self.print_words(sorted_by_frequency, self.all_emojis, limit=limit)
    
    def get_top_words_by_user(self, limit=10, reverse=True):
        for user_id in self.users:
            user_words_dict = self.words_by_users[user_id]
            sorted_by_frequency = self.get_sorted_by_frequency(user_words_dict, reverse=reverse)
            print(self.users[user_id] + ':')
            self.print_words(sorted_by_frequency, user_words_dict, limit)
            print('\n')

    def get_top_emojis_by_user(self, limit=5, reverse=True):
        for user_id in self.users:
            user_emojis_dict = self.emojis_by_users[user_id]
            sorted_by_frequency = self.get_sorted_by_frequency(user_emojis_dict, reverse=reverse)
            print(self.users[user_id] + ':')
            self.print_words(sorted_by_frequency, user_emojis_dict, limit)
            print('\n')

def print_threads(threads):
    for thread_id in threads:
        print(thread_id)

def print_options():
    print("What would you like to do?")
    print("[1] Get top words from conversation")
    print("[2] Get top words per user")
    print("[3] Get top emojis from conversation")
    print("[4] Get top emojis per user")
    print("[5] Get top reactions from conversation")
    print("[6] Get top reactions per user")
    print("[7] Get longest time between messages")
    print("Type exit to quit")

if __name__ == '__main__':
    print("Welcome to Messenger Analysis")
    print("Note: I have a bad memory so I'll forget your email and password after you give it to me. You don't have to worry about it being stolen")
    print("Email", end=": ")
    email = input()
    print("Password", end=": ")
    password = getpass.getpass()

    ma = MessengerAnalysis(email, password)

    print("Here are the 10 most recent messenger threads. Which one would you like to analyze?") 

    while True:
        threads = ma.get_thread_list(10)
        print_threads(threads)
        print("Insert thread ID (type exit to quit)", end=": ")
        thread = input()
        if thread == 'exit':
            break

        print("Analyzing messages...")
        ma.get_messages_and_analyze(thread, 20000)

        while True:
            print_options()
            option = input()
            if option == 'exit':
                break
            if option == '1':
                ma.get_top_words(10, True)
            if option == '2':
                ma.get_top_words_by_user(10, True)
            if option == '3':
                ma.get_top_emojis(5, True)
            if option == '4':
                ma.get_top_emojis_by_user(5, True)
            if option == '5':
                ma.get_top_reactions(True)
            if option == '6':
                ma.get_top_reactions_by_user(True)
            if option == '7':
                ma.convert_millis_to_time()

    
  
    

