import pandas as pd
from src.util.Configuration import Configuration

def load_media_factuality_into_db(config: Configuration):

    DB_database = config.DB_database
    DATA_MEDIA_TABLE = config.DATA_MEDIA_TABLE

    output = config.data_folder_path + config.PRE_MEDIA + '.csv'

    df = pd.read_csv(output)
    db = config.get_db()

    # Iterate over the rows of the dataframe
    for index, row in df.iterrows():
        # Insert the row into the database
        db.execute(f"""
            INSERT INTO {DB_database}.{DATA_MEDIA_TABLE} (id, name, url, factuality) 
            VALUES ({index}, '{row.iloc[0]}', '{row.iloc[1]}', '{row.iloc[2]}')
            ON DUPLICATE KEY UPDATE name=VALUE(name), url=VALUE(url), factuality=VALUE(factuality)
        """)