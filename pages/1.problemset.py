import streamlit as st

st.set_page_config(page_title="영화 선호도 분석 및 모델 설계", layout="wide")

st.title("🎬 1. 문제 정의 및 데이터 수집 (기획/AI 설계)")
st.markdown("사용자 행동 데이터를 기반으로 한 장르별 영화 선호도 분석 목적, 데이터셋 구조, 그리고 AI 모델 선정 논리를 정의하는 공간입니다.")

st.divider()

# 1. 문제 정의 섹션
st.header("💡 1. 문제 정의 (Problem Definition)")
col_prob1, col_prob2 = st.columns([2, 1])

with col_prob1:
    st.markdown("""
    * **🚩 해결하려는 비즈니스/사회적 문제**
        * 글로벌 OTT 및 영화 시장의 급성장으로 콘텐츠는 넘쳐나지만, 유저들은 정작 **"오늘 뭐 보지?"**하는 선택 장애(콘텐츠 패러독스)를 겪고 있습니다.
        * 핵심 원인은 영화의 단순 장르 태그뿐만 아니라, 유저의 시청 환경, 러닝타임, 예산 등 복합적인 요인이 선호도와 흥행에 미치는 영향을 정량적으로 분석하지 못했기 때문입니다.
    * **🎯 프로젝트 목표**
        * 영화 데이터와 유저 반응 데이터를 기반으로 **'특정 조건에서 어떤 장르와 영화가 유저에게 높은 선호도(평점/흥행)를 얻는지'**를 데이터로 명확히 시각화합니다.
        * 이를 통해 정교한 맞춤형 콘텐츠 추천 모델과 흥행 예측 파이프라인의 기초 시스템을 구축합니다.
    """)
with col_prob2:
    st.metric(label="OTT 유저 평균 콘텐츠 탐색 시간", value="18.2분 ⏳")
    st.metric(label="개인화 추천 콘텐츠 시청 비율", value="75.4%")

st.divider()

# 2. 데이터 수집 배경 섹션
st.header("📊 2. 데이터 수집 배경 (Data Collection)")
st.markdown("""
* **🗂️ 사용 데이터셋:** Kaggle 제공 **'Movie Preferences & BoxOffice'** 트렌드 데이터셋 (가상/실제 영화 메타 및 유저 로그 데이터 기반)
* **🧠 수집 배경:** 영화의 기본 메타정보(예산, 러닝타임, 장르)와 유저들의 행동 데이터(평점, 리뷰 수, 관객 수)가 결합된 데이터입니다. 특정 장르에 대한 유저들의 편향성과 선호 히트맵을 도출하고, 영화 제작 및 추천 알고리즘의 설명력을 증명하기에 최적의 데이터입니다.
""")

# 데이터셋 컬럼 설명 표
st.markdown("### 📋 핵심 데이터셋 컬럼 명세 (Data Schema)")
data_schema = {
    "컬럼명": ["movie_id", "genres", "budget", "runtime", "release_season", "viewers", "rating_avg", "review_count", "box_office_gross", "is_disney_plus"],
    "설명": [
        "각 영화의 고유 ID",
        "영화의 주 장르 (Action, Comedy, Drama, Sci-Fi 등)",
        "영화 제작비 (백만 달러 $)",
        "영화 상영 시간 (러닝타임 / 분 단위)",
        "개봉 계절 (Spring, Summer, Fall, Winter)",
        "총 관객 수 (시청자 수)",
        "유저 평균 평점 (0.0 ~ 10.0)",
        "등록된 유저 리뷰 및 댓글 수",
        "최종 박스오피스 흥행 매출액 (백만 달러 $)",
        "독점 스트리밍 플랫폼(OTT) 선공개 여부 (True/False)"
    ]
}
st.table(data_schema)

st.divider()

# 3. AI 모델 선정 논리 섹션
st.header("🤖 3. 분류/회귀 모델 선정 논리 (Model Selection)")
col_mod1, col_mod2 = st.columns(2)

