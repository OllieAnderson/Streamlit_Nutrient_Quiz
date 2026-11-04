
# --------------------------------------------------
# QUIZ SETUP
# --------------------------------------------------

if not st.session_state.quiz_started:

    st.subheader("Quiz Setup")

    # GROUP 1

    groups1 = get_groups(questions, "Group_1")

    selected_group1 = st.multiselect(
        "Choose Group 1 categories to INCLUDE",
        groups1,
        default=[],
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
        "Choose Group 2 categories to INCLUDE",
        groups2,
        default=[],
        key=group2_key
    )

    filtered2 = [
        (i, q)
        for i, q in filtered1
        if set(q["Group_2"]) & set(selected_group2)
    ]

    st.write(
        f"Questions included: {len(filtered2)}"
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
