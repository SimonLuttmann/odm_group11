# Multiplayer Extension: Presentation Segment

**Time budget:** ~2 minutes

---

## COMPACT VERSION: 2 SLIDES ONLY

### Overview

| Slide | Content | Graphics |
|-------|---------|----------|
| 1 | Text: Setup, Results, Discussion | None |
| 2 | Graphics | `fairness.svg`, `excitement.svg`, `hypervolume.svg` |

---

### SLIDE 1: Text Slide

**Title:** Multiplayer Extension: 2-4 Players

#### Version A: Bullet Points

**Setup**
- K = 24 cards, L = 4 categories, R = 1500 simulations
- Fairness = Focus Expert Win Rate (p₄)
- Excitement = Trick Changes / Max Tricks
- 9 configurations tested: 2P, 3P, 4P with varying expert ratios

**Key Results**
- Expert advantage drops with more players: 83% → 56% → 46%
- Excitement increases: 35% → 55% → 67%
- Best overall: 2P (1E vs 1A) — HV: 3.88, Combined: 59%
- Expert vs Expert: Fair duel (~50%), skill still matters

**Methodological Note**
- Fixed K=24 → different game lengths (12/8/6 tricks)
- Excitement normalized per player count
- Higher 4P excitement partly due to normalization effect
- For strict comparison: K ∝ n_players (future work)

---

#### Version B: Continuous Text

**Setup:**
We extended the optimization to 2-4 players (K=24, L=4). Fairness is defined as the win rate of ONE specific expert, ensuring comparability even with multiple experts. Excitement is normalized as `trick_changes / (K / n_players)`.

**Results:**
The expert win rate drops with more players — wins are distributed among more competitors. Excitement increases because fewer cards per player make each trick more impactful. Despite higher excitement, the Hypervolume decreases: the achievable objective space shrinks as both maximum win rate and trick changes are constrained.

**Discussion:**
With fixed K=24, game length varies (12 tricks for 2P vs. 6 for 4P), affecting comparability. We decided to keep K fixed to maintain a realistic scenario. But to offer strict comparison, one would have to increase K proportionally to the number of players. It should be noted that this approach would significantly expand the search space (e.g., 4 players: 4 × 12 × 4 = 192 dimensions) and thus the computation time.

---

### SLIDE 2: Graphics Slide

**Title:** Multiplayer Metrics Comparison

**Layout:**

```
┌─────────────────────────────────────────────────────┐
│        Multiplayer Metrics Comparison               │
├─────────────────┬─────────────────┬─────────────────┤
│                 │                 │                 │
│  fairness.svg   │  excitement.svg │ hypervolume.svg │
│                 │                 │                 │
│   Expert WR ↓   │  Excitement ↑   │  HV ↓ with      │
│   with players  │  with players   │  more players   │
│                 │                 │                 │
└─────────────────┴─────────────────┴─────────────────┘
```

**Files:**
- `plots/optimal_config/fairness.svg`
- `plots/optimal_config/excitement.svg`
- `plots/optimal_config/hypervolume.svg`

**Optional captions:**
- **Fairness:** 83% → 46% (more competition)
- **Excitement:** 35% → 67% (shorter games, more tension)
- **Hypervolume:** 3.88 → 1.40 (shrinking objective space)

---

### Recommendation

| Version | Advantages | Disadvantages |
|---------|------------|---------------|
| **Bullet Points** | Quick to grasp, good for oral presentation | Less detail |
| **Continuous Text** | Complete, self-explanatory | Harder to read during talk |

**Tip:** Use bullet points on slide, continuous text as speaker notes/handout.

---

## EXTENDED VERSION: 4 SLIDES

### Slides Overview (2 min total)

| Slide | Content | Duration | Plot |
|-------|---------|----------|------|
| 1 | Introduction & Setup | 20 sec | None |
| 2 | Fairness Comparison | 40 sec | `fairness.svg` |
| 3 | Excitement Comparison | 30 sec | `excitement.svg` |
| 4 | Conclusion & Best Config | 30 sec | `combined.svg` |

---

## SLIDE 1: Introduction (20 seconds)

