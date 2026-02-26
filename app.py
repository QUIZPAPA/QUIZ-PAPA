import os
import random
from flask import Flask, render_template, request, redirect, session
from quiz_logic import charger_themes, charger_questions

# Création de l'application Flask
app = Flask(__name__)
app.secret_key = "supersecret"

# Route d'accueil
@app.route("/")
def accueil():
    return render_template("accueil.html", themes=charger_themes())

# Démarrage d'une session quiz
@app.route("/start", methods=["POST"])
def start():
    theme = request.form["theme"]

    session["questions"] = charger_questions(theme)
    session["session_actuelle"] = 1
    session["index_question"] = 0
    session["score_session"] = 0
    session["score_total"] = 0
    session["questions_ratees"] = []

    return redirect("/quiz")

# Route du quiz
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "questions" not in session:
        return redirect("/")

    questions = session["questions"]
    session_actuelle = session["session_actuelle"]
    index_question = session["index_question"]

    if request.method == "POST":
        reponse = request.form["reponse"]
        q = questions[str(session_actuelle)][index_question]

        if reponse == q["bonne"]:
            session["score_session"] += 1
            session["score_total"] += 1
            feedback = ("bonne", q["explication"])
        else:
            session["questions_ratees"].append(q)
            feedback = ("fausse", q["bonne"], q["explication"])

        session["index_question"] += 1
        session.modified = True

        return render_template(
            "quiz.html",
            fin=False,
            question=q,
            feedback=feedback
        )

    if index_question < len(questions[str(session_actuelle)]):
        q = questions[str(session_actuelle)][index_question]
        reps = q["reponses"][:]
        random.shuffle(reps)

        return render_template(
            "quiz.html",
            question=q,
            reponses=reps,
            session_actuelle=session_actuelle,
            total=len(questions[str(session_actuelle)]),
            index=index_question,
            fin=False
        )
    else:
        return render_template("quiz.html", fin=True)

# Point d'entrée pour développement local
# Render utilisera gunicorn, donc ce bloc est optionnel
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)