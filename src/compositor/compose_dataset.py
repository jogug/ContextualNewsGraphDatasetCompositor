import json, random, shutil
from src.util.Database import Database
from src.util.Configuration import Configuration
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import traceback
import numpy as np
import nltk
nltk.download('punkt')

def get_source_tag(source_clean):
    return source_clean.strip().split(".")[0] 

def generate_tfidf(expected_features, entity, data):
    if len(entity) != len(data):
        print("entity and data length mismatch", len(entity), len(data))

    # the smaller a word tfidf the less it identifies a document
    # the larger a word tfidf the more unique and thus the more it identifies the document
    # multiple uiniqe words in the same document lower the score 
    vectorizer = TfidfVectorizer(min_df=3,max_df=.90,strip_accents="unicode", stop_words="english", tokenizer=nltk.word_tokenize)
    X = vectorizer.fit_transform(data)
    # To print feature_names = vectorizer.get_feature_names_out()
    X_Array = X.toarray()


    # Condensing: https://stackoverflow.com/questions/34725726/is-it-possible-apply-pca-on-any-text-classification
    svd = TruncatedSVD(n_components=expected_features, random_state=42)
    data = svd.fit_transform(X_Array)

    representations = {}
    for index, entity in enumerate(entity):
        # Why dimensionality lower: https://stackoverflow.com/questions/42558153/truncatedsvd-returning-incorrect-dimensions
        empty = np.zeros((1, expected_features))
        empty[:len(data), :len(data[index])] = data[index]
        representations[entity] = entity +"\t" + "\t".join([str(x) for x in empty[0]])
    return representations

def generate_news_info (config: Configuration, active_entities, article_map, source_map):
    '''
    Generates 
        news_info.tsv
        source_publication.tsv 
        tfidf representations of articles
    '''
    source_name_map = {}
    for source_id, source in source_map.items():
        source_name_map[source["name"]] = source_id
    PRE_ARTICLE = config.PRE_ARTICLE
    PRE_SOURCE = config.PRE_SOURCE
    TFIDF_EXPECTED_FEATURES = config.TFIDF_EXPECTED_FEATURES
    data_dataset_folder_path = config.data_dataset_folder_path
    NEWS_TITLE_COLUMN = config.NEWS_TITLE_COLUMN
    file_path_news_info = data_dataset_folder_path + "news_info.tsv"
    file_path_publication = data_dataset_folder_path +  "source_publication.tsv"
    entity_map = {}
    article_tfidf_entity = []
    article_tfidf_data = []
    try:
        file_publication = open(file_path_publication,"w", encoding="utf-8")
        file_news_info = open(file_path_news_info,"w", encoding="utf-8")
        for article_id, article in article_map.items():
            article_title = article[NEWS_TITLE_COLUMN]
            entity = PRE_ARTICLE+ str(article_id)

            if entity in entity_map:
                continue
            entity_map[entity] = True
            realfake = article["realfake"]
            active_entities["all"].append(entity)
            source_entity = PRE_SOURCE + str(source_name_map[get_source_tag(article["source_clean"])])
            active_entities['article_meta'][entity] = [entity, "news", PRE_ARTICLE + realfake]
            file_news_info.write("\t".join([
                entity,
                realfake,
                article_title
                ])+"\n")
            file_publication.write("\t".join([
                source_entity,
                entity
                ])+"\n")
            article_tfidf_entity.append(entity)
            # content or abstract
            article_tfidf_data.append(article["content"])

        # If we include posts as sources select a predefined amount
        # "SELECT * FROM `tweet` WHERE realfake LIKE 'real' AND source_tweet_id = 0 "
    except:
        traceback.print_exc()
    finally:
        if file_news_info is not None: file_news_info.close()
        if file_publication is not None: file_publication.close()

    active_entities['article_representations'] = generate_tfidf(TFIDF_EXPECTED_FEATURES, article_tfidf_entity, article_tfidf_data)

