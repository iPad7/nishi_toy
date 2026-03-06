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

print("아이템 확인")
print(result[0])
print("확인된 아이템 개수")
print(len(result))

print("글자 깨짐 확인")
print("Print:", result[0]['title'])
print("Repr:", repr(result[0]['title']))