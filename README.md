# Chatbot de remédiation en algèbre - 3AC

Ce projet est un prototype avancé d'application web pour la remédiation des erreurs algébriques et linguistiques chez les élèves de 3AC.

## Fonctionnalités incluses

- Espace élève
- Liste d'exercices d'algèbre
- Analyse automatique des réponses
- Détection de plusieurs erreurs : signe, distribution, réduction, parenthèses, confusion addition/multiplication
- Feedback pédagogique avec correction et remédiation
- Mini-chatbot explicatif
- Tableau de bord enseignant
- Historique temporaire des réponses

## Structure

```text
chatbot-remediation-3ac/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── README_BACKEND.md
└── frontend/
    ├── package.json
    ├── index.html
    └── src/
        ├── App.jsx
        ├── main.jsx
        └── style.css
```

## Lancer le backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
fastapi dev main.py
```

Backend : http://127.0.0.1:8000

## Lancer le frontend

Dans un nouveau terminal :

```bash
cd frontend
npm install
npm run dev
```

Frontend : http://localhost:5173

## Remarque importante

L'historique est stocké temporairement en mémoire. Si tu fermes le backend, l'historique disparaît. La prochaine amélioration sera d'ajouter une vraie base de données SQLite ou PostgreSQL.