def generate_source_tfidf(config: Configuration, active_entities, source_map):
    TFIDF_EXPECTED_FEATURES = config.TFIDF_EXPECTED_FEATURES
    entity_map = {}
    source_tfidf_entity_cache = {}
    source_tfidf_data_cache = {}

    for source_id, source in source_map.items():
        entity = config.PRE_SOURCE + str(source_id)
        if entity in entity_map:
            continue
        entity_map[entity] = True
        source_tfidf_entity_cache[source["name"]] = entity
        home = source["home"] if source["home"] is not None else ""
        about = source["about"] if source["about"] is not None else ""
        source_tfidf_data_cache[source["name"]] = home + " " + about

    source_tfidf_entity = []
    source_tfidf_data = []
    for key, item in source_tfidf_entity_cache.items():
        source_tfidf_entity.append(item)
        source_tfidf_data.append(source_tfidf_data_cache[key])
    
    active_entities['source_representations'] = generate_tfidf(TFIDF_EXPECTED_FEATURES, source_tfidf_entity, source_tfidf_data)


def generate_media_factuality (config:Configuration, active_entities, source_map):
    PRE_SOURCE = config.PRE_SOURCE  
    data_dataset_folder_path = config.data_dataset_folder_path
    file_path_media_factuality = data_dataset_folder_path + "media_factuality.txt"
    try:
        media_factuality_file = open(file_path_media_factuality,"w", encoding="utf-8")
        for source_id, source in source_map.items():
            entity = PRE_SOURCE + str(source_id)
            bias = source["media_factuality"]
            if bias is None or bias == "":
                print("no bias info: " + entity)
                bias = "n"
            active_entities["all"].append(entity)
            active_entities['source_meta'][entity] = [entity, "source", "source_real"]
            media_factuality_file.write("\t".join([
                entity,
                bias
                ])+"\n")
    except:
         traceback.print_exc()
    finally:
        if media_factuality_file is not None: media_factuality_file.close()


def generate_user_tfidf (config: Configuration, active_entities, user_map):
    PRE_USER = config.PRE_USER
    user_tfidf_entity = []
    user_tfidf_data = []
    userID_Failed = []
    entity_map = {}
    for user_id, user in user_map.items():
        entity = PRE_USER + str(user_id)
        if entity in entity_map:
            continue
        entity_map[entity] = True
        active_entities["all"].append(entity)
        active_entities['user_meta'][entity] = [entity, "user", "cluster_na"]
        try:
            user_obj = json.loads(user["content"])
            # User Attributes
            name = user_obj["name"] if "name" in user_obj else user_obj["username"]
            # verified = user_obj["verified"]
            # public_metrics = user_obj["public_metrics"]
            description = user_obj["description"]
            # protected = user_obj["protected"]
            # created_at = user_obj["created_at"]
            user_tfidf_data.append(description)
            user_tfidf_entity.append(entity)
        except Exception as e:
            # Track users with unparsable description
            user_tfidf_data.append("")
            user_tfidf_entity.append(entity)
            userID_Failed.append(user["userID"])

    active_entities['user_representations'] = generate_tfidf(config.TFIDF_EXPECTED_FEATURES, user_tfidf_entity, user_tfidf_data)

def generate_meta_data (config: Configuration, active_entities):
    entities_meta_articles = list(active_entities['article_meta'].values())
    entities_meta_source = list(active_entities['source_meta'].values())
    entities_meta_user = list(active_entities['user_meta'].values())

    data_dataset_folder_path = config.data_dataset_folder_path
    file_path = data_dataset_folder_path + "meta_data.tsv"
    with open(file_path,"w", encoding="utf-8") as file:
        file.write("node_id	node_name	node_type	node_community\n")
        meta_entities = [[str(index)] + meta_entity for index, meta_entity in enumerate(entities_meta_articles + entities_meta_source + entities_meta_user)]
        for entities_meta in meta_entities:
            file.write("\t".join(entities_meta)+"\n")


