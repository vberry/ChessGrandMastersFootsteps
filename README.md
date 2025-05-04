# ChessGrandMastersFootsteps

**ChessGrandMastersFootsteps** est une application éducative qui vous permet de progresser aux échecs en rejouant des parties historiques de grands maîtres.  
Votre objectif est d’identifier le meilleur coup dans des positions critiques, avec un retour immédiat fourni par le moteur d’échecs **Stockfish**.

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

- Mat que le maître n’a pas vu : **+20 pts**  
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

1. Installer `uv` :
   ```bash
   pip install uv
2. Créer un environnement virtuel :
    ```bash
    uv venv
3. Activer l’environnement :
    ```bash
    source .venv/bin/activate
4. Réinstaller Flask (si nécessaire) :
    ```bash
    uv add flask
5. Lancer le serveur :
    ```bash
    python3 run.py
📌 Toutes les autres dépendances sont déjà prises en charge par uv.

---

## ➕ Ajouter de nouvelles parties

Pour l’instant, il n’est pas possible d’ajouter une partie PGN depuis l’interface utilisateur.
Pour enrichir la base de données, placez simplement vos fichiers .pgn dans le dossier :

- app/
    - dossierPGN/

---

## 🧠 Conseils pour progresser

Analysez toujours la position avant de jouer
Identifiez les motifs tactiques classiques (fourchette, clouage, enfilade, etc.)
Comparez votre coup avec celui du maître et apprenez de l’analyse de Stockfish
Prenez votre temps dans le mode Vies ; entraînez votre rapidité avec le mode Timer
Bon jeu et bonne progression 🎓♟️

