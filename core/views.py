import requests
from django.shortcuts import render
import random
import logging

logger = logging.getLogger(__name__)

def analyze_quote_mood(quote_text):
    quote_lower = quote_text.lower()
    mood_keywords = {
        'happy': ['happy', 'joy', 'love', 'success', 'achieve', 'dream', 'hope', 'bright', 'smile', 'celebrate'],
        'motivated': ['work', 'hard', 'effort', 'determination', 'persist', 'never give up', 'strength', 'power'],
        'calm': ['peace', 'calm', 'quiet', 'meditation', 'serene', 'tranquil', 'gentle', 'soft'],
        'energetic': ['energy', 'action', 'move', 'run', 'fast', 'quick', 'alive', 'dynamic'],
        'sad': ['sad', 'pain', 'hurt', 'difficult', 'struggle', 'dark', 'loss', 'grief'],
        'inspirational': ['inspire', 'believe', 'faith', 'courage', 'brave', 'overcome', 'rise', 'uplift']
    }

    mood_scores = {}
    for mood, keywords in mood_keywords.items():
        score = sum(1 for keyword in keywords if keyword in quote_lower)
        if score > 0:
            mood_scores[mood] = score

    return max(mood_scores, key=mood_scores.get) if mood_scores else 'inspirational'

def get_random_quote():
    apis = [
        {
            'name': 'ZenQuotes',
            'url': 'https://zenquotes.io/api/random',
            'parser': lambda data: {'text': data[0]['q'], 'author': data[0]['a']}
        },
        {
            'name': 'Quotable',
            'url': 'https://api.quotable.io/random',
            'parser': lambda data: {'text': data['content'], 'author': data['author']}
        }
    ]

    for api in apis:
        try:
            response = requests.get(api['url'], timeout=5)
            response.raise_for_status()
            data = response.json()
            quote = api['parser'](data)
            logger.info(f"Got quote from {api['name']}: {quote['text'][:50]}...")
            return quote
        except Exception as e:
            logger.warning(f"{api['name']} API failed: {e}")

    logger.error("All quote APIs failed")
    return None

def get_music_for_mood(mood):
    try:
        mood_tags = {
            'happy': 'happy',
            'motivated': 'energetic',
            'calm': 'chill',
            'energetic': 'upbeat',
            'sad': 'melancholic',
            'inspirational': 'uplifting'
        }
        tag = mood_tags.get(mood, 'uplifting')
        response = requests.get(
            f"https://api.jamendo.com/v3.0/tracks/?client_id=56d30c95&format=json&limit=10&tags={tag}&include=musicinfo",
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        if data['results']:
            track = random.choice(data['results'])
            return {
                'title': track['name'],
                'artist': track['artist_name'],
                'audio_url': track['audio'],
                'duration': track['duration'],
                'mood': mood,
                'source': 'Jamendo'
            }
    except Exception as e:
        logger.warning(f"Jamendo API failed: {e}")

    try:
        mood_queries = {
            'happy': 'happy upbeat',
            'motivated': 'motivation workout',
            'calm': 'ambient chill',
            'energetic': 'electronic dance',
            'sad': 'sad acoustic',
            'inspirational': 'inspirational instrumental'
        }
        query = mood_queries.get(mood, 'instrumental')
        response = requests.get(f"https://api.deezer.com/search?q={query}&limit=10", timeout=5)
        response.raise_for_status()
        data = response.json()
        if data['data']:
            track = random.choice(data['data'])
            return {
                'title': track['title'],
                'artist': track['artist']['name'],
                'preview_url': track['preview'],
                'duration': track['duration'],
                'mood': mood,
                'source': 'Deezer'
            }
    except Exception as e:
        logger.warning(f"Deezer API failed: {e}")

    fallback_music = {
        'happy': {'title': 'Happy Vibes', 'artist': 'Various Artists', 'mood': mood},
        'motivated': {'title': 'Motivation Station', 'artist': 'Various Artists', 'mood': mood},
        'calm': {'title': 'Peaceful Moments', 'artist': 'Various Artists', 'mood': mood},
        'energetic': {'title': 'Energy Boost', 'artist': 'Various Artists', 'mood': mood},
        'sad': {'title': 'Reflective Melodies', 'artist': 'Various Artists', 'mood': mood},
        'inspirational': {'title': 'Uplifting Sounds', 'artist': 'Various Artists', 'mood': mood}
    }

    return fallback_music.get(mood, fallback_music['inspirational'])

def get_bright_color():
    seeds = ['FF69B4', 'FFD700', '00FA9A', 'FF4500', '00FFFF', 'FF6347', '9370DB', '20B2AA', 'FF1493', '32CD32']
    seed = random.choice(seeds)
    try:
        response = requests.get(f"https://www.thecolorapi.com/scheme?hex={seed}&mode=analogic&count=5", timeout=5)
        response.raise_for_status()
        data = response.json()
        colors = [c['hex']['value'] for c in data['colors']]
        
        # Return 2-3 colors for gradient instead of just one
        selected_colors = random.sample(colors, min(3, len(colors)))
        logger.info(f"Color API working: seed={seed}, selected={selected_colors}")
        return selected_colors
    except requests.exceptions.RequestException as e:
        logger.warning(f"Color API failed: {e}, using fallback colors")
        # Return multiple fallback colors
        fallback_seeds = random.sample(seeds, 3)
        return [f"#{color}" for color in fallback_seeds]

def mood_generator(request):
    quote = get_random_quote()
    if quote is None:
        quote = {'text': 'Every moment is a fresh beginning.', 'author': 'T.S. Eliot'}

    mood = analyze_quote_mood(quote['text'])
    music = get_music_for_mood(mood)
    bg_colors = get_bright_color()  # Now returns list of colors
    
    # Create gradient string for CSS
    gradient = f"linear-gradient(135deg, {', '.join(bg_colors)})"

    logger.info(f"Quote: {quote['text'][:50]}... by {quote['author']}")
    logger.info(f"Detected mood: {mood}")
    logger.info(f"Music: {music['title']} by {music['artist']}")
    logger.info(f"Colors: {bg_colors}")

    return render(request, 'core/mood.html', {
        'quote': quote['text'],
        'author': quote['author'],
        'bg_gradient': gradient,  # Pass gradient instead of single color
        'music': music,
        'mood': mood.capitalize()
    })