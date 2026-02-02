# Top Trumps Balancing - Case Study

## Automatic Game Balancing mit Multi-Objective Optimization

Diese Case Study löst das Problem der automatischen Spielbalancierung für **Top Trumps** mittels evolutionärer Multi-Objective Optimierung.

---

## 📋 Problem-Definition

| Parameter | Wert | Beschreibung |
|-----------|------|--------------|
| K | 22 | Anzahl Karten im Deck |
| L | 4 | Anzahl Kategorien pro Karte |
| n_var | 88 | Entscheidungsvariablen (K × L) |
| Wertebereich | [1, 10] | Kartenwerte |

### Ziele (zu maximieren)

1. **Fairness** $f_1(x)$: Win-Rate des geschickteren Spielers p4
2. **Excitement** $f_2(x)$: Durchschnittliche Anzahl der Trick Changes

### Spieler-Strategien

- **p0 (Anfänger):** Wählt Kategorie mit höchstem normalisierten Wert
- **p4 (Experte):** Berechnet exakte Gewinnwahrscheinlichkeit basierend auf verbleibenden Karten

---

## 📁 Projektstruktur

```
Tim/
│
├── README.md                          ← Diese Datei
├── simulation.py                      ← Simulation Engine & Pymoo Wrapper
├── plot_config.py                     ← Plot-Styling Konfiguration
│
├── two_player/                        ← 2-Spieler Analyse (Basis)
│   ├── 01_setup_and_exploration.ipynb ← Setup & Sanity Checks
│   ├── 02_optimization.ipynb          ← NSGA-II Optimierung
│   ├── 03_analysis.ipynb              ← Analyse & Interpretation
│   ├── 04_algorithm_comparison.ipynb  ← NSGA-II vs MOEA/D vs SMS-EMOA
│   └── EXPERIMENT_ANALYSIS.md         ← Detaillierte Analyse-Dokumentation
│
├── hyperparameter_tuning/             ← Hyperparameter-Optimierung
│   ├── 01_tuning.ipynb                ← Basis Hyperparameter Tuning
│   ├── 02_spark.ipynb                 ← Spark-basiertes Tuning
│   ├── 03_cloud.ipynb                 ← Cloud Hyperparameter Tuning
│   ├── 04_full.ipynb                  ← Vollständiges Tuning
│   ├── 05_final_optimization.ipynb    ← Finale Optimierung
│   └── HYPERPARAMETER_TUNING_RESULTS.md
│
├── parameter_study/                   ← Parameter-Studien
│   └── 01_parameter_study.ipynb       ← Einfluss der Deckgröße K
│
├── multiplayer/                       ← Multiplayer-Erweiterung (3+ Spieler)
│   ├── 01_setup.ipynb                 ← Multiplayer Setup
│   ├── 02_optimization.ipynb          ← Multiplayer Optimierung
│   ├── 03_configurations.ipynb        ← Konfigurations-Vergleich
│   ├── 04_parameter_study.ipynb       ← K-Studie für Multiplayer
│   ├── 05_optimal_configuration.ipynb ← Optimale Konfiguration (2-6 Spieler)
│   └── MULTIPLAYER_PRESENTATION.md
│
├── landscape_analysis/                ← Fitness Landscape Analysis
│   └── 01_landscape_analysis.ipynb    ← ELA, FDC, Ruggedness
│
├── scripts/                           ← Hilfs-Skripte
│   ├── convert_png_to_svg.py
│   ├── evaluate_deck_scaling.py
│   ├── run_final_optimization.py
│   ├── run_hyperparameter_tuning.py
│   └── run_pipeline.ipynb             ← Pipeline-Steuerung
│
├── results/                           ← Generierte Ergebnisse (gitignored)
└── plots/                             ← Generierte Visualisierungen (gitignored)
```

---

## 🔄 Workflow

### Two-Player Analyse (Basis)