with col_mod1:
    st.subheader("📈 회귀(Regression) 모델: 흥행 매출 및 평점 예측")
    st.warning("**🎯 목표: 영화의 조건(장르, 예산, 러닝타임 등)에 따른 예상 박스오피스 매출액(box_office_gross) 예측**")
    st.markdown("""
    * **사용 알고리즘:** 선형 회귀(Linear Regression), 랜덤 포레스트 회귀, XGBoost, LightGBM
    * **선정 논리:** * 제작비(`budget`)와 러닝타임(`runtime`) 등의 변수가 실제 흥행과 평점에 미치는 인과관계를 정량적으로 밝혀냅니다.
        * 콘텐츠 제작사나 배급사에게 *"이 장르로 이 정도 예산을 투자하면 예측되는 기대 매출은 **XX만 달러**이다"*라는 데이터 기반의 의사결정 지표를 제시하기 위함입니다.
    """)

with col_mod2:
    st.subheader("🎯 분류(Classification) 모델: 유저 킬러콘텐츠(선호작) 판별")
    st.info("**🎯 목표: 유저의 행동 패턴과 평점을 기반으로 해당 영화가 '대중적 선호작(히트작)'이 될지 여부 분류**")
    st.markdown("""
    * **사용 알고리즘:** 로지스틱 회귀, 서포트 벡터 머신(SVM), 랜덤 포레스트 분류기
    * **선정 논리:** * 평균 평점(`rating_avg`)과 리뷰 수(`review_count`)를 조합하여 대중이 열광하는 '선호작(1) / 비선호작(0)'을 정의하는 파생변수 전처리를 선행합니다.
        * 의사결정나무(Decision Tree) 등을 통해 **어떤 조건 조합(예: 여름 개봉 + 액션 장르 + 120분 미만)이 선호작 유행을 유발하는지 설명력(XAI)**을 갖추기 위해 선정했습니다.
    """)

st.divider()

# 선생님 피드백 반영 섹션
st.header("🎯 4. 변수 정의 및 인공지능 모델 유형 확정")

col_var1, col_var2 = st.columns(2)

with col_var1:
    st.subheader("📊 변수 정의 (Variables Definition)")
    st.markdown("""
    선생님 피드백을 반영하여, 우리가 사용할 영화 트렌드 데이터셋의 특성에 맞게 독립변수와 종속변수를 아래와 같이 정의합니다.
    
    * **🧪 독립변수 (Input Features / 원인이 되는 변수)**
        * `genres` (영화 장르)
        * `budget` (제작비)
        * `runtime` (러닝타임)
        * `release_season` (개봉 계절)
        * `is_disney_plus` (플랫폼 독점 여부)
        * *※ 이 변수들을 AI 모델에 입력값으로 주입합니다.*
        
    * **🎯 종속변수 (Target Variable / 결과가 되는 예측 대상)**
        * **[회귀용]** `box_office_gross` (예상 박스오피스 매출액) -> 수치 예측
        * **[분류용]** `is_hit_movie` (평점과 관객 수를 조합해 자체 라벨링한 '대중 선호 히트작 여부': 0 또는 1) -> 범주 예측
    """)

with col_var2:
    st.subheader("🧠 최종 선택한 인공지능 모델 유형")
    st.markdown("""
    본 프로젝트는 콘텐츠 비즈니스 시장에 다각적인 데이터 인사이트를 주기 위해 **[회귀]와 [분류] 모델을 모두 결합한 하이브리드 형태**를 선택했습니다.
    
    1. **회귀(Regression) 모델 선택 이유**
        * **목표:** 독립변수(`budget`, `runtime` 등)를 기반으로 종속변수인 **'예상 흥행 매출($)'**이라는 연속된 숫자를 정확히 예측합니다.
        * **이유:** 영화 기획자들에게 투자 대비 수익률(ROI)을 정량적 수치로 미리 시뮬레이션해 주기 위함입니다.
        
    2. **분류(Classification) 모델 선택 이유**
        * **목표:** 영화 평점과 버즈량을 분석하여 **'비선호(0) / 대중 선호작(1)'**이라는 명확한 그룹(범주)으로 나눕니다.
        * **이유:** 단순 매출액을 넘어, 유저의 취향 저격 성능을 판별하여 **OTT 메인 화면의 추천 알고리즘 큐레이션 시스템**과 직접 연계하기 위함입니다.
    """)

st.divider()
st.success("📢 [기획/AI 설계자 완료] 본 페이지의 영화 장르 선호도 분석 기획 데이터 및 AI 파이프라인 설계 기준이 확정되었습니다.")
