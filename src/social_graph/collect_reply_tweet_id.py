import time, json, html
import pandas as pd
from searchtweets import ResultStream, gen_request_parameters, load_credentials
from src.util.Configuration import Configuration
from tqdm import tqdm

'''
    Looking up Tweet Replies with Twitter v2 API version 06.12.22
    @author Joel Guggisberg adapted Code from https://github.com/twitterdev/search-tweets-python/tree/v2
'''
def build_twitter_search_query (tweet_id) :
    query = [
            "lang:en",      # Lanugage
            "conversation_id:" + str(tweet_id),  # Only original tweets
            #"has:links"     # Looking for link to article
        ]

    out_query = html.escape(" ".join(query))
    if len(out_query) > 1024:
        print("Search Query too long")
        return None
    return out_query


def search_twitter(credential_file, start_time, tweet_id, out_file_path):
    search_args = load_credentials(filename=credential_file,
                 yaml_key="search_tweets_v2",
                 env_overwrite=True)
    search_query = build_twitter_search_query (tweet_id)

    # Search Constraints
    query = gen_request_parameters(
            search_query, 
            start_time=start_time, 
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
    with open(out_file_path,'a') as outfile:
        for tweet in rs.stream():
            x = json.dumps(tweet) # to string
            outfile.write(str(tweet_id)+'~'+x+'\n')


#-------------------------------
def collect_reply_tweet_id(config: Configuration):
    # Parameters
    credential_file = config.twitterv2_credential_file_path
    start_time = config.search_tweets_from
    skip = config.skip_main_tweets

    out_file_name = 'tweets_unfiltered_real_reply.txt'
    in_file_name = 'tweets_filtered_real_main.txt'
    in_file_path = config.data_folder_path + in_file_name
    out_file_path = config.data_folder_path + out_file_name
    tweet_hash = {}
    data = pd.read_csv(in_file_path)
    for index, row in tqdm(data.iterrows()):
        if skip > 0 and index<skip: continue
        tweet_id = row['id']
        if tweet_id in tweet_hash: continue
        tweet_hash[tweet_id] = 1
        search_twitter(
            credential_file=credential_file,
            start_time=start_time,
            tweet_id=tweet_id,
            out_file_path=out_file_path
            )
        time.sleep(5)
    print("uniqe tweets ", len(tweet_hash.keys()))
