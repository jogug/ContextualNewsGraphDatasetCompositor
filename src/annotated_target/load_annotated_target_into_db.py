import json
import pandas as pd
from tqdm import tqdm
from src.util.Database import Database
from src.util.Configuration import Configuration


def load_annotated_target_into_db(config: Configuration):
    DATA_ARTICLE_TABLE = config.DATA_ARTICLE_TABLE

    # Try finding associated tweets according to FakeNewsNet
    in_file_paths = [
        config.data_folder_path + config.articles_combined_filename
    ]

    default_insert_values = {
        "id" : 0,
        "tag" : "",
        "source" : "",
        "target" : "",
        "realfake" : "",
        "url" : "",
        "statement" : "",
        "date" : "",
        "author" : "",
        "fact_sources" : ""
    }

    cur_inserts = []
    for in_file_path in in_file_paths:
        in_file_path = in_file_path
        df = pd.read_csv(in_file_path)

        for index, row in df.iterrows():
            # Resolve Real/Fake
            realfake = ""
            if "target" in row:
                target = row["target"]
                if target in ["false", "pants-fire"]:
                    realfake = "fake"
                else:
                    realfake = "real"

            cur_insert = dict(default_insert_values)
            cur_insert["id"] = row["index"]
            cur_insert["tag"] = ""
            cur_insert["source"] = row["source"]
            cur_insert["source_url"] = json.loads(row["fact_sources"])[0]["source_tag"]
            cur_insert["target"] = row["target"]
            cur_insert["realfake"] = realfake
            cur_insert["url"] = row["url"]
            cur_insert["news_url"] = json.loads(row["fact_sources"])[0]["url"]
            cur_insert["statement"] = row["statement"].replace("\\'", "").replace("\'", "").replace("'", "")
            cur_insert["date"] = row["date"]
            cur_insert["published_date"] = json.loads(row["fact_sources"])[0]["visited_date"]
            cur_insert["author"] = row["author"].replace("\\'", "").replace("\'", "").replace("'", "")
            cur_insert["fact_source"] = json.dumps(row["fact_sources"]).replace("\\'", "").replace("\'", "").replace("'", "")
            cur_inserts.append(cur_insert)


    # Store Article in DB
    statement = f"""
    INSERT INTO {DATA_ARTICLE_TABLE} (`id`, `tag`, `source`, `source_url`,`news_url`, `target`, `realfake`, `url`, `statement`, `date`, `published_date`, `author`, `fact_source`) 
    """ + """
    VALUES ({id},'{tag}','{source}','{source_url}','{news_url}','{target}','{realfake}','{url}','{statement}','{date}','{published_date}','{author}','{fact_source}')
    ON DUPLICATE KEY UPDATE tag=VALUE(tag), realfake=VALUE(realfake), source_url=VALUE(source_url), news_url=VALUE(news_url), published_date=VALUE(published_date)"""

    db = config.get_db()
    for cur_insert in tqdm(cur_inserts):
        db.execute(statement=statement.format(**cur_insert))
    db.disconnect()
    