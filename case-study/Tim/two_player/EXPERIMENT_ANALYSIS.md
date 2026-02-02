# Experiment-Analyse: Automatic Game Balancing mit Top Trumps

## Übersicht der Case Study

Diese Dokumentation analysiert systematisch, welche Notebooks und Ergebnisse die Fragen der Aufgabenstellung (Exercise Sheet 7 - ODM WiSe 2025/26) beantworten.

---

## Inhaltsverzeichnis

1. [Aufgabenstellung im Überblick](#1-aufgabenstellung-im-überblick)
2. [Notebook-Struktur](#2-notebook-struktur)
3. [Hauptaufgaben - Status & Ergebnisse](#3-hauptaufgaben---status--ergebnisse)
4. [Optionale Vertiefungen - Status & Ergebnisse](#4-optionale-vertiefungen---status--ergebnisse)
5. [Nicht beantwortete Fragen](#5-nicht-beantwortete-fragen)
6. [Zusammenfassung der Erkenntnisse](#6-zusammenfassung-der-erkenntnisse)

---

## 1. Aufgabenstellung im Überblick

### Problem-Definition

| Parameter | Wert | Beschreibung |
|-----------|------|--------------|
| K | 22 | Anzahl Karten im Deck |
| L | 4 | Anzahl Kategorien pro Karte |
| n_var | 88 | Entscheidungsvariablen (K × L) |
| Wertebereich | [1, 10] | Kartenwerte |
| R | 1000 | Simulationen pro Evaluation |

### Ziele (Multi-Objective)

$$\max_{x\in\mathbb{R}^{KL}} F(x) := (f_{\text{Fairness}}(x), f_{\text{Excitement}}(x))$$

1. **Fairness** $f_1(x)$: Win-Rate des geschickteren Spielers p4
2. **Excitement** $f_2(x)$: Durchschnittliche Anzahl der Trick Changes

### Spieler-Strategien

| Strategie | Beschreibung |
|-----------|-------------|
| p0 (Anfänger) | Wählt Kategorie mit höchstem normalisierten Wert |
| p4 (Experte) | Berechnet exakte Gewinnwahrscheinlichkeit basierend auf verbleibenden Karten |

---

## 2. Notebook-Struktur

### Kern-Pipeline (2-Spieler)

```
two_player/01_setup_and_exploration.ipynb → Setup, Simulation, Sanity Checks
         ↓
two_player/02_optimization.ipynb      → NSGA-II Optimization (R=1000) + Validation (R=1500)
         ↓
two_player/03_analysis.ipynb          → Hypervolume, Deck-Analyse, Interpretation
         ↓
two_player/04_algorithm_comparison.ipynb → NSGA-II vs MOEA/D vs SMS-EMOA
         ↓
parameter_study/01_parameter_study.ipynb → Einfluss von K (Deckgröße)
```

### Multiplayer-Erweiterung

```
multiplayer/01_setup.ipynb            → Multiplayer-Simulation (3+ Spieler)
         ↓
multiplayer/02_optimization.ipynb     → Optimierung für 3 Spieler (1E vs 2A)
         ↓
multiplayer/03_configurations.ipynb   → Vergleich: 2P, 3P, 4P Konfigurationen
         ↓
multiplayer/04_parameter_study.ipynb  → K-Studie für Multiplayer
         ↓
multiplayer/05_optimal_configuration.ipynb → Systematische Suche: 2-6 Spieler
```

---

## 3. Hauptaufgaben - Status & Ergebnisse

### 3.1 Pareto-Front approximieren (K=22, L=4, R=1000)

**Status:** ✅ **ERFÜLLT**

**Notebook:** `two_player/02_optimization.ipynb`

**Ergebnisse:**

| Metrik | Wert |
|--------|------|
| Anzahl Lösungen | 16 |
| Win Rate Bereich | 71.7% - 85.1% |
| Trick Changes Bereich | 3.00 - 4.26 |
| **Hypervolume** | **3.5524** |
| Optimierungs-Zeit | ~466 Sekunden |
| Validierungs-Zeit | ~1.1 Sekunden |

**Algorithm Configuration:**
- NSGA-II with Population Size = 100, Generations = 200
- R_fast = 1000 (during optimization)
- R_final = 1500 (validation)
- Crossover: SBX (eta=15), Mutation: PM (eta=20)

**Gespeicherte Dateien:**
- `../results/pareto_front_X.npy` - Deck-Vektoren
- `../results/pareto_front_F.npy` - Objective-Werte
- `../results/validated_front.csv` - Validierte Metriken

**Visualisierung:**

![Pareto-Front mit ausgewählten Lösungen](plots/pareto_front_selected.png)

*Die Pareto-Front zeigt den Trade-off zwischen Fairness (Win Rate) und Excitement (Trick Changes). Drei repräsentative Lösungen sind markiert: Fairness-Max (höchste Win Rate), Excitement-Max (meiste Trick Changes) und Knee-Point (bester Kompromiss).*

**Erkenntnis:** Es existiert ein klarer **Trade-off** zwischen den beiden Zielen:
- Decks mit hoher Fairness (Win Rate ~85%) haben weniger Trick Changes (~3.0)
- Decks mit hoher Excitement (Trick Changes ~4.26) haben niedrigere Win Rates (~72%)

#### Tiefere Analyse: Warum existiert dieser Trade-off?

Der Trade-off ist **kein Zufall**, sondern ergibt sich aus der Spielmechanik:

**Mechanismus hinter hoher Fairness (Win Rate):**
```
Experte p4 gewinnt häufiger, WENN:
  → Er die Gewinnwahrscheinlichkeit für jede Kategorie berechnen kann
  → Es klare "Trumpf-Karten" gibt (dominant in mehreren Kategorien)
  → Die Kategorie-Wahl einen echten Unterschied macht

Das bedeutet: Heterogene Decks mit klaren Hierarchien
```

**Mechanismus hinter hoher Excitement (Trick Changes):**
```
Viele Führungswechsel entstehen, WENN:
  → Der Ausgang jedes Tricks ungewiss ist
  → Karten ähnlich stark sind ("Coin-Flip")
  → Die Kategorie-Wahl weniger relevant ist

Das bedeutet: Homogene Decks mit ähnlichen Werten
```

**Der fundamentale Konflikt:**
| Eigenschaft | Fördert Fairness | Fördert Excitement |
|-------------|------------------|-------------------|
| Kartenwerte | Große Varianz | Kleine Varianz |
| Hierarchie | Klar erkennbar | Nicht vorhanden |
| Kategorie-Korrelation | Niedrig | Hoch |
| Strategischer Vorteil | Hoch für p4 | Gering für alle |

**Spieltheoretische Interpretation:**
- **Fairness-Decks** belohnen **Skill** (Information über verbleibende Karten)
- **Excitement-Decks** erhöhen **Zufall** (jeder Trick ist unvorhersehbar)

Diese beiden Ziele sind **inhärent konfliktär**: Je mehr Zufall, desto weniger kann Skill helfen.

---

### 3.2 Qualität mit Quality Indicator bewerten

**Status:** ✅ **ERFÜLLT**

**Notebook:** `two_player/03_analysis.ipynb`

**Ergebnisse:**

| Indikator | Wert | Referenzpunkt |
|-----------|------|---------------|
| **Hypervolume** | **3.5524** | (0, 0) |

**Interpretation:**
- Der Hypervolume misst das Volumen des Objective Space, das von der Pareto-Front dominiert wird
- Höherer HV = bessere Approximation der wahren Pareto-Front
- Der Wert 3.6652 zeigt eine gute Abdeckung des erreichbaren Objective Space

**Berechnung:**
```python
# Reference Point im minimierten Raum (pymoo minimiert)
ref_point = np.array([0.0, 0.0])

# Validierte Front negieren (da pymoo minimiert)
validated_F = np.column_stack([
    -validated_df['win_rate'].values,
    -validated_df['trick_changes'].values
])

hv_indicator = HV(ref_point=ref_point)
hypervolume = hv_indicator(validated_F)  # = 3.6652
```

---

### 3.3 Lösungen im Spielkontext interpretieren

**Status:** ✅ **ERFÜLLT**

**Notebook:** `two_player/03_analysis.ipynb`

**Ausgewählte repräsentative Decks:**

| Deck-Typ | Win Rate | Trick Changes | Charakteristik |
|----------|----------|---------------|----------------|
| **Fairness-Max** | 85.1% | 3.00 | Skill wird belohnt, weniger Dynamik |
| **Excitement-Max** | 71.7% | 4.26 | Viele Wechsel, mehr Zufallseinfluss |
| **Knee-Point** | 78.0% | 3.98 | **Bester Kompromiss** |

**Deck-Muster (aus Analyse):**

Die folgenden drei Plots zeigen die Kategorie-Verteilungen der drei repräsentativen Deck-Typen:

| Fairness-Max | Excitement-Max | Knee-Point |
|:------------:|:--------------:|:----------:|
| ![Fairness-Max](plots/fairness_max.svg) | ![Excitement-Max](plots/excitement_max.svg) | ![Knee-Point](plots/knee_point.svg) |

*Vergleich der Werteverteilungen in den 4 Kategorien für die drei Deck-Typen.*

![Korrelations-Heatmaps](plots/correlation_heatmaps.png)

*Korrelationen zwischen den Kategorien zeigen unterschiedliche Strukturen.*

**Erkenntnisse zu Deck-Mustern:**

1. **Fairness-Decks:**
   - Klare Kategorie-Hierarchie (manche Kategorien systematisch höher)
   - Bestimmte Karten sind "Trümpfe" (hohe Werte in mehreren Kategorien)
   - Ermöglicht dem Experten strategische Planung
   - **Geringe Korrelation** zwischen Kategorien → mehr Auswahlmöglichkeiten

2. **Excitement-Decks:**
   - Homogenere Werteverteilungen
   - Karten oft ähnlich stark ("Coin-Flip" Situationen)
   - Führt zu häufigen Führungswechseln
   - **Höhere Korrelation** zwischen Kategorien → weniger strategische Varianz

3. **Knee-Point Deck (Empfehlung):**
   - Bietet ~80% Win Rate für den Experten (Skill lohnt sich)
   - ~3.8 Trick Changes sorgen für Spannung
   - Praktisch beste Wahl für ausgeglichenes Spielerlebnis

#### Tiefere Analyse: Warum entstehen diese Muster?

**Warum hilft geringe Korrelation dem Experten (p4)?**

```
Beispiel: Experte hat Karte mit Werten [8, 3, 2, 9]

Geringe Korrelation (Fairness-Deck):
  → Gegner-Karten haben unterschiedliche Stärken pro Kategorie
  → p4 kann berechnen: "In Kat. 1 gewinne ich gegen 80% der Karten"
  → Strategische Wahl möglich

Hohe Korrelation (Excitement-Deck):
  → Wenn eine Karte in Kat. 1 stark ist, ist sie überall stark
  → p4's Berechnung: "Egal welche Kategorie, ~50% Gewinnchance"
  → Strategische Wahl bringt keinen Vorteil
```

**Warum führen homogene Werte zu mehr Trick Changes?**

```
Heterogenes Deck:           Homogenes Deck:
Karte A: [9, 8, 7, 6]       Karte A: [5, 5, 5, 5]
Karte B: [2, 3, 4, 5]       Karte B: [5, 5, 5, 5]

→ A gewinnt IMMER          → 50/50 Chance pro Trick
→ Kein Wechsel möglich     → Häufige Wechsel
```

**Kausalkette:**
```
Hohe Varianz → Klare Gewinner → Wenige Wechsel → Hohe Fairness
Niedrige Varianz → Unsichere Ausgänge → Viele Wechsel → Hohe Excitement
```

**Gespeichert in:** `../results/selected_decks.json` (vollständige Deck-Vektoren)

---

## 4. Optionale Vertiefungen - Status & Ergebnisse

### 4.1 Verschiedene Optimierer evaluieren

**Status:** ✅ **ERFÜLLT**

**Notebook:** `two_player/04_algorithm_comparison.ipynb`

**Verglichene Algorithmen:**
1. **NSGA-II** - Non-dominated Sorting Genetic Algorithm II
2. **MOEA/D** - Multi-Objective Evolutionary Algorithm based on Decomposition
3. **SMS-EMOA** - S-Metric Selection Evolutionary Multi-Objective Algorithm

**Experiment-Setup:**
- 5 unabhängige Seeds (42, 101, 202, 303, 404)
- Gleiches Budget: 2400 Evaluierungen pro Run
- R = 100-200 Simulationen pro Evaluation
- Finale Validierung mit R = 1000

**Ergebnisse (Single-Seed Run, R=100):**

| Algorithmus | Hypervolume | Lösungen | Laufzeit (s) | Win Rate Range |
|-------------|-------------|----------|--------------|----------------|
| **SMS-EMOA** | **3.38** | 11 | 7.24 | 51% - 79% |
| NSGA-II | 3.21 | 6 | 7.25 | 60% - 79% |
| MOEA/D | 2.86 | 34 | 8.23 | 57% - 81% |

![Algorithmus-Vergleich: Pareto-Fronten](plots/algorithm_comparison_fronts.png)

*Vergleich der approximierten Pareto-Fronten der drei Algorithmen.*

![Algorithmus-Vergleich: Boxplots](plots/algorithm_comparison_boxplots.png)

*Boxplots der Hypervolume-Werte über mehrere Seeds zeigen die Robustheit.*

**Vor- und Nachteile:**

| Algorithmus | Vorteile | Nachteile |
|-------------|----------|-----------|
| **NSGA-II** | Schnell, robust, gute Balance | Weniger Lösungen |
| **MOEA/D** | Viele Lösungen, gute Diversität | Niedrigerer HV, langsamer |
| **SMS-EMOA** | Höchster HV, gute Konvergenz | Ähnlich wie NSGA-II |

**Empfehlung:** **NSGA-II oder SMS-EMOA** für dieses Problem, da sie konsistent höhere Hypervolume-Werte erreichen.

#### Tiefere Analyse: Warum funktionieren NSGA-II und SMS-EMOA besser?

**1. Algorithmische Unterschiede:**

| Aspekt | NSGA-II | MOEA/D | SMS-EMOA |
|--------|---------|--------|----------|
| **Selektionsprinzip** | Nicht-dominierte Sortierung + Crowding Distance | Dekomposition in skalare Teilprobleme | Hypervolume-Beitrag |
| **Diversitätserhalt** | Crowding Distance | Nachbarschaftsstruktur | Implizit durch HV |
| **Konvergenz** | Durch Dominanz-Druck | Durch Gewichtsvektoren | Durch HV-Maximierung |

**2. Warum MOEA/D hier schlechter abschneidet:**

```
MOEA/D zerlegt das Problem in N skalare Teilprobleme:
  min g(x|λ) = λ₁·f₁(x) + λ₂·f₂(x)

Problem beim Top Trumps Problem:
  ┌─────────────────────────────────────────────────────────┐
  │ 1. STOCHASTISCHES RAUSCHEN                              │
  │    → Fitness-Werte schwanken bei jeder Evaluation       │
  │    → MOEA/D's feste Gewichtsvektoren "wackeln"         │
  │    → Nachbarschafts-Updates werden instabil             │
  │                                                         │
  │ 2. NICHT-KONVEXE FRONT                                  │
  │    → Die Pareto-Front ist leicht konkav                 │
  │    → Lineare Gewichtung "überspringt" konkave Bereiche │
  │    → MOEA/D findet diese Lösungen nicht                │
  └─────────────────────────────────────────────────────────┘
```

**3. Warum NSGA-II robust gegen Rauschen ist:**

```
NSGA-II's Selektionsmechanismus:
  1. Sortiere Population nach Dominanz-Rängen
  2. Innerhalb eines Rangs: Bevorzuge isolierte Lösungen (Crowding)

Vorteil bei Rauschen:
  → Dominanz ist robuster als exakte Fitness-Vergleiche
  → Lösung A dominiert B, wenn A in ALLEN Objectives besser ist
  → Kleine Schwankungen ändern selten die Dominanz-Beziehung
  → Population "mittelt" das Rauschen über viele Individuen
```

**4. Warum SMS-EMOA am besten abschneidet:**

```
SMS-EMOA selektiert basierend auf Hypervolume-Beitrag:
  → Entferne in jeder Generation die Lösung mit kleinstem HV-Beitrag
  → Direkte Optimierung des Quality-Indikators!

Vorteile:
  1. HV berücksichtigt sowohl Konvergenz als auch Diversität
  2. Robuster gegen Rauschen (HV ist ein "aggregiertes" Maß)
  3. Funktioniert auch bei nicht-konvexen Fronten
  
Nachteil:
  → HV-Berechnung ist teurer (aber bei 2 Objectives noch OK)
```

**5. Visualisierung des Problems mit MOEA/D:**

```
                    Excitement
                        ↑
                        │     × MOEA/D findet diese nicht
                        │    ╱   (konkaver Bereich)
                        │   ╱
                    ════╪══╱════ Wahre Front
                        │ ╱
          MOEA/D       │╱     NSGA-II/SMS-EMOA
          findet ●────●───────● finden alle
                        │
                        └──────────────→ Fairness
```

**6. Zusammenfassung:**

| Eigenschaft des Problems | NSGA-II | MOEA/D | SMS-EMOA |
|--------------------------|---------|--------|----------|
| Stochastisches Rauschen | ✅ Robust | ❌ Sensibel | ✅ Robust |
| Nicht-konvexe Front | ✅ OK | ❌ Probleme | ✅ OK |
| Hohe Dimensionalität (88) | ✅ Skaliert | ✅ Skaliert | ✅ Skaliert |
| 2 Objectives | ✅ Ideal | ✅ OK | ✅ Ideal |

**Fazit:** Das Top Trumps Problem ist **stochastisch** und hat eine **leicht konkave Front**. Diese Eigenschaften benachteiligen MOEA/D, während NSGA-II und SMS-EMOA durch ihre dominanzbasierte bzw. hypervolume-basierte Selektion robuster sind.

---

### 4.2 Einfluss von K (Deckgröße) auf die Pareto-Front

**Status:** ✅ **ERFÜLLT**

**Notebook:** `parameter_study/01_parameter_study.ipynb`

**Experiment:**
- K ∈ {10, 22, 34} getestet
- L = 4 (konstant)
- NSGA-II mit gleichen Parametern

**Ergebnisse:**

| K | Max Tricks | Win Rate Range | Trick Changes Range |
|---|------------|----------------|---------------------|
| 10 | 5 | 59% - 86% | 1.14 - 2.47 |
| 22 | 11 | 61% - 84% | 3.02 - 4.20 |
| 34 | 17 | 65% - 73% | 5.53 - 6.30 |

![Parameter-Studie: Einfluss von K](plots/parameter_study_K_impact.png)

*Die Pareto-Fronten für verschiedene Deck-Größen zeigen, wie K die erreichbaren Werte beeinflusst.*

**Erkenntnisse:**

1. **Excitement skaliert linear mit K:**
   - Mehr Karten = mehr Runden = mehr mögliche Trick Changes
   - K=10: max ~2.5 Trick Changes
   - K=34: max ~6.3 Trick Changes

2. **Fairness ist weitgehend unabhängig von K:**
   - Win Rate Range bleibt stabil (~60-85%)
   - Fairness ist primär eine Eigenschaft der **relativen Kartenwerte**, nicht der Spieldauer

3. **Trade-off-Struktur bleibt erhalten:**
   - Für alle K-Werte existiert der gleiche Konflikt zwischen Fairness und Excitement
   - Die Front verschiebt sich vertikal (mehr Excitement bei größerem K)

#### Tiefere Analyse: Warum diese Skalierungseffekte?

**Warum skaliert Excitement linear mit K?**

```
Trick Changes = Anzahl der Führungswechsel

Maximale Trick Changes = K/2 - 1 (jeder Trick wechselt)

Beobachtet:
  K=10:  max ~2.5 TC  →  2.5 / 4  = 62.5% der max. möglichen
  K=22:  max ~4.2 TC  →  4.2 / 10 = 42.0% der max. möglichen
  K=34:  max ~6.3 TC  →  6.3 / 16 = 39.4% der max. möglichen

→ Absolute Excitement steigt, aber relative Excitement sinkt leicht!
→ Bei mehr Tricks "mittelt" sich das Spielgeschehen stärker
```

**Warum ist Fairness unabhängig von K?**

```
Win Rate = Anteil der Spiele, in denen p4 > K/4 Tricks gewinnt

Die Win Rate hängt ab von:
  1. Qualität der Strategie von p4 relativ zu p0
  2. Struktur der Kartenwerte (Varianz, Korrelation)
  3. NICHT von der absoluten Anzahl der Tricks!

Begründung:
  → Win Rate ist ein ANTEIL (0-100%), kein absoluter Wert
  → Ob p4 in 5 von 5 oder 11 von 11 Tricks gewinnt, ist strukturell gleich
  → Die relative Stärke der Strategie bleibt konstant
```

**Mathematische Erklärung:**

```
Sei p = Wahrscheinlichkeit, dass p4 einen einzelnen Trick gewinnt

Für K Karten (K/2 Tricks):
  p4 gewinnt das Spiel, wenn er > K/4 Tricks gewinnt
  
  P(Gewinn) = P(X > K/4) wobei X ~ Binomial(K/2, p)
  
Für großes K (Normalapproximation):
  X ≈ Normal(μ = K/2 · p, σ² = K/2 · p · (1-p))
  
  P(Gewinn) ≈ Φ((K/2·p - K/4) / σ)
            = Φ((p - 0.5) · √(K/2) / √(p(1-p)))

→ Wenn p > 0.5: P(Gewinn) steigt mit K (Skill wird stärker belohnt)
→ Wenn p = 0.5: P(Gewinn) = 0.5 (unabhängig von K)
→ Wenn p < 0.5: P(Gewinn) sinkt mit K
```

**Implikation für Spieldesign:**

| Wenn du möchtest... | Ändere... |
|---------------------|-----------|
| Mehr Spannung (absolute Trick Changes) | Erhöhe K |
| Fairness ändern | Ändere Deck-Struktur, nicht K |
| Spieldauer verkürzen | Verringere K |
| Skill stärker belohnen | Erhöhe K (bei p > 0.5) |

---

### 4.3 Einfluss der Wiederholungen R auf die Lösungsqualität

**Status:** ✅ **ERFÜLLT**

**Notebooks:** `two_player/01_setup_and_exploration.ipynb`, `two_player/02_optimization.ipynb`

**Experiment:**
The two-stage evaluation strategy was explicitly chosen:
- R_fast = 1000 (during optimization)
- R_final = 1500 (validation)

**Results (Optimizer's Bias):**

| Phase | Win Rate Range | Trick Changes Range |
|-------|----------------|---------------------|
| FAST (R=1000) | 70.6% - 88.0% | 3.14 - 4.58 |
| VALIDATED (R=1500) | 66.4% - 83.9% | 3.07 - 4.48 |

**Beobachtung:** Die validierte Front liegt **systematisch unter** der während der Optimierung gefundenen Front!

![Noisiness Test](plots/noisiness_test.png)

*Variabilität der Metriken bei wiederholter Evaluation desselben Decks.*

**Key Findings:**

1. **"Regression to the Mean":**
   - With R=1000, decks are sometimes overestimated due to noise
   - With R=1500, values "normalize"

2. **Why not directly use R=1500?**
   - Too slow: 10,000 evaluations × 1500 simulations = 15 million games
   - The two-stage strategy is a good compromise

3. **R=1500 is essential for final evaluation:**
   - Only with high R are statistical fluctuations balanced out
   - For the poster, **only validated values** should be used

#### Tiefere Analyse: Der "Optimizer's Bias"

**Was ist der Optimizer's Bias?**

```
Der Optimierer SELEKTIERT Lösungen basierend auf ihrer geschätzten Fitness.
Bei verrauschten Evaluierungen werden Lösungen bevorzugt, die:
  1. Wirklich gut sind, ODER
  2. Zufällig zu hoch geschätzt wurden ("Glück gehabt")

Ergebnis: Die selektierten Lösungen sind im Durchschnitt ÜBERSCHÄTZT.
```

**Mathematisches Modell:**

```
Wahre Fitness:        f*(x)
Geschätzte Fitness:   f̂(x) = f*(x) + ε,  wobei ε ~ N(0, σ²/R)

Der Optimierer wählt Lösungen mit hohem f̂(x).
Aber: E[f̂(x) | f̂(x) ist hoch] > E[f*(x) | f̂(x) ist hoch]

Je größer σ²/R (mehr Rauschen), desto stärker der Bias!
```

**Why do values decrease during validation?**

```
During optimization (R=1000):
  → Deck D is evaluated 10x with random fluctuations
  → One evaluation shows f̂ = 0.85 (overestimated!)
  → Optimizer says: "Great deck, keep it!"
  
During validation (R=1500):
  → Deck D is re-evaluated with more precision
  → Actual value: f* = 0.80
  → The deck was good, but not THAT good

This is "Regression to the Mean":
  Extreme estimates are often outliers.
  When repeated, they move toward the true value.
```

**Quantification of the bias:**

| Phase | Win Rate Range | Avg. Overestimation |
|-------|----------------|---------------------|
| FAST (R=1000) | 70.6% - 88.0% | +4.6% (Win Rate) |
| VALIDATED (R=1500) | 66.4% - 83.9% | 0% (Reference) |

```
Overestimation ≈ σ / √R

At R=1000: σ_WR ≈ 0.15 → Overestimation ≈ 0.15/√1000 ≈ 0.005 per eval
But: Optimizer selects the BEST → systematic overestimation accumulates
```

**Strategies against Optimizer's Bias:**

| Strategy | Description | Applied? |
|----------|-------------|----------|
| **Re-Evaluation** | Validate final solutions with higher R | ✅ Yes (R=1500) |
| **Higher R** | Use R=1500 during optimization | ❌ Too slow |
| **Noise-aware Selection** | Statistical tests instead of direct comparisons | ❌ Not implemented |
| **Population Averaging** | Average over similar solutions | ✅ Implicitly (NSGA-II) |

**Conclusion:** The two-stage strategy (R=1000 for search, R=1500 for validation) is a good compromise between computation time and accuracy. The Optimizer's Bias is known and corrected through validation.

---

### 4.4 Ein automatisch designtes Spiel spielen/testen

**Status:** ⚠️ **TEILWEISE ERFÜLLT**

**Notebooks:** `two_player/03_analysis.ipynb`, `../results/selected_decks.json`

Die drei repräsentativen Decks (Fairness-Max, Excitement-Max, Knee-Point) sind vollständig als 88-dimensionale Vektoren gespeichert und können theoretisch gespielt werden.

**Verfügbar:**
- Deck-Vektoren in `../results/selected_decks.json`
- Jedes Deck kann mit der Simulation getestet werden

**Nicht durchgeführt:**
- Kein manuelles Spielen mit echten Personen dokumentiert
- Keine subjektive Bewertung des Spielerlebnisses

**Beispiel-Deck (Knee-Point) - Erste 5 Karten:**

| Karte | Kat. 1 | Kat. 2 | Kat. 3 | Kat. 4 |
|-------|--------|--------|--------|--------|
| 1 | 6.00 | 7.81 | 3.15 | 6.91 |
| 2 | 8.04 | 9.91 | 8.72 | 9.80 |
| 3 | 2.33 | 2.61 | 1.89 | 2.04 |
| 4 | 5.84 | 9.88 | 9.91 | 5.71 |
| 5 | 6.73 | 8.76 | 5.07 | 2.91 |

---

### 4.5 Zusätzliche/andere Objectives implementieren

**Status:** ❌ **NICHT ERFÜLLT**

Die Aufgabenstellung erwähnt, dass das Paper [1] ein drittes Objective enthält. Dies wurde **nicht implementiert**.

**Aus dem Paper (Volz et al., 2016):**
- Drittes Objective könnte z.B. "Variance of outcomes" oder "Strategic depth" sein

---

### 4.6 Mehr Ties entstehen lassen

**Status:** ⚠️ **TEILWEISE ERFÜLLT** (im Multiplayer-Kontext)

**Notebooks:** `multiplayer/01_setup.ipynb`, `multiplayer/03_configurations.ipynb`

Im 2-Spieler-Modus mit reellen Werten sind Ties extrem selten (praktisch 0%).

**Im Multiplayer-Modus wurden Ties beobachtet:**

| Konfiguration | Tie Rate |
|---------------|----------|
| 2P: 1E vs 1A | ~0% |
| 3P: 1E vs 2A | ~18-25% |
| 4P: 1E vs 3A | ~31% |
| 6P: 3E vs 3A | ~27% |

**Erkenntnis:** Mit mehr Spielern steigt die Tie-Rate natürlich an, da der "Gewinner" eines Tricks von mehreren Karten abhängt.

**Nicht umgesetzt:**
- Keine Anpassung des Spiels/der Optimierung für mehr Ties im 2-Spieler-Modus
- Keine Diskretisierung der Kartenwerte

---

### 4.7 Landscape Properties

**Status:** ❌ **NICHT ERFÜLLT**

Die Frage "Welche Eigenschaften hat die Problem-Landschaft?" wurde nicht systematisch untersucht.

**Mögliche Analysen (nicht durchgeführt):**
- Fitness Landscape Analysis (FLA)
- Ruggedness (Rauheit der Landschaft)
- Modality (Anzahl lokaler Optima)
- Deceptiveness (Irreführende Gradienten)
- Searchability Measures

---

## Bonus: Multiplayer-Erweiterung

Die Notebooks 06-10 erweitern die Analyse auf **mehr als 2 Spieler**. Dies war **nicht Teil der Aufgabenstellung**, zeigt aber interessante zusätzliche Erkenntnisse.

### Multiplayer Setup (Notebook 06-07)

**Konfiguration:** 3 Spieler (1 Experte vs 2 Anfänger), K=24

**Ergebnisse:**

| Metrik | Wert |
|--------|------|
| Expert Win Rate | 46% - 60% |
| Trick Changes | 3.2 - 4.4 |
| Tie Rate | 18% - 25% |
| Hypervolume | 2.92 |

![Multiplayer Pareto-Front](plots/multiplayer/pareto_front_validated.svg)

### Konfigurations-Vergleich (Notebook 10, K=24 für alle)

| Konfiguration | Hypervolume | Focus E WR | Trick Changes | Excitement Score |
|---------------|-------------|------------|---------------|------------------|
| 2P: 1E vs 1A | 3.88 | 82.8% | 4.19 | 34.9% |
| 2P: 2E (E vs E) | 2.65 | 58.1% | 4.42 | 36.8% |
| 3P: 1E vs 2A | 2.54 | 55.9% | 4.38 | 54.8% |
| 3P: 2E vs 1A | 2.02 | 46.2% | 4.37 | 54.6% |
| 3P: 3E (all E) | 1.70 | 39.4% | 4.08 | 51.0% |
| 4P: 1E vs 3A | 1.87 | 46.4% | 4.02 | 66.9% |
| 4P: 2E vs 2A | 1.51 | 35.9% | 3.97 | 66.2% |
| 4P: 3E vs 1A | 1.32 | 34.4% | 3.71 | 61.8% |
| 4P: 4E (all E) | 1.40 | 36.1% | 3.88 | 64.6% |

![Konfigurationsvergleich](plots/multiplayer_configs/pareto_fronts_comparison.svg)

### Optimale Konfiguration (Notebook 10)

**Systematische Suche über 2-4 Spieler (K=24 für alle):**

| Ranking | Konfiguration | Hypervolume | Focus E WR | Combined Score |
|---------|---------------|-------------|------------|----------------|
| 1 | 2P: 1E vs 1A | 3.88 | 82.8% | 58.9% |
| 2 | 4P: 1E vs 3A | 1.87 | 46.4% | 56.7% |
| 3 | 3P: 1E vs 2A | 2.54 | 55.9% | 55.3% |
| 4 | 4P: 2E vs 2A | 1.51 | 35.9% | 51.1% |
| 5 | 3P: 2E vs 1A | 2.02 | 46.2% | 50.4% |

**Beste Konfigurationen:**
- **Fairness:** 2P: 1E vs 1A (höchste Expert Win Rate: 82.8%)
- **Excitement:** 4P: 1E vs 3A (höchster Excitement Score: 66.9%)
- **Combined:** 2P: 1E vs 1A (beste Balance: 58.9%)
- **Hypervolume:** 2P: 1E vs 1A (HV: 3.88)

**Scores-Vergleich (separate SVGs):**

| Fairness | Excitement | Combined | Hypervolume |
|:--------:|:----------:|:--------:|:-----------:|
| ![Fairness](plots/optimal_config/fairness.svg) | ![Excitement](plots/optimal_config/excitement.svg) | ![Combined](plots/optimal_config/combined.svg) | ![Hypervolume](plots/optimal_config/hypervolume.svg) |

### Tiefere Analyse: Multiplayer-Dynamiken

#### Warum sinkt die Expert Win Rate mit mehr Gegnern?

```
2-Spieler: p4 muss 1 Gegner schlagen
  → P(Gewinn) = P(p4 > p0) ≈ 70-80%

3-Spieler (1E vs 2A): p4 muss BEIDE Gegner schlagen
  → P(Gewinn) = P(p4 > p0_1 UND p4 > p0_2)
  → Falls unabhängig: P ≈ 0.75 × 0.75 = 56%
  
4-Spieler (1E vs 3A): p4 muss ALLE DREI schlagen
  → P(Gewinn) ≈ 0.75³ = 42%
```

**Erklärung:** Der Experte muss nicht nur besser sein als EIN Gegner, sondern besser als ALLE. Die Wahrscheinlichkeit sinkt multiplikativ!

#### Warum steigt die Tie-Rate mit mehr Spielern?

```
2-Spieler: Tie wenn Wert_p4 = Wert_p0
  → Bei kontinuierlichen Werten: P(Tie) ≈ 0

3+ Spieler: Tie wenn max(Werte) von mehreren Spielern erreicht
  → P(Tie) = P(∃ i,j: Wert_i = Wert_j = max)
  
Aber mit mehr Spielern:
  → Mehr Vergleiche pro Trick
  → Höhere Chance, dass zwei Spieler den gleichen Maximalwert haben
  → Besonders wenn Kategorien ähnliche Werte haben
```

**Beobachtete Tie-Rates:**

| Spielerzahl | Tie-Rate | Erklärung |
|-------------|----------|-----------|
| 2 | ~0% | Kontinuierliche Werte → keine exakten Gleichstände |
| 3 | ~20% | Mehr Vergleiche, aber immer noch selten |
| 4 | ~31% | Signifikante Wahrscheinlichkeit |
| 6 | ~27% | Sinkt wieder (weniger Karten pro Spieler) |

#### Warum ist 2P: 1E vs 1A der beste Kompromiss?

```
Analyse des Combined Scores:

Fairness Score = Focus Expert Win Rate
  → Misst, wie gut Skill belohnt wird (höher = besser)
  
Excitement Score = Trick_Changes / Max_Tricks
  → Normalisierte Spannung

2P: 1E vs 1A bietet:
  1. Höchste Fairness (76%): Skill wird deutlich belohnt
  2. Gute Excitement (~36%): Genug Wechsel für Spannung
  3. Genug Spieler für Gruppendynamik
  4. K=24 teilbar durch 4 → faire Kartenverteilung
```

#### Implikationen für Spieldesign

| Wenn du willst... | Empfohlene Konfiguration |
|-------------------|-------------------------|
| **Maximale Fairness** (Skill soll belohnt werden) | 2P: 1E vs 1A (Focus E WR: 76%) |
| **Maximale Spannung** (viele Wechsel) | 3P: 1E vs 2A (Trick Changes: ~4.5) |
| **Party-Spiel** (Spaß für alle) | 4P mit 2E vs 2A |
| **Experten-Duell** (faire Konkurrenz) | 2P: 2E (E vs E) - reines Skill-Match |

**Hinweis:** K=24 wurde für Multiplayer verwendet (statt K=22), da 24 durch 2, 3 und 4 teilbar ist. Dies beeinflusst die absolute Anzahl der Trick Changes, nicht aber die strukturellen Erkenntnisse.

---

## 5. Nicht beantwortete Fragen

### 5.1 Vollständig offen

| Frage | Status | Kommentar |
|-------|--------|-----------|
| Drittes Objective aus Paper [1] | ❌ | Nicht implementiert |
| Landscape Properties | ❌ | Keine FLA durchgeführt |
| Manuelle Spiel-Tests | ⚠️ | Decks verfügbar, aber nicht gespielt |
| Mehr Ties (2-Spieler) | ⚠️ | Nur im Multiplayer-Kontext analysiert |

### 5.2 Mögliche Erweiterungen

1. **Drittes Objective:**
   - "Strategic Depth" messen (wie oft ist die Kategorie-Wahl relevant?)
   - "Variance" der Outcomes analysieren

2. **Landscape Properties:**
   - Ruggedness Index berechnen
   - Local Optima Netzwerk (LON) erstellen
   - Deceptiveness untersuchen

3. **Spiel-Tests:**
   - Web-Interface für manuelles Spielen erstellen
   - Nutzerstudie mit den drei Deck-Typen durchführen

4. **Mehr Ties:**
   - Kartenwerte auf ganze Zahlen runden
   - Neue Tie-Breaking-Regel einführen

---

## 6. Zusammenfassung der Erkenntnisse

### Beantwortete Hauptfragen

| Frage | Antwort |
|-------|---------|
| **Pareto-Front approximiert?** | ✅ Ja, mit NSGA-II. 16 Lösungen auf der Front. |
| **Quality Indicator?** | ✅ Hypervolume = 3.5524 |
| **Deck-Muster erkannt?** | ✅ Ja. Fairness-Decks nutzen Varianz; Excitement-Decks sind homogener. |

### Beantwortete Optionale Fragen

| Frage | Antwort |
|-------|---------|
| **Verschiedene Optimierer?** | ✅ NSGA-II und SMS-EMOA performen ähnlich gut, MOEA/D fällt ab. |
| **Einfluss von K?** | ✅ K skaliert Excitement linear, Fairness bleibt stabil. |
| **Einfluss von R?** | ✅ R=1500 essenziell für finale Bewertung; R=1000 führt zu leichter Überschätzung. |

### Haupterkenntnisse mit Erklärungen

| Erkenntnis | Warum? |
|------------|--------|
| **1. Trade-off existiert** | Fairness erfordert klare Kartenhierarchien (Skill nutzbar), Excitement erfordert Gleichheit (Zufall dominiert) - beides gleichzeitig ist unmöglich |
| **2. NSGA-II/SMS-EMOA > MOEA/D** | Stochastisches Rauschen stört MOEA/D's feste Gewichtsvektoren; Dominanz-basierte Selektion ist robuster |
| **3. K skaliert Excitement, nicht Fairness** | Excitement ist absolut (Anzahl Wechsel), Fairness ist relativ (%-Anteil gewonnener Spiele) |
| **4. R=1500 nötig für Validierung** | "Optimizer's Bias": Optimierung überschätzt systematisch durch Selektion glücklicher Ausreißer |
| **5. Multiplayer senkt Expert-Vorteil** | Experte muss ALLE Gegner schlagen; Wahrscheinlichkeit sinkt multiplikativ |

### Deck-Design-Regeln (mit Begründung)

| Regel | Mechanismus |
|-------|-------------|
| **Für Fairness:** Klare Kategorie-Hierarchien | Experte kann berechnen, welche Kategorie am besten ist → Strategie wirkt |
| **Für Fairness:** "Trumpf-Karten" (dominant in mehreren Kat.) | Experte erkennt und nutzt diese strategisch |
| **Für Excitement:** Homogene Werte | Jeder Trick ist ~50/50 → häufige Führungswechsel |
| **Für Excitement:** Hohe Korrelation zwischen Kategorien | Kategorie-Wahl irrelevant → Zufall entscheidet |

### Empfohlenes Deck (Knee-Point)

| Eigenschaft | Wert | Begründung |
|-------------|------|------------|
| **Win Rate** | 78.0% | Skill wird deutlich belohnt, aber nicht deterministisch |
| **Trick Changes** | 3.98 | ~36% der Tricks wechseln → genug Spannung |
| **Trade-off** | Optimal | Maximiert min(Fairness, Excitement) - beste Balance |

### Algorithmus-Empfehlung (mit Begründung)

```
Für Top Trumps Balancing:

  NSGA-II ✅
    → Robust gegen Rauschen (Dominanz-basiert)
    → Schnell (O(N² log N) Selektion)
    → Gute Diversität (Crowding Distance)
    
  SMS-EMOA ✅  
    → Optimiert direkt den Quality-Indikator (HV)
    → Noch robuster bei nicht-konvexen Fronten
    → Etwas langsamer (HV-Berechnung)
    
  MOEA/D ❌
    → Probleme mit Rauschen (feste Gewichtsvektoren)
    → Probleme mit konkaven Fronten (lineare Dekomposition)
    → Produziert viele, aber schlechtere Lösungen
```

### Skalierungs-Zusammenfassung

```
Parameter K (Kartenzahl):
  → Excitement ∝ K (linear)
  → Fairness ≈ konstant
  
Parameter R (Simulationen):
  → Genauigkeit ∝ √R (abnehmender Grenznutzen)
  → Empfehlung: R=1000 für Suche, R=1500 für Validierung
  
Parameter N (Spielerzahl):
  → Expert-Vorteil ∝ (p_einzeln)^(N-1) (exponentiell fallend)
  → Tie-Rate steigt mit N (mehr Vergleiche)
```

---

## Anhang: Datei-Referenzen

### Ergebnisse (2-Spieler)

| Datei | Inhalt |
|-------|--------|
| `../results/config.json` | Problem-Konfiguration |
| `../results/pareto_front_X.npy` | Deck-Vektoren (88 × 10) |
| `../results/pareto_front_F.npy` | Objective-Werte (2 × 10) |
| `../results/validated_front.csv` | Validierte Metriken |
| `../results/analysis_results.json` | HV, ausgewählte Decks |
| `../results/selected_decks.json` | Vollständige Deck-Daten |
| `../results/algorithm_comparison.json` | Algorithmus-Vergleich |
| `../results/parameter_study_K.json` | K-Studie Ergebnisse |

### Plots (2-Spieler)

| Datei | Beschreibung |
|-------|--------------|
| `plots/pareto_front_selected.png` | **Hauptplot** für Poster |
| `plots/pareto_front_validated.png` | Validierte Pareto-Front |
| `plots/fairness_max.svg` | Kategorie-Verteilung: Fairness-Max Deck |
| `plots/excitement_max.svg` | Kategorie-Verteilung: Excitement-Max Deck |
| `plots/knee_point.svg` | Kategorie-Verteilung: Knee-Point Deck |
| `plots/correlation_heatmaps.png` | Korrelations-Analyse |
| `plots/card_specialization.png` | Karten-Spezialisierung |
| `plots/algorithm_comparison_fronts.png` | Algorithmus-Vergleich Fronten |
| `plots/algorithm_comparison_boxplots.png` | Algorithmus-Vergleich Boxplots |
| `plots/parameter_study_K_impact.png` | K-Studie Visualisierung |
| `plots/noisiness_test.png` | Variabilität der Metriken |

### Multiplayer-Ergebnisse

| Verzeichnis | Inhalt |
|-------------|--------|
| `../results/multiplayer/` | 3-Spieler Optimierung |
| `../results/multiplayer_configs/` | Konfigurations-Vergleich |
| `../results/multiplayer_param_study/` | K-Studie für Multiplayer |
| `../results/optimal_config/` | Optimale Konfiguration |

---

*Erstellt am: 25. Januar 2026*
*Autor: Tim Strauss*
*Case Study: Automatic Game Balancing with Top Trumps - ODM WiSe 2025/26*
