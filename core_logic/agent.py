# agent.py

import os
import json
from enum import Enum
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key = os.getenv("UPSTAGE_API_KEY"),
    base_url="https://api.upstage.ai/v1/solar"
)

class ArticleStatus(str, Enum):
    NEGATIVE = "Negative" # 후쿠오카 2030과 무관함 (타지역, B2B, 단순 기업 인사/실적, 타겟과 안 맞는 스포츠 등)
    POSITIVE = "Positive" # 500자만으로도 매력적인 후쿠오카 핫플/팝업/맛집/전시회임이 확실함
    MORE_INFO = "More_Info" # 후쿠오카 관련 이벤트 같긴 한데, 500자만으로는 파악이 힘들어 본문 전체를 봐야 함

class ScoutDecision(BaseModel):
    status: ArticleStatus = Field(description="기사의 채택 여부 상태")
    reason: str = Field(description="이러한 결론을 내린 구체적인 이유 (한국어로 1~2문장)")

def evaluate_with_scout(title: str, scout_text: str) -> dict:
    system_prompt = """
    당신은 일본 후쿠오카(福岡) 및 큐슈(九州) 지역의 트렌디한 정보를 수집하는 'Nishi.ai'의 수석 에디터입니다.
    
    [절대 원칙]
    기사의 핵심 주제나 출처가 '후쿠오카(福岡)' 또는 '큐슈(九州)' 지역과 관련이 없다면, 아무리 매력적인 정보라도 무조건 'Negative' 처리하세요. (도쿄, 오사카, 고베, 타지역 온라인 행사 등은 탈락)

    [관심사]
    지역 조건이 충족되었다면, 타겟 독자(2030 한국/일본인)가 후쿠오카 여행/생활 중 즐길 수 있는 [신규 팝업스토어, 감성 카페, 한정판 굿즈, 전시회, 라이프스타일] 정보이거나, 여행 시 구매하기 좋은 [프리미엄 로컬 특산품(고급 차, 디저트 등), 백화점 입점 오미야게, 로컬 브랜드의 글로벌 수상 소식]인지 판단하세요.

    [판단 기준]
    - Negative: 타지역 정보, 완전한 산업용 B2B 뉴스, 행정/인사, 타겟층과 안 맞는 카테고리.
    - Positive: 후쿠오카/큐슈의 매력적인 팝업, 핫플, 식음료 신제품 이벤트임이 명확한 경우. 또는 보도자료 톤(해외 수상 소식 등)이라도 대상이 2030 취향에 맞는 후쿠오카 로컬 특산품/브랜드인 경우.
    - More_info: 관심사는 일치하지만, 후쿠오카 지역과의 구체적인 연관성이나 구매처 등이 500자만으로는 파악이 힘든 경우.
    """

    user_content = f"제목: {title}\n본문(500자): {scout_text}"

    try:
        response = client.chat.completions.create(
            model="solar-pro3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={
                "type": "json_schema",
                "json_schema":{
                    "name": "scout_decision",
                    "schema": ScoutDecision.model_json_schema()
                }
            },
            temperature=0.1
        )

        return json.loads(response.choices[0].message.content)
    
    except Exception as e:
        return {"status": "Error", "reason": str(e)}
    
if __name__ == "__main__":
    # TEST
    test_title = "ジムニーカスタムのAutoRubys、AI対応チャットボットを搭載したホームページを全面リニューアル"
    test_scout_text = "鳥取県鳥取市に本社を置くカスタムカーパーツメーカー・AutoRubys（オートルビーズ、代表：野澤 慎吾）は、2026年3月、公式ホームページを全面リニューアルしたことをお知らせいたします..."
    
    print("🤖 Scout Agent가 기사를 분석 중입니다...")
    decision = evaluate_with_scout(test_title, test_scout_text)
    
    print("\n[AI 에이전트 분석 결과]")
    print(f"판정 상태: {decision.get('status')}")
    print(f"판정 이유: {decision.get('reason')}")