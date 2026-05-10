"""
ShortAI Bot — GitHub Actions
Génère un Short Roblox complet et le publie sur YouTube.
Lance automatiquement toutes les 6h par GitHub.
"""
import os, json, random, textwrap, logging
from datetime import datetime
from pathlib import Path

import anthropic, requests
from PIL import Image, ImageDraw, ImageFont
import moviepy.editor as mpy
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# ── Config ──
ANTHROPIC_API_KEY  = os.environ["ANTHROPIC_API_KEY"]
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
GOOGLE_TOKEN       = os.environ["GOOGLE_TOKEN"]   # JSON string
GOOGLE_CLIENT      = os.environ["GOOGLE_CLIENT"]  # JSON string
VOICE_ID           = "pNInz6obpgDQGcFmaJgB"       # Adam
OUT                = Path("out"); OUT.mkdir(exist_ok=True)
LOG_FILE           = "published.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s",
                    handlers=[logging.StreamHandler()])
log = logging.getLogger(__name__)

# ── Palettes RGB ──
PALETTES = [
    {"bg1":(15,5,40),  "bg2":(80,10,160), "txt":(255,220,80),  "acc":(200,100,255)},
    {"bg1":(5,20,50),  "bg2":(10,80,200), "txt":(80,220,255),  "acc":(255,255,255)},
    {"bg1":(40,5,5),   "bg2":(160,20,20), "txt":(255,200,50),  "acc":(255,120,50)},
    {"bg1":(5,30,20),  "bg2":(10,130,60), "txt":(100,255,180), "acc":(200,255,80)},
    {"bg1":(20,5,40),  "bg2":(110,10,190),"txt":(255,100,200), "acc":(255,220,100)},
    {"bg1":(30,15,5),  "bg2":(140,60,10), "txt":(255,180,80),  "acc":(100,220,255)},
]

TOPICS = [
    "nouvelle mise à jour explosive de Blox Fruits avec un fruit légendaire jamais vu",
    "nouveau jeu Roblox qui dépasse 1 million de joueurs en 24h",
    "événement Roblox avec des items gratuits légendaires à récupérer maintenant",
    "astuce secrète dans Jailbreak que 99% des joueurs ne connaissent pas",
    "pet ultra rare dans Pet Simulator X qui vaut des millions de gemmes",
    "mise à jour d'Adopt Me avec un animal légendaire inédit",
    "glitch incroyable découvert dans Tower of Hell par un joueur",
    "collaboration Roblox x grande marque mondiale qui choque la communauté",
    "nouveau mode de jeu dans Murder Mystery 2 qui rend tout le monde fou",
    "mise à jour de Brookhaven avec des rôles et maisons inédites",
    "joueur français bat le record mondial sur Roblox",
    "nouveau skin légendaire dans Arsenal que tout le monde veut",
]

# ══════════════════════════════════════════════
# ÉTAPE 1 — Générer contenu IA
# ══════════════════════════════════════════════
def generate_content():
    log.info("🤖 Génération du contenu IA...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    topic  = random.choice(TOPICS)

    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=600,
        system="""Tu es un créateur YouTube Shorts viral spécialiste Roblox FR.
Réponds UNIQUEMENT en JSON valide, sans markdown, sans backticks.
Format strict:
{"title":"titre YouTube accrocheur max 70 chars avec emoji","script":"narration 45-55 mots, phrases courtes percutantes, commence par chiffre ou question choc","description":"description SEO YouTube 2 phrases","hashtags":["Roblox","RobloxShorts","RobloxFR","Gaming","Shorts"],"big_text":"3 MOTS MAJUSCULES pour la vidéo"}""",
        messages=[{"role":"user","content":f"Génère un Short Roblox viral sur : {topic}. Ultra énergique, style joueur Roblox FR."}]
    )
    data = json.loads(msg.content[0].text.strip().replace("```json","").replace("```","").strip())
    log.info(f"✅ Généré : {data['title']}")
    return data

# ══════════════════════════════════════════════
# ÉTAPE 2 — Voix ElevenLabs
# ══════════════════════════════════════════════
def generate_voice(script: str) -> str:
    log.info("🎙️ Génération voix ElevenLabs...")
    path = str(OUT / "voice.mp3")
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type":"application/json","Accept":"audio/mpeg"},
        json={"text":script,"model_id":"eleven_multilingual_v2",
              "voice_settings":{"stability":0.35,"similarity_boost":0.88,"style":0.6,"use_speaker_boost":True}},
        timeout=60
    )
    r.raise_for_status()
    with open(path,"wb") as f: f.write(r.content)
    log.info("✅ Voix générée")
    return path