### What to say:
> "As a bonus experiment, we extended the optimization to **multiplayer scenarios** with 2 to 4 players. We tested various expert-beginner ratios, including expert-vs-expert duels. **Important**: We measure the win rate of ONE specific expert to ensure comparable fairness metrics."

### No plot needed - just title slide with:
- "Multiplayer Extension: 2-4 Players"
- "Focus Expert Win Rate as Fairness Metric"

---

## SLIDE 2: Fairness Comparison (40 seconds)

### Plot: `plots/optimal_config/fairness.svg`

### What to say:
> "This plot shows the **Fairness Score** - which is simply the Focus Expert's win rate.
> 
> **Key observation**: With 2 players, the expert wins **83%** of games. But as we add more players, this drops dramatically:
> - With 3 players against 2 beginners: only **56%**
> - With 4 players against 3 beginners: only **46%**
> 
> **Interesting**: When ALL players are experts (the 'all_E' configs), the focus expert's win rate approaches random chance - around **36-39%**. This shows that skill advantage disappears when everyone is skilled!"

---

## SLIDE 3: Excitement Comparison (30 seconds)

### Plot: `plots/optimal_config/excitement.svg`

### What to say:
> "The **Excitement Score** measures how many lead changes occur, normalized by the number of tricks.
> 
> Here we see the **opposite trend**: 4-player games are MORE exciting (up to **67%**) while 2-player games have less excitement (**35%**).
> 
> This is because with more players, each player has fewer cards, so each trick matters more - creating more tension and lead changes."

---

## SLIDE 4: Conclusion (30 seconds)

### Plot: `plots/optimal_config/combined.svg`

### What to say:
> "The **Combined Score** balances fairness and excitement. 
> 
> **Result**: **2 players with 1 Expert vs 1 Beginner** achieves the best combined score of **59%**, followed closely by **4 players (1E vs 3A)** with **57%**.
> 
> **Recommendation**: For skill-based play, stick with 2 players. For party games with more excitement, try 4 players with one expert."

---

## ALTERNATIVE: Single Slide Version (if time is short)

### Plot: `plots/optimal_config/combined.svg` OR `plots/multiplayer_configs/pareto_fronts_comparison.svg`

### Compressed Script (60 seconds):
> "We extended to multiplayer with 2-4 players. Key findings:
> 1. **More players = lower expert advantage** (83% → 46%)
> 2. **More players = higher excitement** (35% → 67%)
> 3. **Best overall: 2P with 1E vs 1A** (combined score 59%)
> 
> The trade-off remains: skill reward vs. excitement - regardless of player count."

---

## Slide: Multiplayer Extension

### Title
**"Extension to 3+ Players: How does the game dynamic change?"**

### Key Concept
**Fairness = Focus Expert Win Rate** (win rate of ONE specific expert, even with multiple experts)

This ensures comparable metrics across all configurations!

### Graphic (choose one)

**Option A - Pareto Fronts Comparison:**

![Configuration Comparison](plots/multiplayer_configs/pareto_fronts_comparison.svg)

**Option B - Scores Comparison (separate SVGs available):**

| Fairness | Excitement | Combined | Hypervolume |
|:--------:|:----------:|:--------:|:-----------:|
| ![Fairness](plots/optimal_config/fairness.svg) | ![Excitement](plots/optimal_config/excitement.svg) | ![Combined](plots/optimal_config/combined.svg) | ![Hypervolume](plots/optimal_config/hypervolume.svg) |

### Bullet Points for the Slide

- **More opponents → Expert advantage drops dramatically**
  - 2P: ~83% → 3P (1v2): ~56% → 4P (1v3): ~46%
  
- **With other experts: Competition, not collaboration!**
  - 2P (E vs E): Focus Expert ~58% (fair duel)
  - 4P (all E): Focus Expert ~36% (near-random!)
  
- **Best balance: 2P with 1E vs 1A**
  - Highest Hypervolume (3.88) and best fairness (82.8%)

---

## Presentation Script

### Introduction (15 seconds)

> "As a bonus, we **extended the optimization to multiplayer** - testing 2 to 4 players with various expert/beginner ratios, including expert-vs-expert scenarios."

### Main Part with Graphic (30 seconds)

