from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

app = Flask(__name__)
app.config['SECRET_KEY'] = "never-tell!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)
# TODO: All lowercases, this is not a constant global variable
# responses = []


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
    Create empty session response list.
    """
    # Broswers will not cache post requests!
    # responses.clear()

    session["responses"] = []
    return redirect("/questions/0")


@app.get("/questions/<int:question_number>")
def show_survey_question(question_number):
    """Route that handles each survey question, it renders the question
    on the page depending on how far the user has progressed through the
    survey (IE first question, then second, and so on).
    If invalid question_number, give flash message and redirect to
    appropriate question
    """
    responses = session["responses"]
    # if survey is compleete
    if len(responses) == len(survey.questions):
        return redirect("/complete")

    # if trying to access a question out of order
    # (if question number!= response length)
    if(len(responses) != question_number):
        flash(
            f"Invalid question number. Redirected to correct survey question.")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[question_number]

    return render_template(
        "question.html",
        prompt=question.prompt,
        choices=question.choices
    )


@app.post("/answer")
def handle_answer():
    """Append response to session response list and redirect to question/
    Checks for answer. If no answer, redirect to questions/len(responses)"""

    answer = request.form.get("answer", None)

    if answer == None:
        flash(f"Please provide a response before moving on.")
        return redirect(f"questions/{len(session['responses'])}")

    # must get the list, mutate it, and then reassign the item in the session
    responses = session["responses"]
    responses.append(answer)
    session["responses"] = responses

    print(f"Responses = {responses}")

    return redirect(f"/questions/{len(responses)}")

# if there is no responses in session
@app.get("/complete")
def show_completion():
    """Show completion page when survey is complete"""
    prompts = [question.prompt for question in survey.questions]

    questions_and_responses = zip(prompts, session["responses"])

    return render_template("completion.html",
                          q_and_a=questions_and_responses)

#   return render_template("completion.html",
#                            indices=range(0, len(session["responses"])),
#                            questions=survey.questions,
#    responses=session["responses"])
