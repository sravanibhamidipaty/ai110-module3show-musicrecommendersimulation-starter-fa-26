from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

GENRE_MATCH_POINTS = 1.0
MOOD_MATCH_POINTS = 1.0
ENERGY_WEIGHT = 2.0


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        ranked = sorted(
            self.songs,
            key=lambda song: _score_song(
                song_dict=_song_to_dict(song),
                user_genre=user.favorite_genre,
                user_mood=user.favorite_mood,
                target_energy=user.target_energy,
                likes_acoustic=user.likes_acoustic,
            )["total"],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        breakdown = _score_song(
            song_dict=_song_to_dict(song),
            user_genre=user.favorite_genre,
            user_mood=user.favorite_mood,
            target_energy=user.target_energy,
            likes_acoustic=user.likes_acoustic,
        )
        reasons = breakdown["reasons"]
        return f"Score {breakdown['total']:.2f}. " + " ".join(reasons)


def _song_to_dict(song: Song) -> Dict:
    """Convert a Song dataclass instance into a dictionary."""
    return {
        "id": song.id,
        "title": song.title,
        "artist": song.artist,
        "genre": song.genre,
        "mood": song.mood,
        "energy": song.energy,
        "tempo_bpm": song.tempo_bpm,
        "valence": song.valence,
        "danceability": song.danceability,
        "acousticness": song.acousticness,
    }


def _score_song(
    song_dict: Dict,
    user_genre: str,
    user_mood: str,
    target_energy: float,
    likes_acoustic: Optional[bool],
) -> Dict:
    """Compute score breakdown for one song against the user preference profile."""
    score = 0.0
    reasons: List[str] = []

    if song_dict["genre"].strip().lower() == user_genre.strip().lower():
        score += GENRE_MATCH_POINTS
        reasons.append(f"+{GENRE_MATCH_POINTS:.1f} genre match")

    if song_dict["mood"].strip().lower() == user_mood.strip().lower():
        score += MOOD_MATCH_POINTS
        reasons.append(f"+{MOOD_MATCH_POINTS:.1f} mood match")

    # Base energy closeness is in [0, 1]; experiment scales it by ENERGY_WEIGHT.
    energy_gap = abs(float(song_dict["energy"]) - float(target_energy))
    energy_bonus = max(0.0, 1.0 - energy_gap) * ENERGY_WEIGHT
    score += energy_bonus
    reasons.append(
        f"+{energy_bonus:.2f} energy closeness (x{ENERGY_WEIGHT:.1f})")

    # Small tie-breaker bonus based on acoustic preference.
    acousticness = float(song_dict.get("acousticness", 0.0))
    if likes_acoustic is True and acousticness >= 0.60:
        score += 0.5
        reasons.append("+0.5 acoustic preference match")
    elif likes_acoustic is False and acousticness <= 0.40:
        score += 0.5
        reasons.append("+0.5 non-acoustic preference match")

    return {"total": score, "reasons": reasons}


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                }
            )
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user prefs; returns (score, reasons) per the recipe."""
    user_genre = user_prefs.get("favorite_genre", user_prefs.get("genre", ""))
    user_mood = user_prefs.get("favorite_mood", user_prefs.get("mood", ""))
    target_energy = float(
        user_prefs.get("target_energy", user_prefs.get("energy", 0.5))
    )
    likes_acoustic = user_prefs.get("likes_acoustic")

    breakdown = _score_song(
        song_dict=song,
        user_genre=user_genre,
        user_mood=user_mood,
        target_energy=target_energy,
        likes_acoustic=likes_acoustic,
    )
    return breakdown["total"], breakdown["reasons"]

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    user_genre = user_prefs.get("favorite_genre", user_prefs.get("genre", ""))
    user_mood = user_prefs.get("favorite_mood", user_prefs.get("mood", ""))
    target_energy = float(user_prefs.get(
        "target_energy", user_prefs.get("energy", 0.5)))
    likes_acoustic = user_prefs.get("likes_acoustic")

    scored: List[Tuple[Dict, float, str]] = []
    for song in songs:
        breakdown = _score_song(
            song_dict=song,
            user_genre=user_genre,
            user_mood=user_mood,
            target_energy=target_energy,
            likes_acoustic=likes_acoustic,
        )
        explanation = "Score recipe: " + ", ".join(breakdown["reasons"])
        scored.append((song, breakdown["total"], explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
