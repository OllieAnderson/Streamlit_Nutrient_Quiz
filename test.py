import streamlit as st
import csv
import random
from pathlib import Path

st.title("Answer Generation Test")

CSV_FILE = Path(__file__).parent / "Database.csv"

with open(CSV_FILE, "r", encoding="utf-8-sig") as file:
    questions = list(csv.DictReader(file))

question = questions[0]

st.subheader(question["Question"])

correct_answer = question["Answer"]

possible_answers = list({
    q["Answer"]
    for q in questions
    if q["Answer"] != correct_answer and q["Answer"]
})

st.write("Correct answer:", correct_answer)
st.write("Available distractors:", len(possible_answers))

if len(possible_answers) >= 3:

    distractors = random.sample(possible_answers, 3)

    options = [correct_answer, *distractors]

    random.shuffle(options)

    selected = st.radio("Choose your answer:", options)

    if st.button("Submit Answer"):
        if selected == correct_answer:
            st.success("Correct!")
        else:
            st.error(f"Incorrect. The answer was {correct_answer}.")

else:
    st.error("Not enough distinct answers.")
