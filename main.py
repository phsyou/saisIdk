import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="장르별 온라인 이용건수 분석",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
    df = df.dropna(how="all")

    rename = {
        "온라인 이용건수": "온라인이용건수",
        "점유율(%)": "점유율",
    }
    df = df.rename(columns=rename)

    for col in ["작품편수", "온라인이용건수", "점유율"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("%", "", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["장르", "작품편수", "온라인이용건수"])
    df = df[~df["장르"].astype(str).str.contains("합계", na=False)]
    df = df[~df["장르"].astype(str).str.contains("성인물", na=False)]

    df["작품당이용건수"] = df["온라인이용건수"] / df["작품편수"]
    df["이용점유율"] = df["온라인이용건수"] / df["온라인이용건수"].sum() * 100
    df["선호등급"] = df["온라인이용건수"].apply(
        lambda x: "높음" if x >= df["온라인이용건수"].median() else "낮음"
    )
    return df.sort_values("온라인이용건수", ascending=False).reset_index(drop=True)

st.title("장르별 온라인 이용건수 기반 영화 선호도 분석")
st.markdown(
    """
    이 프로젝트는 엑셀에 정리된 장르별 온라인 이용건수를 이용하여
    어떤 장르가 많이 이용되었는지 분석하는 Streamlit 데이터 분석 프로젝트입니다.

    왼쪽 메뉴에서 문제 정의, 데이터 전처리, 데이터 시각화, 인공지능 모델링 과정을 차례대로 확인할 수 있습니다.
    """
)

try:
    df = load_data()
except Exception as e:
    st.error("데이터 파일을 불러올 수 없습니다.")
    st.write(e)
    st.stop()

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("문제 정의")
    st.write("장르별 온라인 이용건수를 통해 사람들이 많이 이용한 영화 장르를 확인합니다.")

with col2:
    st.subheader("데이터 전처리")
    st.write("엑셀 파일에서 필요한 행과 열을 가져오고, 숫자 데이터를 분석 가능한 형태로 바꿉니다.")

with col3:
    st.subheader("모델링")
    st.write("간단한 의사결정나무 모델을 이용해 장르의 선호 등급을 분류해 봅니다.")

st.divider()

st.subheader("전체 데이터 요약")

m1, m2, m3, m4 = st.columns(4)
m1.metric("분석 장르 수", f"{len(df)}개")
m2.metric("총 작품편수", f"{int(df['작품편수'].sum()):,}편")
m3.metric("총 온라인 이용건수", f"{int(df['온라인이용건수'].sum()):,}건")
m4.metric("1위 장르", df.iloc[0]["장르"])

st.subheader("상위 5개 장르")
st.dataframe(
    df[["장르", "작품편수", "온라인이용건수", "이용점유율", "작품당이용건수"]].head(5),
    use_container_width=True,
    hide_index=True,
)

st.subheader("실행 방법")
st.code("pip install -r requirements.txt\nstreamlit run main.py")
