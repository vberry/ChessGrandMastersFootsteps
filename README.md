# ChessGrandMastersFootsteps

**ChessGrandMastersFootsteps** est une application éducative qui vous permet de progresser aux échecs en rejouant des parties historiques de grands maîtres.  
Votre objectif est d'identifier le meilleur coup dans des positions critiques, avec un retour immédiat fourni par le moteur d'échecs **Stockfish**.

---

## 🎯 Objectif

- Renforcer votre intuition tactique  
- Comprendre les raisonnements des grands maîtres  
- Apprendre en jouant, avec deux modes adaptés à votre style  

---

## 🕹️ Modes de jeu

### Mode Vies

- **Facile** : 5 vies  
- **Normal** : 3 vies  
- **Difficile** : 1 vie  

> Chaque erreur coûte une vie. Le but est d'avoir le plus de points sachant que moins de vies on utilise, plus on gagne de points

### Mode Timer

- **Facile** : 3 minutes par coup  
- **Normal** : 1 minute par coup  
- **Difficile** : 30 secondes par coup  

> Si le temps est écoulé, vous pouvez encore jouer, mais perdez 5 points.

---

## 🏆 Système de notation

### Coups de mat :

- Mat que le maître n'a pas vu : **+20 pts**  
- Même mat que le maître : **+15 pts**  
- Mat plus lent : **+5 pts**  
- Le maître a vu un mat, vous non : **-5 pts**  
- Mat immédiat : **+20 pts (bonus)**

### Autres coups :

- Meilleur que celui du maître : **+20 pts**  
- Presque aussi bon : **+15 pts**  
- Bonne alternative : **+10 pts**  
- Moins bon mais acceptable : **+5 pts**  
- Inférieur : **0 pt**  
- Grosse erreur : **-10 pts**

---

## 📂 Structure du projet

- ChessGrandMastersFootsteps/
  - run.py
  - app/
    - controllers/
    - dossierPGN/
    - models/
    - routes/
    - services/
    - static/
    - templates/
    - utils/
    - views/
  - chess/
  - docs/
  - .gitignore

---

## ⚙️ Lancer le projet dans GitHub Codespaces

1. Le fichier `devcontainer/devcontainer.json`installe automatiquement ce qu'il faut au démarrage du codespace.

2. Lancer le serveur :
   ```bash
   python3 run.py
   ```
📌 Toutes les autres dépendances sont déjà prises en charge par uv.

---

## 📚 Générer la documentation

Pour générer et consulter la documentation du projet, suivez ces étapes :

1. Eventuellement installer les dépendances nécessaires :
   ```bash
   uv add mkdocs
   uv add mkdocs-material
   uv add mkdocstrings
   uv add mkdocstrings-python
   ```
2. Lancer le serveur de documentation :
   ```bash
   mkdocs serve   
   ```
3. Accéder à la documentation dans votre navigateur à l'adresse :
   ```
   http://127.0.0.1:8000
   ```
---

## ✅ Lancer mypy

Pour tester les codes avec mypy :

Eventuellement installer mypy :
   ```bash
   uv add mypy
   ```
puis:
    mypy --disable-error-code import-untyped .
    (à exécuter depuis la racine du projet)

A régler : si on exécute seulement mypy, il y a des problèmes d'import pour tout ce qui concerne chess et flask.
---


### ✅ Lancer les tests unitaires avec `pytest`

Pour exécuter les tests unitaires du projet :

Eventuellement installer pytest :
   ```bash
   uv add pytest
   ```
puis:
   ```bash
   pytest
   (à executer depuis la racine du projet)
   ```

---

## ➕ Ajouter de nouvelles parties à suivre

Pour l'instant, il n'est pas possible d'ajouter une partie PGN depuis l'interface utilisateur.
Pour enrichir la base de données, placez simplement vos fichiers .pgn dans le dossier :

- app/
    - dossierPGN/

---

## 🧠 Conseils pour progresser

Analysez toujours la position avant de jouer
Identifiez les motifs tactiques classiques (fourchette, clouage, enfilade, etc.)
Comparez votre coup avec celui du maître et apprenez de l'analyse de Stockfish
Prenez votre temps dans le mode Vies ; entraînez votre rapidité avec le mode Timer
Bon jeu et bonne progression 🎓♟️
