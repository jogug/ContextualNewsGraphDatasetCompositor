from pprint import pprint
from src.util.Configuration import Configuration
from src.util.LatexTableUtil import LatexTableUtil

def build_stats(config:Configuration, verbose = False):
    folder = config.data_dataset_folder_path

    news_map_realfake = {}
    for line in open(f"{folder}news_info.tsv","r").readlines():
        cols = line.split("\t")
        news_map_realfake[cols[0]] = cols[1].replace("\n","")

    unique_news_realfake = {}
    for news, key in news_map_realfake.items():
        if key not in unique_news_realfake:
            unique_news_realfake[key] = 0
        unique_news_realfake[key] += 1


    def file_row_count(filepath, news_real_fake_map = None, news_real_fake_filter = None):
        count = 0
        with open(filepath,"r") as file:
            for line in file.readlines():
                cols = line.split("\t")
                ne = cols[1].replace("\n","")
                if news_real_fake_filter != None and news_real_fake_map != None:
                    if news_real_fake_map[ne] not in news_real_fake_filter:
                        continue
                count += 1
        return count

    def file_stance_count(filepath, user_stance_map_b = None, news_stance_map_b = None, news_real_fake_map = None, news_real_fake_filter = None):
        user_stance_map = {} if user_stance_map_b is None else user_stance_map_b
        news_stance_map = {} if news_stance_map_b is None else news_stance_map_b
        with open(filepath,"r") as file:
            for line in file.readlines():            
                cols = line.split("\t")
                ue = cols[0]
                ne = cols[1].replace("\n","")
                if news_real_fake_filter != None and news_real_fake_map != None:              
                    if news_real_fake_map[ne] not in news_real_fake_filter:
                        continue
                if ue not in user_stance_map:
                    user_stance_map[ue] = 0
                user_stance_map[ue] += 1
                if ne not in news_stance_map:
                    news_stance_map[ne] = 0
                news_stance_map[ne] += 1
        return user_stance_map, news_stance_map

    def categorise_ttt(value, intervals):
        for interval in intervals:
            if value <= interval:
                return interval
        return intervals[-1]

    def file_ttt_stats(filepath, ttt_interval_stats_b = None, ttt_interval_stats_b2 = None):
        ttt_interval_stats = {} if ttt_interval_stats_b is None else ttt_interval_stats_b
        ttt_interval_stats2 = {} if ttt_interval_stats_b2 is None else ttt_interval_stats_b2

        ttt_intervals = [60*60*i for i in [12,36,24*14,-1]]
        ttt_intervals2 = [60*60*i for i in [3,6,-1]]
        with open(filepath,"r") as file:
            for line in file.readlines():            
                cols = line.split("\t")
                try:
                    ttt = int(float(cols[2].replace("\n","")))
                    category = categorise_ttt(ttt, ttt_intervals)
                    if category not in ttt_interval_stats:
                        ttt_interval_stats[category] = {"all":0, "fake":0, "real":0}

                    if news_map_realfake[cols[1]] == "fake":
                        ttt_interval_stats[category]["fake"] += 1
                    else:
                        ttt_interval_stats[category]["real"] += 1
                    ttt_interval_stats[category]["all"] += 1

                    category2 = categorise_ttt(ttt, ttt_intervals2)
                    if category2 not in ttt_interval_stats2:
                        ttt_interval_stats2[category2] = {"all":0, "fake":0, "real":0}

                    if news_map_realfake[cols[1]] == "fake":
                        ttt_interval_stats2[category2]["fake"] += 1
                    else:
                        ttt_interval_stats2[category2]["real"] += 1
                    ttt_interval_stats2[category2]["all"] += 1
                except Exception as e:
                    #if verbose: print(cols)
                    pass
                

        return ttt_interval_stats, ttt_interval_stats2

    def interaction_stats (user_stance_map, news_stance_map, article_real_fake_map = None, news_real_fake_filter = None):
        user_stance_map, news_stance_map = file_stance_count(f"{folder}support_negative.tsv", user_stance_map, news_stance_map, article_real_fake_map, news_real_fake_filter)
        user_stance_map, news_stance_map = file_stance_count(f"{folder}support_neutral.tsv", user_stance_map, news_stance_map, article_real_fake_map, news_real_fake_filter)
        user_stance_map, news_stance_map = file_stance_count(f"{folder}source_publication.tsv", user_stance_map, news_stance_map, article_real_fake_map, news_real_fake_filter)
        user_stance_map, news_stance_map = file_stance_count(f"{folder}report.tsv", user_stance_map, news_stance_map, article_real_fake_map, news_real_fake_filter)
        user_stance_map, news_stance_map = file_stance_count(f"{folder}deny.tsv", user_stance_map, news_stance_map, article_real_fake_map, news_real_fake_filter)
        
        user_interaction_counts = sorted(list(user_stance_map.values()))
        user_stance_stats = {
            "avg" : sum(user_interaction_counts)/len(user_interaction_counts),
            "median" : user_interaction_counts[len(user_interaction_counts)//2],
            "min" : min(user_interaction_counts),
            "max" : max(user_interaction_counts)
        }
        if verbose: print("user_stance_map",
            user_stance_stats
        )

        news_stance_counts = sorted(list(news_stance_map.values()))
        news_stance_stats = {
            "avg" : sum(news_stance_counts)/len(news_stance_counts),
            "median" : news_stance_counts[len(news_stance_counts)//2],
            "min" : min(news_stance_counts),
            "max" : max(news_stance_counts)
        }
        if verbose: print("news_stance_counts",
            news_stance_stats
        )
        return user_stance_map, news_stance_map, user_stance_stats, news_stance_stats

    def file_row_stats(article_real_fake_map = None, news_real_fake_filter = None):
        stance_stats = {
            "support_negative" : file_row_count(f"{folder}support_negative.tsv", article_real_fake_map, news_real_fake_filter),
            "support_neutral" : file_row_count(f"{folder}support_neutral.tsv", article_real_fake_map, news_real_fake_filter),
            "source_publication" : file_row_count(f"{folder}source_publication.tsv", article_real_fake_map, news_real_fake_filter),
            "report" : file_row_count(f"{folder}report.tsv", article_real_fake_map, news_real_fake_filter),
            "deny" : file_row_count(f"{folder}deny.tsv", article_real_fake_map, news_real_fake_filter),
        }
        if verbose: print(stance_stats)
        return stance_stats

    def ttt_interaction_stats():
        ttt_intervals_stat = None
        ttt_intervals_stat2 = None
        ttt_intervals_stat, ttt_intervals_stat2 = file_ttt_stats(f"{folder}support_negative.tsv", ttt_intervals_stat, ttt_intervals_stat2)
        ttt_intervals_stat, ttt_intervals_stat2 = file_ttt_stats(f"{folder}support_neutral.tsv", ttt_intervals_stat, ttt_intervals_stat2)
        ttt_intervals_stat, ttt_intervals_stat2 = file_ttt_stats(f"{folder}source_publication.tsv", ttt_intervals_stat, ttt_intervals_stat2)
        ttt_intervals_stat, ttt_intervals_stat2 = file_ttt_stats(f"{folder}report.tsv", ttt_intervals_stat, ttt_intervals_stat2)
        ttt_intervals_stat, ttt_intervals_stat2 = file_ttt_stats(f"{folder}deny.tsv", ttt_intervals_stat, ttt_intervals_stat2)
        if verbose: print(ttt_intervals_stat)
        if verbose: print(ttt_intervals_stat2)
        return ttt_intervals_stat, ttt_intervals_stat2

    output = {}
    output["realfake"] = {
        "name" : "real + fake",
    }
    # Entities
    entity_type_count_map = {}
    with open(f"{folder}entities.txt","r") as file:
        for line in file.readlines():
            entity_type = line.split("_")[0]
            if entity_type not in entity_type_count_map:
                entity_type_count_map[entity_type] = 0
            entity_type_count_map[entity_type] += 1
    output["realfake"]["entity_type_count_map"] = entity_type_count_map

    # User relationships
    user_relationships = file_row_count(f"{folder}user_relationships.tsv")
    output["realfake"]["user_relationships"] = user_relationships

    # User relationships
    stance_stats = file_row_stats()
    output["realfake"]["stance_stats"] = stance_stats

    # Interaction stats
    user_stance_map, news_stance_map, user_stance_stats, news_stance_stats = interaction_stats ({}, {})
    #output["realfake"]["user_stance_map"] = user_stance_map
    #output["realfake"]["news_stance_map"] = news_stance_map
    output["realfake"]["user_stance_stats"] = user_stance_stats
    output["realfake"]["news_stance_stats"] = news_stance_stats
    if verbose: print()

    # Entities
    real_fake_map = {}
    article_real_fake_map = {}
    with open(f"{folder}news_info.tsv","r") as file:
        for line in file.readlines():
            article_name, entity_type, _ = line.split("\t")
            if entity_type not in real_fake_map:
                real_fake_map[entity_type] = 0
            real_fake_map[entity_type] += 1
            article_real_fake_map[article_name] = entity_type
    output["realfake"]["real_fake_map"] = real_fake_map
    #output["article_real_fake_map"] = article_real_fake_map

    # Interaction stats real
    output["real"] = {
        "name" : "real",
    }
    if verbose: print("real")
    stance_stats_real = file_row_stats(article_real_fake_map, "real")
    output["real"]["stance_stats"] = stance_stats_real
    user_stance_map, news_stance_map, user_stance_stats, news_stance_stats = interaction_stats ({}, {}, article_real_fake_map, "real")
    #output["real"]["user_stance_map"] = user_stance_map
    #output["real"]["news_stance_map"] = news_stance_map
    output["real"]["user_stance_stats"] = user_stance_stats
    output["real"]["news_stance_stats"] = news_stance_stats
    entity_type_count_map = {}
    entity_type_count_map["users"] = len(user_stance_map.keys())
    entity_type_count_map["news"] = len(news_stance_map.keys())
    if verbose: print(entity_type_count_map)
    if verbose: print()
    output["real"]["entity_type_count_map"] = entity_type_count_map

    # Interaction stats real
    output["fake"] = {
        "name" : "fake",
    }
    if verbose: print("fake")
    stance_stats_fake = file_row_stats(article_real_fake_map, "fake")
    output["fake"]["stance_stats"] = stance_stats_fake
    user_stance_map, news_stance_map, user_stance_stats, news_stance_stats = interaction_stats ({}, {}, article_real_fake_map, "fake")
    #output["fake"]["user_stance_map"] = user_stance_map
    #output["fake"]["news_stance_map"] = news_stance_map
    output["fake"]["user_stance_stats"] = user_stance_stats
    output["fake"]["news_stance_stats"] = news_stance_stats
    entity_type_count_map = {}
    entity_type_count_map["users"] = len(user_stance_map.keys())
    entity_type_count_map["news"] = len(news_stance_map.keys())
    if verbose: print(entity_type_count_map)
    if verbose: print()
    output["fake"]["entity_type_count_map"] = entity_type_count_map

    ttt_intervals_stat, ttt_intervals_stat2 = ttt_interaction_stats()
    output["realfake"]["ttt_intervals_stat"] = ttt_intervals_stat
    output["realfake"]["ttt_intervals_stat2"] = ttt_intervals_stat2

    # Output to file
    with open(config.data_folder_path + "_statistics_" + config.data_tag + ".json", "w") as f:
        f.write(str(output))
    return output


def build_dataset_statsistics_tex_table_from_final(config:Configuration):
    config = Configuration(Configuration.default_fang)
    fang_stats = build_stats(config, False)

    config = Configuration(Configuration.default_coaid)
    coaid_stats = build_stats(config, False)

    config = Configuration(Configuration.default_ukraine)
    ukraine_stats = build_stats(config, False)

    data = {
        "FANG" : fang_stats,
        "CoAID" : coaid_stats,
        "Ukraine" : ukraine_stats,
    }

    latex_tables = []
    def build_total_table(data):
        tables = []
        for dataset_name, dataset_data in data.items():
            grid = [["" for j in range(5)] for i in range(4)]
            header = ["News", "Users", "Sources", "User Relationships"]
            for idy, key in enumerate(header):
                grid[0][idy+1] = key
            row_header = ["Real", "Fake", "Real + Fake"]
            for idx, key in enumerate(row_header):
                grid[idx+1][0] = key
            for idx, key in enumerate(["real", "fake", "realfake"]):          
                cur_data = dataset_data[key]
                entity_type_count_map = cur_data["entity_type_count_map"]
                for idy, entity_key in enumerate(["news", "user", "source"]):
                    if entity_key in entity_type_count_map:
                        grid[idx+1][idy+1] = entity_type_count_map[entity_key]
                    if entity_key + "s" in entity_type_count_map:
                        grid[idx+1][idy+1] = entity_type_count_map[entity_key + "s"]
                if "user_relationships" in cur_data:
                    grid[idx+1][idy+2] = cur_data["user_relationships"]
            tables.append(LatexTableUtil(grid, name = dataset_name))
        return tables
    latex_tables += build_total_table(data)

    def build_stance_table(data):
        tables = []
        for dataset_name, dataset_data in data.items():
            grid = [["" for j in range(6)] for i in range(4)]
            header = ["Support Negative", "Support Neutral", "Source Publication", "Report", "Deny"]
            for idy, key in enumerate(header):
                grid[0][idy+1] = key
            row_header = ["Real", "Fake", "Real + Fake"]
            for idx, key in enumerate(row_header):
                grid[idx+1][0] = key
            for idx, key in enumerate(["real", "fake", "realfake"]):          
                cur_data = dataset_data[key]
                stance_stats = cur_data["stance_stats"]
                for idy, stance_key in enumerate(["support_negative", "support_neutral", "source_publication", "report", "deny"]):
                    if stance_key in stance_stats:
                        grid[idx+1][idy+1] = stance_stats[stance_key]
            tables.append(LatexTableUtil(grid, name = dataset_name))
        return tables
    latex_tables += build_stance_table(data)

    def build_ttt_intervals_stat2_table(data):
        tables = []
        for dataset_name, dataset_data in data.items():        
            dataset_data = dataset_data["realfake"]["ttt_intervals_stat"]
            grid = [["" for j in range(5)] for i in range(4)]
            header = ["< 12 hours", "< 36 hours", "< 2 weeks", ">= 2 weeks"]
            for idy, key in enumerate(header):
                grid[0][idy+1] = key
            row_header = ["Real", "Fake", "Real + Fake"]
            for idx, key in enumerate(row_header):
                grid[idx+1][0] = key
            for idx, key in enumerate([43200, 129600, 1209600, -3600]):          
                cur_data = dataset_data[key]
                for idy, stance_key in enumerate(["real", "fake", "all"]):
                    if stance_key in cur_data:
                        grid[idy+1][idx+1] = cur_data[stance_key]
            tables.append(LatexTableUtil(grid, name = dataset_name))
        return tables
    latex_tables += build_ttt_intervals_stat2_table(data)

    def build_news_stance_stats_table(data):
        tables = []
        for dataset_name, dataset_data in data.items():
            grid = [["" for j in range(5)] for i in range(4)]
            header = ["Avg", "Median", "Min", "Max"]
            for idy, key in enumerate(header):
                grid[0][idy+1] = key
            row_header = ["Real", "Fake", "Real + Fake"]
            for idx, key in enumerate(row_header):
                grid[idx+1][0] = key
            for idx, key in enumerate(["real", "fake", "realfake"]):          
                cur_data = dataset_data[key]
                stance_stats = cur_data["news_stance_stats"]
                for idy, stance_key in enumerate(["avg", "median", "min", "max"]):
                    if stance_key in stance_stats:
                        grid[idx+1][idy+1] = int(round(stance_stats[stance_key],0))
            tables.append(LatexTableUtil(grid, name = dataset_name))
        return tables
    latex_tables += build_news_stance_stats_table(data)

    def build_user_stance_stats_table(data):
        tables = []
        for dataset_name, dataset_data in data.items():
            grid = [["" for j in range(5)] for i in range(4)]
            header = ["Avg", "Median", "Min", "Max"]
            for idy, key in enumerate(header):
                grid[0][idy+1] = key
            row_header = ["Real", "Fake", "Real + Fake"]
            for idx, key in enumerate(row_header):
                grid[idx+1][0] = key
            for idx, key in enumerate(["real", "fake", "realfake"]):          
                cur_data = dataset_data[key]
                stance_stats = cur_data["user_stance_stats"]
                for idy, stance_key in enumerate(["avg", "median", "min", "max"]):
                    if stance_key in stance_stats:
                        grid[idx+1][idy+1] = int(round(stance_stats[stance_key],0))
            tables.append(LatexTableUtil(grid, name = dataset_name))
        return tables
    latex_tables += build_user_stance_stats_table(data)


    # Write to file
    
    with open(config.data_folder_path + "tex_ds_statistics.tex", "w") as f:
        for table in latex_tables:
            f.write(table.to_latex() + "\n\n")