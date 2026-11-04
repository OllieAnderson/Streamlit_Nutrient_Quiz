
import csv
import random
from pathlib import Path

import streamlit as st


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Nutrient Quiz",
    page_icon="🧠",
    layout="centered"
)


# --------------------------------------------------
# FILE LOCATIONS
# --------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
CSV_FILE = SCRIPT_DIR / "Database.csv"


# --------------------------------------------------
# LOAD QUESTIONS
# --------------------------------------------------

@st.cache_data
def load_questions():

    required_columns = {
        "Answer",
        "Question",
        "Group_1",
        "Group_2",
        "Notes"
    }

    with open(
        CSV_FILE,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                "Database.csv is missing required columns."
            )

        questions = []

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


# --------------------------------------------------
# GROUP FUNCTIONS
# --------------------------------------------------

def get_groups(questions, column):

    groups = {
        group
        for question in questions
        for group in question[column]
    }

    return sorted(groups, key=str.lower)


# --------------------------------------------------
# RESET QUIZ
# --------------------------------------------------

def reset_quiz():

    st.session_state.quiz_started = False
    st.session_state.completed = False

    st.session_state.remaining = []
    st.session_state.result = None
    st.session_state.options = None

    st.session_state.correct_count = 0
    st.session_state.attempts = 0
    st.session_state.total_questions = 0


# --------------------------------------------------
# INITIALISE SESSION STATE
# --------------------------------------------------

defaults = {
    "quiz_started": False,
    "completed": False,
    "remaining": [],
    "result": None,
    "options": None,
    "correct_count": 0,
    "attempts": 0,
    "total_questions": 0
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# --------------------------------------------------
# LOAD DATABASE
# --------------------------------------------------

st.title("🧠 Nutrient Quiz")

try:

    questions = load_questions()

except Exception as error:

    st.error(f"Unable to load database: {error}")
    st.stop()


if not questions:

    st.error("No questions found in Database.csv.")
    st.stop()


# --------------------------------------------------
# QUIZ SETUP
# --------------------------------------------------

if not st.session_state.quiz_started:

    st.subheader("Quiz Setup")

    # GROUP 1

    groups1 = get_groups(questions, "Group_1")

    selected_group1 = st.multiselect(
        "Choose Group 1",
        groups1,
        default=groups1,
        key="group1_selection"
    )

    filtered1 = [
        (i, q)
        for i, q in enumerate(questions)
        if set(q["Group_1"]) & set(selected_group1)
    ]

    # GROUP 2

    groups2 = get_groups(
        [q for i, q in filtered1],
        "Group_2"
    )

    group2_key = "group2_" + str(tuple(selected_group1))

    selected_group2 = st.multiselect(
        "Choose Group 2",
        groups2,
        default=groups2,
        key=group2_key
    )

    filtered2 = [
        (i, q)
        for i, q in filtered1
        if set(q["Group_2"]) & set(selected_group2)
    ]

    st.write(
        f"Questions selected: {len(filtered2)}"
    )

    if len(filtered2) < 4:

        st.warning(
            "Select at least 4 questions to start the quiz."
        )

    if st.button(
        "Start Quiz",
        disabled=len(filtered2) < 4
    ):

        question_indices = [
            i for i, q in filtered2
        ]

        random.shuffle(question_indices)

        st.session_state.remaining = question_indices
        st.session_state.total_questions = len(question_indices)

        st.session_state.correct_count = 0
        st.session_state.attempts = 0

        st.session_state.result = None
        st.session_state.options = None

        st.session_state.completed = False
        st.session_state.quiz_started = True

        st.rerun()


# --------------------------------------------------
# QUIZ SCREEN
# --------------------------------------------------

else:

    remaining = st.session_state.remaining

    total = st.session_state.total_questions
    correct = st.session_state.correct_count
    attempts = st.session_state.attempts

    # SIDEBAR

    with st.sidebar:

        st.subheader("Quiz Progress")

        st.write(f"Correct answers: {correct}/{total}")

        st.write(f"Attempts: {attempts}")

        if attempts > 0:

            accuracy = (correct / attempts) * 100

            st.write(f"Accuracy: {accuracy:.1f}%")

        st.progress(
            correct / total if total else 0
        )

        if st.button("Restart Quiz"):

            reset_quiz()
            st.rerun()

    # --------------------------------------------------
    # COMPLETION SCREEN
    # --------------------------------------------------

    if st.session_state.completed:

        st.header("Quiz Completed!")

        st.success("You have answered every question correctly.")

        st.write(f"Total questions: {total}")

        st.write(f"Correct answers: {correct}")

        st.write(f"Total attempts: {attempts}")

        if attempts > 0:

            accuracy = (correct / attempts) * 100

            st.write(f"Final accuracy: {accuracy:.1f}%")

        if st.button("Start Again"):

            reset_quiz()
            st.rerun()

    # --------------------------------------------------
    # FEEDBACK SCREEN
    # --------------------------------------------------

    elif st.session_state.result is not None:

        result = st.session_state.result

        st.subheader("Your Answer")

        if result["correct"]:

            st.success("Correct!")

        else:

            st.error("Incorrect!")

        st.write("Question:")
        st.write(result["question"])

        st.write("Correct answer:")
        st.write(f"**{result['answer']}**")

        if not result["correct"]:

            st.write("Your answer:")
            st.write(result["selected"])

        st.write("Group 1:")
        st.write(", ".join(result["group1"]))

        st.write("Group 2:")
        st.write(", ".join(result["group2"]))

        if result["notes"]:

            st.write("Notes:")
            st.write(result["notes"])

        if st.button("Next Question"):

            st.session_state.result = None
            st.session_state.options = None

            if not st.session_state.remaining:

                st.session_state.completed = True

            st.rerun()

    # --------------------------------------------------
    # QUESTION SCREEN
    # --------------------------------------------------

    else:

        current_idx = remaining[0]

        question = questions[current_idx]

        # GENERATE ANSWER OPTIONS

        if st.session_state.options is None:

            correct_answer = question["Answer"]

            possible_answers = list({
                q["Answer"]
                for q in questions
                if q["Answer"]
                and q["Answer"] != correct_answer
            })

            if len(possible_answers) < 3:

                st.error(
                    "Not enough distinct answers to generate "
                    "three incorrect options."
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

        st.subheader(
            f"Question {total - len(remaining) + 1} of {total}"
        )

        st.progress(
            correct / total if total else 0
        )

        st.markdown(f"### {question['Question']}")

        # ANSWER FORM

        with st.form(
            key=f"answer_form_{attempts}_{current_idx}"
        ):

            selected_answer = st.radio(
                "Choose your answer:",
                st.session_state.options
            )

            submitted = st.form_submit_button(
                "Submit Answer"
            )

        # CHECK ANSWER

        if submitted:

            is_correct = (
                selected_answer == question["Answer"]
            )

            st.session_state.attempts += 1

            if is_correct:

                st.session_state.correct_count += 1

                # Remove correctly answered question.
                st.session_state.remaining.pop(0)

            else:

                # Move incorrectly answered question
                # to the end of the queue.

                idx = st.session_state.remaining.pop(0)

                st.session_state.remaining.append(idx)

            # SAVE FEEDBACK

            st.session_state.result = {

                "correct": is_correct,

                "question": question["Question"],

                "answer": question["Answer"],

                "selected": selected_answer,

                "group1": question["Group_1"],

                "group2": question["Group_2"],

                "notes": question["Notes"]
            }

            st.rerun()
