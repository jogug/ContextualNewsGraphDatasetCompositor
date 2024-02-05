import json
import pandas as pd
from tqdm import tqdm
from src.util.Configuration import Configuration


def load_tweets_into_db(config: Configuration):
    DATA_TWEET_TABLE = config.DATA_TWEET_TABLE

    # Try finding associated tweets according to FakeNewsNet
    in_files = [
        { "in_file_name" : 'tweets_filtered_fake_main.txt',
          "realfake" : "fake",
          "target" : "main",
        },
        { "in_file_name" : 'tweets_filtered_fake_reply.txt',
          "realfake" : "fake",
          "target" : "reply",
        },
        { "in_file_name" : 'tweets_filtered_real_main.txt',
          "realfake" : "real",
          "target" : "main",
        },
        { "in_file_name" : 'tweets_filtered_real_reply.txt',
          "realfake" : "real",
          "target" : "reply",
        },
        { 
          "in_file_name" : 'tweets_unfiltered_topic_real_main.txt',
          "realfake" : "real",
          "target" : "main",
        }
    ]

    default_insert_values = {
        "article_id" : 0,
        "source_tweet_id" : 0,
        "tweet_id" : 0,
        "author_id" : 0,
        "created_at" : "NULL",
        "realfake" : "NULL",
        "status" : "Reload",
        "content" : "",
        "text" : ""
    }

    cur_inserts = []
    for in_file in in_files:
        in_file_name = in_file["in_file_name"]
        realfake = in_file["realfake"]
        target = in_file["target"]
        in_file_path = config.data_folder_path + in_file_name
        df = pd.read_csv(in_file_path)
        
        for index, row in df.iterrows():
            cur_insert = dict(default_insert_values)
            cur_insert["tweet_id"] = row["id"]
            cur_insert["author_id"] = row["author_id"]
            cur_insert["realfake"] = realfake
            cur_insert["created_at"] = row["created_at"]
            if "source_id" in row:
              cur_insert["source_tweet_id"] = row["source_id"]
            if "text" in row:
              cur_insert["text"] = json.dumps(row["text"]).replace("\\'", "").replace("\'", "").replace("'", "")
            if target == "main":
                if "article_id" in row:
                  cur_insert["article_id"] = row["article_id"]

            cur_insert["content"] = row["content"].replace("\n", "").replace("\\'", "").replace("\'", "").replace("'", "")
            cur_inserts.append(cur_insert)


    # Store Users in DB
    statement = f"""
    INSERT INTO `{DATA_TWEET_TABLE}` (`article_id`, `source_tweet_id`, `tweet_id`, `author_id`, `created_at`, `realfake`, `status`, `content`, `text`) 
    """ + """
    VALUES ({article_id},{source_tweet_id},{tweet_id},{author_id},'{created_at}','{realfake}','{status}','{content}','{text}')
    ON DUPLICATE KEY UPDATE author_id=VALUE(author_id),created_at=VALUE(created_at),article_id=VALUE(article_id),source_tweet_id=VALUE(source_tweet_id),
    realfake=VALUE(realfake),text=VALUE(text),content=VALUE(content)"""

    db = config.get_db()
    for cur_insert in tqdm(cur_inserts):
        db.execute(statement=statement.format(**cur_insert))
    db.disconnect()
    