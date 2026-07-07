import streamlit as st
import pandas as pd

st.set_page_config(page_title="문제정의 및 데이터수집", layout="wide")

DATA_FILE = "장르별_온라인이용건수_20260707_023139.xlsx"

@st.cache_data
def load_data():
    raw = pd.read_excel(DATA_FILE, header=None, dtype=str)
    header_idx = 0
    for i in range(len(raw)):
        row = [str(x).strip() for x in raw.iloc[i].tolist()]
        if "장르" in row and any("온라인" in x and "이용" in x for x in row):
            header_idx = i
            break
    headers = [str(x).strip() for x in raw.iloc[header_idx].tolist()]
    use_cols = [i for i, h in enumerate(headers) if h != "nan" and h != ""]
    df = raw.iloc[header_idx + 1:, use_cols].copy()
    df.columns = [headers[i] for i in use_cols]
    return df.dropna(how="all")

st.title("1. 문제 정의 및 데이터 수집")
st.markdown(
    """
    본 프로젝트의 주제는 장르별 온라인 이용건수 기반 영화 선호도 분석입니다.
    영화나 영상 콘텐츠가 온라인에서 어떤 장르 중심으로 많이 이용되는지 확인하는 것이 목적입니다.
    """
)

st.header("문제 정의")
st.markdown(
    """
    온라인으로 영화를 이용하는 사람이 많아지면서 어떤 장르가 많이 소비되는지 확인하는 것이 중요해졌습니다.
    단순히 작품 수가 많은 장르가 많이 이용되는지, 아니면 작품 수는 적어도 이용이 집중되는 장르가 있는지 비교해 보려고 합니다.

    핵심 질문은 다음과 같습니다.

    - 온라인 이용건수가 가장 많은 장르는 무엇인가?
    - 작품 수와 온라인 이용건수는 비슷한 흐름을 보이는가?
    - 작품 한 편당 이용건수가 높은 장르는 무엇인가?
    - 데이터를 이용해 선호도가 높은 장르와 낮은 장르를 구분할 수 있는가?
    """
)

st.header("데이터 수집")
st.markdown(
    f"""
    사용한 데이터 파일은 `{DATA_FILE}`입니다.
    이 파일에는 장르별 작품편수, 온라인 이용건수, 점유율 정보가 들어 있습니다.
    본 프로젝트에서는 이 데이터를 이용하여 장르별 선호도를 분석합니다.
    """
)

try:
    df = load_data()
except Exception as e:
    st.error("엑셀 파일을 불러오지 못했습니다.")
    st.write(e)
    st.stop()

st.subheader("원본 데이터 미리보기")
st.dataframe(df.head(10), use_container_width=True, hide_index=True)

st.subheader("데이터 컬럼 설명")
info = pd.DataFrame({
    "컬럼명": ["순위", "장르", "작품편수", "온라인 이용건수", "점유율(%)"],
    "설명": [
        "온라인 이용건수 기준 순위",
        "영화 또는 영상 콘텐츠의 장르",
        "해당 장르에 포함된 작품 수",
        "해당 장르의 온라인 이용 횟수",
        "전체 온라인 이용건수에서 차지하는 비율",
    ]
})
st.table(info)

st.header("분석 방향")
st.markdown(
    """
    이 프로젝트에서는 온라인 이용건수를 선호도를 판단하는 기준으로 사용했습니다.
    이용건수가 많다는 것은 그 장르의 콘텐츠가 온라인에서 많이 소비되었다는 뜻이므로,
    수행평가에서는 이를 장르 선호도의 근거로 해석했습니다.
    """
)