> "The **key insight** is shown in this graphic:
> 
> With **more opponents, the expert advantage drops dramatically**:
> - With 2 players, the expert wins about 83%
> - With 3 players against 2 beginners, only 56%
> - With 4 against 3, only 46%
> 
> **Important**: With multiple experts, they **compete, not collaborate**!
> In an all-expert game, each expert wins only ~36% - near-random!
> This is because we measure the win rate of ONE specific expert."

### Recommendation (20 seconds)

> "The **best configuration** depends on your goal:
> 
> **2 players with 1 Expert vs 1 Beginner** achieves the highest Hypervolume (3.88) and best fairness (83%).
> For a **party game**, try **4 players with 1E vs 3A** - 
> highest excitement score (67%) with reasonable skill reward."

### Transition (10 seconds)

> "The **core mechanism remains the same**: 
> There's always a trade-off between skill reward and excitement - 
> regardless of player count."

---

## Numbers for Q&A

### Configuration Comparison (Focus Expert Win Rate, K=24)

| Configuration | Focus E WR | Trick Changes | Excitement | Hypervolume |
|---------------|------------|---------------|------------|-------------|
| 2P: 1E vs 1A | 82.8% | 4.19 | 34.9% | 3.88 |
| 2P: 2E (E vs E) | 58.1% | 4.42 | 36.8% | 2.65 |
| 3P: 1E vs 2A | 55.9% | 4.38 | 54.8% | 2.54 |
| 3P: 2E vs 1A | 46.2% | 4.37 | 54.6% | 2.02 |
| 3P: 3E (all E) | 39.4% | 4.08 | 51.0% | 1.70 |
| 4P: 1E vs 3A | 46.4% | 4.02 | 66.9% | 1.87 |
| 4P: 2E vs 2A | 35.9% | 3.97 | 66.2% | 1.51 |
| 4P: 3E vs 1A | 34.4% | 3.71 | 61.8% | 1.32 |
| 4P: 4E (all E) | 36.1% | 3.88 | 64.6% | 1.40 |

### Best Configurations (2-4 Players)

| Criterion | Best Configuration | Value |
|-----------|---------------------|------|
| **Fairness** | 2P: 1E vs 1A | Focus E WR: 82.8% |
| **Excitement** | 4P: 1E vs 3A | Excitement: 66.9% |
| **Combined** | 2P: 1E vs 1A | Combined: 58.9% |
| **Hypervolume** | 2P: 1E vs 1A | HV: 3.88 |

### Why does Focus Expert Win Rate drop?

```
With more experts:
  2P (E vs E): Focus Expert competes with 1 other expert
    → P(Win) ≈ 58% (fair duel)

  3P (2E vs 1A): Focus Expert competes with 1 expert + 1 beginner
    → P(Win) ≈ 46% (other expert takes some wins)

  4P (all E): Focus Expert competes with 3 other experts
    → P(Win) ≈ 36% (near-random!)

→ More experts = more competition for the Focus Expert!
```

---

## DISCUSSION POINTS / LIMITATIONS

### Slide: Methodology Considerations (Optional - for Q&A or extended version)

**Title:** "Comparing Apples to Apples? Methodological Notes"

---

### Point 1: Fixed Deck Size vs. Proportional Scaling

| Players | Current (K=24) | Proportional (12 cards/player) |
|---------|----------------|-------------------------------|
| 2 | 24 cards → **12 tricks** | 24 cards → 12 tricks |
| 3 | 24 cards → **8 tricks** | 36 cards → 12 tricks |
| 4 | 24 cards → **6 tricks** | 48 cards → 12 tricks |

**The Issue:**
- With fixed K=24, players have **different game lengths**
- 2-player games have 12 tricks, 4-player games only 6
- This affects statistical comparability

**Why we kept K=24:**
- Divisible by 2, 3, and 4 (fair distribution)
- Keeps search space constant (96 dimensions)
- Represents realistic game scenario (fixed deck)

**Alternative approach:**
> For strict comparability, K should scale with player count (K = 12 × n_players). This would ensure equal game length but increases optimization difficulty.

---

### Point 2: Excitement Score Normalization Effect

**Formula:** `Excitement = trick_changes / max_tricks` where `max_tricks = K / n_players`

