from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

app = Flask(__name__)
app.config['SECRET_KEY'] = "never-tell!"
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)
# TODO: All lowercases, this is not a constant global variable
RESPONSES = []


@app.get("/")
def home():
    """Shows survey information based on the instance of the survey
        -Starts with default satisfaction_survey instance
        -Populates survey with survey title, instructions, and a button
    """
    # Broswers COULD cache get requests!
    # RESPONSES.clear()
    return render_template(
        "survey_start.html",
        title=survey.title,
        instructions=survey.instructions
    )


@app.post("/begin")
def survey_redirect():
    """Route that handles initial survey start form submission. Per
    given instructions, the form must get to '/questions/0' but the
    given start form and instructions, the form lands at /begin. Must
    redirect.
    """
    # Broswers will not cache post requests!
    RESPONSES.clear()
    return redirect("/questions/0")


@app.get("/questions/<int:question_number>")
def show_survey_question(question_number):
    """Route that handles each survey question, it renders the question
    on the page depending on how far the user has progressed through the
    survey (IE first question, then second, and so on).
    """
    if len(RESPONSES) == len(survey.questions):
        return redirect("/complete")

    question = survey.questions[question_number]

    return render_template(
        "question.html",
        prompt=question.prompt,
        choices=question.choices
    )


@app.post("/answer")
def handle_answer():
    """Append response to response list and redirect to question/"""
    # What if they do not choose an answer? -> BadRequest
    answer = request.form.get("answer", None)
    # if answer:
    RESPONSES.append(answer)

    print(f"Responses = {RESPONSES}")

    return redirect(f"/questions/{len(RESPONSES)}")
    # else:
    #     return render_template


@app.get("/complete")
def show_completion():
    """Show completion page when survey is complete"""

    return render_template("completion.html",
                           indices=range(0, len(RESPONSES)),
                           questions=survey.questions,
                           responses=RESPONSES)
