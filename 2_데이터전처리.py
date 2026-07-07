import streamlit as st
import pandas as pd

st.set_page_config(page_title="데이터 전처리", layout="wide")

DATA_FILE = "장르별_온라인이용건수_20260707_023139.xlsx"

@st.cache_data
def load_raw_data():
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

@st.cache_data
def clean_data(raw_df):
    df = raw_df.copy()
    df = df.rename(columns={"온라인 이용건수": "온라인이용건수", "점유율(%)": "점유율"})
    df = df.dropna(how="all")
    df = df[~df["장르"].astype(str).str.contains("합계", na=False)]
    df = df[~df["장르"].astype(str).str.contains("성인물", na=False)]

    for col in ["작품편수", "온라인이용건수", "점유율"]:
        df[col] = df[col].astype(str).str.replace(",", "", regex=False).str.replace("%", "", regex=False)
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["장르", "작품편수", "온라인이용건수"])
    df["작품편수"] = df["작품편수"].astype(int)
    df["온라인이용건수"] = df["온라인이용건수"].astype(int)

    df["이용점유율"] = df["온라인이용건수"] / df["온라인이용건수"].sum() * 100
    df["작품당이용건수"] = df["온라인이용건수"] / df["작품편수"]
    df["선호등급"] = df["온라인이용건수"].apply(
        lambda x: "높음" if x >= df["온라인이용건수"].median() else "낮음"
    )
    return df.sort_values("온라인이용건수", ascending=False).reset_index(drop=True)

st.title("2. 데이터 전처리")
st.markdown(
    """
    원본 엑셀 파일을 분석하기 쉬운 형태로 정리합니다.
    문자열로 들어 있는 숫자를 정수형으로 바꾸고, 분석에 사용하지 않을 행을 제거합니다.
    """
)

try:
    raw_df = load_raw_data()
    df = clean_data(raw_df)
except Exception as e:
    st.error("전처리를 진행할 수 없습니다.")
    st.write(e)
    st.stop()

st.header("전처리 전 데이터")
st.dataframe(raw_df.head(10), use_container_width=True, hide_index=True)

st.header("전처리 과정")
st.markdown(
    """
    - 엑셀에서 실제 표가 시작되는 행을 찾아 불러왔습니다.
    - 빈 행과 합계 행을 제거했습니다.
    - 수행평가 주제와 맞지 않는 성인물 장르는 제외했습니다.
    - 쉼표가 포함된 숫자를 정수형 데이터로 변환했습니다.
    - 전체 이용건수 기준 점유율을 다시 계산했습니다.
    - 작품당이용건수와 선호등급 컬럼을 새로 만들었습니다.
    """
)

col1, col2, col3 = st.columns(3)
col1.metric("원본 행 수", f"{len(raw_df)}개")
col2.metric("전처리 후 행 수", f"{len(df)}개")
col3.metric("제거된 행 수", f"{len(raw_df) - len(df)}개")

st.header("전처리 후 데이터")
st.dataframe(df, use_container_width=True, hide_index=True)

st.header("새로 만든 컬럼")
st.markdown(
    """
    `이용점유율`은 전체 온라인 이용건수 중 해당 장르가 차지하는 비율입니다.
    `작품당이용건수`는 온라인 이용건수를 작품편수로 나눈 값입니다.
    `선호등급`은 온라인 이용건수가 중앙값 이상이면 높음, 그렇지 않으면 낮음으로 구분했습니다.
    """
)