# ══════════════════════════════════════════════
# ÉTAPE 3 — Créer vidéo MP4
# ══════════════════════════════════════════════
def create_video(content: dict, audio_path: str) -> str:
    log.info("🎬 Création de la vidéo...")
    W, H   = 1080, 1920
    pal    = random.choice(PALETTES)
    c1,c2  = pal["bg1"], pal["bg2"]

    # Fond dégradé
    img  = Image.new("RGB",(W,H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y/H
        draw.line([(0,y),(W,y)], fill=tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3)))

    # Cercles déco
    for _ in range(10):
        cx,cy = random.randint(0,W), random.randint(0,H)
        r     = random.randint(60,280)
        a     = pal["acc"]
        draw.ellipse([cx-r,cy-r,cx+r,cy+r], outline=(a[0],a[1],a[2]), width=3)

    # Polices
    def font(size):
        for name in ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
            if os.path.exists(name):
                return ImageFont.truetype(name, size)
        return ImageFont.load_default()

    f_big  = font(110)
    f_med  = font(58)
    f_sm   = font(38)

    # Titre en haut
    big = content.get("big_text","ROBLOX 🎮").upper()
    draw.text((W//2, 220), big, font=f_big, fill=pal["txt"], anchor="mm",
              stroke_width=4, stroke_fill=(0,0,0))

    # Ligne
    draw.rectangle([80,300,W-80,308], fill=pal["acc"])

    # Script au centre
    lines = textwrap.wrap(content["script"], width=25)
    y0    = H//2 - len(lines)*70//2
    for i,line in enumerate(lines):
        y = y0 + i*74
        draw.text((W//2+3,y+3), line, font=f_med, fill=(0,0,0), anchor="mm")
        draw.text((W//2,y),     line, font=f_med, fill=(255,255,255), anchor="mm")

    # Hashtags bas
    tags = "  ".join(f"#{t}" for t in content["hashtags"][:4])
    draw.text((W//2, H-220), tags, font=f_sm, fill=pal["acc"], anchor="mm")

    # Branding
    draw.text((W//2, H-130), "🎮 ShortAI Roblox", font=f_sm, fill=(160,160,160), anchor="mm")

    # Sauvegarder image
    bg_path = str(OUT/"bg.png")
    img.save(bg_path)

    # Assembler vidéo
    audio = mpy.AudioFileClip(audio_path)
    dur   = min(audio.duration + 0.3, 58)
    video = mpy.ImageClip(bg_path).set_duration(dur).set_audio(audio)
    out   = str(OUT/"short.mp4")
    video.write_videofile(out, fps=30, codec="libx264", audio_codec="aac", logger=None)
    log.info(f"✅ Vidéo créée : {out}")
    return out

# ══════════════════════════════════════════════
# ÉTAPE 4 — Auth YouTube
# ══════════════════════════════════════════════
def get_youtube():
    log.info("🔐 Connexion YouTube...")
    # Écrire les fichiers JSON depuis les secrets
    token_path  = OUT/"token.json"
    client_path = OUT/"client.json"
    token_path.write_text(GOOGLE_TOKEN)
    client_path.write_text(GOOGLE_CLIENT)

    creds = Credentials.from_authorized_user_file(str(token_path), ["https://www.googleapis.com/auth/youtube.upload"])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Mettre à jour le token (dans les logs pour que tu puisses copier le nouveau)
        log.info(f"🔄 Token rafraîchi. Nouveau token:\n{creds.to_json()}")
        log.warning("⚠️  IMPORTANT: Copie le token ci-dessus dans ton secret GitHub GOOGLE_TOKEN !")

    return build("youtube","v3",credentials=creds)

# ══════════════════════════════════════════════
# ÉTAPE 5 — Publier sur YouTube
# ══════════════════════════════════════════════
def upload(youtube, content: dict, video_path: str) -> str:
    log.info("📤 Upload YouTube...")
    desc = (content["description"] + "\n\n" +
            " ".join(f"#{t}" for t in content["hashtags"]) +
            "\n\n#Shorts #YouTube #Roblox #Gaming")

    body = {
        "snippet": {
            "title":       content["title"],
            "description": desc,
            "tags":        content["hashtags"] + ["Shorts","Roblox","Gaming","RobloxFR"],
            "categoryId":  "20",
        },
        "status": {
            "privacyStatus":           "public",
            "selfDeclaredMadeForKids": False,
        }
    }
    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
    req   = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status: log.info(f"   {int(status.progress()*100)}%")

    url = f"https://youtube.com/shorts/{resp['id']}"
    log.info(f"✅ Publié ! → {url}")
    return url

# ══════════════════════════════════════════════
# SAUVEGARDER LE LOG
# ══════════════════════════════════════════════
def save_log(content: dict, url: str):
    history = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            history = json.load(f)
    history.insert(0, {
        "date":  datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "title": content["title"],
        "url":   url,
        "topic": content.get("big_text",""),
    })
    with open(LOG_FILE,"w") as f:
        json.dump(history[:50], f, ensure_ascii=False, indent=2)

# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════
if __name__ == "__main__":
    log.info("="*50)
    log.info(f"🚀 ShortAI Bot — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    log.info("="*50)

    content    = generate_content()
    audio_path = generate_voice(content["script"])
    video_path = create_video(content, audio_path)
    youtube    = get_youtube()
    url        = upload(youtube, content, video_path)
    save_log(content, url)

    log.info("🎉 DONE !")
