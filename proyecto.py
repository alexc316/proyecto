import streamlit as st
import tweepy
from textblob import TextBlob
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import nltk
import re
import qrcode
from io import BytesIO
from PIL import Image
from datetime import datetime, timedelta
import time
import random

nltk.download('punkt')

# --- CREDENCIALES ---
SPOTIFY_CLIENT_ID = 'a64730f41d9a4b97851f683ed0a6209b'
SPOTIFY_CLIENT_SECRET = 'bfacefaaefa14cdab8f86dc8a37ac69c'
TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAEdv0QEAAAAAlQIeQI9FtCptBIVnEAl0Pj1vNUw%3DfJqrzLtdV7rjS1tyXTT2A1PPm1XdXncJDAd87jSByNQNsZ92ND'

# --- AUTENTICACIÓN ---
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))
twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

# --- FUNCIONES ---
def limpiar_texto(texto):
    texto = re.sub(r"http\S+", "", texto)          # quitar URLs
    texto = re.sub(r"@\w+", "", texto)             # quitar menciones
    texto = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]", "", texto)  # quitar emojis y símbolos
    return texto.lower().strip()

def detectar_emocion(texto):
    texto = texto.lower()

    emociones = {
        'amor': [
            'amor', 'enamorado', 'romántico', 'te quiero', 'te amo', 'beso', 'caricia', 'abrazo', 'cariño',
            'querido', 'adorado', 'afecto', 'mi vida', 'mi cielo', 'mi amor', 'te extraño', 'contigo todo',
            'me encantas', 'deseo verte', 'me haces feliz'
        ],
        'celos': [
            'celos', 'celoso', 'celosa', 'posesivo', 'inseguro', 'desconfianza', 'por qué le hablas',
            'te vi con alguien', 'no me gusta eso', 'quién es él', 'quién es ella'
        ],
        'envidia': [
            'envidia', 'envidioso', 'envidiosa', 'ojalá fuera yo', 'me gustaría tener', 'quién pudiera',
            'yo quiero eso', 'por qué no yo', 'qué suerte tienen otros', 'eso debería ser mío'
        ],
        'euforia': [
            'emocionado', 'increíble', 'eufórico', 'euforia', 'wow', 'alucinante', 'extraordinario',
            'fantástico', 'brutal', 'épico', 'no lo creo', 'demasiado bueno', 'exageradamente feliz'
        ],
        'entusiasmo': [
            'entusiasmado', 'feliz', 'contento', 'motivado', 'emocionante', 'genial', 'me encanta',
            'qué bien', 'ánimo', 'ímpetu', 'estoy listo', 'con ganas', 'super feliz', 'a darle'
        ],
        'alegría': [
            'alegría', 'sonrisa', 'felicidad', 'risa', 'diversión', 'me alegra', 'gracias',
            'afortunado', 'júbilo', 'regocijo', 'estoy feliz', 'día perfecto', 'maravilloso'
        ],
        'serenidad': [
            'tranquilo', 'sereno', 'paz', 'calma', 'relajado', 'zen', 'sosiego', 'quietud',
            'equilibrio', 'momento de paz', 'todo en orden', 'sin preocupaciones'
        ],
        'melancolía': [
            'melancolía', 'nostalgia', 'extraño', 'soledad', 'recuerdo', 'pasado', 'vacío',
            'añoranza', 'remordimiento', 'me hace falta', 'tiempos mejores', 'cuando todo era mejor'
        ],
        'tristeza': [
            'triste', 'llorando', 'dolor', 'deprimido', 'desilusión', 'pena', 'sufrimiento',
            'desesperanza', 'desdicha', 'lágrimas', 'me siento mal', 'nada tiene sentido', 'no puedo más'
        ],
        'enojo': [
            'enojo', 'molesto', 'furioso', 'enojado', 'coraje', 'odio', 'fastidio', 'irritación',
            'exasperación', 'me harté', 'ya basta', 'no lo soporto', 'maldito', 'me da rabia'
        ],
        'frustración': [
            'frustrado', 'hartazgo', 'cansado', 'agotado', 'rendido', 'harto', 'desánimo',
            'desesperación', 'no me sale nada', 'no puedo más', 'nada funciona', 'todo mal'
        ],
        'miedo': [
            'miedo', 'temor', 'miedoso', 'asustado', 'pánico', 'terror', 'aprensión',
            'me da cosa', 'tengo miedo', 'me asusta', 'inseguridad'
        ],
        'sorpresa': [
            'sorpresa', 'inesperado', 'inopinado', 'impactante', 'asombro', 'no lo esperaba',
            'qué locura', 'me sorprendió', 'de la nada', 'no lo puedo creer'
        ],
        'gratitud': [
            'gracias', 'agradecido', 'agradecida', 'apreciado', 'reconocido', 'mil gracias',
            'te lo agradezco', 'muy agradecido', 'gracias de corazón'
        ],
        'orgullo': [
            'orgullo', 'orgulloso', 'orgullosa', 'satisfecho', 'triunfante', 'me siento realizado',
            'lo logré', 'meta cumplida', 'valió la pena'
        ],
        'vergüenza': [
            'vergüenza', 'avergonzado', 'avergonzada', 'culpable', 'remordimiento', 'metí la pata',
            'me da pena', 'no quería hacerlo', 'fue mi culpa'
        ],
        'esperanza': [
            'esperanza', 'esperanzado', 'esperanzada', 'optimista', 'fe', 'todo saldrá bien',
            'tengo fe', 'creo en el cambio', 'confío'
        ],
        'desesperanza': [
            'desesperanza', 'desesperado', 'desesperada', 'desmoralizado', 'abatido', 'todo está perdido',
            'ya no importa', 'sin salida', 'no hay esperanza'
        ]
    }

    emojis = {
        'alegría': ['😂', '😊', '😄', '😁', '😃'],
        'tristeza': ['😢', '😭', '💔', '😞'],
        'enojo': ['😠', '😡'],
        'amor': ['❤️', '😍', '😘', '💖'],
        'neutral': ['🙂', '😐'],
        'frustración': ['😣', '😤'],
        'melancolía': ['🥺', '😔'],
    }

    # Detección por palabras clave
    for emocion, palabras in emociones.items():
        if any(palabra in texto for palabra in palabras):
            return emocion

    # Detección por emojis
    for emocion, simbolos in emojis.items():
        if any(simbolo in texto for simbolo in simbolos):
            return emocion

    # Detección por análisis de sentimiento (si no se detectó nada)
    blob = TextBlob(texto)
    polaridad = blob.sentiment.polarity
    print(f"Polaridad detectada: {polaridad}")  # Puedes comentar esta línea si no quieres verla

    if polaridad > 0.4:
        return 'alegría'
    elif polaridad > 0.1:
        return 'entusiasmo'
    elif -0.1 <= polaridad <= 0.1:
        return 'neutral'
    elif -0.4 < polaridad < -0.1:
        return 'melancolía'
    elif polaridad <= -0.4:
        return 'tristeza'

    return 'neutral'