def generate_entities (config: Configuration, entities):
    data_dataset_folder_path = config.data_dataset_folder_path
    file_path = data_dataset_folder_path + "entities.txt"
    with open(file_path,"w", encoding="utf-8") as file:
        for entity in entities:
            file.write(str(entity)+"\n")


def generate_source_citation (config: Configuration):
    data_dataset_folder_path = config.data_dataset_folder_path
    file_path = data_dataset_folder_path + "source_citation.tsv"
    with open(file_path,"w", encoding="utf-8") as file:
        # No citations
        pass

def generate_stance_files(config: Configuration, article_tweet_map):
    data_dataset_folder_path = config.data_dataset_folder_path
    file_path_support_neutral = data_dataset_folder_path + "support_neutral.tsv"
    file_path_support_negative = data_dataset_folder_path + "support_negative.tsv"
    file_path_report = data_dataset_folder_path + "report.tsv"
    file_path_deny = data_dataset_folder_path + "deny.tsv"

    try:
        file_support_neutral = open(file_path_support_neutral,"w", encoding="utf-8")
        file_support_negative = open(file_path_support_negative,"w", encoding="utf-8")
        file_report = open(file_path_report,"w", encoding="utf-8")
        file_deny = open(file_path_deny,"w", encoding="utf-8")

        for article_tweets in article_tweet_map.values():
            for row in article_tweets:
                author_id = row["author_id"]
                ttt = abs(row["ttt"])
                article_id = row["article_id"]
                if article_id == 0:
                    article_id = row["source_tweet_id"]
                stance = row["stance"]
                if stance == "support_neutral":
                    file_support_neutral.write("\t".join([
                        "user_" + str(author_id),
                        "news_" + str(article_id),
                        str(ttt)
                        ])+"\n")
                elif stance == "support_negative":
                    file_support_negative.write("\t".join([
                        "user_" + str(author_id),
                        "news_" + str(article_id),
                        str(ttt)
                        ])+"\n")
                elif stance == "deny":
                    file_deny.write("\t".join([
                        "user_" + str(author_id),
                        "news_" + str(article_id),
                        str(ttt)
                        ])+"\n")
                elif stance == "report":
                    file_report.write("\t".join([
                        "user_" + str(author_id),
                        "news_" + str(article_id),
                        str(ttt)
                        ])+"\n")
    except:
        traceback.print_exc()
    finally:
        if file_support_neutral is not None: file_support_neutral.close()
        if file_support_negative is not None: file_support_negative.close()
        if file_report is not None: file_report.close()
        if file_deny is not None: file_deny.close()
  
def generate_user_relationships (config: Configuration, user_map):
    data_dataset_folder_path = config.data_dataset_folder_path
    file_path = data_dataset_folder_path + "user_relationships.tsv"
    DB_database = config.DB_database
    DATA_USER_RELATIONS = config.DATA_USER_RELATIONS
    DATA_TWEET_TABLE = config.DATA_TWEET_TABLE
    db = config.get_db()
    user_user_data = db.fetchall(f"""
    SELECT * FROM 
        {DB_database}.{DATA_USER_RELATIONS} 
    WHERE 
        followerID IN (SELECT author_id FROM {DB_database}.{DATA_TWEET_TABLE})
    """)
    db.disconnect()
    
    with open(file_path,"w", encoding="utf-8") as file:
        for userID, followerID in user_user_data:
            if userID not in user_map or followerID not in user_map: continue
            file.write("user_" + str(userID) + "\t" + "user_" + str(followerID) +"\n")

def generate_entity_features (config: Configuration, active_entities):
    data_dataset_folder_path = config.data_dataset_folder_path
    file_path = data_dataset_folder_path + "entity_features.tsv"
    entity_features = \
        list(active_entities["user_representations"].values()) + \
        list(active_entities["source_representations"].values()) + \
        list(active_entities["article_representations"].values()) 

    # print(len(entity_features))
    with open(file_path,"w", encoding="utf-8") as file:
        for entity_feature in entity_features:
            file.write(entity_feature+"\n")

