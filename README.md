# Repository of Master Thesis Contextual News Graph Compositor

This tool aids in the collection and preprocessing of contextual news graph datasets as used in the [FANG](https://github.com/nguyenvanhoang7398/FANG) model.
[FANG](https://github.com/nguyenvanhoang7398/FANG) has shown that it is possible build highly representative embeddings from these contextual news graph datasets.
We found that to further study, extend and apply these models additional datasets are necessary of similar contextual depth.


## Preparing the environment

* Install MariaDB Server and PhpMyAdmin or preferred database inspection Tool. 
> Our Reasoning: We found that it is invaluable to be able to easily look and query the already collected data. This is why after temporarily storing the data in text files we insert it into a mysql database. 

* Install python 3.11.5

* Install dependencies

* Setup a config file with your database credentials

* Create a Twitter account and fill in twitter_v1_credentials.txt and twitter_v2_credentials.yaml


## Running

* Run by executing main.py

* Running can be limited to specific subtask by specifying the execution target in the main.py file. 

| Task ID | Task Name                                       | Task Description                                                                                        | Function Name                                    |
|---------|-------------------------------------------------|---------------------------------------------------------------------------------------------------------|--------------------------------------------------|
| 1       | Create DB structure                             | Create the structure for the database                                                                   | `create_database_structure`                      |
| 2       | Collect articles                                | Collect Politifact annotated target by topics                                                           | `collect_politifact_annotated_target_by_topics`  |
| 3       | Combine articles and index                      | Combine annotated targets                                                                               | `combine_annotated_targets`                      |
| 4       | Load articles into DB                           | Load annotated targets into the database                                                                | `load_annotated_target_into_db`                  |
| 5       | Try extracting dates from articles              | Clean annotated target date to extract dates from articles                                              | `clean_annotated_target_date`                    |
| 6       | Try extracting dates from wayback machine       | Collect article dates from Wayback Machine                                                              | `collect_article_date_from_wayback`              |
| 7       | Collect media factuality                        | Collect media factuality information                                                                    | `collect_media_factuality`                       |
| 8       | Load media factuality into DB                   | Load media factuality information into the database                                                     | `load_media_factuality_into_db`                  |
| 9       | Clean sources                                   | Clean sources of data                                                                                   | `clean_source`                                   |
| 10      | Collect source                                  | Collect source information                                                                              | `collect_source`                                 |
| 11      | Collect main tweet IDs                          | Collect main tweet IDs and find associated tweets as FakeNewsNet did                                    | `collect_main_tweet_id`                          |
| 12      | Collect user tweets by Topic                    | Collect user tweets by specific topics                                                                  | `collect_user_tweets_topic`                      |
| 13      | Clean fake main Tweet IDs                       | Clean IDs of main tweets marked as fake                                                                 | `clean_fake_main_tweet_id`                       |
| 14      | Clean real main Tweet IDs                       | Clean IDs of main tweets marked as real                                                                 | `clean_real_main_tweet_id`                       |
| 15      | Load replies to these tweets                    | Collect reply tweet IDs                                                                                 | `collect_reply_tweet_id`                         |
| 16      | Clean replies to these fake tweets              | Clean IDs of replies to fake tweets                                                                     | `clean_reply_tweet_fake_id`                      |
| 17      | Clean replies to these real tweets              | Clean IDs of replies to real tweets                                                                     | `clean_reply_tweet_real_id`                      |
| 18      | Load tweets into DB                             | Load tweets into the database                                                                           | `load_tweets_into_db`                            |
| 19      | Clean user IDs                                  | Clean user IDs                                                                                          | `clean_user_id`                                  |
| 20      | Collect users                                   | Collect user information                                                                                | `collect_users`                                  |
| 21      | Collect followers                               | Collect follower information                                                                            | `collect_followers`                              |
| 22      | Clean followers                                 | Clean follower information                                                                              | `clean_followers`                                |
| 23      | Collect tweet context                           | Collect tweet context information                                                                       | `collect_tweet_context`                          |
| 24      | Prepare stance for Politifact article           | Prepare stance detection target from DB for Politifact                                                  | `prepare_stance_prediction_from_db_politifact`   |
| 25      | Manual Execution of stance detection            | Execute stance detection manually                                                                       | `press_enter_to_continue`                        |
| 26      | Prepare Stance Detection Target Post            | Prepare stance detection target from DB for real Twitter posts                                          | `prepare_stance_prediction_from_db_real_twitter` |
| 27      | Manual Execution of stance detection            | Execute stance detection manually                                                                       | `press_enter_to_continue`                        |
| 28      | Clean Stance                                    | Clean stance data                                                                                       | `clean_stance`                                   |
| 29      | Extract Temporal Aspect                         | Load temporal tweet data                                                                                | `load_ttt_tweet`                                 |
| 30      | Compose news_graph                              | Compose the dataset for news graph                                                                      | `compose_dataset`                                |
| 31      | Generate Train Test split                       | Generate train and test variations for the dataset                                                      | `fang_data_generate_train_test_variations`       |
| 32      | build news_graph statistics                     | Build statistics for the news graph                                                                     | `build_stats`                                    |
| 33      | build news_graph statistics tex table           | Build TeX table of dataset statistics from the final news graph                                         | `build_dataset_statsistics_tex_table_from_final` |



# Running Stance Detection and Sentiment Classification from FANG

* Please refer to [FANG-helper](https://github.com/nguyenvanhoang7398/FANG-helper)


## For Fang Statistic and Train Test Split Variations

Please load the [FANG news_graph folder](https://github.com/nguyenvanhoang7398/FANG/tree/master/data/news_graph) into /outputs/data_fang.
This allows to run the utility scripts 'fang_data_generate_train_test_variations.py' and 


## Code Credits and Reference, usage also mentioned directly in the code

* [FANG](https://github.com/nguyenvanhoang7398/FANG) 
* [CoAID](https://github.com/TIMAN-group/covid19_misinformation/tree/master) partially used in various rehydriation steps of the social graph
* [FNN](https://github.com/KaiDMML/FakeNewsNet) idea on how to lookup topics on twitter
* Politifact Scraping: The code is given by [Scrape A Political Website To Build A Fake & Real News Data Set Using Python](https://randerson112358.medium.com/scrape-a-political-website-for-fake-real-news-using-python-b4f5b2af830b). 
Small adaptations were made.
* Mediafactuality Scraping: Inspired from https://github.com/IgniparousTempest/mediabiasfactcheck.com-bias
* Emoji Cleaning: https://stackoverflow.com/questions/33404752/removing-emojis-from-a-string-in-python
* Dependencies in requirements.txt