```
┌───────────────────────────────────────────┐
│  two_player/01_setup_and_exploration      │  ⏱️ < 10 Sek
│  ───────────────────────────────────────  │
│  • Pakete installieren                    │
│  • Simulation testen                      │
│  • Sanity Checks durchführen              │
└──────────────┬────────────────────────────┘
               │
               ▼
┌───────────────────────────────────────────┐
│  two_player/02_optimization               │  ⏱️ ~4-5 Min
│  ───────────────────────────────────────  │
│  • NSGA-II Optimierung (R=500)            │
│  • Validation mit R=1000                  │
└──────────────┬────────────────────────────┘
               │
               ▼
┌───────────────────────────────────────────┐
│  two_player/03_analysis                   │  ⏱️ < 10 Sek
│  ───────────────────────────────────────  │
│  • Hypervolume berechnen                  │
│  • Repräsentative Decks auswählen         │
│  • Poster-Plots erstellen                 │
└──────────────┬────────────────────────────┘
               │
               ▼
┌───────────────────────────────────────────┐
│  two_player/04_algorithm_comparison       │  ⏱️ ~1-2 Min
│  ───────────────────────────────────────  │
│  • NSGA-II vs MOEA/D vs SMS-EMOA          │
│  • Multi-Seed Validation                  │
└───────────────────────────────────────────┘
```

### Weitere Analysen

| Ordner | Inhalt |
|--------|--------|
| `hyperparameter_tuning/` | Systematisches Hyperparameter-Tuning (lokal, Spark, Cloud) |
| `parameter_study/` | Einfluss der Deckgröße K auf die Pareto-Front |
| `multiplayer/` | Erweiterung auf 3+ Spieler mit verschiedenen Konfigurationen |
| `landscape_analysis/` | Fitness Landscape Analysis (ELA, FDC, Ruggedness) |

---

## 🧠 Design-Entscheidungen

### Warum 3+1 Notebooks statt einem großen?

1. **Modularer Workflow:** Optimierung kann separat laufen und bei Bedarf wiederholt werden
2. **Kernel-Stabilität:** Lange Optimierungsläufe können den Kernel belasten
3. **Iterative Analyse:** Analyse kann mehrfach angepasst werden ohne Neuoptimierung
4. **Parallele Ausführung:** Notebook 04 kann parallel zu 02+03 laufen

### Warum FAST (R=100) + Validation (R=1000)?

| Phase | R | Zweck |
|-------|---|-------|
| FAST | 500 | Schnelle Suche im Lösungsraum |
| FINAL | 1000 | Robuste Schätzung für finale Bewertung |

**Grund:** Bei R=1000 pro Evaluation wäre die Optimierung zu langsam. Die zweistufige Strategie ermöglicht schnelle Exploration mit anschließender Validierung.

### Warum Hypervolume als Quality Indicator?

- Standard-Indikator für Multi-Objective Optimization
- Berücksichtigt Konvergenz UND Diversität
- Gut interpretierbar bei 2 Objectives
- Von pymoo direkt unterstützt

### Warum diese 3 repräsentativen Decks?

| Deck | Auswahl-Kriterium | Poster-Relevanz |
|------|-------------------|-----------------|
| Fairness-Max | Höchste Win Rate | Zeigt "faire" Decks |
| Excitement-Max | Höchste Trick Changes | Zeigt "spannende" Decks |
| Knee-Point | Bester Trade-off | Praktisch sinnvollste Wahl |

---

## ⚙️ Konfiguration

### Optimierungs-Parameter (Notebook 02)

```python
POP_SIZE = 100     # Population Size (erhöht für Diversität)
N_GEN = 100        # Generationen (erhöht für Konvergenz)
R_EVAL_FAST = 500  # Simulationen während Optimierung (erhöht für Stabilität)
R_EVAL_FINAL = 1000 # Simulationen für Validation
```

### Algorithmen-Vergleich (Notebook 04)

```python
POP_SIZE = 40      # Kleinere Population für schnelleren Vergleich
N_GEN = 80         # Mehr Generationen
R_SIMULATIONS = 500
```

---

## 📊 Erwartete Ergebnisse

### Pareto-Front

- **Win Rate:** ~50% bis ~85%
- **Trick Changes:** ~3 bis ~7
- **Trade-off:** Höhere Fairness → Weniger Excitement (typischerweise)

