from src.util.Configuration import Configuration

from src.util.create_database_structure import create_database_structure

from src.annotated_target.collect_politifact_annotated_target_by_topic import collect_politifact_annotated_target_by_topics
from src.annotated_target.combine_annotated_targets import combine_annotated_targets
from src.annotated_target.load_annotated_target_into_db import load_annotated_target_into_db
from src.annotated_target.clean_annotated_target_date import clean_annotated_target_date
from src.annotated_target.collect_article_date_from_wayback import collect_article_date_from_wayback

from src.media_factuality.collect_media_factuality import collect_media_factuality
from src.media_factuality.load_media_factuality_into_db import load_media_factuality_into_db

from src.source.clean_source import clean_source
from src.source.collect_source import collect_source

from src.social_graph.collect_main_tweet_id import collect_main_tweet_id
from src.social_graph.collect_user_tweets_topic import collect_user_tweets_topic

from src.social_graph.clean_fake_main_tweet_id import clean_fake_main_tweet_id
from src.social_graph.clean_real_main_tweet_id import clean_real_main_tweet_id

from src.social_graph.collect_reply_tweet_id import collect_reply_tweet_id
from src.social_graph.clean_reply_tweet_fake_id import clean_reply_tweet_fake_id
from src.social_graph.clean_reply_tweet_real_id import clean_reply_tweet_real_id
from src.social_graph.load_tweets_into_db import load_tweets_into_db

from src.social_graph.clean_user_id import clean_user_id
from src.social_graph.collect_user import collect_users
from src.social_graph.collect_followers import collect_followers
from src.social_graph.clean_followers import clean_followers

from src.social_graph.collect_tweet_context import collect_tweet_context

from src.stance_prediction.prepare_stance_prediction_from_db_politifact import prepare_stance_prediction_from_db_politifact
from src.stance_prediction.prepare_stance_prediction_from_db_real_twitter import prepare_stance_prediction_from_db_real_twitter
from src.stance_prediction.clean_stance import clean_stance

from src.compositor.compose_dataset import compose_dataset

from src.util.fang_data_generate_train_test_variations import fang_data_generate_train_test_variations
from src.social_graph.load_ttt_tweet import load_ttt_tweet
from src.util.build_dataset_statsistics_table_from_final import build_dataset_statsistics_tex_table_from_final, build_stats

# Task "Press enter to continue"
def press_enter_to_continue():
    input("Press Enter to continue...")

exec_order = [
    # TASK 1 Create DB Structure
    create_database_structure,
    # TASK 2 Collect Articles
    collect_politifact_annotated_target_by_topics,
    # TASK 3 Combine Articles and Index
    combine_annotated_targets,
    # TASK 4 Load Articles into DB
    load_annotated_target_into_db,
    # TASK 5 Try extracting dates from articles
    clean_annotated_target_date,
    # TASK 6 Try extracting dates from wayback machine
    collect_article_date_from_wayback,

    # TASK 7 Collect Media Factuality
    collect_media_factuality,
    # TASK 8 Load Media Factuality into DB
    load_media_factuality_into_db,

    # TASK 9 Clean Sources
    clean_source,
    # TASK 10 Collect Source
    collect_source,

    # TASK 11 Download Main Tweet IDs; Try finding associated tweets as FakeNewsNet did
    collect_main_tweet_id,
    # TASK 12 Download User Tweets by Topic
    collect_user_tweets_topic,

    # TASK 13 Clean Fake Main Tweet IDs
    clean_fake_main_tweet_id,
    # TASK 14 Clean Real Main Tweet IDs
    clean_real_main_tweet_id,

    # TASK 15 Load Replies to these tweets
    collect_reply_tweet_id,
    # TASK 16 Clean Replies to these fake tweets
    clean_reply_tweet_fake_id,
    # TASK 17 Clean Replies to these real tweets
    clean_reply_tweet_real_id,

    # TASK 18 Load Tweets into DB
    load_tweets_into_db,

    # TASK 19 Clean User IDs
    clean_user_id,
    # TASK 20 Download Users
    collect_users,
    # TASK 21 Download Followers
    collect_followers,
    # TASK 22 Clean Followers
    clean_followers,

    # TASK 23 Download Tweet Context : Extends the tweet data with context
    collect_tweet_context,

    # TASK 24 Prepare Stance Detection Target News
    prepare_stance_prediction_from_db_politifact,
    # TASK 25 Manual Execution of stance detection > https://github.com/nguyenvanhoang7398/FANG-helper
    # It generates the "predict_1.tsv" file for Stance Detection. 
    # Expects the output to be in the form of a csv file with the following columns:
    # Stance Detection yields the file: "predict_results_1.tsv" where 0 support, 1 deny; 
    # Sentiment Classification yields: "predict_results_yelp_1_classification.tsv" where 0 support positive, 1 support negative;
    press_enter_to_continue,

    # TASK 26 Prepare Stance Detection Target Post
    prepare_stance_prediction_from_db_real_twitter,
    # TASK 27 Manual Execution of stance detection > https://github.com/nguyenvanhoang7398/FANG-helper
    # It generates the "predict_2.tsv" file for Stance Detection. 
    # Expects the output to be in the form of a csv file with the following columns:
    # Stance Detection yields the file: "predict_results_2.tsv" where 0 support, 1 deny; 
    # Sentiment Classification yields: "predict_results_yelp_2_classification.tsv" where 0 support positive, 1 support negative;
    press_enter_to_continue,

    # TASK 28 Clean Stance
    clean_stance,

    # TASK 29 Extract Temporal Aspect
    load_ttt_tweet,

    # TASK 30 Compose news_graph
    compose_dataset,

    # UTIL Task 31 Generate Train Test split
    fang_data_generate_train_test_variations,

    # UTIL TASK 32 build news_graph statistics
    build_stats,
    # UTIL TASK 33 build news_graph statistics tex table
    build_dataset_statsistics_tex_table_from_final,

]

exec_targets = {
    "full" : [0,34],
    "task1" : [0,1],
    "task2" : [1,2],
    "task3" : [2,3],
    "task4" : [3,4],
    "task5" : [4,5],
    "task6" : [5,6],
    "task7" : [6,7],
    "task8" : [7,8],
    "task9" : [8,9],
    "task10" : [9,10],
    "task11" : [10,11],
    "task12" : [11,12],
    "task13" : [12,13],
    "task14" : [13,14],
    "task15" : [14,15],
    "task16" : [15,16],
    "task17" : [16,17],
    "task18" : [17,18],
    "task19" : [18,19],
    "task20" : [19,20],
    "task21" : [20,21],
    "task22" : [21,22],
    "task23" : [22,23],
    "task24" : [23,24],
    "task25" : [24,25],
    "task26" : [25,26],
    "task27" : [26,27],
    "task28" : [27,28],
    "task29" : [28,29],
    "task30" : [29,30],
    "task31" : [30,31],
    "task32" : [31,32],
    "task33" : [32,33],
    "task34" : [33,34],
}

def run (exec_target, conf: Configuration, test_run):
    for task in exec_order[exec_target[0]:exec_target[1]]:
        print("Running task: " + task.__name__)
        if test_run: continue
        else:
            task(conf)

# Main Entry Point
if __name__ == "__main__":

    exec_target_name = "full"
    test_run = False

    conf = Configuration(config_file=Configuration.default_test)
    exec_target = exec_targets[exec_target_name]

    run(exec_target, conf, test_run)