import requests
from bs4 import BeautifulSoup

def extract_and_clean_sitemap(xml_content):
    soup = BeautifulSoup(xml_content, 'xml')
    articles = []
    
    for url_tag in soup.find_all('url'):
        loc = url_tag.find('loc').text if url_tag.find('loc') else ""
        
        news_tag = url_tag.find('news:news')
        if not news_tag:
            continue
            
        raw_title = news_tag.find('news:title').text if news_tag.find('news:title') else ""
        raw_keywords = news_tag.find('news:keywords').text if news_tag.find('news:keywords') else ""
        pub_date = news_tag.find('news:publication_date').text if news_tag.find('news:publication_date') else ""
        
        keyword_list = [k.strip() for k in raw_keywords.split(',') if k.strip()]
        
        articles.append({
            "url": loc,
            "title": raw_title,
            "keywords": keyword_list,
            "published_at": pub_date
        })
        
    return articles

res = requests.get("https://prtimes.jp/sitemap-news.xml")
res.encoding = "UTF-8"
result = extract_and_clean_sitemap(res.content)
print(result[150], len(result), sep='\n\n')