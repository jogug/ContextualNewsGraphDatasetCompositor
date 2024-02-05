import json, csv
import pandas as pd
from src.util.Configuration import Configuration
from tqdm import tqdm

def clean_real_main_tweet_id(conf: Configuration):
    in_file_name = 'tweets_unfiltered_real_main.txt'
    out_file_name = 'tweets_filtered_real_main.txt'    
    in_file_path = conf.data_folder_path + in_file_name
    out_file_path = conf.data_folder_path + out_file_name

    # Cache
    tweet_id_dict = {}
    tweets_out = {
        'respectable':[],
        'tag':[],
        'id':[],
        'author_id':[],
        'created_at':[],  
        'text':[],
        'content':[],
    }

    failed = 0
    available = 0
    with open(in_file_path,'r') as file:
        for line in tqdm(file.readlines()):
            split_line = line.split("~")
            split_identifier = split_line[0].split(",")
            respectable = split_identifier[0]
            tag = split_identifier[1]
            try:
                tweet_text = "~".join(split_line[1:]).strip()
                tweet = json.loads(tweet_text)
                for s in tweet["data"]:
                    if s['id'] in tweet_id_dict: continue
                    available+=1
                    tweet_id_dict[s['id']] = True
                    tweets_out['respectable'].append(respectable) 
                    tweets_out['tag'].append(tag) 
                    tweets_out['id'].append(s['id']) 
                    tweets_out['author_id'].append(s['author_id'])
                    tweets_out['created_at'].append(s['created_at'].replace('\n',''))
                    tweets_out['text'].append(s['text'].replace('\n',''))
                    s['text'] = s['text'].replace('\n','').replace('\r','').replace('\t','').replace('"','').replace('\'','').replace('\\','').replace('\"','')
                    tweets_out['content'].append(json.dumps(s).replace('\n',''))
            except Exception as e:
                failed+=1
                print(e)
    df = pd.DataFrame(tweets_out)
    df.to_csv(index=False, path_or_buf=out_file_path,quoting=csv.QUOTE_NONNUMERIC)
