# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

Real-world recommendation systems combine many signals (content, past behavior, context, and popularity) to estimate how likely a user is to enjoy each item, then rank results to balance relevance and variety. Platforms like Spotify blend **collaborative filtering** (learning from what similar listeners played) with **content-based filtering** (matching song attributes to your taste). This simulation focuses on transparent **content-based** signals only: it prioritizes songs that match a user on genre and mood while rewarding songs whose energy is close to the user's target, with acoustic preference used as an additional tie-break style signal. The tradeoff is that a purely content-based system tends to recommend "more of the same," which is the filter-bubble risk documented later in the model card.

### Features Used by Each Object

**`Song`** carries these attributes (from `data/songs.csv`):
- `id`, `title`, `artist` — identity fields (not scored)
- `genre` — categorical, used for exact genre match
- `mood` — categorical, used for exact mood match
- `energy` (0–1) — numeric, used for closeness-to-target scoring
- `tempo_bpm`, `valence`, `danceability`, `acousticness` — additional attributes; `acousticness` is used for the acoustic tie-break, the rest are available for future scoring extensions

**`UserProfile`** stores the taste preferences the scorer compares against:
- `favorite_genre` — matched against each song's `genre`
- `favorite_mood` — matched against each song's `mood`
- `target_energy` (0–1) — the energy the user wants; songs are rewarded for being close to it
- `likes_acoustic` (bool) — drives the acoustic vs. non-acoustic tie-break bonus

### Plan Input to Process to Output

Input:
- User preferences: favorite genre, favorite mood, target energy, acoustic preference.
- Song catalog loaded from data/songs.csv.

Process:
- Iterate through each song in the catalog.
- Score each song with the same recipe.
- Store song, score, and explanation text.

Output:
- Sort all songs by score in descending order.
- Return the top k recommendations.

### Scoring Logic Design

Finalized Algorithm Recipe:
- Genre match: `+2.0` points if song genre equals the user's favorite genre.
- Mood match: `+1.0` points if song mood equals the user's favorite mood.
- Energy similarity: `+(1 - abs(song_energy - target_energy))` points, clipped to `[0.0, 1.0]`.
- Acoustic tie-break:
  - `+0.5` if user likes acoustic songs and `acousticness >= 0.60`
  - `+0.5` if user prefers non-acoustic songs and `acousticness <= 0.40`

Final score formula:

`score = genre_points + mood_points + energy_similarity + acoustic_bonus`

Ranking rule:
- Compute score for every song.
- Sort songs by descending score.
- Return top `k` songs.

Potential bias note:
- This system may over-prioritize genre, which can push down strong mood or energy matches from other genres. Genre is worth `+2.0` — twice the mood match — so a same-genre song almost always outranks a different-genre song even when the second is a better mood/energy fit. This is the core filter-bubble risk: the recommender keeps returning the user's favorite genre and rarely surfaces good cross-genre matches.
- Because the catalog is small (28 songs), recommendations also reflect dataset coverage and may under-serve niche tastes. Genres with only one entry can never form a varied result set.
- The acoustic tie-break only rewards the extremes (`>= 0.60` or `<= 0.40`), so mid-acoustic songs (0.40–0.60) get no signal either way.

### Example User Profile (Step 2)

A concrete taste profile the recommender compares against:

```python
user_profile = {
    "favorite_genre": "lofi",
    "favorite_mood": "chill",
    "target_energy": 0.40,
    "likes_acoustic": True,
}
```

This profile is deliberately specific enough to differentiate "chill lofi" from "intense rock": a low `target_energy` (0.40) plus the `lofi`/`chill` anchors will rank calm, acoustic-leaning tracks highly and push high-energy rock/metal to the bottom. It is not too narrow — the energy-closeness term still lets moderately different songs score partial points, so results aren't limited to exact genre+mood twins.

### Data Flow Map

Input:
- User preferences (`favorite_genre`, `favorite_mood`, `target_energy`, `likes_acoustic`)
- Song catalog from `data/songs.csv`

Process:
- Load all songs.
- Loop through songs one by one.
- For each song, compute score components:
  - genre points
  - mood points
  - energy similarity
  - acoustic tie-break bonus
- Store `(song, score, explanation)`.

Output:
- Sort all scored songs by score descending.
- Return top `k` recommendations.

