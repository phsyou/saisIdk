import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="데이터 시각화", layout="wide")

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
    df = df.rename(columns={"온라인 이용건수": "온라인이용건수", "점유율(%)": "점유율"})
    df = df.dropna(how="all")
    df = df[~df["장르"].astype(str).str.contains("합계", na=False)]
    df = df[~df["장르"].astype(str).str.contains("성인물", na=False)]

    for col in ["작품편수", "온라인이용건수", "점유율"]:
        df[col] = df[col].astype(str).str.replace(",", "", regex=False).str.replace("%", "", regex=False)
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["장르", "작품편수", "온라인이용건수"])
    df["이용점유율"] = df["온라인이용건수"] / df["온라인이용건수"].sum() * 100
    df["작품당이용건수"] = df["온라인이용건수"] / df["작품편수"]
    df["선호등급"] = df["온라인이용건수"].apply(
        lambda x: "높음" if x >= df["온라인이용건수"].median() else "낮음"
    )
    return df.sort_values("온라인이용건수", ascending=False).reset_index(drop=True)

st.title("3. 데이터 시각화")
st.markdown("전처리한 데이터를 그래프로 나타내어 장르별 이용 경향을 비교합니다.")

try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러올 수 없습니다.")
    st.write(e)
    st.stop()

st.header("장르별 온라인 이용건수")
fig1 = px.bar(
    df.sort_values("온라인이용건수", ascending=True),
    x="온라인이용건수",
    y="장르",
    orientation="h",
    text="온라인이용건수",
    title="장르별 온라인 이용건수",
)
fig1.update_traces(texttemplate="%{text:,}", textposition="outside")
st.plotly_chart(fig1, use_container_width=True)

st.header("장르별 이용점유율")
fig2 = px.pie(
    df.head(8),
    names="장르",
    values="이용점유율",
    title="상위 8개 장르의 이용점유율",
)
st.plotly_chart(fig2, use_container_width=True)

st.header("작품편수와 온라인 이용건수 비교")
compare = df[["장르", "작품편수", "온라인이용건수"]].head(10)
fig3 = px.bar(
    compare,
    x="장르",
    y=["작품편수", "온라인이용건수"],
    barmode="group",
    title="상위 10개 장르의 작품편수와 온라인 이용건수 비교",
)
st.plotly_chart(fig3, use_container_width=True)

st.header("작품당 이용건수")
fig4 = px.bar(
    df.sort_values("작품당이용건수", ascending=True),
    x="작품당이용건수",
    y="장르",
    orientation="h",
    text="작품당이용건수",
    title="작품 한 편당 온라인 이용건수",
)
fig4.update_traces(texttemplate="%{text:,.1f}", textposition="outside")
st.plotly_chart(fig4, use_container_width=True)

st.header("그래프 해석")
top_genre = df.iloc[0]["장르"]
top_count = int(df.iloc[0]["온라인이용건수"])
per_work_top = df.sort_values("작품당이용건수", ascending=False).iloc[0]["장르"]
st.markdown(
    f"""
    온라인 이용건수가 가장 많은 장르는 `{top_genre}`이며, 이용건수는 `{top_count:,}`건입니다.
    작품당 이용건수가 가장 높은 장르는 `{per_work_top}`입니다.
    따라서 단순히 작품 수가 많은 장르만 많이 이용된다고 보기보다는,
    장르별 이용 집중도도 함께 확인해야 합니다.
    """
)