### Hypervolume

- **Referenzpunkt:** (0, 0) im minimierten Raum
- **Typischer HV:** 4-6 (abhängig von Algorithmus und Budget)

### Deck-Charakteristiken

- **Faire Decks:** Klare Kategorie-Unterschiede, p4 kann besser optimieren
- **Spannende Decks:** Ausgeglichene Werte, häufige Führungswechsel
- **Korrelationen:** Geringe Korrelationen → mehr strategische Vielfalt

---

## 🎨 Poster-Inhalte

Die folgenden Plots sind direkt für das A0-Poster verwendbar:

1. **`pareto_front_selected.png`** - Hauptvisualisierung der Pareto-Front
2. **`category_distributions.png`** - Vergleich der Deck-Typen
3. **`correlation_heatmaps.png`** - Kategoriekorrelationen
4. **`algorithm_comparison_fronts.png`** - Algorithmen-Vergleich (falls verwendet)

### Vorgeschlagene Poster-Struktur

```
┌────────────────────────────────────────────────────────────┐
│                    TITEL + AUTOREN                         │
├────────────────────────────────────────────────────────────┤
│  Problem-          │         Pareto-Front                  │
│  Definition        │         (pareto_front_selected.png)   │
│  ───────────       │                                       │
│  K=22, L=4         │                                       │
│  2 Objectives      │                                       │
├────────────────────┼───────────────────────────────────────┤
│  Methodik          │  Deck-Analyse                         │
│  ───────────       │  (category_distributions.png)         │
│  NSGA-II           │  (correlation_heatmaps.png)           │
│  R=1000            │                                       │
│  HV = X.XX         │                                       │
├────────────────────┴───────────────────────────────────────┤
│                    FAZIT + REFERENZEN                      │
└────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

```bash
# 1. In den Ordner wechseln
cd case-study/Tim

# 2. Two-Player Analyse (Basis):
#    Notebooks in two_player/ der Reihe nach ausführen:
#    - two_player/01_setup_and_exploration.ipynb
#    - two_player/02_optimization.ipynb
#    - two_player/03_analysis.ipynb
#    - two_player/04_algorithm_comparison.ipynb (optional)

# 3. Weitere Analysen:
#    - parameter_study/01_parameter_study.ipynb
#    - multiplayer/01_setup.ipynb → ... → 05_optimal_configuration.ipynb
#    - landscape_analysis/01_landscape_analysis.ipynb

