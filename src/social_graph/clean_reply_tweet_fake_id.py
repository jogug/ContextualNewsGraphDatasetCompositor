import json, csv
import pandas as pd
from src.util.Configuration import Configuration
from tqdm import tqdm


def clean_reply_tweet_fake_id(conf:Configuration):
    in_file_name = 'tweets_unfiltered_fake_reply.txt'
    out_file_name = 'tweets_filtered_fake_reply.txt'    
    in_file_path = conf.data_folder_path + in_file_name
    out_file_path = conf.data_folder_path + out_file_name

    # Cache
    tweet_id_dict = {}
    tweets_out = {
        'id':[],
        'author_id':[],
        'source_id':[],
        'created_at':[],
        'text':[],
        'content':[],
    }

    # Filter 
    # sequence_filter = conf.sequence_filter
    politifact_filter = conf.politifact_filter
    fake_filter = conf.fake_filter

    failed = 0
    available = 0
    with open(in_file_path,'r') as file:
        for line in tqdm(file.readlines()):
            split_line = line.split("~")
            source_id = int(split_line[0])
            try:
                tweet_text = "~".join(split_line[1:]).strip()
                tweet = json.loads(tweet_text)
                for s in tweet["data"]:
                    if s['id'] in tweet_id_dict: continue
                    available+=1
                    # filters
                    filter_text = s['text'].lower()
                    # if sequence_filter and statement not in filter_text: continue
                    if politifact_filter and "politifact" in filter_text: continue
                    if fake_filter and "fake" in filter_text: continue

                    tweet_id_dict[s['id']] = True
                    tweets_out['id'].append(s['id']) 
                    tweets_out['author_id'].append(s['author_id']) 
                    tweets_out['source_id'].append(source_id) 
                    tweets_out['created_at'].append(s['created_at'].replace('\n',''))
                    tweets_out['text'].append(s['text'].replace('\n','')) 
                    s['text'] = s['text'].replace('\n','').replace('\r','').replace('\t','').replace('"','').replace('\'','').replace('\\','').replace('\"','')
                    tweets_out['content'].append(json.dumps(s).replace('\n',''))
                    # print(statement,">>>",s['id'], s['author_id'], s['text'])
            except Exception as e:
                failed+=1
                #print(e)


    df = pd.DataFrame(tweets_out)
    df.to_csv(index=False, path_or_buf=out_file_path,quoting=csv.QUOTE_NONNUMERIC)