```mermaid
flowchart TD
    A[Input User Preferences] --> B[Load songs.csv]
    B --> C{For each song in catalog}
    A --> C
    C --> D[Check genre match +2.0]
    D --> E[Check mood match +1.0]
    E --> F[Compute energy similarity score]
    F --> G[Apply acoustic tie-break bonus]
    G --> H[Create song score and explanation]
    H --> I[Append to scored list]
    I --> C
    C -->|after last song| J[Sort by score descending]
    J --> K[Select Top K songs]
    K --> L[Output Ranked Recommendations]
```

Prompt to use in a new chat session named "Scoring Logic Design" (with `#file:songs.csv` attached):

"Using #file:songs.csv, help me tune a transparent scoring rule for a small music recommender. I currently use +2.0 for genre match, +1.0 for mood match, and up to +1.0 for energy closeness using 1 - abs(song_energy - target_energy). Suggest 2-3 alternative weight settings and explain tradeoffs (precision vs variety). Also recommend reasonable thresholds for an acousticness tie-break bonus and how large that bonus should be so it does not overpower genre/mood." 

Song features used in this simulation:
- `id`
- `title`
- `artist`
- `genre`
- `mood`
- `energy`
- `tempo_bpm`
- `valence`
- `danceability`
- `acousticness`

UserProfile features used in this simulation:
- `favorite_genre`
- `favorite_mood`
- `target_energy`
- `likes_acoustic`

### Phase 2 Designing the Simulation: Create a User Profile
taste_profile = {
  "favorite_genre": "lofi",
  "favorite_mood": "chill",
  "target_energy": 0.40,
  "likes_acoustic": True
}

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

### Terminal Output Screenshot

The image below shows the formatted recommendation output from running `python -m src.main` with the default profile (`pop` / `happy` / energy `0.8`).

![Terminal recommendations output](assets/terminal_recommendations.png)

### Stress Test with Diverse Profiles

Profiles evaluated in `src/main.py`:
- High-Energy Pop
- Chill Lofi
- Deep Intense Rock
- Edge Case: High Energy + Sad Mood
- Edge Case: Unknown Genre/Mood

Prompt for a new chat session named "System Evaluation" (with `#codebase` context):

"Using #codebase, suggest adversarial user preference profiles for this music recommender so I can stress-test scoring behavior. Include at least 3 edge cases with conflicting or unusual preferences (for example: very high energy + mood that does not exist in the catalog, unknown genre, or acoustic preference that conflicts with energy target). For each profile, explain what failure mode or bias it is testing and what outputs would look suspicious." 

Stress test screenshots:

#### High-Energy Pop
![High-Energy Pop recommendations](assets/stress_high_energy_pop.png)

#### Chill Lofi
![Chill Lofi recommendations](assets/stress_chill_lofi.png)

#### Deep Intense Rock
![Deep Intense Rock recommendations](assets/stress_deep_intense_rock.png)

#### Edge Case: High Energy + Sad Mood
![Edge case high energy sad mood recommendations](assets/stress_edge_case_high_energy_sad_mood.png)

#### Edge Case: Unknown Genre/Mood
![Edge case unknown genre mood recommendations](assets/stress_edge_case_unknown_genre_mood.png)

---

## Sample Recommendation Output

Output from `python -m src.main` for the default High-Energy Pop profile (genre=pop, mood=happy, energy=0.8):

```
Loaded songs: 28

=== Profile: High-Energy Pop ===
Preferences: genre=pop, mood=happy, energy=0.8, likes_acoustic=False
Top 5 recommendations:

1. Sunrise City
   Score   : 4.46
   Reasons :
     - +1.0 genre match
     - +1.0 mood match
     - +1.96 energy closeness (x2.0)
     - +0.5 non-acoustic preference match

2. Rooftop Lights
   Score   : 3.42
   Reasons :
     - +1.0 mood match
     - +1.92 energy closeness (x2.0)
     - +0.5 non-acoustic preference match

3. Gym Hero
   Score   : 3.24
   Reasons :
     - +1.0 genre match
     - +1.74 energy closeness (x2.0)
     - +0.5 non-acoustic preference match

4. Retro Arcade
   Score   : 2.50
   Reasons :
     - +2.00 energy closeness (x2.0)
     - +0.5 non-acoustic preference match

5. Block Party
   Score   : 2.46
   Reasons :
     - +1.96 energy closeness (x2.0)
     - +0.5 non-acoustic preference match
```

The top result, "Sunrise City", is a pop/happy track with energy 0.82 — a full match on genre, mood, energy, and the non-acoustic preference, exactly what the recipe should reward most.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



