
import time, json, html
import pandas as pd
from searchtweets import ResultStream, gen_request_parameters, load_credentials
from src.util.StringCleanUtil import clean_text_for_search

'''
    Looking up Tweets with Twitter v2 API version 06.11.22

    TLDR: search_args contains auth, query contains search constraints, 
    !Note granularity=None means searching for tweets. wtf? implicit vs explicit much..

    pip package: https://pypi.org/project/searchtweets-v2/

    Query: Build A Query Guide
    https://developer.twitter.com/en/docs/twitter-api/tweets/counts/integrate/build-a-query

    Quick Start
    https://developer.twitter.com/en/docs/twitter-api/tweets/lookup/quick-start

    Expansion - expands objects referenced in the payload
    explanation: https://developer.twitter.com/en/docs/twitter-api/expansions

    Fields
    https://developer.twitter.com/en/docs/twitter-api/fields

    @author Joel Guggisberg adapted Code from https://github.com/twitterdev/search-tweets-python/tree/v2
'''

def build_twitter_search_query (text, max_query_length) :
    '''
        If you have Essential or Elevated access, your query can be 512 characters long.
        If you have Academic Research access, your query can be 1024 characters long.
    '''
    if len(text) > max_query_length:
        print("Search Text too long")
        return None
    text = clean_text_for_search(text.strip() + '\n')

    query = [
            text,
            "lang:en",      # Lanugage
            "-is:retweet",  # Only original tweets
            #"has:links"     # Looking for link to article
        ]

    out_query = html.escape(" ".join(query))
    if len(out_query) > max_query_length:
        print("Search Query too long")
        return None
    return out_query


def search_twitter(credential_file, search_tweets_from, search_text, statement, max_query_length):
    search_args = load_credentials(filename=credential_file,
                 yaml_key="search_tweets_v2",
                 env_overwrite=True)
    search_query = build_twitter_search_query (search_text, max_query_length)

    # Search Constraints
    query = gen_request_parameters(
            search_query, 
            start_time=search_tweets_from, 
            results_per_call=100, # TODO set to max,  (default 10; max 100)
            expansions='author_id,geo.place_id,referenced_tweets.id', 
            tweet_fields='conversation_id,in_reply_to_user_id,author_id,text,created_at,geo',
            #user_fields='description,location', 
            granularity=None # day returns count else None returns search
        )

    # Actual Search
    rs = ResultStream(request_parameters=query,
                        max_results=100,
                        max_pages=100,
                        max_tweets=1000,
                        **search_args)

    # Collecting results
    result = []
    for tweet in rs.stream():
        result.append(json.dumps(tweet)) # to string
    return result


#-------------------------------
def shorten_statement (statement, nr_words_statement):
    return " ".join(statement.strip().split(" ")[:nr_words_statement])

def download_tweet_ids(out_file_path: str, data: pd.DataFrame, search_tweets_from, credential_file, 
        nr_words_statement, max_query_length, filter_by_source_tweets = False, skip=0):
    statement_hash = {}
    unique_statements = 0
    for index, row in data.iterrows():
        if skip > 0 and index<skip: continue
        if not filter_by_source_tweets or row['source'] == "Tweets": 
            statement = shorten_statement (row["statement"], nr_words_statement)
            if statement in statement_hash: continue
            statement_hash[statement] = 1
            unique_statements+=1
            print(statement)
            result = search_twitter(
                credential_file=credential_file,
                search_text=statement,
                search_tweets_from=search_tweets_from,
                statement=statement,
                max_query_length=max_query_length
                )
            with open(out_file_path,'a') as outfile:
                for tweets in result:
                    outfile.write(str(row["index"])+'~'+tweets+'\n')
            time.sleep(5)

    print("uniqe statements", unique_statements)


def download_main_tweet_id(conf):
    misinformation_data = []
    in_file_path = conf.data_folder_path + 'articles.csv'
    out_file_path = conf.data_folder_path + 'tweets_unfiltered_fake_main.txt'

    df = pd.read_csv(in_file_path)
    misinformation_data.append(df)
    misinformation_data = pd.concat(misinformation_data)

    download_tweet_ids(
        out_file_path=out_file_path, 
        data=misinformation_data, 
        search_tweets_from=conf.search_tweets_from, 
        credential_file=conf.twitterv2_credential_file_path, 
        nr_words_statement=conf.nr_words_statement, 
        max_query_length=conf.max_query_length, 
        filter_by_source_tweets=conf.filter_by_source_tweets, 
        skip=conf.skip)
