
import csv
import random
import streamlit as st
from pathlib import Path


# --------------------------------
# CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="My Quiz App",
    page_icon="🧠",
    layout="centered"
)

SCRIPT_DIR = Path(__file__).resolve().parent
CSV_FILE = SCRIPT_DIR / "Database.csv"


# --------------------------------
# LOAD DATABASE
# --------------------------------

@st.cache_data
def load_questions():

    questions = []

    with open(
        CSV_FILE,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        required_columns = {
            "Answer",
            "Question",
            "Group_1",
            "Group_2",
            "Notes"
        }

        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                f"CSV must contain: {required_columns}"
            )

        for row in reader:

            questions.append({
                "Answer": row["Answer"].strip(),
                "Question": row["Question"].strip(),
                "Group_1": [
                    x.strip()
                    for x in row["Group_1"].split(";")
                    if x.strip()
                ],
                "Group_2": [
                    x.strip()
                    for x in row["Group_2"].split(";")
                    if x.strip()
                ],
                "Notes": row["Notes"].strip()
            })

    return questions


# --------------------------------
# HELPER FUNCTIONS
# --------------------------------

def get_groups(questions, column):

    groups = set()

    for question in questions:
        groups.update(question[column])

    return sorted(groups, key=str.lower)


def reset_quiz():

    st.session_state.quiz_started = False
    st.session_state.completed = False
    st.session_state.remaining = []
    st.session_state.result = None
    st.session_state.current_idx = None
    st.session_state.options = None
    st.session_state.correct_count = 0
    st.session_state.attempts = 0


# --------------------------------
# SESSION STATE
# --------------------------------

defaults = {
    "quiz_started": False,
    "completed": False,
    "remaining": [],
    "result": None,
    "current_idx": None,
    "options": None,
    "correct_count": 0,
    "attempts": 0
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# --------------------------------
# LOAD QUESTIONS
# --------------------------------

st.title("🧠 My Quiz App")

try:
    questions = load_questions()

except Exception as error:
    st.error(f"Could not load Database.csv: {error}")
    st.stop()


if not questions:
    st.error("Your database contains no questions.")
    st.stop()


# =================================
# SETUP SCREEN
# =================================

if not st.session_state.quiz_started:

    st.header("Choose your questions")

    # GROUP 1

    group1_options = get_groups(
        questions,
        "Group_1"
    )

    selected_group1 = st.multiselect(
        "Group 1",
        group1_options,
        default=group1_options
    )

    # Filter using Group 1

    group1_questions = [

        q for q in questions

        if set(q["Group_1"]) & set(selected_group1)
    ]

    # GROUP 2

    group2_options = get_groups(
        group1_questions,
        "Group_2"
    )

    group2_key = (
        "group2_" +
        str(hash(tuple(selected_group1)))
    )

    selected_group2 = st.multiselect(
        "Group 2",
        group2_options,
        default=group2_options,
        key=group2_key
    )

    # Filter using Group 2

    filtered_questions = [

        q for q in group1_questions

        if set(q["Group_2"]) & set(selected_group2)
    ]

    st.write(
        f"**{len(filtered_questions)} questions selected**"
    )

    st.divider()

    if st.button("Start Quiz", type="primary"):

        if len(filtered_questions) < 4:

            st.error(
                "You need at least 4 questions to start."
            )

        else:

            # Get original database indexes

            selected_indexes = [
                questions.index(q)
                for q in filtered_questions
            ]

            random.shuffle(selected_indexes)

            st.session_state.remaining = selected_indexes

            st.session_state.quiz_started = True
            st.session_state.completed = False
            st.session_state.correct_count = 0
            st.session_state.attempts = 0
            st.session_state.result = None
            st.session_state.current_idx = None
            st.session_state.options = None

            st.rerun()


# =================================
# QUIZ SCREEN
# =================================

elif st.session_state.quiz_started:

    remaining = st.session_state.remaining

    total = len(remaining) + st.session_state.correct_count

    # PROGRESS

    correct = st.session_state.correct_count

    progress = correct / total if total else 0

    st.progress(progress)

    st.write(
        f"**Score:** {correct} / {total}"
    )

    if st.session_state.attempts > 0:

        accuracy = (
            correct / st.session_state.attempts * 100
        )

        st.caption(
            f"Accuracy: {accuracy:.1f}%"
        )

    st.divider()

    # COMPLETION

    if st.session_state.completed:

        st.success("Quiz completed!")

        st.header("Final Results")

        st.metric(
            "Correct answers",
            f"{correct} / {total}"
        )

        accuracy = (
            correct / st.session_state.attempts * 100
            if st.session_state.attempts else 0
        )

        st.metric(
            "Accuracy",
            f"{accuracy:.1f}%"
        )

        if st.button("Start Again"):

            reset_quiz()
            st.rerun()

    # FEEDBACK SCREEN

    elif st.session_state.result is not None:

        result = st.session_state.result

        if result["correct"]:

            st.success("Correct!")

        else:

            st.error("Incorrect!")

        st.write(
            f"**Correct answer:** {result['answer']}"
        )

        st.write(
            f"**Group 1:** {', '.join(result['group1'])}"
        )

        st.write(
            f"**Group 2:** {', '.join(result['group2'])}"
        )

        if result["notes"]:

            st.info(result["notes"])

        if st.button("Next Question", type="primary"):

            st.session_state.result = None
            st.session_state.current_idx = None
            st.session_state.options = None

            if not st.session_state.remaining:
                st.session_state.completed = True

            st.rerun()

    # QUESTION SCREEN

    else:

        # Select current question

        if st.session_state.current_idx is None:

            st.session_state.current_idx = remaining[0]

        idx = st.session_state.current_idx

        question = questions[idx]

        # Generate four answer options once

        if st.session_state.options is None:

            correct_answer = question["Answer"]

            possible_answers = list({

                q["Answer"]

                for q in questions
                if q["Answer"] != correct_answer
                and q["Answer"]
            })

            if len(possible_answers) < 3:

                st.error(
                    "Not enough distinct answers "
                    "in your database to create four options."
                )

                st.stop()

            distractors = random.sample(
                possible_answers,
                3
            )

            options = [
                correct_answer,
                *distractors
            ]

            random.shuffle(options)

            st.session_state.options = options

        # DISPLAY QUESTION

        st.subheader(question["Question"])

        with st.form(
            key=f"question_{idx}_{st.session_state.attempts}"
        ):

            selected_answer = st.radio(
                "Choose your answer:",
                st.session_state.options
            )

            submitted = st.form_submit_button(
                "Submit Answer",
                type="primary"
            )

        # CHECK ANSWER

        if submitted:

            is_correct = (
                selected_answer == question["Answer"]
            )

            st.session_state.attempts += 1

            if is_correct:

                st.session_state.correct_count += 1

                # Remove correctly answered question

                st.session_state.remaining.pop(0)

            else:

                # Move incorrectly answered question
                # to the end of the queue

                st.session_state.remaining.pop(0)

                st.session_state.remaining.append(idx)

            st.session_state.result = {

                "correct": is_correct,
                "answer": question["Answer"],
                "group1": question["Group_1"],
                "group2": question["Group_2"],
                "notes": question["Notes"]

            }

            st.rerun()


# --------------------------------
# SIDEBAR
# --------------------------------

with st.sidebar:

    st.header("Quiz Controls")

    if st.session_state.quiz_started:

        if st.button("Restart Quiz"):

            reset_quiz()
            st.rerun()

    st.caption("Powered by Streamlit")
