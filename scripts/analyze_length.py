# scripts/analyze_length.py

import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from tqdm import tqdm
import concurrent.futures

from data_ingestion.scrapper import extract_and_clean_sitemap, scrape_article_body

def analyze_text_length():
    print("1. 사이트맵에서 기사 URL 목록을 가져옵니다...")
    res = requests.get("https://prtimes.jp/sitemap-news.xml")
    res.encoding = "UTF-8"
    articles = extract_and_clean_sitemap(res.content)
    
    sample_size = 500
    target_articles = articles[:sample_size]
    
    lengths = []

    def fetch_length(article):
        body_result = scrape_article_body(article['url'])
        if "error" not in body_result:
            return body_result['text_length']
        return None

    print(f"2. {len(target_articles)}개 기사의 본문을 멀티스레딩으로 고속 스크랩합니다...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(tqdm(executor.map(fetch_length, target_articles), total=len(target_articles)))
    
    lengths = [l for l in results if l is not None]

    if not lengths:
        print("데이터를 수집하지 못했습니다.")
        return

    avg_len = sum(lengths) / len(lengths)
    max_len = max(lengths)
    min_len = min(lengths)
    
    print("\n✅ [분석 결과]")
    print(f"- 수집된 유효 기사 수: {len(lengths)}개")
    print(f"- 평균 글자 수: {avg_len:.0f}자")
    print(f"- 최대 글자 수: {max_len}자")
    print(f"- 최소 글자 수: {min_len}자")

    plt.figure(figsize=(10, 6))
    plt.hist(lengths, bins=40, color='skyblue', edgecolor='black', alpha=0.7)
    
    plt.axvline(x=500, color='red', linestyle='dashed', linewidth=2, label='Scout Cut-off (500 chars)')
    
    plt.title('PR TIMES Article Text Length Distribution', fontsize=15)
    plt.xlabel('Text Length (characters)', fontsize=12)
    plt.ylabel('Number of Articles', fontsize=12)
    plt.legend()
    plt.grid(axis='y', alpha=0.5)
    
    plt.savefig('length_distribution.png', dpi=300)
    print("\n그래프가 'length_distribution.png' 파일로 저장되었습니다. 프로젝트 폴더에서 확인해 보세요!")

if __name__ == "__main__":
    analyze_text_length()