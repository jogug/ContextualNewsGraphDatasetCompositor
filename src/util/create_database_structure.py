from src.util.Configuration import Configuration


def create_database_structure(config: Configuration):
    db = config.get_db()
    DB_database = config.DB_database

    drop_database = config.drop_database

    DATA_TWEET_TABLE = config.DATA_TWEET_TABLE
    DATA_ARTICLE_TABLE = config.DATA_ARTICLE_TABLE
    DATA_USER_TABLE = config.DATA_USER_TABLE
    DATA_MEDIA_TABLE = config.DATA_MEDIA_TABLE
    DATA_USER_RELATION_TABLE = config.DATA_USER_RELATION_TABLE
    DATA_SOURCE_TABLE = config.DATA_SOURCE_TABLE

    # Drop Database
    if drop_database:
        statement_db = f"""DROP DATABASE IF EXISTS {DB_database}"""
        db.execute(statement=statement_db)
        
    # Create Database
    statement_db = f"""CREATE DATABASE IF NOT EXISTS {DB_database}"""
    db.execute(statement=statement_db)

    # Create Tables
    statement_create_tweet_table = f"""
    CREATE TABLE IF NOT EXISTS {DB_database}.`{DATA_TWEET_TABLE}` (
        `article_id` int(11) NOT NULL,
        `source_tweet_id` bigint(25) NOT NULL,
        `tweet_id` bigint(25) NOT NULL,
        `author_id` bigint(25) NOT NULL,
        `created_at` varchar(50) DEFAULT NULL,
        `ttt` int(30) DEFAULT NULL,
        `realfake` enum('real','fake') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
        `status` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
        `selected` int(4) NOT NULL DEFAULT 0,
        `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
        `text` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
        `stance` varchar(25) DEFAULT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
    """
    statement_create_tweet_table_key = f"""
    ALTER TABLE {DB_database}.`{DATA_TWEET_TABLE}`
        ADD PRIMARY KEY (`tweet_id`),
        ADD KEY `source tweet id` (`source_tweet_id`),
        ADD KEY `realfake selector` (`source_tweet_id`,`realfake`);
    """
    
    statement_create_article_table = f"""
    CREATE TABLE IF NOT EXISTS {DB_database}.`{DATA_ARTICLE_TABLE}` (
        `id` int(11) NOT NULL,
        `tag` varchar(20) NOT NULL,
        `source` varchar(255) NOT NULL,
        `source_url` text DEFAULT NULL,
        `source_clean` varchar(255) DEFAULT NULL,
        `news_url` text DEFAULT NULL,
        `news_url2` text DEFAULT NULL,
        `news_url3` text DEFAULT NULL,
        `news_url4` text DEFAULT NULL,
        `news_url5` text DEFAULT NULL,
        `target` varchar(20) NOT NULL,
        `realfake` varchar(10) NOT NULL,
        `url` varchar(255) NOT NULL,
        `statement` text NOT NULL,
        `newstitle` text NOT NULL DEFAULT '',
        `content` text NOT NULL DEFAULT '',
        `abstract` text NOT NULL DEFAULT '',
        `date` varchar(255) NOT NULL DEFAULT '',
        `author` varchar(255) NOT NULL DEFAULT '',
        `fact_source` text NOT NULL DEFAULT '',
        `published_date` varchar(255) NOT NULL DEFAULT '',
        `published_date2` varchar(255) NOT NULL DEFAULT '',
        `published_date_cleaned` varchar(255) NOT NULL DEFAULT ''
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
    """
    statement_create_article_table_key = f"""
    ALTER TABLE {DB_database}.`{DATA_ARTICLE_TABLE}`
       ADD PRIMARY KEY (`id`);
    """

    statement_create_user_table = f"""
    CREATE TABLE IF NOT EXISTS {DB_database}.`{DATA_USER_TABLE}` (
        `userID` bigint(20) NOT NULL,
        `status` varchar(10) NOT NULL DEFAULT 'False',
        `content` longtext NOT NULL DEFAULT '',
        `status_followers` int(11) NOT NULL DEFAULT 0,
        `status_timeline` varchar(10) NOT NULL DEFAULT 'Reload',
        `timeline` text DEFAULT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
    """
    statement_create_user_table_key = f"""
    ALTER TABLE {DB_database}.`{DATA_USER_TABLE}`
        ADD PRIMARY KEY (`userID`);
    """

    statement_create_user_relation_table = f"""
    CREATE TABLE IF NOT EXISTS {DB_database}.`{DATA_USER_RELATION_TABLE}` (
        `userID` bigint(25) NOT NULL,
        `followerID` bigint(25) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
    """
    statement_create_user_relation_table_key = f"""
    ALTER TABLE {DB_database}.`{DATA_USER_RELATION_TABLE}`
        ADD PRIMARY KEY (`userID`,`followerID`); 
    """

    statement_create_source_table = f"""
    CREATE TABLE IF NOT EXISTS {DB_database}.`{DATA_SOURCE_TABLE}` (
        `id` int(11) NOT NULL,
        `name` varchar(255) NOT NULL,
        `url` varchar(255) NOT NULL,
        `status_home` varchar(25) NOT NULL DEFAULT 'False',
        `home` text DEFAULT NULL,
        `status_about` varchar(25) NOT NULL DEFAULT 'False',
        `about` text DEFAULT NULL,
        `media_factuality_status` varchar(25) NOT NULL DEFAULT 'False',
        `media_factuality` varchar(50) DEFAULT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    """
    statement_create_source_table_key = f"""
    ALTER TABLE {DB_database}.`{DATA_SOURCE_TABLE}`
        ADD PRIMARY KEY (`id`),
        ADD UNIQUE KEY `name` (`name`);
    """
    statement_create_source_table_auto_increment = f"""
    ALTER TABLE {DB_database}.`{DATA_SOURCE_TABLE}`
        MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
    """

    statement_create_media_table = f"""
    CREATE TABLE IF NOT EXISTS {DB_database}.`{DATA_MEDIA_TABLE}` (
        `id` int(11) NOT NULL DEFAULT 0,
        `name` varchar(63) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
        `url` varchar(95) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
        `factuality` varchar(14) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    """
    statement_create_media_table_key = f"""
    ALTER TABLE {DB_database}.`{DATA_MEDIA_TABLE}`
        ADD PRIMARY KEY (`id`),
        ADD UNIQUE KEY `name` (`name`);
    """

    queries = [
        statement_create_tweet_table, statement_create_tweet_table_key,
        statement_create_article_table, statement_create_article_table_key,
        statement_create_user_table, statement_create_user_table_key,
        statement_create_user_relation_table, statement_create_user_relation_table_key,
        statement_create_source_table, statement_create_source_table_key, statement_create_source_table_auto_increment,
        statement_create_media_table, statement_create_media_table_key
    ]
    for query in queries:
        db.execute(query)