def emocion_a_genero(emocion):
    return {
        'euforia': 'electronic',
        'entusiasmo': 'dance',
        'alegría': 'pop',
        'serenidad': 'classical',
        'neutral': 'chill',
        'melancolía': 'jazz',
        'tristeza': 'acoustic',
        'enojo': 'metal',
        'frustración': 'grunge',
        'amor': 'romantic',
        'celos': 'blues',
        'envidia': 'hip-hop',
        'indefinida': 'world'
    }.get(emocion, 'pop')


def buscar_artista(texto):
    palabras = texto.split()
    posibles_nombres = [p for p in palabras if p.istitle()]
    if not posibles_nombres:
        return None
    artista = posibles_nombres[0]
    try:
        time.sleep(1)
        resultados = sp.search(q=artista, type='artist', limit=1)
        if resultados and resultados.get('artists') and resultados['artists']['items']:
            return resultados['artists']['items'][0]['name']
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 429:
            st.error("Spotify está rechazando demasiadas solicitudes. Intenta más tarde.")
            return None
    return None

def recomendar_playlist_personalizada(emocion, texto):
    artista = buscar_artista(texto)
    
    if emocion == "amor" and artista:
        q = f"{artista} amor"
    else:
        genero = emocion_a_genero(emocion)
        # Mejora el query para evitar 'genre:' que puede fallar
        q = f"{genero} mood"  # Por ejemplo: "dance mood" o "grunge mood"

    try:
        time.sleep(1)
        resultados = sp.search(q=q, type='playlist', limit=10)
        playlists = resultados.get('playlists', {}).get('items', [])
        urls = []
        for p in playlists:
            if not p:
                continue
            external_urls = p.get('external_urls')
            if external_urls and 'spotify' in external_urls:
                urls.append(external_urls['spotify'])
        if urls:
            return random.choice(urls)
        else:
            st.warning(f"No se encontraron playlists con el término: {q}")
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 429:
            st.error("⚠️ Límite de solicitudes alcanzado en Spotify. Intenta de nuevo en unos segundos.")
    return None

def obtener_tweet(usuario):
    try:
        user = twitter_client.get_user(username=usuario)
        tweets = twitter_client.get_users_tweets(id=user.data.id, max_results=5, exclude=['retweets', 'replies'])
        if tweets.data:
            return tweets.data[0].text
        else:
            return "No se encontró ningún tweet reciente."
    except tweepy.TooManyRequests:
        hora_reintento = datetime.now() + timedelta(minutes=15)
        return f"⚠️ Has hecho muchas solicitudes. Intenta de nuevo a las {hora_reintento.strftime('%H:%M:%S')}"
    except Exception as e:
        return f"Error: {str(e)}"

def generar_qr_url(url):
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    return Image.open(buf)

# --- INTERFAZ ---
st.title("🎧 Emocify")

opcion = st.radio("¿Desde dónde quieres analizar el texto?", ("Twitter", "Facebook (manual)"))

if opcion == "Twitter":
    usuario = st.text_input("Ingresa el nombre de usuario de Twitter (sin @):")
    if st.button("Analizar y recomendar"):
        tweet = obtener_tweet(usuario)
        if tweet.startswith("Error") or tweet.startswith("⚠️"):
            st.error(tweet)
        else:
            texto = limpiar_texto(tweet)
            emocion = detectar_emocion(texto)
            url = recomendar_playlist_personalizada(emocion, texto)
            st.markdown(f"**Texto original:** {tweet}")
            st.markdown(f"**Emoción detectada:** {emocion}")
            if url:
                st.markdown(f"[🎧 Escuchar playlist recomendada]({url})")
                img = generar_qr_url(url)
                st.image(img, caption="Escanea el QR para abrir la playlist")
            else:
                st.warning("No se pudo generar la playlist para este texto.")
else:
    texto_manual = st.text_area("Pega aquí tu texto:")
    if st.button("Analizar manual"):
        texto = limpiar_texto(texto_manual)
        emocion = detectar_emocion(texto)
        url = recomendar_playlist_personalizada(emocion, texto)
        st.markdown(f"**Emoción detectada:** {emocion}")
        if url:
            st.markdown(f"[🎧 Escuchar playlist recomendada]({url})")
            img = generar_qr_url(url)
            st.image(img, caption="Escanea el QR para abrir la playlist")
        else:
            st.warning("No se pudo generar la playlist para este texto.")