def generate_test_train_split(config: Configuration, splits, active_entities, version="v1"):
    '''
    Generates 
        train_test_{split}.json
    by randomly selecting articles for train, test and val with a ratio of fake to real.
    '''

    data_dataset_folder_path = config.data_dataset_folder_path
    article_count = len(list(active_entities["article_meta"].keys()))
    # count  fake and real
    fake_count = 0
    real_count = 0
    fake_articles_base = []
    real_articles_base = []
    for article_id, article in active_entities["article_meta"].items():
        if article[2] == "news_fake":
            fake_count += 1
            fake_articles_base.append(article_id)
        else:
            real_count += 1
            real_articles_base.append(article_id)

    ratio = fake_count/article_count

    for split in splits:
        fake_articles = fake_articles_base.copy()
        real_articles = real_articles_base.copy()

        file_path = data_dataset_folder_path + "train_test_{split}.json.{version}"
        nr_articles = int(article_count * split/100)
        nr_in_train = int(nr_articles * 0.6)
        nr_in_train_fake = int(nr_in_train * ratio)
        nr_in_train_real = nr_in_train - nr_in_train_fake

        nr_in_test = int(nr_articles * 0.2)
        nr_in_val = nr_articles - nr_in_test - nr_in_train
        nr_in_val_fake = int(nr_in_val * ratio)
        nr_in_val_real = nr_in_val - nr_in_val_fake

        train_subset_fake = random.sample(fake_articles, nr_in_train_fake)
        fake_articles = [x for x in fake_articles if x not in train_subset_fake]
        train_subset_real = random.sample(real_articles, nr_in_train_real)
        real_articles = [x for x in real_articles if x not in train_subset_real]
        train_subset = train_subset_fake + train_subset_real

        val_subset_fake = random.sample(fake_articles, nr_in_val_fake)
        fake_articles = [x for x in fake_articles if x not in val_subset_fake]
        val_subset_real = random.sample(real_articles, nr_in_val_real)
        real_articles = [x for x in real_articles if x not in val_subset_real]
        val_subset = val_subset_fake + val_subset_real

        test_subset = fake_articles + real_articles

        out = {
            "train": ",".join(train_subset),
            "val": ",".join(val_subset),
            "test": ",".join(test_subset)
        }

        with open(file_path.format(split=split, version=version),"w", encoding="utf-8") as file:
            file.write(json.dumps(out))

def print_stats(article_map):
    print("Articles", len(article_map))
    realfake = {
        "real": 0,
        "fake": 0
    }
    for article_id, article in article_map.items(): 
        print(article_id, article["tweet_count"], article["tweet_count_with_user"])
        if article["realfake"] == 'fake':
            print(article_id, article["tweet_count"], article["tweet_count_with_user"])
            pass
        realfake[article["realfake"]] += 1
    print("realfake", realfake)


def save_failed_ids (id_list, file_path):
    with open(file_path, "w") as f:
        for id in id_list:
            f.write(f"{id}\n")

