import tweepy
import time
from grammarbot import GrammarBotClient
# import grammar_check
# import language_check
# import language_tool
# from spellchecker import SpellChecker

CONSUMER_KEY = 'wYZG3AOqdYucmU7otA199zRHZ'
CONSUMER_SECRET = 'G69wpB429jfXOTJwlrlk3sz4xlCmS0Ah5Wd9JjP9KsmqHqHAhQ'
ACCESS_KEY = '1212186443621122048-FQ96m7gvRm1I7ZUzd2chB4zAAQjc0j'
ACCESS_SECRET = 'sRtp39G8jh3sL8Ky0FWnFv7HUFWWKUJjLXjfisl2mBRfw'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

ID_DATA_BASE = 'last_seen_id.txt'


# Returns ID of the last tweet replied to
def get_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id


# Stores ID of the last tweet replied to in last_seen_id.txt
def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return


# Creates tweet with correction suggestions
def fix_tweet(text):
    # spell = SpellChecker()
    # list_text = list(text.split(" "))
    # misspelled = spell.unknown(list_text)

    # print(text)
    # for word in misspelled:
    #     print(word)
    #     text.replace(word, spell.correction(word))

    # print(text)

    # lang_tool = language_tool.LanguageTool("en-US")
    # matches = lang_tool.check(text)

    # tool = language_check.LanguageTool('en-US')
    # matches = tool.check(text)
    # print(language_check.correct(text, matches))

    # print(res.raw_json)

    NEWLINE = '\n'

    # Creating the client
    client = GrammarBotClient()

    # check the text, returns GrammarBotApiResponse object
    res = client.check(text)

    tweets_to_make = []
    correct_text = ""
    limit = ""

    # Construct tweet
    for match in res.matches:
        # Create messages
        if (match.category == 'TYPOS'):
            correct_text += "At the start of character number " + \
                str(match.replacement_offset) + " did you mean any of the following instead: " + \
                str(match.replacements[0:3]) + "."
        else:
            correct_text += match.message

        # Insert a new line after each recommendation
        correct_text += NEWLINE

        # Make sure it doesn't exceed the tweet character limit
        if (len(limit) + len(correct_text)) > 280:
            tweets_to_make.append(limit)
            limit = ""
        limit += correct_text
        correct_text = ""

    tweets_to_make.append(limit)

    return tweets_to_make


# Replies to tweet with potential corrections
def reply_to_tweets():
    # Tesing ID - 1212534863007559682
    last_seen_id = get_last_seen_id(ID_DATA_BASE)
    # Gets mentions occurring after last_seen_id
    mentions = api.mentions_timeline(last_seen_id, tweet_mode='extended')
    # mentions = api.mentions_timeline()

    # Responds to each mention in order
    for mention in reversed(mentions):
        print(str(mention.id) + " - " + mention.full_text)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, ID_DATA_BASE)
        # removes mention text and leading/trailing whitespace
        new_text = mention.full_text.replace(
            "@tweetcheckerbot", "").lstrip().rstrip()
        # gets reply tweets
        tweets_to_make = fix_tweet(new_text)
        # if their tweet had no errors it does not reply
        if tweets_to_make:
            for tweet in tweets_to_make:
                if tweet != "":
                    api.update_status('@' + mention.user.screen_name +
                              " " + tweet, mention.id)


# checks for new mentions every 15 seconds
while True:
    reply_to_tweets()
    time.sleep(15)
