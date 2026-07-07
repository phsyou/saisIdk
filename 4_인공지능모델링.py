import streamlit as st
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix

st.set_page_config(page_title="인공지능 모델링", layout="wide")

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

    df = df.dropna(subset=["장르", "작품편수", "온라인이용건수", "점유율"])
    df["작품당이용건수"] = df["온라인이용건수"] / df["작품편수"]
    df["선호등급"] = df["온라인이용건수"].apply(
        lambda x: "높음" if x >= df["온라인이용건수"].median() else "낮음"
    )
    return df.sort_values("온라인이용건수", ascending=False).reset_index(drop=True)

st.title("4. 인공지능 모델링")
st.markdown(
    """
    전처리한 데이터를 이용하여 선호등급을 분류하는 간단한 인공지능 모델을 만들어 봅니다.
    여기서는 이해하기 쉬운 의사결정나무 모델을 사용했습니다.
    """
)

try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러올 수 없습니다.")
    st.write(e)
    st.stop()

st.header("모델링 목표")
st.markdown(
    """
    목표는 장르가 `높음` 선호등급인지 `낮음` 선호등급인지 분류하는 것입니다.
    선호등급은 온라인 이용건수가 전체 장르의 중앙값 이상이면 높음, 중앙값보다 낮으면 낮음으로 정했습니다.
    """
)

features = ["작품편수", "점유율", "작품당이용건수"]
target = "선호등급"

model_df = df[features + [target, "장르", "온라인이용건수"]].dropna()
X = model_df[features]
y = model_df[target]

if len(model_df) < 6 or y.nunique() < 2:
    st.warning("모델 학습에 사용할 데이터가 부족합니다.")
    st.stop()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X_train, y_train)
pred = model.predict(X_test)
acc = accuracy_score(y_test, pred)

col1, col2, col3 = st.columns(3)
col1.metric("학습 데이터", f"{len(X_train)}개")
col2.metric("테스트 데이터", f"{len(X_test)}개")
col3.metric("정확도", f"{acc * 100:.1f}%")

st.header("모델 입력값")
st.dataframe(model_df[["장르", "작품편수", "점유율", "작품당이용건수", "선호등급"]], use_container_width=True, hide_index=True)

st.header("예측 결과")
result = X_test.copy()
result["실제값"] = y_test.values
result["예측값"] = pred
result["정답여부"] = result["실제값"] == result["예측값"]
st.dataframe(result, use_container_width=True, hide_index=True)

st.header("혼동 행렬")
labels = sorted(y.unique())
cm = confusion_matrix(y_test, pred, labels=labels)
cm_df = pd.DataFrame(cm, index=["실제 " + x for x in labels], columns=["예측 " + x for x in labels])
st.table(cm_df)

st.header("직접 예측해 보기")
work_count = st.slider("작품편수", 1, int(df["작품편수"].max()) + 100, int(df["작품편수"].median()))
share = st.slider("점유율", 0.0, float(df["점유율"].max()) + 5.0, float(df["점유율"].median()))
per_work = st.slider("작품당 이용건수", 0.0, float(df["작품당이용건수"].max()) + 1000.0, float(df["작품당이용건수"].median()))

input_data = pd.DataFrame([{
    "작품편수": work_count,
    "점유율": share,
    "작품당이용건수": per_work,
}])
user_pred = model.predict(input_data)[0]
st.success(f"예측된 선호등급은 {user_pred}입니다.")

st.header("모델 해석")
st.markdown(
    """
    이 모델은 데이터 수가 많지 않기 때문에 실제 서비스에 사용할 정도의 모델은 아닙니다.
    하지만 수행평가에서는 데이터 전처리, 학습 데이터와 테스트 데이터 분리, 모델 학습, 정확도 확인 과정을 보여주는 예시로 사용할 수 있습니다.
    """
)
