from flask import Flask, render_template, request
import json
import re
from datetime import datetime

app = Flask(__name__)


# -------------------------
# LOAD QUESTIONS FROM JSON
# -------------------------
def load_questions():
    with open("questions.json", "r") as file:
        return json.load(file)


# -------------------------
# VALIDATIONS
# -------------------------
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


# -------------------------
# SELF-EFFICACY RESULT LOGIC
# -------------------------
def get_state(score):

    if score <= 15:
        return "Very High Self-Efficacy"
    elif score <= 30:
        return "Good Confidence"
    elif score <= 45:
        return "Moderate Confidence"
    elif score <= 60:
        return "Low Self-Efficacy"
    else:
        return "Very Low Self-Efficacy"


# -------------------------
# ROUTES
# -------------------------

# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# START SURVEY (USER INPUT VALIDATION)
@app.route("/survey", methods=["POST"])
def survey():

    name = request.form.get("name")
    dob = request.form.get("dob")
    student_id = request.form.get("student_id")

    # VALIDATION CHECKS
    if not validate_name(name):
        return "Invalid name format (Only letters, spaces, - and ' allowed)"

    if not validate_dob(dob):
        return "Invalid date of birth (Use YYYY-MM-DD)"

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


# SUBMIT SURVEY (CALCULATE SCORE + SAVE RESULT)
@app.route("/submit", methods=["POST"])
def submit():

    questions = load_questions()
    total_score = 0

    # CALCULATE SCORE
    for i in range(len(questions)):
        answer = request.form.get(f"q{i+1}")
        if answer:
            total_score += int(answer)

    state = get_state(total_score)

    # SAVE RESULT TO JSON
    result_data = {
        "name": request.form.get("name"),
        "student_id": request.form.get("student_id"),
        "date_of_birth": request.form.get("dob"),
        "score": total_score,
        "state": state
    }

    with open("results.json", "w") as file:
        json.dump(result_data, file, indent=4)

    return render_template(
        "result.html",
        score=total_score,
        state=state
    )


# -------------------------
# RUN APP
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)