| Players | Example: 4 Lead Changes | Max Tricks | Normalized Score |
|---------|------------------------|------------|------------------|
| 2 | 4 / 12 | 12 | **33%** |
| 3 | 4 / 8 | 8 | **50%** |
| 4 | 4 / 6 | 6 | **67%** |

**The Effect:**
- Same absolute excitement (4 lead changes) → **different scores**
- Fewer tricks = higher normalized excitement
- 4P games appear "more exciting" partly due to normalization

**Interpretation:**
> The higher excitement in 4P games is **partially real** (more competition per trick) but **partially an artifact** of normalizing to fewer total tricks.

**Key insight for presentation:**
> "4-player games show higher excitement scores, but this reflects TWO effects: (1) more competition per trick, AND (2) fewer tricks to normalize against. For strict comparison, proportional deck sizes would be needed."

---

### Suggested Q&A Response

**Q: "Is the excitement comparison fair across player counts?"**

> "Good observation! We normalize by max_tricks, which differs per player count. The higher 4P excitement is partly real (more competition) and partly a normalization effect. For truly comparable metrics, we would need proportional deck sizes - but this would change the optimization problem significantly."

**Q: "Why not use proportional K values?"**

> "Three reasons: (1) It keeps the search space constant at 96 dimensions. (2) Real card games typically have fixed deck sizes. (3) It allows us to study how the SAME deck performs with different player counts. A proportional study would be valuable future work."

---

### PowerPoint Bullet Points (if you want a slide)

**Title:** Methodological Considerations

- **Fixed deck size (K=24)** for all player counts
  - 2P: 12 tricks | 3P: 8 tricks | 4P: 6 tricks
  
- **Excitement normalization effect:**
  - Same lead changes → higher score with fewer tricks
  - 4P appears more exciting (partly artifact)

- **For strict comparison:** K should scale proportionally
  - 2P: 24 cards | 3P: 36 cards | 4P: 48 cards
  - Trade-off: Larger search space, different optimization

- **Our approach:** Fixed K shows how ONE deck adapts to player count

---

## Notes for the Presentation

### What to emphasize

1. **Contrast**: 2P vs 3P/4P (the effect is dramatic)
2. **Key insight**: Other experts are competitors, not allies!
3. **Practical recommendation**: 2P with 1E vs 1A (best overall) or 4P with 1E vs 3A (most exciting)

### What to skip

- Parameter study K for multiplayer (too detailed)
- Tie rates (interesting, but not essential)
- Mathematical formulas (no time)
- Individual Pareto fronts (comparison graphic is enough)

### Possible Q&A

**"Why K=24 instead of K=22?"**
> "24 is divisible by 2, 3, and 4 - necessary for fair card distribution with different player counts."

**"What is Focus Expert Win Rate?"**
> "We measure the win rate of ONE specific expert (Player 0), not the combined win rate of all experts. This ensures comparable fairness metrics across all configurations."

**"Why not measure all experts combined?"**
> "With 2E vs 1A, 'any expert wins' would be ~80% - almost trivial. Focus Expert shows the TRUE individual success rate."

**"Which configuration for party games?"**
> "4P with 1E vs 3A - highest excitement (67%) while still rewarding skill (46% expert win rate)."

---

## Graphic Files

| Graphic | Path | Usage |
|---------|------|-------|
| Pareto Fronts Comparison | `plots/multiplayer_configs/pareto_fronts_comparison.svg` | Main graphic Option A |
| Fairness Score | `plots/optimal_config/fairness.svg` | Score comparison |
| Excitement Score | `plots/optimal_config/excitement.svg` | Score comparison |
| Combined Score | `plots/optimal_config/combined.svg` | Score comparison |
| Hypervolume | `plots/optimal_config/hypervolume.svg` | Score comparison |
| Single 3P Front | `plots/multiplayer/pareto_front_validated.svg` | Backup |
| Metrics Boxplots | `plots/multiplayer_configs/metrics_boxplots.svg` | For Q&A |

---

*Created for presentation: ODM WiSe 2025/26 - Case Study Top Trumps*

**Note:** All multiplayer experiments now use **Focus Expert Win Rate** as the fairness metric, ensuring comparable results across all configurations including E vs E scenarios.
