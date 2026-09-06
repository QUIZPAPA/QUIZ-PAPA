import os
import random
from flask import Flask, render_template, request, redirect, session
from quiz_logic import charger_themes, charger_questions

app = Flask(__name__)
app.secret_key = "supersecret"


@app.route("/")
def accueil():
    return render_template("accueil.html", themes=charger_themes())


# =========================================================
# INSCRIPTION POUR RECEVOIR LES NOUVEAUX THÈMES
# =========================================================

@app.route("/inscription", methods=["POST"])
def inscription():

    email = request.form.get("email", "").strip()

    if email:

        # Le fichier contact.txt sera créé dans le dossier
        # où se trouve ce fichier app.py
        chemin_contact = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "contact.txt"
        )

        # Lire les adresses déjà enregistrées
        adresses = []

        if os.path.exists(chemin_contact):

            with open(chemin_contact, "r", encoding="utf-8") as f:
                adresses = [
                    ligne.strip().lower()
                    for ligne in f
                    if ligne.strip()
                ]

        # Ajouter seulement si l'adresse n'est pas déjà présente
        if email.lower() not in adresses:

            with open(chemin_contact, "a", encoding="utf-8") as f:
                f.write(email + "\n")

    return redirect("/")


# =========================================================
# DÉMARRAGE DU QUIZ
# =========================================================

@app.route("/start", methods=["POST"])
def start():

    theme = request.form["theme"]

    session["questions"] = charger_questions(theme)
    session["session_actuelle"] = 1
    session["index_question"] = 0
    session["questions_ratees"] = []
    session["mode_revision"] = False

    return redirect("/quiz")


# =========================================================
# QUIZ
# =========================================================

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

                feedback = (
                    "fausse",
                    q["bonne"],
                    q["explication"]
                )

            session["index_question"] += 1
            session.modified = True

            return render_template(
                "quiz.html",
                fin=False,
                question=q,
                feedback=feedback
            )

        # -------------------------
        # QUESTIONS DE LA SESSION
        # -------------------------

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

        # -------------------------
        # FIN DE SESSION
        # -------------------------

        else:

            if str(session_actuelle + 1) in questions:

                session["session_actuelle"] += 1
                session["index_question"] = 0
                session.modified = True

                return redirect("/quiz")

            # -------------------------
            # TOUTES LES SESSIONS TERMINÉES
            # -------------------------

            else:

                if session["questions_ratees"]:

                    session["mode_revision"] = True
                    session["index_question"] = 0
                    session.modified = True

                    return redirect("/quiz")

                else:

                    return render_template(
                        "quiz.html",
                        fin=True
                    )

    # =====================================================
    # MODE RÉVISION
    # =====================================================

    else:

        erreurs = session["questions_ratees"]

        if request.method == "POST":

            reponse = request.form["reponse"]
            q = erreurs[index_question]

            if reponse == q["bonne"]:

                erreurs.pop(index_question)

                feedback = (
                    "bonne",
                    q["explication"]
                )

            else:

                feedback = (
                    "fausse",
                    q["bonne"],
                    q["explication"]
                )

                session["index_question"] += 1

            session.modified = True

            return render_template(
                "quiz.html",
                fin=False,
                question=q,
                feedback=feedback
            )

        # -------------------------
        # QUESTIONS À RÉVISER
        # -------------------------

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

        # -------------------------
        # FIN DE LA RÉVISION
        # -------------------------

        else:

            return render_template(
                "quiz.html",
                fin=True
            )


# =========================================================
# LANCEMENT DE L'APPLICATION
# =========================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )