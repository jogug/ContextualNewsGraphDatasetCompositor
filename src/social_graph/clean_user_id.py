import pandas as pd
from src.util.Database import Database
from src.util.Configuration import Configuration

def clean_user_id(config: Configuration):
    DB_database = config.DB_database
    DATA_USER_TABLE = config.DATA_USER_TABLE

    in_file_names = [
        'tweets_filtered_fake_main.txt',
        'tweets_filtered_fake_reply.txt',
        'tweets_filtered_real_main.txt',
        'tweets_filtered_real_reply.txt',
        'tweets_unfiltered_topic_real_main.txt'
    ]

    user_ids = set()
    for in_file_name in in_file_names:
        in_file_path = config.data_folder_path + in_file_name
        df = pd.read_csv(in_file_path)
        for author_id in df['author_id']:
            user_ids.add(author_id)

    # Store Users in DB
    status = "Reload"
    content = ""
    statement = "INSERT IGNORE INTO " + DB_database + "." + DATA_USER_TABLE + " (`userID`, `status`, `content`) VALUES ('{user_id}', '{status}', '{content}');"
    db = Database()
    for user_id in user_ids:
        db.execute(statement=statement.format(user_id=user_id, status=status, content=content))
    db.disconnect()