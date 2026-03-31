from flask import Flask, render_template, request
import json
import os
import re
from datetime import datetime

app = Flask(__name__)


# =========================
# LOAD QUESTIONS
# =========================
def load_questions():
    with open("questions.json", "r") as file:
        return json.load(file)


# =========================
# SAVE RESULTS (LIST MODE)
# =========================
def save_result(new_data):
    if os.path.exists("results.json"):
        with open("results.json", "r") as file:
            try:
                data = json.load(file)
            except:
                data = []
    else:
        data = []

    data.append(new_data)

    with open("results.json", "w") as file:
        json.dump(data, file, indent=4)


# =========================
# VALIDATIONS
# =========================
def validate_name(name):
    pattern = r"^[A-Za-z\s'-]+$"
    return re.match(pattern, name)


def validate_student_id(student_id):
    return student_id.isdigit()


def validate_dob(dob):
    try:
        datetime.strptime(dob, "%Y-%m-%d")
        return True
    except ValueError:
        return False


# =========================
# SCORE INTERPRETATION
# =========================
def get_state(score):
    if score <= 15:
        return "Very High Self-Efficacy"
    elif score <= 30:
        return "Good Confidence"
    elif score <= 45:
        return "Moderate Self-Doubt"
    else:
        return "Low Self-Efficacy"


# =========================
# ROUTES
# =========================

# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# START SURVEY
@app.route("/survey", methods=["POST"])
def survey():

    name = request.form.get("name")
    dob = request.form.get("dob")
    student_id = request.form.get("student_id")

    if not validate_name(name):
        return "Invalid name format"

    if not validate_dob(dob):
        return "Invalid date of birth"

    if not validate_student_id(student_id):
        return "Student ID must contain only digits"

    questions = load_questions()

    return render_template(
        "survey.html",
        questions=questions,
        name=name,
        dob=dob,
        student_id=student_id
    )


# SUBMIT ANSWERS
@app.route("/submit", methods=["POST"])
def submit():

    questions = load_questions()
    total_score = 0

    # ===== WHILE LOOP =====
    i = 0
    while i < len(questions):
        answer = request.form.get(f"q{i}")

        if answer is None:
            return f"Error: Question {i+1} not answered"

        total_score += int(answer)
        i += 1

    # ===== EXTRA VARIABLE TYPES =====
    sample_float = float(total_score) / len(questions)
    sample_tuple = ("survey", "result")
    sample_set = {"A", "B", "C"}
    sample_frozenset = frozenset(sample_set)
    sample_bool = total_score > 30

    print(sample_float, sample_tuple, sample_set, sample_frozenset, sample_bool)

    state = get_state(total_score)

    result_data = {
        "name": request.form.get("name"),
        "student_id": request.form.get("student_id"),
        "date_of_birth": request.form.get("dob"),
        "score": total_score,
        "state": state
    }

    save_result(result_data)

    return render_template(
        "result.html",
        score=total_score,
        state=state
    )


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)