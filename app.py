import os
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, session, send_file
from quiz_logic import charger_themes, charger_questions

app = Flask(__name__)
app.secret_key = "supersecret"


@app.route("/")
def accueil():

    fichier_visites = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "visites.txt"
    )

    with open(fichier_visites, "a", encoding="utf-8") as f:
        maintenant = datetime.now()
        f.write(maintenant.strftime("%d/%m/%Y;%H:%M:%S") + "\n")

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


@app.route("/inscription", methods=["POST"])
def inscription():

    email = request.form.get("email", "").strip()

    if email:

        fichier = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "adresse.txt"
        )

        with open(fichier, "a", encoding="utf-8") as f:
            f.write(email + "\n")

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


@app.route("/adresses", methods=["GET", "POST"])
def adresses():

    mot_de_passe = os.environ.get("ADMIN_PASSWORD")

    if not mot_de_passe:
        return "ADMIN_PASSWORD n'est pas configuré sur Render.", 500

    if request.method == "GET":

        return """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Accès administrateur</title>
        </head>
        <body style="font-family:Arial; text-align:center; margin-top:80px;">

            <h2>Accès aux adresses inscrites</h2>

            <form method="post">

                <input
                    type="password"
                    name="password"
                    placeholder="Mot de passe"
                    required
                    style="padding:10px;"
                >

                <button
                    type="submit"
                    style="padding:10px 20px; margin-left:5px;"
                >
                    Télécharger
                </button>

            </form>

        </body>
        </html>
        """

    if request.form.get("password") != mot_de_passe:
        return "Mot de passe incorrect.", 403

    fichier = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "adresse.txt"
    )

    if not os.path.exists(fichier):

        with open(fichier, "w", encoding="utf-8"):
            pass

    return send_file(
        fichier,
        as_attachment=True,
        download_name="adresse.txt",
        mimetype="text/plain"
    )


@app.route("/admin", methods=["GET", "POST"])
def admin():

    mot_de_passe = os.environ.get("ADMIN_PASSWORD")

    if not mot_de_passe:
        return "ADMIN_PASSWORD n'est pas configuré sur Render.", 500

    if request.method == "GET":

        return """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Administration Quiz Papa</title>
        </head>

        <body style="
            font-family:Arial;
            text-align:center;
            margin-top:80px;
        ">

            <h2>Administration Quiz Papa</h2>

            <form method="post">

                <input
                    type="password"
                    name="password"
                    placeholder="Mot de passe"
                    required
                    style="padding:10px; font-size:16px;"
                >

                <button
                    type="submit"
                    style="
                        padding:10px 20px;
                        margin-left:5px;
                        font-size:16px;
                    "
                >
                    Voir les statistiques
                </button>

            </form>

        </body>
        </html>
        """

    if request.form.get("password") != mot_de_passe:
        return "Mot de passe incorrect.", 403

    fichier_visites = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "visites.txt"
    )

    if not os.path.exists(fichier_visites):
        visites = []
    else:
        with open(fichier_visites, "r", encoding="utf-8") as f:
            visites = [
                ligne.strip()
                for ligne in f
                if ligne.strip()
            ]

    maintenant = datetime.now()

    aujourd_hui = maintenant.strftime("%d/%m/%Y")
    debut_semaine = maintenant.date().toordinal() - maintenant.weekday()

    visites_aujourd_hui = 0
    visites_semaine = 0

    for visite in visites:

        try:

            date_visite = datetime.strptime(
                visite.split(";")[0],
                "%d/%m/%Y"
            )

            if visite.startswith(aujourd_hui + ";"):
                visites_aujourd_hui += 1

            if date_visite.date().toordinal() >= debut_semaine:
                visites_semaine += 1

        except ValueError:
            pass

    total_visites = len(visites)

    dernieres_visites = visites[-20:]
    dernieres_visites.reverse()

    lignes_visites = ""

    for visite in dernieres_visites:

        try:

            date_visite, heure_visite = visite.split(";")

            lignes_visites += f"""
            <tr>
                <td style="padding:8px;">{date_visite}</td>
                <td style="padding:8px;">{heure_visite}</td>
            </tr>
            """

        except ValueError:
            pass

    return f"""
    <!DOCTYPE html>
    <html lang="fr">

    <head>

        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>Administration Quiz Papa</title>

    </head>

    <body style="
        font-family:Arial;
        margin:40px;
        background:#f5f5f5;
    ">

        <div style="
            max-width:800px;
            margin:auto;
            background:white;
            padding:30px;
            border-radius:15px;
        ">

            <h1 style="text-align:center;">
                Administration Quiz Papa
            </h1>

            <h2>Statistiques des visites</h2>

            <div style="
                display:flex;
                gap:15px;
                flex-wrap:wrap;
                margin-bottom:30px;
            ">

                <div style="
                    flex:1;
                    min-width:180px;
                    padding:20px;
                    background:#95F5A6;
                    border-radius:10px;
                    text-align:center;
                ">
                    <div>Visites aujourd'hui</div>
                    <strong style="font-size:30px;">
                        {visites_aujourd_hui}
                    </strong>
                </div>

                <div style="
                    flex:1;
                    min-width:180px;
                    padding:20px;
                    background:#70d5ff;
                    border-radius:10px;
                    text-align:center;
                ">
                    <div>Visites cette semaine</div>
                    <strong style="font-size:30px;">
                        {visites_semaine}
                    </strong>
                </div>

                <div style="
                    flex:1;
                    min-width:180px;
                    padding:20px;
                    background:#eeeeee;
                    border-radius:10px;
                    text-align:center;
                ">
                    <div>Total des visites</div>
                    <strong style="font-size:30px;">
                        {total_visites}
                    </strong>
                </div>

            </div>

            <h2>20 dernières visites</h2>

            <table style="
                width:100%;
                border-collapse:collapse;
                text-align:left;
            ">

                <tr style="background:#eeeeee;">
                    <th style="padding:8px;">Date</th>
                    <th style="padding:8px;">Heure</th>
                </tr>

                {lignes_visites}

            </table>

            <div style="
                margin-top:30px;
                text-align:center;
            ">

                <a href="/adresses">
                    Télécharger les adresses inscrites
                </a>

            </div>

        </div>

    </body>

    </html>
    """


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

    app.run(host="0.0.0.0", port=port)