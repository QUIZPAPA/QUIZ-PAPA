import os
import random
from flask import Flask, render_template, request, redirect, session
from quiz_logic import charger_themes, charger_questions

app = Flask(__name__)
app.secret_key = "supersecret"

@app.route("/")
def accueil():
    return render_template("accueil.html", themes=charger_themes())


@app.route("/start", methods=["POST"])
def start():
    theme = request.form["theme"]

    session["questions"] = charger_questions(theme)
    session["session_actuelle"] = 1
    session["index_question"] = 0
    session["questions_ratees"] = []
    session["mode_revision"] = False

    return redirect("/quiz")


@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    if "questions" not in session:
        return redirect("/")

    questions = session["questions"]
    session_actuelle = session["session_actuelle"]
    index_question = session["index_question"]
    mode_revision = session.get("mode_revision", False)

    # -------------------------
    # MODE NORMAL (Sessions 1,2,3...)
    # -------------------------
    if not mode_revision:

        questions_session = questions[str(session_actuelle)]

        if request.method == "POST":
            reponse = request.form["reponse"]
            q = questions_session[index_question]

            if reponse == q["bonne"]:
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

        # Si encore des questions dans la session
        if index_question < len(questions_session):
            q = questions_session[index_question]
            reps = q["reponses"][:]
            random.shuffle(reps)

            return render_template(
                "quiz.html",
                question=q,
                reponses=reps,
                session_actuelle=session_actuelle,
                total=len(questions_session),
                index=index_question,
                fin=False
            )

        # Fin de session → passer à la suivante
        else:
            if str(session_actuelle + 1) in questions:
                session["session_actuelle"] += 1
                session["index_question"] = 0
                session.modified = True
                return redirect("/quiz")

            # Toutes les sessions terminées
            else:
                if session["questions_ratees"]:
                    session["mode_revision"] = True
                    session["index_question"] = 0
                    session.modified = True
                    return redirect("/quiz")
                else:
                    return render_template("quiz.html", fin=True)

    # -------------------------
    # MODE RÉVISION
    # -------------------------
    else:

        erreurs = session["questions_ratees"]

        if request.method == "POST":
            reponse = request.form["reponse"]
            q = erreurs[index_question]

            if reponse == q["bonne"]:
                erreurs.pop(index_question)
                feedback = ("bonne", q["explication"])
            else:
                feedback = ("fausse", q["bonne"], q["explication"])
                session["index_question"] += 1

            session.modified = True

            return render_template(
                "quiz.html",
                fin=False,
                question=q,
                feedback=feedback
            )

        if erreurs:

            if index_question >= len(erreurs):
                session["index_question"] = 0

            q = erreurs[session["index_question"]]
            reps = q["reponses"][:]
            random.shuffle(reps)

            return render_template(
                "quiz.html",
                question=q,
                reponses=reps,
                session_actuelle="Révision",
                total=len(erreurs),
                index=session["index_question"],
                fin=False
            )

        else:
            return render_template("quiz.html", fin=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)