# 4. Plots für Poster in plots/ verwenden
```

---

## 📚 Referenzen

- **Paper:** Volz, V., Rudolph, G., & Naujoks, B. (2016). "Demonstrating the Feasibility of Automatic Game Balancing". GECCO '16.
- **pymoo:** https://pymoo.org
- **Aufgabenstellung:** Exercise Sheet 7 - ODM Winter 2025/26

---

*Erstellt für die Case Study "Automatic Game Balancing with Top Trumps"*

## 🔬 Detaillierte Analyse & Ergebnisse

Dieser Abschnitt fasst die Erkenntnisse aus den durchgeführten Experimenten zusammen und beantwortet die Leitfragen der Aufgabenstellung.

### 1. Die Pareto-Front: Trade-off zwischen Fairness und Excitement
Die Optimierung mit NSGA-II zeigt einen klaren Konflikt (Trade-off) zwischen den beiden Zielen:
*   **Fairness** (Win-Rate des Experten p4) reicht von **~65% bis ~84%**.
*   **Excitement** (Anzahl Trick Changes) reicht von **~3.0 bis ~4.5** Wechsel pro Spiel.
*   **Erkenntnis:** Decks, die "fairer" sind (Skill wird belohnt), tendieren dazu, weniger Führungswechsel zu haben (deterministischer). Decks mit vielen Wechseln sind oft zufallsgetriebener und senken die Win-Rate des Experten.

**Empfohlenes Deck ("Knee Point"):**
Das Deck am "Knie" der Pareto-Front bietet den besten Kompromiss:
*   **Win Rate:** ~80% (Der Experte gewinnt immer noch souverän)
*   **Trick Changes:** ~3.8 (Das Spiel ist dynamisch und nicht einseitig)

### 2. Deck-Charakteristiken (Patterns)
Die Analyse der Deck-Strukturen (`two_player/03_analysis.ipynb`) offenbart signifikante Muster:
*   **Fairness-Decks:** Zeigen oft eine klare Hierarchie in den Kategorien. Bestimmte Karten sind "Trümpfe", die fast immer gewinnen. Dies ermöglicht dem Experten (p4), diese Karten strategisch einzusetzen.
*   **Excitement-Decks:** Haben homogenere Werteverteilungen. Karten sind oft ähnlich stark ("Coin-Flip" Situationen), was zu häufigen Führungswechseln führt, aber den strategischen Vorteil von p4 mindert.

### 3. Methodische Validierung
*   **Stochastisches Rauschen:** Da das Spiel Zufallselemente enthält (Mischen, Startspieler), variieren die Ergebnisse stark.
*   **Lösung:** Eine zweistufige Evaluierung (`R_FAST=500` für Optimierung, `R_FINAL=1000` für Validierung) eliminiert den "Optimizer's Bias". Die validierte Front liegt leicht unterhalb der im Optimierungsprozess gefundenen Front ("Regression to the Mean"), ist aber statistisch belastbar.
*   **Algorithmus-Wahl:** Der Vergleich über 5 unabhängige Seeds zeigt, dass **NSGA-II** und **SMS-EMOA** signifikant bessere Ergebnisse (höherer Hypervolume) liefern als MOEA/D für dieses spezifische Problem.

### 4. Parameter-Studie: Einfluss der Deckgröße (K)
Die Untersuchung von $K \in \{10, 22, 34\}$ (`parameter_study/01_parameter_study.ipynb`) zeigt:
*   **Excitement skaliert mit K:** Mehr Karten führen linear zu mehr möglichen Trick Changes (Front verschiebt sich nach oben).
*   **Fairness ist stabil:** Die erreichbare Win-Rate bleibt weitgehend unabhängig von der Deckgröße konstant (~60-85%). Fairness ist also primär eine Eigenschaft der relativen Kartenwerte, nicht der Spieldauer.

### 5. Antworten auf die Leitfragen

| Frage | Antwort / Ergebnis |
| :--- | :--- |
| **Approximate Pareto front?** | ✅ Erfolgreich approximiert mit NSGA-II (2 Mio. Simulationen). Dichte Front gefunden. |
| **Quality indicator?** | ✅ Hypervolume (HV) berechnet. Finaler HV ≈ 3.67 (validiert). |
| **Recognizable patterns?** | ✅ Ja. Fairness-Decks nutzen Varianz/Spezialisierung; Excitement-Decks nutzen Balance/Zufall. |
| **Different optimizers?** | ✅ NSGA-II und SMS-EMOA performen ähnlich stark und robust. MOEA/D fällt ab. |
| **Impact of K?** | ✅ $K$ skaliert die absolute Anzahl der Trick Changes, ändert aber nicht die Fairness-Balance. |
| **Influence of R?** | ✅ Hohes R (1000) ist essenziell für die finale Bewertung, da R=100 zu optimistisch verzerrt ist. |

---

## 🎮 Multiplayer-Erweiterung (3+ Spieler)

Die Multiplayer-Erweiterung ermöglicht die Analyse von Top Trumps mit **mehr als 2 Spielern** und **konfigurierbaren Strategien**.

### Konfigurierbare Spieler

| Strategie | Beschreibung |
|-----------|-------------|
| `p0` | **Anfänger:** Wählt Kategorie mit höchstem normalisierten Wert |
| `p4` | **Experte:** Berechnet Gewinnwahrscheinlichkeit gegen verbleibende Karten |

### Beispiel-Konfigurationen

```python
# 2 Spieler (Standard)
PLAYER_STRATEGIES = ['p4', 'p0']

