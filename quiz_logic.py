import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOSSIER_THEMES = os.path.join(BASE_DIR, "Themes")

def charger_themes():
    return [f[:-4] for f in os.listdir(DOSSIER_THEMES) if f.endswith(".txt")]

def charger_questions(theme):
    questions_par_session = {}
    chemin = os.path.join(DOSSIER_THEMES, theme + ".txt")

    session = None
    q = {}

    with open(chemin, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("SESSION|"):
                session = int(line.split("|")[1])
                questions_par_session.setdefault(session, [])
            elif line.startswith("QUESTION|"):
                q = {"question": line.split("|", 1)[1]}
            elif line.startswith("REPONSES|"):
                q["reponses"] = line.split("|", 1)[1].split(";")
            elif line.startswith("BONNE|"):
                q["bonne"] = line.split("|", 1)[1]
            elif line.startswith("EXPLICATION|"):
                q["explication"] = line.split("|", 1)[1]
                questions_par_session[session].append(q)

    for s in questions_par_session:
        random.shuffle(questions_par_session[s])

    return questions_par_session