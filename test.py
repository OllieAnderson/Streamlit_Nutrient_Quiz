import streamlit as st
import csv
from pathlib import Path

st.title("Database Test")

CSV_FILE = Path(__file__).parent / "Database.csv"

st.write("Looking for database...")

if CSV_FILE.exists():
    st.success("Database.csv found!")

    with open(CSV_FILE, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    st.write("Number of questions:", len(rows))
    st.write("Column headers:", reader.fieldnames)

else:
    st.error("Database.csv not found!")
