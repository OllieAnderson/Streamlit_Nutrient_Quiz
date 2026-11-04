import streamlit as st
import csv
from pathlib import Path

st.title("Group 2 Test")

CSV_FILE = Path(__file__).parent / "Database.csv"

with open(CSV_FILE, "r", encoding="utf-8-sig") as file:
    questions = list(csv.DictReader(file))

groups1 = sorted({
    x.strip()
    for q in questions
    for x in q["Group_1"].split(";")
    if x.strip()
})

selected1 = st.multiselect(
    "Group 1",
    groups1,
    default=groups1
)

filtered1 = [
    q for q in questions
    if set(x.strip() for x in q["Group_1"].split(";")) & set(selected1)
]

groups2 = sorted({
    x.strip()
    for q in filtered1
    for x in q["Group_2"].split(";")
    if x.strip()
})

selected2 = st.multiselect(
    "Group 2",
    groups2,
    default=groups2
)

filtered2 = [
    q for q in filtered1
    if set(x.strip() for x in q["Group_2"].split(";")) & set(selected2)
]

st.write(f"Questions selected: {len(filtered2)}")

if st.button("Start Quiz"):
    st.session_state.questions = filtered2
    st.session_state.started = True

if st.session_state.get("started"):
    st.success("Quiz started!")
    st.write(st.session_state.questions[0]["Question"])
