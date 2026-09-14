import os
import random
import json
import urllib.request

from flask import Flask, render_template, request, redirect, session

from quiz_logic import charger_themes, charger_questions


app = Flask(__name__)
app.secret_key = "supersecret"


GOOGLE_SHEETS_URL = "https://script.google.com/macros/s/AKfycbwJI0uvYL_YaDOGE7IjnuBlVHHRbPGza9WLBqyCn6ROjf8CWKwozpjUI62oOknMlzPdpw/exec"


def envoyer_donnee_google(donnees):

    try:

        contenu = json.dumps(donnees).encode("utf-8")

        requete = urllib.request.Request(
            GOOGLE_SHEETS_URL,
            data=contenu,
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(requete, timeout=10) as reponse:

            resultat = reponse.read().decode("utf-8")

            return resultat

    except Exception as erreur:

        print("Erreur Google Sheets :", erreur)

        return None


@app.route("/")
def accueil():

    envoyer_donnee_google({
        "type": "visite"
    })

    themes = charger_themes()

    matieres = {}

    for t in themes:

        matiere = t.split()[0]

        if matiere not in matieres:
            matieres[matiere] = []

        matieres[matiere].append(t)

    return render_template(
        "accueil.html",
        matieres=matieres
    )


@app.route("/inscription", methods=["POST"])
def inscription():

    email = request.form.get("email", "").strip()

    if email:

        envoyer_donnee_google({
            "type": "inscription",
            "email": email
        })

    themes = charger_themes()

    matieres = {}

    for t in themes:

        matiere = t.split()[0]

        if matiere not in matieres:
            matieres[matiere] = []

        matieres[matiere].append(t)

    return render_template(
        "accueil.html",
        matieres=matieres,
        message_inscription="Inscription prise en compte"
    )


@app.route("/start", methods=["POST"])
def start():

    theme = request.form["theme"]

    session["theme"] = theme
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

    theme = session.get("theme", "Quiz")
    theme = theme.replace("_", " ").replace(".txt", "")

    questions = session["questions"]
    session_actuelle = session["session_actuelle"]
    index_question = session["index_question"]
    mode_revision = session.get("mode_revision", False)

    # -------------------------
    # MODE NORMAL
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
                theme=theme,
                fin=False,
                question=q,
                feedback=feedback
            )

        if index_question < len(questions_session):

            q = questions_session[index_question]
            reps = q["reponses"][:]
            random.shuffle(reps)

            return render_template(
                "quiz.html",
                theme=theme,
                question=q,
                reponses=reps,
                session_actuelle=session_actuelle,
                total=len(questions_session),
                index=index_question,
                fin=False
            )

        else:

            if str(session_actuelle + 1) in questions:

                session["session_actuelle"] += 1
                session["index_question"] = 0
                session.modified = True

                return redirect("/quiz")

            else:

                if session["questions_ratees"]:

                    session["mode_revision"] = True
                    session["index_question"] = 0
                    session.modified = True

                    return redirect("/quiz")

                else:

                    return render_template(
                        "quiz.html",
                        theme=theme,
                        fin=True
                    )

    # -------------------------
    # MODE REVISION
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
                theme=theme,
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
                theme=theme,
                question=q,
                reponses=reps,
                session_actuelle="Révision",
                total=len(erreurs),
                index=session["index_question"],
                fin=False
            )

        else:

            return render_template(
                "quiz.html",
                theme=theme,
                fin=True
            )


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )