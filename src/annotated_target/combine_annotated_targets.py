import csv
import pandas as pd
from src.util.Configuration import Configuration

def combine_annotated_targets(config: Configuration):
    '''
    This fuction loads annotated targets into a single csv file.
    '''
    in_file_names = [ tag + '.csv' for tag in config.tag_names]
    in_file_paths = [config.data_folder_path + in_file_name for in_file_name in in_file_names]
    out_file_path = config.data_folder_path + config.articles_combined_filename

    out_df = None
    for in_file_path in in_file_paths:
        tag_file = pd.read_csv(in_file_path)
        if out_df is None:
            out_df = tag_file
        else:
            out_df = pd.concat([out_df,tag_file])

    out_df.drop_duplicates().reset_index(drop=True)
    out_df['index'] = range(1, len(out_df) + 1)

    # move to first position
    first_column = out_df.pop('index')
    out_df.insert(0, 'index', first_column)

    out_df.to_csv(index=False, path_or_buf=out_file_path,quoting=csv.QUOTE_NONNUMERIC)

