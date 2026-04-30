import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="PhonoTrack", layout="wide")

st.title("🗣️ PhonoTrack")
st.write("언어치료사를 위한 아동 발음 오류 분석 프로그램입니다.")

os.makedirs("data", exist_ok=True)

def analyze_pronunciation(target, actual):
    if not target or not actual:
        return "입력 오류", "목표 단어와 아동 발음을 모두 입력하세요."

    if target == actual:
        return "정반응", "오류 없음"

    if len(target) == len(actual):
        return "오반응", "대치 오류"

    if len(target) > len(actual):
        return "오반응", "생략 오류"

    if len(target) < len(actual):
        return "오반응", "첨가 오류"

    return "오반응", "복합 오류"


st.sidebar.header("아동 정보")
child_name = st.sidebar.text_input("아동 이름")
age = st.sidebar.text_input("생활연령")
session_date = st.sidebar.date_input("검사일")

st.subheader("발음 자료 입력")

st.write("예시: 목표 단어 = 라디오 / 아동 발음 = 나디오")

target_words = st.text_area(
    "목표 단어를 한 줄에 하나씩 입력하세요",
    "라디오\n사탕\n바나나\n학교"
)

actual_words = st.text_area(
    "아동 발음을 한 줄에 하나씩 입력하세요",
    "나디오\n따탕\n바나나\n하교"
)

if st.button("분석하기"):
    targets = [x.strip() for x in target_words.split("\n") if x.strip()]
    actuals = [x.strip() for x in actual_words.split("\n") if x.strip()]

    if len(targets) != len(actuals):
        st.error("목표 단어 수와 아동 발음 수가 같아야 합니다.")
    else:
        results = []

        for target, actual in zip(targets, actuals):
            status, error_type = analyze_pronunciation(target, actual)

            results.append({
                "목표 단어": target,
                "아동 발음": actual,
                "반응": status,
                "오류 유형": error_type
            })

        df = pd.DataFrame(results)

        total = len(df)
        correct = len(df[df["반응"] == "정반응"])
        incorrect = total - correct
        accuracy = round((correct / total) * 100, 1) if total > 0 else 0

        st.subheader("분석 결과")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("총 단어 수", total)
        col2.metric("정반응", correct)
        col3.metric("오반응", incorrect)
        col4.metric("정확도", f"{accuracy}%")

        st.subheader("상세 분석표")
        st.dataframe(df)

        st.subheader("오류 유형 통계")
        error_counts = df["오류 유형"].value_counts()
        st.bar_chart(error_counts)

        st.subheader("치료 목표 추천")
        if accuracy >= 80:
            st.success("발음 정확도가 높습니다. 문장 수준과 대화 수준으로 일반화하는 활동을 추천합니다.")
        elif accuracy >= 50:
            st.warning("일부 발음 오류가 나타납니다. 자주 틀리는 음소를 중심으로 단어 수준 반복 연습을 추천합니다.")
        else:
            st.error("발음 정확도가 낮은 편입니다. 음소 인식, 음절, 단어 순서로 단계적인 조음 훈련을 추천합니다.")

        file_path = "data/phonotrack_results.csv"
        df.to_csv(file_path, index=False, encoding="utf-8-sig")

        st.success(f"결과가 저장되었습니다: {file_path}")

        csv = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="CSV 파일 다운로드",
            data=csv,
            file_name="phonotrack_results.csv",
            mime="text/csv"
        )