"""
Script à lancer UNE SEULE FOIS sur ton PC pour générer le token YouTube.

1. Installe : pip install google-auth-oauthlib
2. Mets client_secrets.json dans le même dossier
3. Lance : python get_token.py
4. Copie les valeurs dans les secrets GitHub
"""
import json
from google_auth_oauthlib.flow import InstalledAppFlow

print("\n🔐 Génération du token YouTube...")
print("Une fenêtre de navigateur va s'ouvrir.\n")

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secrets.json',
    scopes=['https://www.googleapis.com/auth/youtube.upload']
)
creds = flow.run_local_server(port=0)

print("\n" + "="*60)
print("✅ Copie ces valeurs dans tes secrets GitHub :")
print("="*60)

print("\n📋 Secret : GOOGLE_TOKEN")
print("-"*40)
print(creds.to_json())

print("\n📋 Secret : GOOGLE_CLIENT")
print("-"*40)
with open('client_secrets.json') as f:
    print(json.dumps(json.load(f)))

print("\n" + "="*60)
print("✅ Copie tout ça dans GitHub → Settings → Secrets !")
print("="*60 + "\n")
