import json, requests
from src.util.Configuration import Configuration

# Credits adapted from 
# https://github.com/twitterdev/Twitter-API-v2-sample-code/blob/main/User-Tweet-Timeline/user_tweets.py

def connect_to_endpoint(url, params, bearer_token):
    response = requests.request("GET", url, params=params, headers={
        "Authorization" : f"Bearer {bearer_token}",
        "User-Agent" : "v2UserTweetsPython",
    })
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def download_user_timeline(config: Configuration):
    # Load User IDs
    bearer_token = config.search_tweets_v2["bearer_token"]
    user_id = 2244994945
    nytimes = 807095
    user_id = nytimes
    url_default = "https://api.twitter.com/2/users/{user_id}/tweets"
    url = url_default.format(user_id=user_id)
    params = {
        "exclude" : "retweets,replies",
        "tweet.fields" : "attachments,author_id,created_at,geo,id,in_reply_to_user_id,lang,public_metrics,referenced_tweets,source,text,withheld",    
        "max_results" : 100, 
        "end_time" : "2022-02-01T00:00:00Z",
    }
    json_response = connect_to_endpoint(url, params, bearer_token)
    print(json.dumps(json_response, indent=4, sort_keys=True))


download_user_timeline(Configuration())