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

class RegionMatch(str, Enum):
    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"

class ArticleStatus(str, Enum):
    NEGATIVE = "Negative"
    POSITIVE = "Positive"
    MORE_INFO = "More_Info"

class ScoutDecision(BaseModel):
    extracted_location: str = Field(
        description="1. 기사의 물리적 무대 또는 '다루고 있는 브랜드/특산품의 출신지(산지)'를 추출하세요. (예: 도쿄 세타가야, 후쿠오카 텐진, 교토 우지 등. 불분명할 경우 '알 수 없음')"
    )
    reasoning_process: str = Field(
        description="2. (중요) 결론을 내리기 전에 생각하는 과정입니다. 추출된 장소가 지도상 어디인지 팩트를 확인하세요. 만약 행사가 타지역/해외(런던 등)에서 열렸더라도 주인공(특산품, 브랜드)이 후쿠오카/큐슈 출신이라면 지역 관련성이 있는 것(Yes)으로 논리적으로 분석하세요. 단서가 아예 없다면 정보 부족으로 분석하세요."
    )
    is_kyushu_region: RegionMatch = Field(
        description="3. 위 분석(reasoning_process)을 바탕으로 기사의 핵심 주체(물리적 장소 OR 특산품/브랜드의 산지)가 큐슈 지역인지 마킹하세요. 해당 정보만으로 판단하기 애매하다면 unknown으로 남겨두세요."
    )
    status: ArticleStatus = Field(
        description="4. 기사의 최종 채택 여부. (주의: is_kyushu_region이 'no'라면 무조건 Negative, 'unknown'이라면 무조건 More_Info를 선택할 것)"
    )

def evaluate_with_scout(title: str, scout_text: str) -> dict:
    system_prompt = """
    당신은 일본 후쿠오카(福岡) 및 큐슈(九州) 지역의 트렌디한 정보를 수집하는 'Nishi.ai'의 수석 에디터입니다.
    Nishi.ai는 후쿠오카 및 큐슈의 2030 세대 주민 및 여행객들에게 생활&관광에 유익한 정보를 제공하는 서비스이며, 현재 당신은 보도자료를 읽고 해당 자료가 편집하여 게시할 만한 가치가 있는 자료인지 선별하는 작업을 도와주고 있습니다. 
    사용자가 제공하는 기사의 '제목'과 '본문'을 읽고, [판단 로직 순서]에 따라 분석한 뒤 JSON 스키마에 맞추어 출력하십시오.
    
    [절대 원칙: 지역 필터가 최우선입니다]
    1. '타지역(도쿄, 홋카이도, 오사카 등)'의 행사임이 명확히 명시되어 있고 큐슈와 무관하다면 즉시 'Negative' 처리하세요.
    2. 행사 장소가 타지역/해외라도 기사의 주인공이 '후쿠오카/큐슈 로컬 브랜드/특산품'이라면 'Yes(지역 일치)'로 간주합니다.
    3. 제공된 500자 텍스트 내에 지리적 단서가 전혀 없다면, 절대 임의로 추측하여 기각하지 말고 반드시 'Unknown'을 선택하여 최종 상태를 'More_Info'로 보류하십시오.

    [판단 로직 순서]
    1. 지역 판별 (가장 중요)
    - 행사 장소 또는 핵심 브랜드의 출신지가 큐슈/후쿠오카인가? -> [Yes / No / Unknown]
    - 만약 [No]라면 -> 즉시 status: "Negative"로 종료.
    - 만약 [Unknown]이라면 -> 즉시 status: "More_Info"로 설정하고 종료.

    2. 가치 판별 (지역이 [Yes]인 경우에만 수행)
    - 2030 한국/일본인이 즐길 수 있는 [신규 팝업스토어, 감성 카페, 한정판 굿즈, 전시회, 라이프스타일] 정보이거나, 여행 시 구매하기 좋은 [프리미엄 로컬 특산품(고급 차, 디저트 등), 백화점 입점 오미야게, 로컬 브랜드의 글로벌 수상 소식]인가? -> [Yes / No]
    - 만약 [Yes]라면 -> status: "Positive"
    - 만약 [No]라면 -> status: "Negative"

    [관심사]
    2030 한국/일본인이 즐길 수 있는 [신규 팝업스토어, 감성 카페, 한정판 굿즈, 전시회, 라이프스타일] 정보이거나, 여행 시 구매하기 좋은 [프리미엄 로컬 특산품(고급 차, 디저트 등), 백화점 입점 오미야게, 로컬 브랜드의 글로벌 수상 소식]인지 확인하세요.
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
    # TEST:
    test_title = "【登別石水亭】今春限定！海の幸堪能プランのご紹介♪"
    test_scout_text = "登別石水亭でございます。今回ご紹介するのは、今春限定のプラン、「【温泉グルメ】海の幸堪能プラン」です。..."
    
    print("🤖 Scout Agent가 기사를 정밀 분석 중입니다...")
    decision = evaluate_with_scout(test_title, test_scout_text)
    
    print("\n[AI 에이전트 분석 결과]")
    print(f"추출 장소: {decision.get('extracted_location')}")
    print(f"지역 일치: {decision.get('is_kyushu_region')}")
    print(f"최종 상태: {decision.get('status')}")
    print(f"추론 과정: {decision.get('reasoning_process')}")