# 3 Spieler: 1 Experte vs 2 Anfänger
PLAYER_STRATEGIES = ['p4', 'p0', 'p0']

# 3 Spieler: 2 Experten vs 1 Anfänger
PLAYER_STRATEGIES = ['p4', 'p4', 'p0']

# 4 Spieler: 1 Experte vs 3 Anfänger
PLAYER_STRATEGIES = ['p4', 'p0', 'p0', 'p0']
```

### Wichtige Unterschiede

| Aspekt | 2-Spieler | Multiplayer |
|--------|-----------|-------------|
| **Karten pro Spieler** | K/2 | K/N |
| **Metriken** | p4 Win Rate | Expert(s) Win Rate |
| **Tie-Handling** | Selten | Häufiger |
| **Ergebnisse** | `results/` | `results/multiplayer/` |
| **Plots** | `plots/` | `plots/multiplayer/` |

### Multiplayer-Workflow

```
┌─────────────────────────────────────┐
│  multiplayer/01_setup.ipynb         │
│  ─────────────────────────────────  │
│  • Spieler-Konfiguration wählen     │
│  • Simulation testen                │
│  • Sanity Checks durchführen        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  multiplayer/02_optimization.ipynb  │
│  ─────────────────────────────────  │
│  • NSGA-II Optimierung              │
│  • Validierung mit R=1000           │
│  • Pareto-Front & Analyse           │
└─────────────────────────────────────┘
```

### Hinweise

- **Deckgröße K muss durch Spieleranzahl teilbar sein!** (z.B. K=24 für 3 oder 4 Spieler)
- Ergebnisse werden **separat** in `results/multiplayer/` gespeichert
- Die 2-Spieler-Analyse bleibt **vollständig unberührt**

### Erweiterte Multiplayer-Analysen

```
┌─────────────────────────────────────────┐
│  multiplayer/03_configurations.ipynb    │
│  ─────────────────────────────────────  │
│  Vergleicht verschiedene Konfigurationen│
│  • 2P: 1v1 (Baseline)                   │
│  • 3P: 1v2, 2v1                         │
│  • 4P: 1v3, 2v2                         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  multiplayer/04_parameter_study.ipynb   │
│  ─────────────────────────────────────  │
│  Parameter-Studie: Kartenzahl K         │
│  • K = 12, 18, 24, 30, 36               │
│  • Korrelationsanalyse                  │
└─────────────────────────────────────────┘
```

### Fragestellungen der erweiterten Analysen

| Notebook | Fragestellung |
|----------|--------------|
| `multiplayer/03_configurations` | Wie verändert sich die Spieldynamik mit mehr Spielern? |
| `multiplayer/03_configurations` | Ist 2v2 fairer als 1v3? |
| `multiplayer/03_configurations` | Wie stark ist der Expert-Advantage bei verschiedenen Konstellationen? |
| `multiplayer/04_parameter_study` | Beeinflusst die Kartenzahl die Fairness bei Multiplayer? |
| `multiplayer/04_parameter_study` | Gibt es ein optimales K für Multiplayer? |

### Optimale Konfiguration (`multiplayer/05_optimal_configuration.ipynb`)

Systematische Suche nach der besten Spielerkonfiguration für K=22, L=4:

**Getestete Konfigurationen:**
- 2 Spieler: 1E vs 1A
- 3 Spieler: 1E vs 2A, 2E vs 1A
- 4 Spieler: 1E vs 3A, 2E vs 2A, 3E vs 1A
- 5 Spieler: 1E vs 4A, 2E vs 3A, 3E vs 2A, 4E vs 1A
- 6 Spieler: 1E vs 5A, 2E vs 4A, 3E vs 3A, 4E vs 2A, 5E vs 1A

**Metriken:**
| Metrik | Beschreibung |
|--------|-------------|
| Fairness Score | Focus Expert Win Rate (Skill wird belohnt) |
| Excitement Score | Trick Changes / Max mögliche Tricks |
| Combined Score | (Fairness + Excitement) / 2 |
| Hypervolume | Qualität der gesamten Pareto-Front |

**Ergebnisse in:** `results/optimal_config/`
