import { useEffect, useState } from "react";
import { Bot, GraduationCap, BarChart3, Send, CheckCircle, XCircle } from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [activeTab, setActiveTab] = useState("student");
  const [studentName, setStudentName] = useState("Élève 1");
  const [exercises, setExercises] = useState({});
  const [selectedExercise, setSelectedExercise] = useState(1);
  const [studentAnswer, setStudentAnswer] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [chatMessage, setChatMessage] = useState("");
  const [chatReplies, setChatReplies] = useState([
    { role: "bot", text: "Bonjour ! Je suis ton assistant de remédiation en algèbre. Choisis un exercice ou pose-moi une question." },
  ]);

  useEffect(() => {
    fetch(`${API_URL}/exercises`)
      .then((response) => response.json())
      .then((data) => setExercises(data))
      .catch(() => setFeedback({ feedback: "Erreur : backend non lancé. Lance d'abord FastAPI." }));
  }, []);

  const loadDashboard = () => {
    fetch(`${API_URL}/dashboard`)
      .then((response) => response.json())
      .then((data) => setDashboard(data));
  };

  useEffect(() => {
    if (activeTab === "teacher") loadDashboard();
  }, [activeTab]);

  const analyzeAnswer = async () => {
    if (!studentAnswer.trim()) return;
    const response = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        student_name: studentName,
        exercise_id: Number(selectedExercise),
        student_answer: studentAnswer,
      }),
    });
    const data = await response.json();
    setFeedback(data);
  };

  const sendChat = async () => {
    if (!chatMessage.trim()) return;
    const userText = chatMessage;
    setChatReplies((old) => [...old, { role: "student", text: userText }]);
    setChatMessage("");
    const response = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userText, level: "3AC" }),
    });
    const data = await response.json();
    setChatReplies((old) => [...old, { role: "bot", text: data.reply }]);
  };

  const exercise = exercises[selectedExercise];

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1><Bot size={34} /> Chatbot de remédiation en algèbre - 3AC</h1>
          <p>Prototype avancé : exercices, analyse des erreurs, remédiation et tableau de bord enseignant.</p>
        </div>
      </header>

      <nav className="tabs">
        <button className={activeTab === "student" ? "active" : ""} onClick={() => setActiveTab("student")}>
          <GraduationCap size={18} /> Espace élève
        </button>
        <button className={activeTab === "teacher" ? "active" : ""} onClick={() => setActiveTab("teacher")}>
          <BarChart3 size={18} /> Tableau de bord enseignant
        </button>
      </nav>

      {activeTab === "student" && (
        <main className="grid">
          <section className="card main-card">
            <h2>Exercice de remédiation</h2>
            <label>Nom de l'élève</label>
            <input value={studentName} onChange={(e) => setStudentName(e.target.value)} />

            <label>Choisir un exercice</label>
            <select
              value={selectedExercise}
              onChange={(e) => {
                setSelectedExercise(e.target.value);
                setStudentAnswer("");
                setFeedback(null);
              }}
            >
              {Object.entries(exercises).map(([id, ex]) => (
                <option key={id} value={id}>Exercice {id} - {ex.skill} - {ex.level}</option>
              ))}
            </select>

            {exercise && (
              <div className="exercise-box">
                <p className="skill">Compétence : {exercise.skill}</p>
                <h3>{exercise.statement}</h3>
                <input
                  placeholder="Exemple : -3x+6"
                  value={studentAnswer}
                  onChange={(e) => setStudentAnswer(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && analyzeAnswer()}
                />
                <button className="primary" onClick={analyzeAnswer}>Vérifier ma réponse</button>
              </div>
            )}

            {feedback && (
              <div className={feedback.is_correct ? "feedback ok" : "feedback wrong"}>
                <h3>{feedback.is_correct ? <CheckCircle size={22} /> : <XCircle size={22} />} Résultat</h3>
                <p><strong>Statut :</strong> {feedback.is_correct ? "Réponse correcte" : "Réponse incorrecte"}</p>
                {feedback.error_type && <p><strong>Type d'erreur :</strong> {feedback.error_type}</p>}
                <p><strong>Explication :</strong> {feedback.feedback}</p>
                <p><strong>Correction :</strong> {feedback.correction}</p>
                <p><strong>Remédiation :</strong> {feedback.remediation}</p>
                {feedback.similar_exercise && <p><strong>Exercice similaire :</strong> {feedback.similar_exercise}</p>}
              </div>
            )}
          </section>

          <aside className="card chat-card">
            <h2>Assistant chatbot</h2>
            <div className="messages">
              {chatReplies.map((msg, index) => (
                <div key={index} className={msg.role === "bot" ? "msg bot" : "msg student"}>{msg.text}</div>
              ))}
            </div>
            <div className="chat-input">
              <input
                placeholder="Pose une question : développer, réduire, signe..."
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendChat()}
              />
              <button onClick={sendChat}><Send size={18} /></button>
            </div>
          </aside>
        </main>
      )}

      {activeTab === "teacher" && (
        <main className="card dashboard">
          <div className="dashboard-head">
            <h2>Tableau de bord enseignant</h2>
            <button className="primary" onClick={loadDashboard}>Actualiser</button>
          </div>
          {!dashboard || dashboard.total_answers === 0 ? (
            <p>Aucune réponse enregistrée pour le moment. Faites quelques tests dans l'espace élève.</p>
          ) : (
            <>
              <div className="stats">
                <div><strong>{dashboard.total_answers}</strong><span>Réponses</span></div>
                <div><strong>{dashboard.correct_answers}</strong><span>Correctes</span></div>
                <div><strong>{dashboard.success_rate}%</strong><span>Taux de réussite</span></div>
              </div>

              <h3>Erreurs fréquentes</h3>
              <table>
                <thead><tr><th>Type d'erreur</th><th>Nombre</th></tr></thead>
                <tbody>
                  {Object.entries(dashboard.errors_by_type).map(([name, count]) => (
                    <tr key={name}><td>{name}</td><td>{count}</td></tr>
                  ))}
                </tbody>
              </table>

              <h3>Dernières réponses</h3>
              <table>
                <thead><tr><th>Élève</th><th>Exercice</th><th>Réponse</th><th>Résultat</th></tr></thead>
                <tbody>
                  {dashboard.recent_answers.map((item, index) => (
                    <tr key={index}>
                      <td>{item.student_name}</td>
                      <td>{item.exercise_id}</td>
                      <td>{item.student_answer}</td>
                      <td>{item.result.is_correct ? "Correcte" : item.result.error_type}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </main>
      )}
    </div>
  );
}

export default App;
