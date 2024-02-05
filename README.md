# Repository of Master Thesis Contextual News Graph Collector

This tool aids in the collection and preprocessing of contextual news graph datasets as used in the [FANG](https://github.com/nguyenvanhoang7398/FANG) model.
[FANG](https://github.com/nguyenvanhoang7398/FANG) was shown to build highly representative embeddings from these contextual news graph datasets.
To further study, extend and apply these models additional datasets are necneeded of similar contextual depth. This tool helps in this endeavour.


## Preparing the environment

* Install MariaDB Server and PhpMyAdmin / preferred database inspection tool. 
> Our Reasoning: We found that it is invaluable to be able to easily look and query the already collected data. This is why after temporarily storing the data in text files we insert it into a mysql database. 

* Install python 3.11.5

* Install dependencies

* Setup a config file with your database credentials

* Create a Twitter account and fill in twitter_v1_credentials.txt and twitter_v2_credentials.yaml


## Running

* The subtasks of the collection and prepocessing process are split in single individual easily checkable steps. 
* Each task is described inside the main.py file

* Run by executing main.py
* Running can be limited to specific subtask by specifying the execution target in the main.py file. 


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