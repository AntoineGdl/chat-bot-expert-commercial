from flask import Flask, request, jsonify, render_template, redirect, url_for
import requests
import json

app = Flask(__name__)
app.secret_key = "votre_cle_secrete"

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        try:
            # Log des données reçues
            print("Données reçues :", request.data)

            # Vérifie si le JSON est valide
            data = request.get_json()
            if not data or "message" not in data:
                return jsonify({"error": "Message manquant ou format invalide"}), 400

            user_message = data["message"]

            # Appel à l'API externe
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={"model": "mistral", "messages": [
                    {"role": "system", "content": "Vous êtes un expert commercial d'une entreprise. Répondez de manière professionnelle et claire."},
                    {"role": "user", "content": user_message}]},
                stream=True
            )

            if response.status_code != 200:
                return jsonify({"error": f"Erreur avec Ollama : {response.status_code}"}), 500

            # Traitement de la réponse
            bot_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        json_line = json.loads(line)
                        bot_response += json_line.get("message", {}).get("content", "")
                    except json.JSONDecodeError:
                        continue

            return jsonify({"bot_response": bot_response or "Aucune réponse"})

        except Exception as e:
            return jsonify({"error": f"Erreur serveur : {str(e)}"}), 500

    return render_template("chat.html")

@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("chat"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)