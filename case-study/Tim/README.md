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
├── run_pipeline.ipynb                 ← ⚡ Steuerungs-Notebook (Führt alles aus)
├── simulation.py                      ← Simulation Engine & Pymoo Wrapper (Shared Logic)
│
├── 01_setup_and_exploration.ipynb     ← Setup & Sanity Checks
├── 02_optimization.ipynb              ← NSGA-II Optimierung
├── 03_analysis.ipynb                  ← Analyse & Interpretation
├── 04_algorithm_comparison.ipynb      ← Algorithmen-Vergleich (NSGA-II vs MOEA/D vs SMS-EMOA)
├── 05_parameter_study.ipynb           ← Parameter-Studie (Einfluss von Deckgröße K)
│
├── 06_multiplayer_setup.ipynb         ← 🆕 Multiplayer Setup (3+ Spieler)
├── 07_multiplayer_optimization.ipynb  ← 🆕 Multiplayer Optimierung
├── 08_multiplayer_configurations.ipynb ← 🆕 Konfigurations-Vergleich
├── 09_multiplayer_parameter_study.ipynb ← 🆕 K-Studie für Multiplayer
├── 10_optimal_configuration.ipynb     ← 🆕 Optimale Konfiguration (2-6 Spieler)
│
├── 11_landscape_analysis.ipynb        ← 🔬 Fitness Landscape Analysis (ELA, FDC, Ruggedness)
├── 07_multiplayer_optimization.ipynb  ← 🆕 Multiplayer Optimierung
│
├── results/                           ← Generierte Ergebnisse (2-Spieler)
│   ├── config.json                    ← Konfiguration
│   ├── pareto_front_X.npy             ← Lösungen (Deck-Vektoren)
│   ├── pareto_front_F.npy             ← Objective-Werte
│   ├── validated_front.csv            ← Validierte Metriken
│   ├── optimization_results.json      ← Optimierungs-Statistiken
│   ├── selected_decks.json            ← Ausgewählte repräsentative Decks
│   ├── analysis_results.json          ← Analyse-Ergebnisse (HV etc.)
│   └── algorithm_comparison.json      ← Vergleichs-Ergebnisse
│
├── results/multiplayer/               ← 🆕 Multiplayer-Ergebnisse (getrennt!)
│   ├── config.json                    ← Multiplayer-Konfiguration
│   ├── pareto_front_X.npy
│   ├── pareto_front_F.npy
│   ├── validated_front.csv
│   ├── selected_decks.json
│   └── optimization_results.json
│
├── plots/                             ← Generierte Visualisierungen (2-Spieler)
    ├── noisiness_test.png             ← Variabilität der Metriken
    ├── objective_space_exploration.png
    ├── pareto_front_fast.png
    ├── pareto_front_validated.png
    ├── pareto_front_selected.png      ← ⭐ Hauptplot fürs Poster
    ├── category_distributions.png
    ├── correlation_heatmaps.png
    ├── card_specialization.png
    ├── algorithm_comparison_fronts.png
    └── algorithm_comparison_metrics.png
