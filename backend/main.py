from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List

app = FastAPI(title="Chatbot Remediation 3AC", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StudentAnswer(BaseModel):
    student_name: str = "Élève"
    exercise_id: int
    student_answer: str

class ChatMessage(BaseModel):
    message: str
    level: str = "3AC"

exercises: Dict[int, Dict[str, Any]] = {
    1: {
        "statement": "Développer et réduire : -3(x - 2)",
        "correct_answer": "-3x+6",
        "skill": "Développement",
        "level": "Facile",
        "expected_steps": ["Multiplier -3 par x", "Multiplier -3 par -2", "Appliquer la règle des signes"],
    },
    2: {
        "statement": "Développer : 2(x + 3)",
        "correct_answer": "2x+6",
        "skill": "Développement",
        "level": "Facile",
        "expected_steps": ["Multiplier 2 par x", "Multiplier 2 par 3"],
    },
    3: {
        "statement": "Réduire : 3x + 2x",
        "correct_answer": "5x",
        "skill": "Réduction",
        "level": "Facile",
        "expected_steps": ["Identifier les termes semblables", "Additionner les coefficients"],
    },
    4: {
        "statement": "Développer : -(x + 4)",
        "correct_answer": "-x-4",
        "skill": "Parenthèses et signes",
        "level": "Moyen",
        "expected_steps": ["Comprendre que le signe - signifie multiplier par -1", "Changer tous les signes dans la parenthèse"],
    },
    5: {
        "statement": "Réduire : x + x",
        "correct_answer": "2x",
        "skill": "Réduction",
        "level": "Facile",
        "expected_steps": ["Additionner deux termes semblables", "Ne pas transformer l'addition en multiplication"],
    },
    6: {
        "statement": "Développer et réduire : -2(x + 5) + 3x",
        "correct_answer": "x-10",
        "skill": "Développement et réduction",
        "level": "Moyen",
        "expected_steps": ["Développer -2(x+5)", "Réduire les termes en x", "Garder le terme constant"],
    },
}

error_types = {
    "E1": {
        "name": "Erreur de signe",
        "description": "L'élève ne respecte pas la règle des signes.",
        "remediation": "Revoir la règle : - × - = + et - × + = -.",
    },
    "E2": {
        "name": "Erreur de distribution",
        "description": "L'élève ne multiplie pas tous les termes de la parenthèse.",
        "remediation": "Le facteur devant la parenthèse doit multiplier chaque terme à l'intérieur.",
    },
    "E3": {
        "name": "Erreur de réduction",
        "description": "L'élève confond addition des termes semblables et puissance.",
        "remediation": "On additionne seulement les coefficients des termes semblables.",
    },
    "E4": {
        "name": "Erreur de parenthèses",
        "description": "L'élève ne change pas tous les signes après un signe moins devant une parenthèse.",
        "remediation": "Quand il y a un signe - devant une parenthèse, tous les signes à l'intérieur changent.",
    },
    "E5": {
        "name": "Confusion addition/multiplication",
        "description": "L'élève transforme x + x en x² au lieu de 2x.",
        "remediation": "x + x signifie deux fois x, donc x + x = 2x.",
    },
    "E6": {
        "name": "Erreur non identifiée automatiquement",
        "description": "La réponse est incorrecte, mais elle ne correspond pas aux erreurs prévues dans cette version.",
        "remediation": "Refaire l'exercice étape par étape et comparer avec la règle utilisée.",
    },
}

history: List[Dict[str, Any]] = []


def normalize_answer(answer: str) -> str:
    return (
        answer.replace(" ", "")
        .replace("*", "")
        .replace("X", "x")
        .replace("−", "-")
        .replace("²", "^2")
        .lower()
    )


def make_response(is_correct: bool, error_code: Optional[str], feedback: str, correction: str, similar_exercise: Optional[str] = None):
    error = error_types.get(error_code) if error_code else None
    return {
        "is_correct": is_correct,
        "error_code": error_code,
        "error_type": error["name"] if error else None,
        "feedback": feedback,
        "correction": correction,
        "remediation": error["remediation"] if error else "Continue avec un exercice plus difficile.",
        "similar_exercise": similar_exercise,
    }


def analyze_error(exercise_id: int, student_answer: str):
    exercise = exercises.get(exercise_id)
    if not exercise:
        return {"status": "error", "message": "Exercice introuvable."}

    student = normalize_answer(student_answer)
    correct = normalize_answer(exercise["correct_answer"])

    if student == correct:
        return make_response(
            True,
            None,
            "Très bien ! Ta réponse est correcte. Tu as bien appliqué la règle.",
            exercise["correct_answer"],
            "Essaie maintenant un exercice de niveau plus difficile.",
        )

    if exercise_id == 1 and student in ["-3x-6", "-3x+-6"]:
        return make_response(False, "E1", "Tu as bien distribué -3 sur x, mais tu as fait une erreur avec -3 × (-2).", "-3(x - 2) = -3x + 6", "Développer : -2(x - 5)")

    if exercise_id == 2 and student in ["2x+3", "2x3"]:
        return make_response(False, "E2", "Tu as multiplié 2 par x, mais tu as oublié de multiplier 2 par 3.", "2(x + 3) = 2x + 6", "Développer : 4(x + 2)")

    if exercise_id == 3 and student in ["5x2", "5x^2", "5xx"]:
        return make_response(False, "E3", "Tu as additionné 3 et 2, mais tu as transformé x en x². Ici, on additionne seulement les coefficients.", "3x + 2x = 5x", "Réduire : 4x + 5x")

    if exercise_id == 4 and student in ["-x+4", "-1x+4"]:
        return make_response(False, "E4", "Tu as changé le signe de x, mais tu n'as pas changé le signe de 4.", "-(x + 4) = -x - 4", "Développer : -(x - 7)")

    if exercise_id == 5 and student in ["x^2", "x2", "xx"]:
        return make_response(False, "E5", "Tu as confondu x + x avec x × x. Une addition de deux x donne 2x.", "x + x = 2x", "Réduire : a + a")

    if exercise_id == 6 and student in ["-2x-10+3x", "3x-2x-10"]:
        return make_response(False, "E6", "Ta réponse contient les bonnes étapes, mais elle n'est pas encore réduite complètement.", "-2(x + 5) + 3x = -2x - 10 + 3x = x - 10", "Développer et réduire : -3(x + 2) + 5x")

    return make_response(False, "E6", "Ta réponse n'est pas correcte, mais cette première version ne reconnaît pas encore précisément cette erreur.", exercise["correct_answer"], "Refais le même exercice en détaillant chaque étape.")


@app.get("/")
def home():
    return {"message": "Backend du chatbot de remédiation 3AC fonctionne correctement."}


@app.get("/exercises")
def get_exercises():
    return exercises


@app.get("/error-types")
def get_error_types():
    return error_types


@app.post("/analyze")
def analyze_answer(answer: StudentAnswer):
    result = analyze_error(answer.exercise_id, answer.student_answer)
    record = {
        "student_name": answer.student_name,
        "exercise_id": answer.exercise_id,
        "student_answer": answer.student_answer,
        "result": result,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    history.append(record)
    return result


@app.get("/history")
def get_history():
    return history


@app.get("/dashboard")
def dashboard():
    total = len(history)
    if total == 0:
        return {"total_answers": 0, "success_rate": 0, "errors_by_type": {}, "recent_answers": []}

    correct = sum(1 for item in history if item["result"].get("is_correct"))
    errors: Dict[str, int] = {}
    for item in history:
        error_type = item["result"].get("error_type")
        if error_type:
            errors[error_type] = errors.get(error_type, 0) + 1

    return {
        "total_answers": total,
        "correct_answers": correct,
        "success_rate": round((correct / total) * 100, 2),
        "errors_by_type": errors,
        "recent_answers": history[-10:],
    }


@app.post("/chat")
def chat(message: ChatMessage):
    text = message.message.lower()
    if "développer" in text or "developper" in text:
        reply = "Développer signifie enlever les parenthèses en multipliant chaque terme à l'intérieur. Exemple : 2(x+3)=2x+6."
    elif "réduire" in text or "reduire" in text:
        reply = "Réduire signifie regrouper les termes semblables. Exemple : 3x+2x=5x."
    elif "signe" in text:
        reply = "Règle des signes : - × - = +, + × + = +, - × + = -, + × - = -."
    elif "factoriser" in text:
        reply = "Factoriser signifie transformer une somme en produit. Exemple : 2x+6 = 2(x+3)."
    else:
        reply = "Je peux t'aider en algèbre : développement, réduction, règles des signes et parenthèses. Pose-moi une question ou réponds à un exercice."
    return {"reply": reply}
