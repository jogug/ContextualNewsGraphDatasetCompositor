import json, random
from src.util.Configuration import Configuration


def fang_data_generate_train_test_variations(config: Configuration):
    data_folder_path = config.data_folder_path
    data_dataset_folder_path = data_folder_path + "/news_graph/"

    splits = config.splits

    # load train_test_90.json in data_fang/news_graph
    with open(data_dataset_folder_path +"train_test_90.json", "r") as f:
        train_test_90 = json.load(f)

    # all values in single list
    all_values = []
    for key in train_test_90.keys():
        all_values += train_test_90[key]

    # Load news_info.tsv in data_fang/news_graph
    news_info = {}
    with open(data_dataset_folder_path + "news_info.tsv", "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.split("\t")
            news_info[line[0]] = line[1]

    def generate_test_train_split(all_values, news_info, splits, version="v1"):
        article_count = len(all_values)
        # count  fake and real
        fake_count = 0
        real_count = 0
        fake_articles_base = []
        real_articles_base = []
        for article_id in all_values:
            if article_id not in news_info: 
                article_count -= 1
                continue
            if news_info[article_id] == "fake":
                fake_count += 1
                fake_articles_base.append(article_id)
            else:
                real_count += 1
                real_articles_base.append(article_id)
        
        ratio = fake_count/article_count
        
        for split in splits:
            print("split", split, "version", version)
            fake_articles = fake_articles_base.copy()
            real_articles = real_articles_base.copy()

            file_path = data_dataset_folder_path + "train_test_{split}.json.{version}"
            nr_articles = int(article_count * split/100)
            nr_in_train = int(nr_articles * 0.6)
            nr_in_train_fake = int(nr_in_train * ratio)
            nr_in_train_real = nr_in_train - nr_in_train_fake

            nr_in_test = int(nr_articles * 0.2)
            nr_in_val = nr_articles - nr_in_test - nr_in_train
            nr_in_val_fake = int(nr_in_val * ratio)
            nr_in_val_real = nr_in_val - nr_in_val_fake

            train_subset_fake = random.sample(fake_articles, nr_in_train_fake)
            fake_articles = [x for x in fake_articles if x not in train_subset_fake]
            train_subset_real = random.sample(real_articles, nr_in_train_real)
            real_articles = [x for x in real_articles if x not in train_subset_real]
            train_subset = train_subset_fake + train_subset_real

            print("fake_articles", len(fake_articles), "real_articles", len(real_articles), "sum", len(fake_articles) + len(real_articles))

            val_subset_fake = random.sample(fake_articles, nr_in_val_fake)
            fake_articles = [x for x in fake_articles if x not in val_subset_fake]
            val_subset_real = random.sample(real_articles, nr_in_val_real)
            real_articles = [x for x in real_articles if x not in val_subset_real]
            val_subset = val_subset_fake + val_subset_real

            print("fake_articles", len(fake_articles), "real_articles", len(real_articles), "sum", len(fake_articles) + len(real_articles))

            test_subset = fake_articles + real_articles

            out = {
                "train": ",".join(train_subset),
                "val": ",".join(val_subset),
                "test": ",".join(test_subset)
            }

            with open(file_path.format(split=split, version=version),"w", encoding="utf-8") as file:
                file.write(json.dumps(out))

    for version in range(10):
        generate_test_train_split(all_values, news_info, splits, version="v"+str(version))

