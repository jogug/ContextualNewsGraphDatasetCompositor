import json, requests, html
from src.util.Configuration import Configuration
from searchtweets import ResultStream, gen_request_parameters, load_credentials
from src.util.StringCleanUtil import clean_text_for_search

# Adapted from Documentation https://pypi.org/project/searchtweets-v2/

def connect_to_endpoint(url, params, bearer_token):
    response = requests.request("GET", url, params=params, headers={
        "Authorization" : f"Bearer {bearer_token}",
        "User-Agent" : "v2UserTweetsPython",
    })
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def build_twitter_search_query (twitter_handle, text, max_query_length) :
    '''
        If you have Essential or Elevated access, your query can be 512 characters long.
        If you have Academic Research access, your query can be 1024 characters long.
    '''
    if len(text) > max_query_length:
        print("Search Text too long")
        return None
    text = clean_text_for_search(text.strip() + '\n')

    query = [
            "from:" + twitter_handle,
            "lang:en",      # Lanugage
            "-is:retweet",  # Only original tweets
            text,
            #"has:links"     # Looking for link to article
        ]

    out_query = html.escape(" ".join(query))
    if len(out_query) > max_query_length:
        print("Search Query too long")
        return None
    return out_query

def collect_user_tweets_topic(config: Configuration):

    out_filename = "tweets_unfiltered_topic_real_main.txt"
    out_filepath = config.data_folder_path + out_filename

    respected_sources = config.respected_sources
    tag_names = config.tag_names
    start_time = config.search_tweets_from

    for respected_source in respected_sources:
        for tag_name in tag_names:
            search_query = build_twitter_search_query (respected_source,tag_name, 500)
            query = gen_request_parameters(
                    search_query, 
                    start_time=start_time, 
                    results_per_call=100, 
                    expansions='author_id,geo.place_id,referenced_tweets.id', 
                    tweet_fields='attachments,author_id,created_at,geo,id,in_reply_to_user_id,lang,public_metrics,referenced_tweets,source,text,withheld',
                    #user_fields='description,location', 
                    granularity=None # day returns count else None returns search
                )
            search_args = load_credentials(filename=config.twitterv2_credential_file_path,
                        yaml_key="search_tweets_v2",
                        env_overwrite=True)

            # Actual Search
            rs = ResultStream(request_parameters=query,
                                max_results=100,
                                max_pages=15,
                                max_tweets=1500,
                                **search_args)

            # Collecting results
            result = []
            for tweet in rs.stream():
                result.append(json.dumps(tweet)) # to string

            with open(out_filepath,'a') as outfile:
                for tweets in result:
                    outfile.write(respected_source+","+tag_name+'~'+tweets+'\n') 