def compose(config: Configuration, db: Database, printStats = False):
    mode = 1
    DB_database = config.DB_database
    DATA_TWEET_TABLE = config.DATA_TWEET_TABLE
    DATA_ARTICLE_TABLE = config.DATA_ARTICLE_TABLE
    DATA_USER_TABLE = config.DATA_USER_TABLE
    DATA_SOURCE_TABLE = config.DATA_SOURCE_TABLE

    subsets = config.subsets

    # Cache
    # Base Entity
    # Meta
    # Representation
    active_entities = {
        'all': [],
        'user': {},
        'source': {},
        'article': {},
        'user_representations': {},
        'source_representations': {},
        'article_representations': {},
        'user_meta': {},
        'source_meta': {},
        'article_meta': {},
    }

    not_in_user_map = {}
    not_in_article_tweet_map = {}

    # Load Users
    user_data = db.fetchall(f"SELECT * FROM {DB_database}.{DATA_USER_TABLE}", dictionary=True)
    user_map = {}
    user_tweet_count = {}
    for user in user_data:
        user_map[user["userID"]] = user
        user_tweet_count[user["userID"]] = 0

    # Load Tweets
    tweet_data = db.fetchall(f"SELECT * FROM {DB_database}.{DATA_TWEET_TABLE} WHERE text NOT LIKE '' AND author_id != 0 AND stance IS NOT NULL AND article_id != 0", dictionary=True)
    article_tweet_map = {}
    for tweet in tweet_data:
        article_id = tweet["article_id"]

        if article_id not in article_tweet_map:
            article_tweet_map[article_id] = []
        article_tweet_map[article_id].append(tweet)

        # Load Tweet Users
        author_id = tweet["author_id"]
        active_entities["user"][author_id] = None
        if author_id not in user_map:
            not_in_user_map[author_id] = True
            continue

        user_tweet_count[author_id] += 1
        active_entities["user"][author_id] = user_map[author_id]


    # Load Sources
    source_data = db.fetchall(f"SELECT * FROM {DB_database}.{DATA_SOURCE_TABLE}", dictionary=True)
    source_map = {}
    source_article_count = {}
    for source in source_data:
        source_map[source["id"]] = source
        source_article_count[source["url"]] = 0

    # Use User Posts as Articles > Load Tweet Articles Sources
    article_map = {}
    if config.HAS_TWEET_ARTICLES:
        NEWS_TITLE_COLUMN = config.NEWS_TITLE_COLUMN
        
        # Load Tweet Article Sources to ameliorate tweet articles
        tweet_article_source_map = {}
        respected_sources = config.respected_sources
        respected_sources_twitter_ids = config.respected_sources_twitter_ids
        respected_sources_websites = config.respected_sources_websites
        for i in range(len(respected_sources)):
            tweet_article_source_map[respected_sources_twitter_ids[i]] = {
                "article_id": respected_sources[i],
                "source_id": respected_sources[i],
                "source_clean": respected_sources_websites[i],
                "url": respected_sources_websites[i],
                "name": respected_sources[i],
                "realfake": "real"
            }

        # Load Tweet Articles Tweets
        tweet_article_tweet_data = db.fetchall(f"""
            SELECT * FROM {DB_database}.{DATA_TWEET_TABLE} WHERE source_tweet_id IN (
            SELECT tweet_id FROM {DB_database}.{DATA_TWEET_TABLE} WHERE article_id=0 AND source_tweet_id=0
            )""", dictionary=True)
        for tweet in tweet_article_tweet_data:
            if tweet["source_tweet_id"] not in article_tweet_map:
                article_tweet_map[tweet["source_tweet_id"]] = []
            article_tweet_map[tweet["source_tweet_id"]].append(tweet)

            # Load Tweet Users
            author_id = tweet["author_id"]
            active_entities["user"][author_id] = None
            if author_id not in user_map:
                not_in_user_map[author_id] = True
                continue
            
            user_tweet_count[author_id] += 1
            active_entities["user"][author_id] = user_map[author_id]

        # Load Tweet Articles
        # respected_sources_twitter_ids
        # SELECT author_id, count(*) FROM `tweet` WHERE article_id=0 AND source_tweet_id=0 GROUP BY author_id
        tweet_article_data = db.fetchall(f"SELECT * FROM {DB_database}.{DATA_TWEET_TABLE} WHERE article_id=0 AND source_tweet_id=0", dictionary=True)
        for article in tweet_article_data:
            article_id = article["tweet_id"]
            # Set Tweets
            if article_id not in article_tweet_map:
                not_in_article_tweet_map[article_id] = True
                continue

            # Map author back to source
            author_id = str(article["author_id"])
            if author_id in tweet_article_source_map:
                article = {**article, **tweet_article_source_map[author_id]}
            else:
                print("Tweet Article Source not found >" ,author_id)
                continue

            article["tweet"] = article_tweet_map[article_id]
            article["tweet_count"] = len(article["tweet"])
            article["tweet_count_with_user"] = 0
            
            # Check Users
            for tweet in article["tweet"]:
                tweet_author_id = tweet["author_id"]
                if mode == 0:
                    if tweet_author_id in user_map: 
                        article["tweet_count_with_user"] += 1
                else:
                    if tweet_author_id not in user_map: 
                        user = {
                            "content": json.dumps({
                            "name" : tweet["author_id"],
                            "description" : "",
                            })
                        }
                    article["tweet_count_with_user"] += 1

            # check if article has tweets with users
            if article["tweet_count_with_user"] == 0:
                continue
            
            # Set Title as article
            article[NEWS_TITLE_COLUMN] = article["text"]
            source_article_count[article["source_clean"]] += 1
            article_map[article_id] = article

    # Loald Articles
    article_data = db.fetchall(f"SELECT * FROM {DB_database}.{DATA_ARTICLE_TABLE}", dictionary=True)
    no_tweets = 0
    for article in article_data:
        article_id = article["id"]

        # Set Tweets
        if article_id not in article_tweet_map:
            not_in_article_tweet_map[article_id] = True
            # print("Article Tweets not found >" ,article_id)
            no_tweets += 1
            continue

        article["tweet"] = article_tweet_map[article_id]
        article["tweet_count"] = len(article["tweet"])
        article["tweet_count_with_user"] = 0

        # Check Users
        for tweet in article["tweet"]:
            tweet_author_id = tweet["author_id"]
            if mode == 0:
                if tweet_author_id in user_map: 
                    article["tweet_count_with_user"] += 1
            else:
                if tweet_author_id not in user_map: 
                    user = {
                        "content": json.dumps({
                        "name" : tweet["author_id"],
                        "description" : "",
                        })
                    }
                    user_map[tweet_author_id] = user
                article["tweet_count_with_user"] += 1

        # check if article has tweets with users
        if article["tweet_count_with_user"] == 0:
            # print("Article Tweets with users not found >" ,article_id)
            continue

        source_article_count[article["source_clean"]] += 1
        article_map[article_id] = article

    # Delete Sources with no articles
    clean_source_map = {}
    for source_id, source in source_map.items():
        if source["url"] not in source_article_count or source_article_count[source["url"]] == 0: continue
        clean_source_map[source_id] = source
    source_map = clean_source_map

    # Delete Users with no tweets
    clean_user_map = {}
    for user_id, user in user_map.items():
        if user_tweet_count[user_id] == 0: continue
        clean_user_map[user_id] = user
    user_map = clean_user_map

    # Save Failed Stats
    save_failed_ids (list(not_in_user_map.keys()), config.data_folder_path + "compose_user_id_failed.csv")
    save_failed_ids(list(not_in_article_tweet_map.keys()),config.data_folder_path + "compose_article_id_failed.csv")

    # Generate Dataset
    generate_news_info(config, active_entities, article_map, source_map)
    generate_source_tfidf(config, active_entities, source_map)
    generate_media_factuality(config, active_entities, source_map)
    generate_user_tfidf(config, active_entities, user_map)

    generate_meta_data(config, active_entities)
    generate_entities(config, active_entities["all"])
    generate_source_citation(config)
    generate_stance_files(config, article_tweet_map)

    generate_user_relationships (config, user_map)
    generate_entity_features (config, active_entities)

    # generate random train test split
    for version in range(10):
        generate_test_train_split(config, subsets, active_entities, version="v"+str(version))

    # Package Dataset
    folder_to_zip = config.data_dataset_folder_path
    output_file_name = config.data_folder_path + config.zip_file_name
    shutil.make_archive(output_file_name, 'zip', folder_to_zip)
    if printStats: print_stats(article_map)


def compose_dataset(config: Configuration):
    try:
        db = config.get_db()
        compose(config, db, printStats=True)
    except:
        traceback.print_exc()
    finally:
        if db is not None: db.disconnect()
