# Utilise une image Python officielle
FROM python:3.10-slim

# Définit le répertoire de travail
WORKDIR /app

# Copie les fichiers nécessaires
COPY requirements.txt requirements.txt
COPY app.py app.py

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Expose le port 5000
EXPOSE 5000

# Commande pour démarrer l'application
CMD ["python", "app.py"]