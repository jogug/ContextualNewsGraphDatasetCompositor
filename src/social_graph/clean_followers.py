from src.util.Configuration import Configuration

def clean_followers(config: Configuration):
    # Extracts active User Relations from All User Relations
    DATA_USER_RELATIONS = config.DATA_USER_RELATIONS
    DATA_USER_RELATIONS_ACITVE = config.DATA_USER_RELATIONS_ACITVE

    db = config.get_db()
    reset_query = f"""
    DROP TABLE IF EXISTS {DATA_USER_RELATIONS_ACITVE};
    """
    query = f"""
    CREATE TABLE 
        {DATA_USER_RELATIONS_ACITVE} 
    AS SELECT * FROM 
        {DATA_USER_RELATIONS} 
    WHERE 
        followerID IN (SELECT userID FROM {DATA_USER_RELATIONS})
    """
    create_primary_key = f"""
    ALTER TABLE `data_twitter_user_relation_active`
    ADD PRIMARY KEY (`userID`,`followerID`);
    """
    db.execute(reset_query)
    db.execute(query)
    db.execute(create_primary_key)
    db.disconnect()

