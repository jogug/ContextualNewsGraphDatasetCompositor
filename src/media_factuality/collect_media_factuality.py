

import requests, csv, re, bs4
from src.util.Configuration import Configuration

# Inspired from https://github.com/IgniparousTempest/mediabiasfactcheck.com-bias
# This script collects the mediabiasfactcheck website for news sources and their biases

def get_wrapper(url):
    response = requests.get(url)
    content_type = response.headers['Content-Type'].lower()
    is_valid = (response.status_code == 200
        and content_type is not None
        and content_type.find('html') > -1)

    if is_valid:
        return response.content
    else:
        raise Exception(f'Could not get "{url}"')

def collect_source(url):
    raw_html = get_wrapper(url)
    bs = bs4.BeautifulSoup(raw_html, 'html.parser')
    source_name = url.replace("https://mediabiasfactcheck.com/", "").replace("/", "").strip().replace("-", " ")
    try:
        result = re.search(r"Factual Reporting:(.*)", bs.text)
        x = result.group(0)
        factual = x.replace("Factual Reporting:", "").strip()
        if factual is None: raise Exception()
    except Exception as e:
        raise Exception(f'Could not find factual information on "{source_name}" with url "{url}"')

    return [source_name, url, factual] 

def collect_sources(config: Configuration,urls):
    output = config.data_folder_path + config.PRE_MEDIA + '.csv'
    sources = []
    with open(output, mode='w') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for url in urls:
            try:
                row = collect_source(url)
                writer.writerow(row)
            except Exception as e:
                print(e)
    return sources

def get_pages():
    sources = ['https://mediabiasfactcheck.com/fake-news/', 'https://mediabiasfactcheck.com/left/',
               'https://mediabiasfactcheck.com/leftcenter/', 'https://mediabiasfactcheck.com/center/',
               'https://mediabiasfactcheck.com/right-center/', 'https://mediabiasfactcheck.com/right/']

    pages = []
    for source in sources:
        raw_html = get_wrapper(source)
        bs = bs4.BeautifulSoup(raw_html, 'html.parser')
        links = bs.find('table', attrs={'id': 'mbfc-table'})
        if links is None: continue
        for a in links.select('a'):
            pages.append(a['href'])
    return pages

def collect_media_factuality(config:Configuration):
    try:
        collect_sources(config,get_pages())
    except Exception as e:
        print(e)