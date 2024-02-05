import re

# Clean Emojis
# Reference: https://stackoverflow.com/questions/33404752/removing-emojis-from-a-string-in-python
emoji_pattern = re.compile("["
    u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u2066"
        u"\u2069"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
        "]+", flags=re.UNICODE)

def clean_tweet_text (text):
    text = emoji_pattern.sub(r'', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'https\S+', '', text)
    text = text.replace("\t", "")
    text = text.replace("\n", "")
    text = text.replace("\r", "")
    return text

rep = {" and ": "", " and\n": "", ":": "", ".": "", "'": "", " and\n": "", "'s": "", "&": "", "—": "", "‘": "", "\n": "", "...": ""} 
rep = dict((re.escape(k), v) for k, v in rep.items()) 
clean_search_pattern = re.compile("|".join(rep.keys()))

def clean_text_for_search(text):
    return clean_search_pattern.sub(lambda m: rep[re.escape(m.group(0))], text).strip()

def clean_text_name(text):
    return text.replace("'", "").replace("\\", "").replace('"', '').replace("\n", "").replace("•","")

def clean_statements(statements):
    return [statement.replace("“","").replace("”", "").replace('"', "").replace("’", "'") for statement in statements]
