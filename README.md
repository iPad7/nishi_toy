# ⚡️ Nishi.ai: Fukuoka Trend Scout (Comprehensive Spike)

> **"Fine Curation of Fukuoka Lifestyle"**
> 
> PR TIMES의 일본 뉴스 홍수 속에서 후쿠오카의 '진짜' 트렌드만 건져 올리는 에이전틱 파이프라인 PoC 프로젝트입니다. 본 단계는 시스템 전체 구축 전, 기술적 난제들을 조각 단위로 검증(Spike)하는 것을 목표로 합니다.

---

## 🎯 Spike Goals (검증 과제)

이번 스파이크를 통해 다음 5가지 핵심 기능의 기술적 실현 가능성을 확정합니다.

### 1. Data Sanitization (세척)
- [ ] **Regex Power**: 일본어 유니코드 및 전각 문자 사이의 화이트스페이스 노이즈를 정규표현식으로 완벽 제거.
- [ ] **Encoding Integrity**: iPad Juno 및 로컬 환경에서 일본어 텍스트가 깨지지 않고 처리되는지 `repr()` 기반 검증.

### 2. Intelligent Scraper & Visual Extraction (추출)
- [ ] **Smart Slicing**: 본문 500자(Scout용)와 전체 텍스트(Deep용)를 한 번의 I/O로 분리 저장.
- [ ] **Image Hunter**: 보도자료 내 메인 이미지 URL을 정확히 추출하여 썸네일 데이터 확보.

### 3. Dual-Agent Routing (판단)
- [ ] **Scout Agent**: 500자만 읽고 `positive / negative / more_info`를 판별하여 토큰 비용 80% 절감.
- [ ] **Deep Agent**: `more_info` 시 버퍼에서 전체 본문을 호출하여 최종 적합성 판정.
- [ ] **Auto-Tagging**: AI가 '패션/미식/팝업/전시' 등의 카테고리를 자동 분류하는 기능 검증.

### 4. Creative Synthesis (각색)
- [ ] **Trendy Paraphrasing**: 일본어 원문을 2030 감성의 한국어 톤앤매너로 각색.
- [ ] **Structured Output**: AI가 JSON 형식을 지켜 초안을 작성하는지 Pydantic으로 데이터 규격 검증.

### 5. Persistence & Governance (저장 및 관리)
- [ ] **Idempotency**: `prtimes_url` UNIQUE 제약을 통한 중복 데이터 입수 원천 차단.
- [ ] **Status Life-cycle**: `DRAFT` 상태로 입수된 데이터가 관리자 명령으로 상태가 변경되는지 확인.

---

## 🏛️ System Architecture

[Image: Ingestion -> Pre-processing -> Agentic Routing -> Curation -> Persistence]

1. **SitemapScanner**: XML 파싱 및 정규식 세척 (Cleaner).
2. **SmartBuffer**: 본문/이미지 추출 및 메모리 캐싱 (Extractor).
3. **AgenticEngine**: 2단계 판단 및 한국어 힙스터 톤앤매너 각색 (Brain).
4. **Supabase**: 데이터 적재 및 중복 방지 (Warehouse).

---

## 🛠️ Tech Stack

- **Language**: Python 3.10+ (iPad Juno / Desktop)
- **AI Engine**: Upstage Solar (or OpenAI GPT-4o-mini)
- **Database**: Supabase (PostgreSQL)
- **Key Libraries**: `BeautifulSoup4`, `re`, `requests`, `pydantic`, `httpx` (async)

---

## 📝 Roadmap (The Spike Sequence)

### Phase 1: Ingestion Spike
- [ ] XML에서 `news:` 네임스페이스 기반 태그 추출 함수 완성
- [ ] 제목/키워드 내 일본어 텍스트 정상 출력 여부 검증

### Phase 2: Intelligence Spike
- [ ] 본문 앞 500자 추출 및 이미지 URL 확보 테스트
- [ ] **[핵심]** 2단계 라우팅 프롬프트 실행 및 `more_info` 트리거 정확도 확인
- [ ] 한국어 각색 초안의 '감도' 체크

### Phase 3: Persistence Spike
- [ ] Supabase 프로젝트 생성 및 `posts` 테이블 스키마 설정
- [ ] 중복 URL 인서트 시 `IntegrityError` 발생 여부 확인

---
**Build by Jaebeom Lee**
