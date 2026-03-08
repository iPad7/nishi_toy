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

def scrape_article_body(url):
    """
    PR TIMES 기사 URL에 접속하여 순수 본문 텍스트를 추출하고,
    정찰용 500자와 전체 텍스트를 반환합니다.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        article_body = soup.select_one('#press-release-body')

        if not article_body:
            return {"error": "본문 영역을 찾을 수 없습니다."}
        
        raw_text = article_body.get_text(separator=' ', strip=True)
        clean_text = ' '.join(raw_text.split())

        scout_text = clean_text[:500]

        all_images = []
        image_list_container = soup.select_one('#js-press-release-image-list')

        if image_list_container:
            for img in image_list_container.find_all('img'):
                src = img.get('src')
                if src:
                    clean_src = src.split('?')[0]
                    if clean_src not in all_images:
                        all_images.append(clean_src)

        main_image_url = all_images[0] if len(all_images) > 0 else ""
        gallery_images = all_images[1:] if len(all_images) > 1 else []

        return {
            "url": url,
            "main_image_url": main_image_url,
            "gallery_images": gallery_images,
            "scout_text": scout_text,
            "full_text": clean_text,
            "text_length": len(clean_text)
        }
    
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
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
    
    test_url = result[0]['url']

    print(f"[{test_url}] 본문 스크랩 시작...\n")

    body_result = scrape_article_body(test_url)

    if "error" in body_result:
        print("에러 발생:", body_result["error"])
    else:
        print("스크랩 성공")
        print("length:", body_result['text_length'])
        print()
        print('Scout Agent 용 앞 500자 미리보기')
        print(body_result['scout_text'])
        print("..." if body_result['text_length'] > 500 else "")
        print()
        print("썸네일 이미지:", body_result['main_image_url'])


    # test_url = "https://prtimes.jp/main/html/rd/p/000002876.000038094.html"
    
    # try:
    #     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    #     response = requests.get(test_url, headers=headers, timeout=10)
    #     print(f"상태 코드: {response.status_code}")
        
    #     if response.status_code == 200:
    #         print("✅ 하드코딩된 URL로는 정상적으로 접속됩니다!")
    #         print("본문 일부:", response.text[:500])
    # except Exception as e:
    #     print(f"❌ 에러 발생: {e}")

    