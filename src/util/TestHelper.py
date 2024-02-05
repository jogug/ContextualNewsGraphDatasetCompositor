import random

from src.util.Database import Database
from src.util.Configuration import Configuration


def select_randomly (config, db: Database, select_nr, array, selected):
   if selected >= select_nr:
      print("already selected / more selected than needed")
      return
   index_already_selected = set()
   available_nr = len(array)
   if available_nr > select_nr:
      for r in range(select_nr):
         notSelected = True
         while notSelected:
            cur_rand_index = random.randrange(len(array))
            if cur_rand_index in index_already_selected:
               continue

            index_already_selected.add(cur_rand_index)
            notSelected = False
   else:
      # just select all
      index_already_selected = set(list(range(len(array))))

   selected_elements = []
   for index in index_already_selected:
      selected_elements.append(array[index])
   return selected_elements
       

def select_tweets_randomly(config: Configuration):
   DATA_TWEET_TABLE = config.DATA_TWEET_TABLE
   db = config.get_db()
   statement_counter = f"""
   SELECT realfake, count(*) as count FROM
   (SELECT * FROM {DATA_TWEET_TABLE} WHERE source_tweet_id = 0) a 
   GROUP BY realfake
   """
   statement_counter_selected = f"""
   SELECT realfake, count(*) as count FROM
   (SELECT * FROM {DATA_TWEET_TABLE} WHERE source_tweet_id = 0) a 
   WHERE selected!=0
   GROUP BY realfake
   """
   result = db.fetchall(statement=statement_counter_selected, dictionary=True)
   tweet_map_selected = {
      "real" : 0,
      "fake" : 0,
   }
   for row in result:
      tweet_map_selected[row["realfake"]] = row["count"]
 
   statement_tweet_with_structure = f"""
   SELECT * FROM
   (SELECT source_tweet_id,realfake, count(*) as sub_structure_count, GROUP_CONCAT(tweet_id,'') as selected_ids FROM {DATA_TWEET_TABLE} GROUP BY source_tweet_id,realfake) a 
   WHERE sub_structure_count > 0 AND source_tweet_id != 0
   """
   
   result = db.fetchall(statement=statement_tweet_with_structure, dictionary=True)
   tweet_map_structure = {
      "real" : [],
      "fake" : [],
   }
   for row in result:
      tweet_map_structure[row["realfake"]].append(row)
   
   print("real", len(tweet_map_structure["real"]))
   print("fake", len(tweet_map_structure["fake"]))
   select_nr = config.nr_per_realfake
   print("select nr", select_nr)

   # real / fake
   real = select_randomly(config, db, select_nr, tweet_map_structure["real"], tweet_map_selected["real"])
   fake = select_randomly(config, db, select_nr, tweet_map_structure["fake"], tweet_map_selected["fake"])

   for selected in real:
      id_list = str(selected["source_tweet_id"]) + "," + selected["selected_ids"]
      # TODO set selected to 1

   db.disconnect()
   return real, fake
    
config = Configuration("ukraine.yaml")
real, fake = select_tweets_randomly(config)
