<<<<<<< HEAD
FROM python:3.9-slim

WORKDIR /app

# Copier d'abord requirements.txt pour mieux utiliser le cache Docker
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers
COPY . .

# Exposer le port
EXPOSE 7860

# Lancer Streamlit
=======
FROM python:3.9-slim

WORKDIR /app

# Copier d'abord requirements.txt pour mieux utiliser le cache Docker
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers
COPY . .

# Exposer le port
EXPOSE 7860

# Lancer Streamlit
>>>>>>> ba3058378dee71b1a95fe6c4ef390310c261661d
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0", "--server.headless=true"]