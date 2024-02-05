#Import the dependencies
from bs4 import BeautifulSoup
import pandas as pd
import requests, csv, json
from src.util.Configuration import Configuration
from tqdm import tqdm
from src.util.StringCleanUtil import clean_statements

'''
## Reference
The code is adapted from [Scrape A Political Website To Build A Fake & Real News Data Set Using Python]
(https://randerson112358.medium.com/scrape-a-political-website-for-fake-real-news-using-python-b4f5b2af830b).
Only a slight changes were made.
'''

def collect_politifact_annotated_target_by_topic(config, tag):
    #Create lists to store the scraped data
    authors = []
    dates = []
    statements = []
    sources = []
    targets = []
    politurls = []
    source_urls = []
    fact_sources = []

    def scrape_subsite(SUBURL):
        # Scrape Fact sources
        fact_sources = []
        subpage = requests.get(SUBURL)

        soup2 = BeautifulSoup(subpage.text, "html.parser")
        sources_box = soup2.find(id="sources")

        if sources_box is not None:
            for p in sources_box.find_all('p'):
                p_text = p.text.strip()
                p_text = p_text.split(',')

                p_tag = ""
                p_year = ""
                p_date = ""
                if len(p_text) > 2:
                    p_tag = p_text[0].strip()
                    p_year = p_text[-1].strip()
                    p_date = p_text[-2].strip()

                a = p.find('a')
                if a is not None:
                    url = a['href']
                    text = a.text.strip()
                    fact_sources.append({
                        "source_tag" : p_tag, 
                        "url" : url,
                        "text" : text,
                        "visited_date" : p_date+" "+p_year})
        return json.dumps(fact_sources)

    #Create a function to scrape the site
    def scrape_website(page_number, source):
        page_num = str(page_number) #Convert the page number to a string

        '''politifact base'''
        BASE_URL = 'https://www.politifact.com'

        '''source: category'''
        URL = 'https://www.politifact.com/factchecks/list/?page={}&category={}'.format(page_num, source)

        '''source: speaker'''
        # URL = 'https://www.politifact.com/factchecks/list/?page={}&speaker={}'.format(page_num, source)
        '''source: all'''
        # URL = 'https://www.politifact.com/factchecks/list/?page='+page_num #append the page number to complete the URL

        webpage = requests.get(URL)

        #time.sleep(3)
        soup = BeautifulSoup(webpage.text, "html.parser") # Parse the text from the website
        #Get the tags and it's class
        statement_footer =  soup.find_all('footer',attrs={'class':'m-statement__footer'})   # Get the tag and it's class
        statement_quote = soup.find_all('div', attrs={'class':'m-statement__quote'})        # Get the tag and it's class
        statement_meta = soup.find_all('div', attrs={'class':'m-statement__meta'})          # Get the tag and it's class
        target = soup.find_all('div', attrs={'class':'m-statement__meter'})                 # Get the tag and it's class
        #loop through the footer class m-statement__footer to get the date and author
        for i in statement_footer:
            link1 = i.text.strip()
            name_and_date = link1.split()
            first_name = name_and_date[1]
            last_name = name_and_date[2]
            full_name = first_name+' '+last_name
            month = name_and_date[4]
            day = name_and_date[5]
            year = name_and_date[6]
            date = month+' '+day+' '+year
            dates.append(date)
            authors.append(full_name)
        #Loop through the div m-statement__quote to get the link
        for i in statement_quote:
            link2 = i.find_all('a')
            # read subpages
            suburl = link2[0]['href']
            fact_sources.append(scrape_subsite(BASE_URL + suburl))
            politurls.append(suburl)
            statements.append(link2[0].text.strip())
        #Loop through the div m-statement__meta to get the source
        for i in statement_meta:
            link3 = i.find_all('a') #Source
            source_text = link3[0].text.strip()
            sources.append(source_text)
        #Loop through the target or the div m-statement__meter to get the facts about the statement (True or False)
        for i in target:
            fact = i.find('div', attrs={'class':'c-image'}).find('img').get('alt')
            targets.append(fact)


    #Loop through 'n-1' webpages to scrape the data
    n=config.max_politifact_pages
    source = tag
    for i in tqdm(range(1, n)):
        scrape_website(i, source=source)

    # Create a new DataFrame
    data = pd.DataFrame(columns = [ 'source', 'target', 'url', 'statement', 'date', 'author', 'fact_sources'])

    data['url'] = politurls
    data['statement'] = clean_statements(statements)
    data['source'] = sources
    data['date'] = dates
    data['target'] = targets
    data['author'] = authors
    data['fact_sources'] = fact_sources

    #Show the data set
    file = config.data_folder_path + source + '.csv'
    data.to_csv(file, index=False, sep=',', quoting=csv.QUOTE_NONNUMERIC)

def collect_politifact_annotated_target_by_topics(config):
    for tag_name in config.tag_names:
        collect_politifact_annotated_target_by_topic(config, tag_name)