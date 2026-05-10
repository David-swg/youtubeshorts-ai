# 🎮 ShortAI — Guide Setup 10 minutes

## Ce qui va se passer une fois configuré
✅ GitHub publie automatiquement 4 Shorts Roblox par jour (6h, 12h, 18h, 0h)
✅ Ton site Vercel montre tous les Shorts publiés en temps réel
✅ Zéro action de ta part après la configuration

---

## ÉTAPE 1 — Upload sur GitHub (2 min)

1. Va sur **github.com** → connecte-toi
2. Clique **"New repository"**
3. Nom : `shortai` → **Public** → **Create repository**
4. Clique **"uploading an existing file"**
5. Glisse TOUS les fichiers du ZIP dans la page
6. Clique **"Commit changes"**

---

## ÉTAPE 2 — Connecter Vercel (2 min)

1. Va sur **vercel.com** → connecte-toi avec GitHub
2. Clique **"Add New Project"**
3. Sélectionne ton repo `shortai`
4. Clique **"Deploy"** → ton site sera en ligne !

---

## ÉTAPE 3 — Obtenir le token YouTube (3 min)

C'est la seule étape technique. Tu fais ça **une seule fois**.

### 3a. Télécharger client_secrets.json
1. Va sur **console.cloud.google.com**
2. Ton projet → APIs → Identifiants → ton Client OAuth
3. Clique **Télécharger JSON** → sauvegarde le fichier

### 3b. Générer le token une fois sur ton PC
Ouvre le terminal Windows (cherche "cmd" dans le menu démarrer) et tape :

```
pip install google-auth-oauthlib
```

Puis crée un fichier `get_token.py` avec ce contenu :
```python
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_secrets_file(
    'client_secrets.json',
    ['https://www.googleapis.com/auth/youtube.upload']
)
creds = flow.run_local_server(port=0)
print("=== GOOGLE_TOKEN ===")
print(creds.to_json())
print("=== GOOGLE_CLIENT ===")
import json
print(json.dumps(json.load(open('client_secrets.json'))))
```

Lance-le : `python get_token.py`
→ Une fenêtre Google s'ouvre → connecte-toi → autorise
→ Copie les deux valeurs affichées dans le terminal

---

## ÉTAPE 4 — Ajouter les secrets GitHub (3 min)

1. Ton repo GitHub → **Settings** → **Secrets and variables** → **Actions**
2. Clique **"New repository secret"** pour chacun :

| Nom du secret | Valeur |
|--------------|--------|
| `ANTHROPIC_API_KEY` | Ta clé sur console.anthropic.com |
| `ELEVENLABS_API_KEY` | Ta clé sur elevenlabs.io → Profile |
| `GOOGLE_TOKEN` | Le JSON copié à l'étape 3b |
| `GOOGLE_CLIENT` | Le JSON client copié à l'étape 3b |

---

## ÉTAPE 5 — Tester (30 secondes)

1. Ton repo → onglet **Actions**
2. Clique **"ShortAI Bot"** → **"Run workflow"** → **"Run"**
3. Regarde le bot tourner en direct !
4. Après ~5 min → va sur YouTube → ton Short est publié 🎉

---

## C'est fini ! 🎉

Le bot tourne maintenant **pour toujours** sans que tu fasses quoi que ce soit.
Ton site Vercel se met à jour automatiquement avec chaque nouveau Short.

---

## ❓ Problèmes fréquents

**"invalid_grant" dans les logs**
→ Le token a expiré. Relance `get_token.py`, copie le nouveau `GOOGLE_TOKEN` dans les secrets.

**Le workflow ne se lance pas**
→ GitHub Actions peut être désactivé. Repo → Settings → Actions → "Allow all actions"

**ElevenLabs erreur 429**
→ Limite mensuelle atteinte. Attends le mois prochain ou upgrade le plan.