```

---

## 🔄 Workflow

### Ausführungsreihenfolge (via `run_pipeline.ipynb`)

```
┌─────────────────────────────────────┐
│  01_setup_and_exploration.ipynb     │  ⏱️ < 10 Sek
│  ─────────────────────────────────  │
│  • Pakete installieren              │
│  • Simulation testen                │
│  • Sanity Checks durchführen        │
│  • config.json erstellen            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  02_optimization.ipynb              │  ⏱️ ~4-5 Min (High Quality)
│  ─────────────────────────────────  │
│  • NSGA-II Optimierung (R=500)      │
│  • Validation mit R=1000            │
│  • Pareto-Front speichern           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  03_analysis.ipynb                  │  ⏱️ < 10 Sek
│  ─────────────────────────────────  │
│  • Hypervolume berechnen            │
│  • Repräsentative Decks auswählen   │
│  • Deck-Analyse (Kategorien, Korr.) │
│  • Poster-Plots erstellen           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  04_algorithm_comparison.ipynb      │  ⏱️ ~1-2 Min (5 Seeds)
│  ─────────────────────────────────  │
│  • NSGA-II vs MOEA/D vs SMS-EMOA    │
│  • Multi-Seed Validation (R=1000)   │
│  • Boxplots zur Signifikanz         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  05_parameter_study.ipynb           │  ⏱️ ~3-4 Min (K=10,22,34)
│  ─────────────────────────────────  │
│  • Einfluss der Deckgröße (K)       │
│  • Vergleich der Pareto-Fronten     │
└─────────────────────────────────────┘
```

### Abhängigkeiten

| Notebook | Benötigt | Erzeugt |
|----------|----------|---------|
| 01 | - | `config.json` |
| 02 | `config.json` | `pareto_front_*.npy`, `validated_front.csv` |
| 03 | Alles von 02 | `selected_decks.json`, Plots |
| 04 | `config.json` | `algorithm_comparison.json` |

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
cd /Users/tim.strauss/ODM/odm_sheet1/case-study/Tim

# 2. Pipeline ausführen (empfohlen):
#    Öffne und starte `run_pipeline.ipynb`
#    ODER führe die Notebooks manuell nacheinander aus:

# 3. Notebooks der Reihe nach ausführen (manuell):
#    - 01_setup_and_exploration.ipynb
#    - 02_optimization.ipynb
#    - 03_analysis.ipynb
#    - (optional) 04_algorithm_comparison.ipynb

# 3. Plots für Poster in plots/ verwenden
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
Die Analyse der Deck-Strukturen (`03_analysis.ipynb`) offenbart signifikante Muster:
*   **Fairness-Decks:** Zeigen oft eine klare Hierarchie in den Kategorien. Bestimmte Karten sind "Trümpfe", die fast immer gewinnen. Dies ermöglicht dem Experten (p4), diese Karten strategisch einzusetzen.
*   **Excitement-Decks:** Haben homogenere Werteverteilungen. Karten sind oft ähnlich stark ("Coin-Flip" Situationen), was zu häufigen Führungswechseln führt, aber den strategischen Vorteil von p4 mindert.

### 3. Methodische Validierung
*   **Stochastisches Rauschen:** Da das Spiel Zufallselemente enthält (Mischen, Startspieler), variieren die Ergebnisse stark.
*   **Lösung:** Eine zweistufige Evaluierung (`R_FAST=500` für Optimierung, `R_FINAL=1000` für Validierung) eliminiert den "Optimizer's Bias". Die validierte Front liegt leicht unterhalb der im Optimierungsprozess gefundenen Front ("Regression to the Mean"), ist aber statistisch belastbar.
*   **Algorithmus-Wahl:** Der Vergleich über 5 unabhängige Seeds zeigt, dass **NSGA-II** und **SMS-EMOA** signifikant bessere Ergebnisse (höherer Hypervolume) liefern als MOEA/D für dieses spezifische Problem.

### 4. Parameter-Studie: Einfluss der Deckgröße (K)
Die Untersuchung von $K \in \{10, 22, 34\}$ (`05_parameter_study.ipynb`) zeigt:
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
│  06_multiplayer_setup.ipynb         │
│  ─────────────────────────────────  │
│  • Spieler-Konfiguration wählen     │
│  • Simulation testen                │
│  • Sanity Checks durchführen        │
│  • results/multiplayer/config.json  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  07_multiplayer_optimization.ipynb  │
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
│  08_multiplayer_configurations.ipynb    │
│  ─────────────────────────────────────  │
│  Vergleicht verschiedene Konfigurationen│
│  • 2P: 1v1 (Baseline)                   │
│  • 3P: 1v2, 2v1                         │
│  • 4P: 1v3, 2v2                         │
│  → results/multiplayer_configs/         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  09_multiplayer_parameter_study.ipynb   │
│  ─────────────────────────────────────  │
│  Parameter-Studie: Kartenzahl K         │
│  • K = 12, 18, 24, 30, 36               │
│  • Korrelationsanalyse                  │
│  → results/multiplayer_param_study/     │
└─────────────────────────────────────────┘
```

### Fragestellungen der erweiterten Analysen

| Notebook | Fragestellung |
|----------|--------------|
| 08 | Wie verändert sich die Spieldynamik mit mehr Spielern? |
| 08 | Ist 2v2 fairer als 1v3? |
| 08 | Wie stark ist der Expert-Advantage bei verschiedenen Konstellationen? |
| 09 | Beeinflusst die Kartenzahl die Fairness bei Multiplayer? |
| 09 | Gibt es ein optimales K für Multiplayer? |

### Optimale Konfiguration (10_optimal_configuration.ipynb)

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
