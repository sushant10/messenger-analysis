from fbchat import Client
from fbchat.models import *
import string
import getpass

class MessengerAnalysis:
    def __init__(self, email, password):
        self.client = Client(email, password)
        self.all_words = {}
        self.users = {}
        self.words_by_users = {}
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
            'youre'
        ]
        self.punctuation_table = str.maketrans({key: None for key in string.punctuation})

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

        for message in self.messages:

            user_id = message.author

            if user_id not in self.users:
                self.users[user_id] = self.get_user_name(user_id)

            if user_id not in self.words_by_users:
                self.words_by_users[user_id] = {}

            user_name = self.users[user_id]

            if not message.text:
                continue
            
            words = message.text.split()
            cleaned_words = self.clean_up_words(words)

            for word in cleaned_words:
                if word not in self.all_words:
                    self.all_words[word] = 0
                self.all_words[word] += 1

                user_words_dict = self.words_by_users[user_id]
                if word not in user_words_dict:
                    user_words_dict[word] = 0
                user_words_dict[word] += 1

        print('Analysis Complete!')

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


    def get_top_words(self, limit=10, reverse=True):
        sorted_by_frequency = self.get_sorted_by_frequency(self.all_words, reverse=reverse)
        self.print_words(sorted_by_frequency, self.all_words, limit)
            
    
    def get_top_words_by_user(self, limit=10, reverse=True):
        for user_id in self.users:
            user_words_dict = self.words_by_users[user_id]
            sorted_by_frequency = self.get_sorted_by_frequency(user_words_dict, reverse=reverse)
            print(self.users[user_id] + ':')
            self.print_words(sorted_by_frequency, user_words_dict, limit)
            print('\n')


if __name__ == '__main__':
    print("Welcome to Messenger Analysis")
    print("Note: I have a bad memory so I'll forget your email and password after you give it to me. You don't have to worry about it being stolen")
    print("Email", end=": ")
    email = input()
    print("Password", end=": ")
    password = getpass.getpass()

    ma = MessengerAnalysis(email, password)

    print("Here are the 5 most recent messenger threads. Which one would you like to analyze?")
    threads = ma.get_thread_list(5) 

    for thread_id in threads:
        print(thread_id)

    print("Insert thread ID", end=": ")

    thread = input()

    ma.get_messages_and_analyze(thread, 5000)
    ma.get_top_words_by_user(10, True)

