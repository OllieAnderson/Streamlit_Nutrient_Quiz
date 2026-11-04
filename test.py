import streamlit as st
import csv
from pathlib import Path

st.title("Quiz Test")

CSV_FILE = Path(__file__).parent / "Database.csv"

with open(CSV_FILE, "r", encoding="utf-8-sig") as file:
    questions = list(csv.DictReader(file))

st.write(f"Loaded {len(questions)} questions")

groups = sorted({
    group.strip()
    for q in questions
    for group in q["Group_1"].split(";")
    if group.strip()
})

selected = st.multiselect(
    "Choose Group 1",
    groups,
    default=groups
)

st.write("Selected groups:", selected)

filtered = [
    q for q in questions
    if set(q["Group_1"].split(";")) & set(selected)
]

st.write(f"Questions selected: {len(filtered)}")
