import codecs, os, codecs, re
from src.util.Configuration import Configuration
from src.util.StringCleanUtil import clean_tweet_text

'''
Generates the file for stance prediction
'''
def prepare_stance_prediction_from_db_real_twitter(config: Configuration):
    DB_database = config.DB_database
    DATA_TWEET_TABLE = config.DATA_TWEET_TABLE
    data_folder_path = config.data_folder_path

    out_file_name = 'predict_2.tsv'
    out_file_path = data_folder_path + out_file_name

    def generate_stance_predict (config : Configuration):
        db = config.get_db()
        out_file = codecs.open(out_file_path, "w", "utf-8")
        cursor = db.get_cursor(dictionary=True)
        cursor.execute(f"SELECT a.*, b.text as statement FROM (SELECT * FROM {DB_database}.{DATA_TWEET_TABLE} WHERE article_id = 0) a LEFT JOIN {DB_database}.{DATA_TWEET_TABLE} b ON a.source_tweet_id = b.tweet_id")
        for row in cursor:
            tweetID = row['tweet_id']
            articleID = row['article_id']
            title = row['statement']
            tweet_text = clean_tweet_text (row["text"])
            # Publication
            if title == "" or title is None:
                title = tweet_text
            title = clean_tweet_text (title)
            if tweet_text == "" or title == "" or tweet_text is None or title is None:
                continue
            out_file.write(
                "\t".join([str(articleID)+"_"+str(tweetID), title, tweet_text]) + "\n"
            )
        out_file.close()

    generate_stance_predict (config)
