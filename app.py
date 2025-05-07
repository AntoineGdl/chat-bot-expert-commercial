import pandas as pd
from flask import Flask, request, jsonify, render_template, redirect, url_for
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests

app = Flask(__name__)
app.secret_key = "votre_cle_secrete"

SEUIL_SIMILARITE = 0.7  # Augmentation du seuil pour être plus sélectif

# Charger le fichier CSV
df = pd.read_csv("static/questions_commerciales.csv", delimiter=';')
questions = df["Questions"].tolist()
reponses = df["réponses"].tolist()

print(f"Questions chargées du CSV : {questions}")
print(f"Nombre de questions : {len(questions)}")

# Préparer le modèle TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(questions)


def trouver_reponse(question_client):
    """Trouve la réponse la plus proche ou utilise l'IA si aucune correspondance."""
    question_vect = vectorizer.transform([question_client])
    similarites = cosine_similarity(question_vect, tfidf_matrix)
    max_similarite = similarites.max()
    index_meilleure_reponse = similarites.argmax()

    # Logs détaillés pour comprendre ce qui se passe
    print(f"Question: '{question_client}'")
    print(f"Similarité maximale: {max_similarite}")
    print(f"Question la plus proche: '{questions[index_meilleure_reponse]}'")
    print(f"Réponse associée: '{reponses[index_meilleure_reponse]}'")

    # Si la similarité est trop faible, utiliser l'IA externe
    if max_similarite < SEUIL_SIMILARITE:
        print("Similarité insuffisante, utilisation de l'IA externe")
        return appeler_ia_externe(question_client)

    print(f"Similarité suffisante ({max_similarite}), utilisation du CSV")
    return reponses[index_meilleure_reponse]


def appeler_ia_externe(question_client):
    """Appelle une IA externe pour générer une réponse."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",  # Endpoint correct pour Ollama
            json={
                "model": "mistral",
                "prompt": f"Tu es un expert commercial. Réponds à cette question en détails: {question_client}",
                "stream": False
            }
        )

        if response.status_code == 200:
            # Structure correcte pour la réponse d'Ollama
            response_json = response.json()
            return response_json.get("response", "Je n'ai pas de réponse pour le moment.")
        else:
            print(f"Erreur API: {response.status_code}")
            return f"Erreur lors de l'appel à l'IA. Code: {response.status_code}"

    except Exception as e:
        print(f"Exception: {str(e)}")
        return "Je ne peux pas répondre à cette question pour le moment. Nos experts sont à votre disposition pour plus d'informations."


@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        try:
            data = request.get_json()
            if not data or "message" not in data:
                return jsonify({"error": "Message manquant ou format invalide"}), 400

            user_message = data["message"]
            force_ia = data.get("force_ia", False)  # Option pour forcer l'IA

            # Si force_ia est True, on utilise directement l'IA externe
            if force_ia:
                bot_response = appeler_ia_externe(user_message)
            else:
                bot_response = trouver_reponse(user_message)

            return jsonify({"bot_response": bot_response})

        except Exception as e:
            print(f"Erreur dans la route /chat: {str(e)}")
            return jsonify({"error": f"Erreur serveur : {str(e)}"}), 500

    return render_template("chat.html")


@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("chat"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)