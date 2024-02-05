from src.util.Configuration import Configuration

def clean_stance(config: Configuration):
    DB_database = config.DB_database
    DATA_TWEET_TABLE = config.DATA_TWEET_TABLE

    nrs = [1,2]
    ending_predict = ".tsv"
    ending_predict_result = ".txt"
    name_predict = "predict_"
    # 0 support
    # 1 deny
    name_predict_result = "predict_results_{nr}"
    # 1 support negative
    # 0 support positive
    name_predict_result_yelp = "predict_results_yelp_{nr}_classification"

    statement_update_stance = "UPDATE {DB_database}.{DATA_TWEET_TABLE} SET stance='{stance}' WHERE tweet_id={tweet_id}"
    for nr in nrs:
        try:
            db = config.get_db()
            predict_file_path = config.data_folder_path + name_predict + str(nr) + ending_predict
            predict_result_file_path = config.data_folder_path + name_predict_result.format(nr=nr) + ending_predict_result
            predict_result_yelp_file_path = config.data_folder_path + name_predict_result_yelp.format(nr=nr) + ending_predict_result
            
            predict_file = open(predict_file_path, "r")
            predict_result_file = open(predict_result_file_path, "r")
            predict_result_yelp_file = open(predict_result_yelp_file_path, "r")
            
            for line in predict_file.readlines():
                result = predict_result_file.readline()
                result = int(result.replace("\n", ""))
                result_yelp = predict_result_yelp_file.readline()
                result_yelp = int(result_yelp.replace("\n", ""))
                header, title, tweet_text = line.split("\t")
                _, tweet_id = header.split("_")

                stance = "na"
                if title in tweet_text:
                    stance = "report"
                else:
                    # Classify as deny or support
                    if result == 0:
                        stance = "support"
                        if result_yelp == 1:
                            stance = "support_negative"
                        else:
                            stance = "support_neutral"
                    else:
                        stance = "deny"
                db.execute(statement_update_stance.format(DB_database=DB_database,DATA_TWEET_TABLE=DATA_TWEET_TABLE,stance=stance, tweet_id=tweet_id))

        except Exception as e:
            e.with_traceback()
        finally:
            if predict_file is not None: predict_file.close()
            if predict_result_yelp_file is not None: predict_file.close()
            if predict_result_file is not None: predict_result_file.close()
            if db is not None: db.disconnect()
