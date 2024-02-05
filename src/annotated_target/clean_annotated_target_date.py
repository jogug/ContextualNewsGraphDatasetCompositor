from src.util.Configuration import Configuration
from src.util.DateCleanUtil import try_parse_multi_date

def clean_annotated_target_date(config: Configuration):

    db = config.get_db()
    db_insert = config.get_db()

    DB_database = config.DB_database
    DATA_ARTICLE_TABLE = config.DATA_ARTICLE_TABLE

    cursor = db.get_cursor(dictionary=True)

    cursor.execute("""
    SELECT id, published_date_cleaned, published_date, date FROM {DB_database}.{DATA_ARTICLE_TABLE} WHERE published_date_cleaned IS NULL OR published_date_cleaned = ""
    """.format(DB_database=DB_database,DATA_ARTICLE_TABLE=DATA_ARTICLE_TABLE))

    for row in cursor:
        published_date_cleaned = row['published_date_cleaned']
        if published_date_cleaned is None or published_date_cleaned == "":
            article_id = row["id"]
            publish_date = row["published_date"]
            if publish_date == "" or publish_date is None:
                publish_date = row["date"]

            result = try_parse_multi_date(publish_date)

            if result is None:
                 publish_date = row["date"]
                 result = try_parse_multi_date(row["date"])
            
            if result is not None:
                mysql_datetime_str = result.strftime('%Y-%m-%d %H:%M:%S')
                statement = """
                        UPDATE {DB_database}.{DATA_ARTICLE_TABLE} SET published_date_cleaned = '{ts}' WHERE id = {article_id}
                    """.format(DB_database=DB_database,DATA_ARTICLE_TABLE=DATA_ARTICLE_TABLE, ts=mysql_datetime_str, article_id=article_id)
                db_insert.execute(statement)
            else:
                print("Failed", article_id, publish_date)

    cursor.close()
    db.disconnect()
    db_insert.disconnect()
