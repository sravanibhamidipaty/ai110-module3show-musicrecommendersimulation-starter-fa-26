# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

A content-based music recommender that matches songs to a listener's stated taste.

---

## 2. Intended Use

VibeFinder suggests songs from a small catalog based on a user's favorite genre, favorite mood, target energy, and acoustic preference. It generates a ranked top-5 list with a plain-language reason for each pick.

- **What it generates:** an explainable, ranked list of song suggestions.
- **What it assumes:** the user can describe their taste as a few simple preferences, and every song is honestly tagged.
- **Who it's for:** this is a **classroom simulation** for learning how recommenders work — not a production system for real listeners.

---

## 3. How the Model Works

Think of the recommender as a judge giving every song a point total, then lining the songs up from highest to lowest and handing back the top few.

For each song, the judge looks at four things about the listener's taste:

- **Genre** — if the song's genre is the listener's favorite, it earns points. This is the strongest signal.
- **Mood** — if the song's mood matches the listener's favorite mood, it earns points too, but fewer than genre.
- **Energy** — the listener says how energetic they want their music (a number from calm to intense). A song scores higher the *closer* its energy is to that target — so a song that's exactly right beats one that's a little too mellow or too hyped. This is about matching a vibe, not just "louder is better."
- **Acoustic preference** — a small bonus if the song's acoustic-ness lines up with whether the listener likes acoustic or produced music.

The judge adds those pieces into one score and also writes down *why* it gave those points ("+1.0 genre match", "+1.96 energy closeness"), so the recommendation is explainable, not a black box. To pick recommendations, the system scores every song in the catalog and sorts the whole list by score, then returns the top 5.

**What changed from the starter:** the starter left the scoring function empty. I implemented it to return both a number and a list of reasons, and (in the experiment) I tuned the weights — doubling the energy weight and adjusting genre — which shifted the rankings toward "energy vibe" matches and revealed the filter-bubble behavior documented below.

---

## 4. Data

- **Size:** 28 songs (expanded from the 18-song starter by adding 10 tracks).
- **Features per song:** id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness.
- **Coverage:** 25 genres and 24 moods, from pop, lofi, and rock to techno, doom metal, funk, and new age. Energy spans 0.20–0.94.
- **What I added:** genres and moods missing from the starter (world, chiptune, fusion, soul, future bass, etc.) so results aren't limited to a few styles.
- **What's missing:** the catalog is tiny compared to a real service, several genres have only one entry, and there's no listening history — so the system can only do content matching, not collaborative filtering.

---

## 5. Strengths

- **Clear-taste profiles work well.** When a user's genre, mood, and energy all point the same way (e.g. Chill Lofi at energy 0.40), the top results are exactly the right tracks (Midnight Coding, Library Rain, Focus Flow) and every pick lines up with intuition.
- **Explanations are honest.** Each recommendation lists the exact points earned, so it's easy to see *why* a song ranked where it did.
- **Graceful fallback.** For unknown genres/moods, the system doesn't crash or invent matches — it falls back to energy closeness and still returns a sensible calm-or-hyped list.

---

## 6. Limitations and Bias

This system can create a filter bubble because songs that are closest in energy keep rising to the top, even when mood does not match. During the experiment, I doubled energy weight and cut genre weight in half, and this made high-energy songs dominate many profiles. That is why tracks like Gym Hero still show up for users who asked for happy pop or even conflicting moods, because its energy is close and it also gets genre points for pop. Another limitation is that the catalog is small and mood labels are narrow, so users with uncommon moods or genres get results based mostly on energy distance instead of true taste fit.

Put plainly for a non-programmer: "Gym Hero" keeps showing up for people who just want "Happy Pop" because it *is* pop (so it grabs the genre points) and its energy is very close to what those users asked for. The system rewards being loud-and-pop more than it rewards actually being *happy*, so an intense workout song sneaks into a happy playlist. That's the bias — the math notices intensity and genre far more than it notices emotion.

---

## 7. Evaluation

I tested five profiles: High-Energy Pop, Chill Lofi, Deep Intense Rock, Edge Case High Energy + Sad Mood, and Edge Case Unknown Genre/Mood. I looked at the top 5 songs and checked whether the reasons matched what the profile asked for. The results were partly accurate and partly just different after the weight shift: genre mattered less, and energy closeness took over the ranking. The most surprising pattern was that Gym Hero kept appearing for multiple profiles, not because it matched mood well, but because its energy is very close to high-energy targets and it is in the pop genre. In plain language, the model is good at matching "vibe intensity" but weaker at understanding emotional intent.

**Profile-pair comparisons:**

- **High-Energy Pop vs. Chill Lofi:** Pop pulled bright, high-energy tracks (Sunrise City, Rooftop Lights) while Lofi pulled calm, acoustic ones (Midnight Coding, Library Rain). This makes sense — the target energy (0.8 vs 0.4) and acoustic preference (False vs True) flip, so the two lists share almost no songs. This is the clearest sign the preferences actually steer the output.
- **Chill Lofi vs. Deep Intense Rock:** opposite ends of the energy scale. Lofi favors low-energy, acoustic-leaning songs; Rock favors high-energy, non-acoustic ones (Storm Runner, Gym Hero). The acoustic bonus reinforces the split — the same energy gap that helps a mellow track for Lofi hurts it for Rock.
- **High-Energy Pop vs. Edge Case (High Energy + Sad):** both want energy 0.8–0.9 and pop, so they overlap on Gym Hero and Sunrise City. The difference: "sad" matches no song, so the sad profile loses all mood points and its scores are lower across the board. It shows the system can't honor an emotion it has no data for — it silently ignores it.
- **Deep Intense Rock vs. Edge Case (Unknown Genre/Mood):** Rock gets a clean genre+mood top pick (Storm Runner, 4.48); the unknown "kpop/melancholic" profile gets no genre or mood points at all, so every score collapses to just energy + acoustic (~2.2–2.4). Same engine, but with no matching tags the ranking is decided purely by energy distance.

---

## 8. Future Work

- **Rebalance or normalize the weights** so genre can't crowd out mood and energy; consider capping how much any single factor can contribute.
- **Add a diversity rule** so the top 5 don't repeat the same artist or genre (a "filter-bubble breaker").
- **Handle unknown/close tags smarter** — fuzzy genre matching or mood synonyms so "melancholic" can still connect to "wistful" or "moody."

---

## 9. Personal Reflection

**Biggest learning moment:** seeing that a recommendation is really just *scoring + sorting*. Once the score function returned a number and reasons, the "recommendation" was just ranking that list — there was no magic, and that demystified how big apps work at a basic level.

**How AI helped, and when I double-checked it:** AI was useful for brainstorming the scoring recipe and generating diverse sample songs quickly. But I had to verify the math myself — especially the energy-closeness term and the weight experiment — because a plausible-sounding suggestion can still skew results (the Gym Hero filter-bubble was something I only caught by actually running the profiles, not by trusting the design on paper).

**What surprised me:** how much a handful of simple rules can *feel* like a real recommender. With just genre, mood, and energy, the top picks genuinely matched the vibe of each profile — yet the same simplicity is exactly what created the bias.

**What I'd try next:** adding a listening-history signal (a tiny bit of collaborative filtering) and a diversity penalty, so the system balances "matches your taste" with "shows you something new."
