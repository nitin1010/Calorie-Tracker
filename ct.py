import streamlit as st
import pandas as pd


def calculate_bmi(weight, height):
    return weight / ((height / 100) ** 2)


def bmi_category(bmi):
    if bmi < 18.5:
        return "Lean"
    elif 18.5 <= bmi < 25:
        return "Healthy"
    else:
        return "Fat"


def exercise_suggestion(negative_calories):
    minutes_running = (-negative_calories // 500) * 10
    return f"{minutes_running} minutes of running"


def food_suggestion(macro, deficit):
    if macro == "Protein":
        return f"Consider eating {deficit / 6:.1f} extra eggs or {deficit / 31:.1f} extra grams of chicken to reach your protein goal."
    elif macro == "Carbs":
        return f"Consider eating {deficit / 30:.1f} extra grams of rice or {deficit / 12:.1f} extra grams of bread to reach your carbohydrate goal."
    elif macro == "Fat":
        return f"Consider eating {deficit / 9:.1f} extra grams of avocado or {deficit / 14:.1f} extra nuts to reach your fat goal."
    else:
        return ""


def main():
    st.title("Calorie Tracker App")

    # Custom CSS for better UI
    st.markdown("""
        <style>
            .main {background-color: #f5f5f5;}
            .stButton > button {background-color: #4CAF50; color: white;}
            .stProgress > div > div {background-color: #4CAF50;}
            .header {color: #4CAF50; font-size: 24px;}
            .subheader {color: #007BFF; font-size: 20px;}
            .bmi-category-lean {color: #FFA500; font-size: 20px;}
            .bmi-category-healthy {color: #32CD32; font-size: 20px;}
            .bmi-category-fat {color: #FF4500; font-size: 20px;}
            .intake-table {margin-top: 20px;}
            .progress-table {margin-top: 20px;}
            .exercise-suggestion {color: #FF4500; font-size: 20px; font-weight: bold;}
            .food-suggestion {color: #007BFF; font-size: 20px; font-weight: bold;}
        </style>
        """, unsafe_allow_html=True)

    st.markdown("<div class='header'>Enter Your Personal Details</div>", unsafe_allow_html=True)
    age = st.number_input("Age", min_value=0, max_value=120, value=25)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    weight = st.number_input("Weight (kg)", min_value=0.0, value=70.0)
    height = st.number_input("Height (cm)", min_value=0.0, value=170.0)

    bmi = calculate_bmi(weight, height)
    category = bmi_category(bmi)
    category_class = {
        "Lean": "bmi-category-lean",
        "Healthy": "bmi-category-healthy",
        "Fat": "bmi-category-fat"
    }[category]

    st.markdown(f"<div class='subheader'>Your BMI is {bmi:.2f}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='{category_class}'>Category: {category}</div>", unsafe_allow_html=True)

    st.markdown("<div class='header'>Set Your Goals</div>", unsafe_allow_html=True)
    goal_calories = st.number_input("Daily Calorie Goal (kcal)", min_value=0, value=2000)
    goal_carbs = st.number_input("Daily Carbohydrates Goal (g)", min_value=0, value=250)
    goal_protein = st.number_input("Daily Protein Goal (g)", min_value=0, value=50)
    goal_fat = st.number_input("Daily Fat Goal (g)", min_value=0, value=70)

    st.markdown("<div class='header'>Track Your Caloric Intake</div>", unsafe_allow_html=True)
    intake_type = st.selectbox("Type", ["Food", "Drink"])
    item = st.text_input(f"{intake_type} Item")
    calories = st.number_input("Calories", min_value=0.0, value=0.0)
    carbs = st.number_input("Carbohydrates (g)", min_value=0.0, value=0.0)
    protein = st.number_input("Protein (g)", min_value=0.0, value=0.0)
    fat = st.number_input("Fat (g)", min_value=0.0, value=0.0)

    if st.button("Add Intake"):
        if 'intake_data' not in st.session_state:
            st.session_state.intake_data = pd.DataFrame(columns=["Type", "Item", "Calories", "Carbs", "Protein", "Fat"])

        new_intake = pd.DataFrame({
            "Type": [intake_type],
            "Item": [item],
            "Calories": [calories],
            "Carbs": [carbs],
            "Protein": [protein],
            "Fat": [fat]
        })

        st.session_state.intake_data = pd.concat([st.session_state.intake_data, new_intake], ignore_index=True)

    if 'intake_data' in st.session_state and not st.session_state.intake_data.empty:
        st.markdown("<div class='subheader'>Today's Intake</div>", unsafe_allow_html=True)
        st.table(st.session_state.intake_data.style.set_table_styles([
            {'selector': 'thead th', 'props': [('background-color', '#4CAF50'), ('color', 'white')]},
            {'selector': 'tbody td', 'props': [('text-align', 'center')]}
        ]).set_properties(**{'text-align': 'center'}))

        total_calories = st.session_state.intake_data["Calories"].sum()
        total_carbs = st.session_state.intake_data["Carbs"].sum()
        total_protein = st.session_state.intake_data["Protein"].sum()
        total_fat = st.session_state.intake_data["Fat"].sum()

        st.markdown("<div class='header'>Progress Towards Goals</div>", unsafe_allow_html=True)
        progress_data = pd.DataFrame({
            "Goal": ["Calories (kcal)", "Carbohydrates (g)", "Protein (g)", "Fat (g)"],
            "Goal Value": [goal_calories, goal_carbs, goal_protein, goal_fat],
            "Consumed": [total_calories, total_carbs, total_protein, total_fat],
            "Remaining": [goal_calories - total_calories, goal_carbs - total_carbs, goal_protein - total_protein,
                          goal_fat - total_fat]
        })

        st.table(progress_data.style.set_table_styles([
            {'selector': 'thead th', 'props': [('background-color', '#4CAF50'), ('color', 'white')]},
            {'selector': 'tbody td', 'props': [('text-align', 'center')]}
        ]).set_properties(**{'text-align': 'center'}))

        for index, row in progress_data.iterrows():
            if row["Remaining"] < 0:
                suggestion = exercise_suggestion(row["Remaining"])
                st.markdown(
                    f"<div class='exercise-suggestion'>To burn {abs(row['Remaining'])} kcal, consider: {suggestion}</div>",
                    unsafe_allow_html=True)
            else:
                for macro in ["Carbohydrates", "Protein", "Fat"]:
                    deficit = row["Remaining"] if row["Goal"] == macro else 0
                    if deficit > 0:
                        suggestion = food_suggestion(macro, deficit)
                        if suggestion:
                            st.markdown(
                                f"<div class='food-suggestion'>To reach your {macro.lower()} goal, {suggestion}</div>",
                                unsafe_allow_html=True)

        with st.beta_expander("Dashboard"):
            st.markdown(
                f"<div class='subheader'>Total Calories Consumed: {total_calories} kcal / {goal_calories} kcal</div>",
                unsafe_allow_html=True)
            st.progress(total_calories / goal_calories)
            st.markdown(f"<div class='subheader'>Total Carbs Consumed: {total_carbs} g / {goal_carbs} g</div>",
                        unsafe_allow_html=True)
            st.progress(total_carbs / goal_carbs)
            st.markdown(f"<div class='subheader'>Total Protein Consumed: {total_protein} g / {goal_protein} g</div>",
                        unsafe_allow_html=True)
            st.progress(total_protein / goal_protein)
            st.markdown(f"<div class='subheader'>Total Fat Consumed: {total_fat} g / {goal_fat} g</div>",
                        unsafe_allow_html=True)
            st.progress(total_fat / goal_fat)

            if 'progress_data' not in st.session_state:
                st.session_state.progress_data = pd.DataFrame(columns=["Day", "Total Calories", "Goal Calories"])
            new_day = len(st.session_state.progress_data) + 1
            new_progress = pd.DataFrame({
                "Day": [new_day],
                "Total Calories": [total_calories],
                "Goal Calories": [goal_calories]
            })
            st.session_state.progress_data = pd.concat([st.session_state.progress_data, new_progress],
                                                       ignore_index=True)

            st.markdown("<div class='subheader'>Progress Over Time</div>", unsafe_allow_html=True)
            st.table(st.session_state.progress_data.style.set_table_styles([
                {'selector': 'thead th', 'props': [('background-color', '#4CAF50'), ('color', 'white')]},
                {'selector': 'tbody td', 'props': [('text-align', 'center')]}
            ]).set_properties(**{'text-align': 'center'}))


if __name__ == "__main__":
    main()
