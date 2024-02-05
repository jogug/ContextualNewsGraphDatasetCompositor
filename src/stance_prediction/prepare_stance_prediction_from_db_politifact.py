import codecs, codecs
from src.util.Configuration import Configuration
from src.util.StringCleanUtil import clean_tweet_text

'''
Generates the file for stance prediction
'''
def prepare_stance_prediction_from_db_politifact(config: Configuration):
    DB_database = config.DB_database
    DATA_TWEET_TABLE = config.DATA_TWEET_TABLE
    DATA_ARTICLE_TABLE = config.DATA_ARTICLE_TABLE
    data_folder_path = config.data_folder_path
    NEWS_TITLE_COLUMN = config.NEWS_TITLE_COLUMN

    out_file_name = 'predict_1.tsv'
    out_file_path = data_folder_path + out_file_name

    def generate_stance_predict (config: Configuration):
        db = config.get_db()
        out_file = codecs.open(out_file_path, "w", "utf-8")
        cursor = db.get_cursor(dictionary=True)
        print(f"SELECT * FROM (SELECT * FROM {DB_database}.{DATA_TWEET_TABLE} WHERE article_id > 0) a LEFT JOIN {DB_database}.{DATA_ARTICLE_TABLE} b ON a.article_id = b.id")
        cursor.execute(f"SELECT * FROM (SELECT * FROM {DB_database}.{DATA_TWEET_TABLE} WHERE article_id > 0) a LEFT JOIN {DB_database}.{DATA_ARTICLE_TABLE} b ON a.article_id = b.id")
        for row in cursor:
            tweetID = row['tweet_id']
            articleID = row['article_id']
            title = row[NEWS_TITLE_COLUMN]
            tweet_text = clean_tweet_text (row["text"])
            if title is None or title == "" or tweet_text is None or tweet_text == "":
                continue
            out_file.write(
                "\t".join([str(articleID)+"_"+str(tweetID), title, tweet_text]) + "\n"
            )
        out_file.close()

    generate_stance_predict (config)
