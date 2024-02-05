from src.util.Configuration import Configuration
from newspaper import Article
import traceback

def download_content(urls):
    for url in urls:
        try:
            scrape = Article(url=url, language='en')
            scrape.download()
            scrape.parse()
            scrape.nlp()
            text = scrape.text+" "+scrape.meta_description
            text = text.replace("\n", "").replace("\\'", "").replace("\'", "").replace("'", "")
            return True, text
        except:
            traceback.print_exc()
            pass
    return False, ""

def collect_source(config:Configuration):
    DATA_SOURCE_TABLE = config.DATA_SOURCE_TABLE
    DB_database = config.DB_database

    try:
        db = config.get_db()
        # DB fetch all sources
        data = db.fetchall(f"SELECT * FROM {DB_database}.{DATA_SOURCE_TABLE} WHERE name NOT LIKE 'unknown'", dictionary=True)    
        for row in data:
            sources = ["https://" + row["url"], "http://" + row["url"], "http://www." + row["url"], row["url"]]
            if row["status_home"] == "False":
                for source in sources:
                    success, text = download_content([source+"/home", source+"/index", source+"/index.html", source+"/home.html", source])
                    if success:
                        db.execute(f"UPDATE {DB_database}.{DATA_SOURCE_TABLE} SET status_home='True', home='{text}' WHERE id={row['id']}")
                        break
            if row["status_about"] == "False":
                for source in sources:
                    success, text = download_content([source+"/about", source+"/about.html", source+"/about-us", source+"/about-us.html", source])
                    if success:
                        db.execute(f"UPDATE {DB_database}.{DATA_SOURCE_TABLE} SET status_about='True', about='{text}' WHERE id={row['id']}")
                        break
    except:
        traceback.print_exc()
    finally:
        if db is None: db.close()