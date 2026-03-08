# scripts/run_pipeline.py

import time
import json
import requests
from data_ingestion.scrapper import extract_and_clean_sitemap, scrape_article_body
from core_logic.agent import evaluate_with_scout

def run_mini_batch():
    print("1. 사이트맵 파싱 중...")
    res = requests.get("https://prtimes.jp/sitemap-news.xml")
    res.encoding = "UTF-8"
    articles = extract_and_clean_sitemap(res.content)
    
    test_articles = articles
    results = []

    print(f"\n2. 총 {len(test_articles)}개 기사에 대한 파이프라인 가동 시작!\n")
    
    for idx, article in enumerate(test_articles, 1):
        print(f"[{idx}/{len(test_articles)}] 스크레이핑: {article['title'][:30]}...")
        
        scraped_data = scrape_article_body(article['url'])
        
        if "error" in scraped_data:
            print(f"  -> 스크랩 실패: {scraped_data['error']}\n")
            continue
            
        decision = evaluate_with_scout(article['title'], scraped_data['scout_text'])
        
        final_record = {
            "title": article['title'],
            "url": article['url'],
            "published_at": article['published_at'],
            "main_image": scraped_data.get('main_image_url'),
            "status": decision.get('status'),
            "reason": decision.get('reason')
        }
        results.append(final_record)
        
        print(f"  -> 🤖 판정: {final_record['status']} ({final_record['reason']})\n")
        
        time.sleep(1)

    with open('batch_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print("✅ 배치 테스트 완료! 'batch_results.json'을 확인해 보세요.")

if __name__ == "__main__":
    run_mini_batch()