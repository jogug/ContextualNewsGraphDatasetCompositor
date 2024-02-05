from src.util.Configuration import Configuration
from src.util.SourceMapperHelper import DEFAULT_SOURCE_MAPPINGS
from url_parser import get_url

def get_source_names(row):
    sources = []
    if "source_url" in row:
        sources.append(row["source_url"].strip().split(" ")[0].lower())
    if "source" in row:
        sources.append(row["source"].strip().split(" ")[0].lower())
    if "source_url" in row:
        sources.append(row["source_url"].strip().lower())
    if "news_url" in row:
        source = row["news_url"].strip().lower()
        try:
            # Check if there is no news url
            if row["news_url"] == "" and row["news_url2"] == "" and row["news_url3"] == "" and row["news_url4"] == "" and row["news_url5"] == "":
                source = "unknown"
            else:
                url = get_url(source)
                source = url.domain + "." + url.top_domain
            sources.append(source)
        except Exception as e:
            try:
                source = source.split(".com")[0].replace("https://", "").replace("http://", "").replace("www.", "") + ".com"
                sources.append(source)
            except Exception as e:
                print("ERROR", e)
    return sources

def try_get_source(sources, source_mapping):
    notFoundSource = True
    insert_source = "unknown"
    insert_source_name = "unknown"
    for cur_source in sources:
        cur_source = cur_source.strip().lower()
        if notFoundSource:
            if cur_source in source_mapping:
                insert_source = source_mapping[cur_source]
                notFoundSource = False
            else:
                insert_source = cur_source
            insert_source_name = insert_source.split(".")[0]
    return notFoundSource, insert_source, insert_source_name

def try_get_factuality(sources, source_mapping, media_facuality_map):
    notFoundFactuality = True
    insert_factuality = "unknown"
    for cur_source in sources:
        if cur_source in source_mapping:
            cur_source = source_mapping[cur_source]
        source_name = cur_source.split(".")[0]
        if notFoundFactuality and source_name in media_facuality_map:
            insert_factuality = media_facuality_map[source_name]
            notFoundFactuality = False
    return notFoundFactuality, insert_factuality

def clean_source(config: Configuration):
    DB_database = config.DB_database
    DATA_ARTICLE_TABLE = config.DATA_ARTICLE_TABLE
    DATA_SOURCE_TABLE = config.DATA_SOURCE_TABLE
    source_mapping = config.source_mapping
    source_mapping = {**DEFAULT_SOURCE_MAPPINGS, **source_mapping}

    Db_database = config.DB_database
    DATA_MEDIA_TABLE = config.DATA_MEDIA_TABLE
    factuality_column = config.factuality_column
    db = config.get_db()
    media_data = db.fetchall(f"SELECT * FROM {Db_database}.{DATA_MEDIA_TABLE}", dictionary=True)
    media_facuality_map = {}
    for row in media_data:
        media_facuality_map[row["name"].lower().strip()] = row[factuality_column]
    db.disconnect()

    statement_update_factuality = "UPDATE {DB_database}.{DATA_SOURCE_TABLE} SET media_factuality='{factuality}' WHERE name='{source_name}'"
    statement_update_source = "UPDATE {DB_database}.{DATA_ARTICLE_TABLE} SET source_clean='{source}' WHERE id={id}"
    db = config.get_db()
    rows = db.fetchall(f"SELECT * FROM {DB_database}.{DATA_ARTICLE_TABLE}", dictionary=True)

    statement_insert_source = "INSERT IGNORE INTO {DB_database}.{DATA_SOURCE_TABLE} (`id`, `name`, `url`, `status_home`, `home`, `status_about`, `about`) VALUES ({id}, '{source_name}', '{source}', 'False', NULL, 'False', NULL)"
    for row in rows:
        sources = get_source_names(row)

        notFoundSource, insert_source, insert_source_name = try_get_source(sources, source_mapping)
        notFoundFactuality, insert_factuality = try_get_factuality(sources, source_mapping, media_facuality_map)

        if notFoundSource is False:
            db.execute(statement_insert_source.format(DB_database=DB_database,DATA_SOURCE_TABLE=DATA_SOURCE_TABLE,source_name=insert_source_name, source=insert_source, id="NULL"))
            db.execute(statement_update_source.format(DB_database=DB_database,DATA_ARTICLE_TABLE=DATA_ARTICLE_TABLE,source=insert_source, id=row["id"]))
        else:
            # print("Please Map the following source in the config file:")
            # print("RAW TAGS", row)            
            pass

        if notFoundFactuality is False:
            db.execute(statement_update_factuality.format(DB_database=DB_database,DATA_SOURCE_TABLE=DATA_SOURCE_TABLE,factuality=insert_factuality, source_name=insert_source_name))
        else:
            # print("Please Map the following source in the config file:", sources)
            # print("RAW TAGS", row)   
            pass

    factuality_mapping = config.factuality_mapping

    # Insert Tweet Article Sources 
    if config.HAS_TWEET_ARTICLES:
        for i in range(len(config.respected_sources)):
            #config.respected_sources
            twitter_id = config.respected_sources_twitter_ids[i]
            website = config.respected_sources_websites[i]
            
            url = get_url(website)
            sources = [url.domain + "." + url.top_domain, url.domain]

            notFoundSource, insert_source, insert_source_name = try_get_source(sources, source_mapping)

            # Add Faculty Mapping
            temp_sources = []
            for source in sources:
                temp_sources.append(source)
                if source in factuality_mapping:
                    temp_sources.append(factuality_mapping[source])
            sources = temp_sources

            notFoundFactuality, insert_factuality = try_get_factuality(sources, source_mapping, media_facuality_map)
            print(notFoundFactuality, sources, insert_factuality)

            if notFoundSource is False:
                db.execute(statement_insert_source.format(DB_database=DB_database,DATA_SOURCE_TABLE=DATA_SOURCE_TABLE,source_name=insert_source_name, source=insert_source, id=twitter_id))
      
            if notFoundFactuality is False:
                db.execute(statement_update_factuality.format(DB_database=DB_database,DATA_SOURCE_TABLE=DATA_SOURCE_TABLE,factuality=insert_factuality, source_name=insert_source_name))
    db.disconnect()