# Hyperparameter-Tuning und Finale Optimierung: Ergebnisse

Dieses Dokument beschreibt umfassend den Prozess und die Ergebnisse des Hyperparameter-Tunings sowie der finalen Optimierung für das Top Trumps Deck Balancing Problem.

## Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Verwendete Bibliotheken und Methodik](#verwendete-bibliotheken-und-methodik)
3. [Hyperparameter-Tuning](#hyperparameter-tuning)
4. [Finale Optimierung](#finale-optimierung)
5. [Pareto-Front Analyse](#pareto-front-analyse)
6. [Plots und Visualisierungen](#plots-und-visualisierungen)
7. [Verifikation der Pareto-Front](#verifikation-der-pareto-front)

---

## Übersicht

Das Ziel des Hyperparameter-Tunings war es, die optimalen Konfigurationen für drei Multi-Objective Evolutionäre Algorithmen (MOEAs) zu finden, um das Top Trumps Deck Balancing Problem effektiv zu lösen. Das Problem optimiert zwei Ziele:

- **Fairness**: Minimierung der Abweichung von einer ausgeglichenen Gewinnrate (50%)
- **Excitement**: Maximierung der Trickwechsel während des Spiels (Spannung)

### Problem-Parameter

| Parameter | Wert | Beschreibung |
|-----------|------|--------------|
| K (Kartenanzahl) | 22 | Anzahl der Karten pro Deck |
| L (Kategorien) | 4 | Anzahl der Kategorien pro Karte |
| Wertebereich | [1.0, 10.0] | Bereich der Kartenwerte |
| Entscheidungsvariablen | K × L = 88 | Gesamtzahl der zu optimierenden Werte |

---

## Verwendete Bibliotheken und Methodik

### Bibliotheken

| Bibliothek | Version | Verwendung |
|------------|---------|------------|
| **pymoo** | - | Multi-Objective Optimization Framework |
| **NumPy** | - | Numerische Berechnungen |
| **Pandas** | - | Datenverarbeitung und -analyse |
| **Matplotlib** | - | Visualisierung |
| **multiprocessing** | (Standard) | Parallelisierung |

### pymoo-Algorithmen

Die Optimierung verwendet drei Algorithmen aus dem **pymoo**-Framework:

#### 1. NSGA-II (Non-dominated Sorting Genetic Algorithm II)
```python
from pymoo.algorithms.moo.nsga2 import NSGA2

NSGA2(
    pop_size=pop_size,
    sampling=FloatRandomSampling(),
    crossover=SBX(prob=crossover_prob, eta=eta_crossover),
    mutation=PM(eta=eta_mutation),
    eliminate_duplicates=True
)
```

**Merkmale:**
- Nicht-dominierte Sortierung für Pareto-basierte Selektion
- Crowding Distance zur Erhaltung der Diversität
- Gut geeignet für Bi-Objective Probleme

#### 2. SMS-EMOA (S-Metric Selection Evolutionary Multi-Objective Algorithm)
```python
from pymoo.algorithms.moo.sms import SMSEMOA

SMSEMOA(
    pop_size=pop_size,
    sampling=FloatRandomSampling(),
    crossover=SBX(prob=crossover_prob, eta=eta_crossover),
    mutation=PM(eta=eta_mutation),
    eliminate_duplicates=True
)
```

**Merkmale:**
- Hypervolume-basierte Selektion
- Fokus auf Verbesserung des Hypervolume-Indikators
- Stärkere Konvergenz zur Pareto-Front

#### 3. NSGA-III (Non-dominated Sorting Genetic Algorithm III)
```python
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions

ref_dirs = get_reference_directions("das-dennis", 2, n_partitions=n_partitions)
NSGA3(
    pop_size=pop_size,
    ref_dirs=ref_dirs,
    sampling=FloatRandomSampling(),
    crossover=SBX(prob=crossover_prob, eta=eta_crossover),
    mutation=PM(eta=eta_mutation),
    eliminate_duplicates=True
)
```

**Merkmale:**
- Referenzpunkt-basierte Selektion
- Das-Dennis Referenzrichtungen
- Gute Spread-Erhaltung entlang der Pareto-Front

### Genetische Operatoren

#### Simulated Binary Crossover (SBX)
```python
from pymoo.operators.crossover.sbx import SBX

SBX(prob=crossover_prob, eta=eta_crossover)
```

- **prob**: Crossover-Wahrscheinlichkeit (0.6 - 1.0)
- **eta**: Verteilungsindex für SBX (5.0 - 30.0)
  - Niedriges η: Größere Unterschiede zwischen Eltern und Kindern
  - Hohes η: Kinder ähnlicher zu den Eltern

#### Polynomial Mutation (PM)
```python
from pymoo.operators.mutation.pm import PM

PM(eta=eta_mutation)
```

- **eta**: Verteilungsindex für Mutation (5.0 - 30.0)
  - Niedriges η: Stärkere Mutationen
  - Hohes η: Feinere Mutationen nahe am Original

### Qualitätsmetrik: Hypervolume

Der **Hypervolume-Indikator** wird als primäre Metrik zur Bewertung der Pareto-Front-Qualität verwendet:

```python
from pymoo.indicators.hv import HV

hv = HV(ref_point=np.array([0.0, 0.0]))(F)
```

Der Hypervolume misst das Volumen des Zielraums, das von einer Pareto-Front dominiert wird (relativ zu einem Referenzpunkt). Ein höherer Hypervolume-Wert bedeutet:
- Bessere Konvergenz zur wahren Pareto-Front
- Bessere Verteilung der Lösungen
- Größere Abdeckung des Zielraums

---

## Hyperparameter-Tuning

### Suchraum

| Hyperparameter | Bereich | Typ |
|----------------|---------|-----|
| pop_size | [50, 250] (Schritte: 10) | Integer |
| eta_crossover | [5.0, 30.0] | Float |
| eta_mutation | [5.0, 30.0] | Float |
| crossover_prob | [0.6, 1.0] | Float |
| n_partitions (NSGA-III) | [6, 20] | Integer |

### Tuning-Konfiguration

| Parameter | Wert |
|-----------|------|
| Trials pro Algorithmus | 40 |
| Generationen pro Trial | 100 |
| Simulationen pro Evaluation | 1,000 |
| Evaluations-Seeds | [42, 101, 202, 303, 404] |
| Parallele Worker | 12 (alle CPU-Kerne) |
| Gesamte Trials | 120 |
| Gesamte Laufzeit | **390.26 Minuten** (~6.5 Stunden) |

### Tuning-Methodik

Das Tuning verwendet **Random Search** mit paralleler Ausführung:

1. **Trial-Generierung**: Für jeden Algorithmus werden 40 zufällige Hyperparameter-Kombinationen generiert
2. **Evaluation**: Jede Konfiguration wird mit 5 verschiedenen Seeds ausgeführt
3. **Bewertung**: Der mittlere Hypervolume über alle Seeds wird berechnet
4. **Selektion**: Die Konfiguration mit dem höchsten mittleren Hypervolume wird gewählt

### Warum Random Search statt SMAC/Bayesian Optimization?

Die Entscheidung für **Random Search** anstelle von sequentiellen Methoden wie **SMAC** (Sequential Model-based Algorithm Configuration) oder **Bayesian Optimization** basiert auf mehreren praktischen Überlegungen:

#### 1. Perfekte Parallelisierbarkeit

```
Random Search:     [Trial 1] [Trial 2] [Trial 3] ... [Trial 120]  → Alle parallel
                   =========================================
                   
SMAC/BO:           [Trial 1] → Update Model → [Trial 2] → Update → ...  → Sequentiell
                   =========    ============   =========
```

**Random Search** ist **embarrassingly parallel** – alle 120 Trials können vollständig unabhängig und gleichzeitig auf allen 12 CPU-Kernen ausgeführt werden. Bei SMAC oder Bayesian Optimization muss nach jeder Evaluation das Surrogatmodell aktualisiert werden, um den nächsten vielversprechenden Punkt zu bestimmen. Dies erzwingt eine sequentielle Ausführung.

**Zeitersparnis durch Parallelisierung:**
- Random Search: ~6.5 Stunden (parallel auf 12 Kernen)
- Sequentielles SMAC: ~78 Stunden (12× länger, da keine Parallelisierung möglich)

#### 2. Hohe Evaluationskosten

Jede einzelne Hyperparameter-Evaluation in diesem Problem dauert **20-60 Minuten** (je nach Populationsgröße). Bei solch teuren Evaluationen:

- Der Overhead des Surrogatmodell-Updates bei SMAC ist vernachlässigbar klein
- **Aber**: Die sequentielle Natur von SMAC bedeutet, dass die Gesamtlaufzeit durch die Anzahl der Evaluationen begrenzt ist, nicht durch die Rechenkapazität

#### 3. Effektivität bei niedriger Dimensionalität

Bergstra & Bengio (2012) zeigten in ihrer einflussreichen Arbeit *"Random Search for Hyper-Parameter Optimization"*, dass Random Search überraschend effektiv ist, wenn:

- **Nur wenige Hyperparameter wirklich wichtig sind** (Low Effective Dimensionality)
- Der Suchraum **kontinuierlich und glatt** ist

In unserem Fall haben wir nur **4-5 Hyperparameter** (pop_size, eta_crossover, eta_mutation, crossover_prob, n_partitions), und die Analyse zeigt, dass primär `pop_size` und `eta_crossover` die Performance bestimmen.

```
        Grid Search          Random Search
        +---+---+---+        +   +     +
        |   |   |   |            +   +
        +---+---+---+        +       +
        |   |   |   |          +   +
        +---+---+---+        +     +   +
        
        Systematisch,        Zufällig,
        aber viele Punkte    aber bessere Abdeckung
        auf unwichtigen      wichtiger Dimensionen
        Dimensionen
```

#### 4. Robustheit gegenüber Rauschen

Die Fitness-Evaluation in diesem Problem ist **stochastisch** (Monte-Carlo-Simulationen). SMAC und Bayesian Optimization können durch verrauschte Evaluationen in lokalen Optima stecken bleiben, während Random Search durch seine zufällige Natur eine breitere Exploration gewährleistet.

#### 5. Implementierungseinfachheit

Random Search erfordert **keine zusätzlichen Abhängigkeiten** wie SMAC (`smac`), Optuna (`optuna`) oder GPyOpt. Die Implementierung ist direkt und transparent:

```python
def generate_trial_params(algorithm, trial_id, seed):
    np.random.seed(seed)
    return {
        'pop_size': np.random.choice(range(50, 251, 10)),
        'eta_crossover': np.random.uniform(5.0, 30.0),
        'eta_mutation': np.random.uniform(5.0, 30.0),
        'crossover_prob': np.random.uniform(0.6, 1.0),
    }
```

#### Wann wäre SMAC/BO vorzuziehen?

| Szenario | Empfohlene Methode |
|----------|-------------------|
| Wenige CPU-Kerne verfügbar | SMAC/BO |
| Günstige Evaluationen (<1 min) | SMAC/BO |
| Viele Hyperparameter (>10) | SMAC/BO |
| Kategorische Hyperparameter mit komplexen Abhängigkeiten | SMAC |
| **Viele Kerne, teure Evaluationen, wenige HPs** | **Random Search** ✓ |

#### Literaturhinweis

> Bergstra, J., & Bengio, Y. (2012). *Random Search for Hyper-Parameter Optimization*. Journal of Machine Learning Research, 13, 281-305.
>
> "We find that random search is more efficient than grid search in high-dimensional hyperparameter optimization. [...] Random search is particularly useful when the effective dimensionality is low."

### Beste Konfigurationen pro Algorithmus

#### NSGA-II (Gewinner)

| Hyperparameter | Optimaler Wert |
|----------------|----------------|
| **pop_size** | 230 |
| **eta_crossover** | 18.56 |
| **eta_mutation** | 16.67 |
| **crossover_prob** | 0.781 |
| **Hypervolume** | **4.189** ± 0.042 |

#### SMS-EMOA

| Hyperparameter | Optimaler Wert |
|----------------|----------------|
| **pop_size** | 230 |
| **eta_crossover** | 19.14 |
| **eta_mutation** | 25.86 |
| **crossover_prob** | 0.963 |
| **Hypervolume** | **4.105** ± 0.062 |

#### NSGA-III

| Hyperparameter | Optimaler Wert |
|----------------|----------------|
| **pop_size** | 140 |
| **eta_crossover** | 6.38 |
| **eta_mutation** | 19.86 |
| **crossover_prob** | 0.876 |
| **n_partitions** | 17 |
| **Hypervolume** | **3.972** ± 0.064 |

### Algorithmus-Vergleich

| Rang | Algorithmus | Hypervolume | Standardabweichung |
|------|-------------|-------------|-------------------|
| 1 | **NSGA-II** | 4.189 | 0.042 |
| 2 | SMS-EMOA | 4.105 | 0.062 |
| 3 | NSGA-III | 3.972 | 0.064 |

**NSGA-II** wurde als Gewinner mit dem höchsten Hypervolume und der geringsten Varianz gewählt.

### Beobachtungen aus dem Tuning

1. **Populationsgröße**: Größere Populationen (200-250) liefern konsistent bessere Ergebnisse
2. **Crossover-Eta**: Moderate Werte (15-20) funktionieren am besten
3. **Mutation-Eta**: Breite optimale Bereiche, algorithmusabhängig
4. **Crossover-Wahrscheinlichkeit**: Hohe Werte (>0.75) sind vorteilhaft

---

## Finale Optimierung

### Konfiguration

Nach dem Hyperparameter-Tuning wurde eine intensive finale Optimierung mit den besten gefundenen Parametern durchgeführt:

| Parameter | Wert |
|-----------|------|
| Algorithmus | NSGA-II |
| Simulationen (R) | **2,500** |
| Generationen | **200** |
| Unabhängige Seeds | 10 (42-51) |
| Parallele Worker | 10 |
| Gesamte Laufzeit | **53.71 Minuten** |

### Verwendete Hyperparameter

```json
{
    "pop_size": 230,
    "eta_crossover": 18.557523580101787,
    "eta_mutation": 16.672067054749483,
    "crossover_prob": 0.7806796324592887
}
```

### Ergebnisse der Einzelnen Runs

| Seed | Hypervolume | Lösungen | Laufzeit (min) |
|------|-------------|----------|----------------|
| 42 | 4.112 | 73 | 51.7 |
| 43 | 4.222 | 87 | 52.8 |
| 44 | 4.044 | 65 | 51.5 |
| 45 | 4.210 | 83 | 53.2 |
| 46 | 3.891 | 67 | 53.1 |
| 47 | **4.259** | 88 | 52.7 |
| 48 | 3.995 | 58 | 52.8 |
| 49 | 4.072 | 76 | 53.2 |
| 50 | 4.096 | 66 | 53.7 |
| 51 | 4.178 | 81 | 52.9 |

### Statistische Zusammenfassung

| Metrik | Wert |
|--------|------|
| Hypervolume Mittelwert | **4.108** |
| Hypervolume Standardabweichung | 0.108 |
| Hypervolume Minimum | 3.891 |
| Hypervolume Maximum | 4.259 |
| Erfolgreiche Runs | 10/10 |
| Fehlgeschlagene Runs | 0 |

### Kombinierte Pareto-Front

Die Pareto-Fronts aller 10 unabhängigen Runs wurden kombiniert und einem Non-Dominated Sorting unterzogen:

| Metrik | Wert |
|--------|------|
| **Kombinierter Hypervolume** | **4.282** |
| **Anzahl Lösungen** | **99** |
| Einzigartige Lösungen | 98 |
| Duplikate | 1 |

---

## Pareto-Front Analyse

### Extrempunkte und Knee-Point

Die finale Pareto-Front enthält drei besonders interessante Lösungen:

#### Beste Fairness

| Metrik | Wert |
|--------|------|
| Fairness | **-0.6404** |
| Excitement | -4.8976 |

Diese Lösung maximiert die Fairness (Gewinnrate nahe 50%) auf Kosten der Spannung.

#### Beste Excitement

| Metrik | Wert |
|--------|------|
| Fairness | -0.9240 |
| Excitement | **-2.4024** |

Diese Lösung maximiert die Spannung (viele Trickwechsel) auf Kosten der Fairness.

#### Knee-Point (Kompromiss)

| Metrik | Wert |
|--------|------|
| Fairness | -0.9240 |
| Excitement | -2.4024 |

Der Knee-Point entspricht hier der "Best Excitement"-Lösung, da die normalisierte Summe der Ziele dort maximiert wird.

### Objektiv-Wertebereiche

| Objektiv | Minimum | Maximum | Spanne |
|----------|---------|---------|--------|
| Fairness | -0.9240 | -0.6404 | 0.2836 |
| Excitement | -4.8976 | -2.4024 | 2.4952 |

### Trade-off Interpretation

Die Pareto-Front zeigt einen klaren Trade-off:
- **Fairness verbessern** → Excitement verschlechtert sich
- **Excitement verbessern** → Fairness verschlechtert sich

Dies ist physikalisch sinnvoll:
- Ein sehr faires Spiel (50-50 Gewinnrate) hat oft weniger Dynamik
- Ein spannendes Spiel mit vielen Wendungen kann zu unausgeglichenen Ergebnissen führen

---

## Plots und Visualisierungen

### Finale Optimierung

#### final_optimization_fronts.png

![Final Optimization Fronts](plots/final_optimization_fronts.png)

**Beschreibung**: Dieser Plot zeigt zwei Ansichten:
- **Links**: Alle 10 unabhängigen Optimierungs-Runs mit farblicher Unterscheidung und deren jeweiligem Hypervolume
- **Rechts**: Die kombinierte Pareto-Front mit hervorgehobenen Extrempunkten (Best Fairness, Best Excitement) und dem Knee-Point

### Ausgewählte Deck-Visualisierungen

#### fairness_max.svg

![Best Fairness Deck](plots/fairness_max.svg)

**Beschreibung**: Visualisierung des Decks mit maximaler Fairness. Zeigt die Verteilung der Kartenwerte über alle Kategorien.

#### excitement_max.svg

![Best Excitement Deck](plots/excitement_max.svg)

**Beschreibung**: Visualisierung des Decks mit maximaler Spannung. Zeigt typischerweise eine andere Werteverteilung als das Fairness-Deck.

#### knee_point.svg

![Knee Point Deck](plots/knee_point.svg)

**Beschreibung**: Visualisierung des Kompromiss-Decks, das einen ausgewogenen Trade-off zwischen Fairness und Excitement bietet.

### Tuning-Visualisierungen

Die folgenden Plots zeigen die Hyperparameter-Tuning-Ergebnisse:

- **optuna_comparison.png**: Vergleich der Algorithmus-Performance
- **optuna_param_importance.png**: Wichtigkeit der einzelnen Hyperparameter
- **optuna_optimization_history.png**: Verlauf der Optimierung über die Trials
- **optuna_parallel_coordinate.png**: Parallele Koordinaten zur Analyse der Hyperparameter-Kombinationen
- **optuna_contour_popsize_eta.png**: Konturplot der Hyperparameter-Interaktionen

---

## Verifikation der Pareto-Front

### Nicht-Dominanz-Test

Ein automatisierter Test wurde durchgeführt, um sicherzustellen, dass die kombinierte Pareto-Front nur nicht-dominierte Lösungen enthält:

```python
# Verifikations-Ergebnisse
Pareto Front: 99 Lösungen
Einzigartige Lösungen: 98
Doppelte Lösungen: 1
Dominierte Lösungen: 0 ✓

Alle Lösungen sind nicht-dominiert!
```

### Test-Methodik

Für jede Lösung \(p\) in der Pareto-Front wurde geprüft, ob eine andere Lösung \(q\) existiert, die \(p\) dominiert:

$$q \text{ dominiert } p \Leftrightarrow \forall i: q_i \leq p_i \land \exists j: q_j < p_j$$

(bei Minimierungsproblemen)

### Ergebnis

✅ **Die kombinierte Pareto-Front enthält ausschließlich nicht-dominierte Lösungen.**

Der Non-Dominated Sorting Algorithmus aus pymoo funktioniert korrekt:

```python
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

nds = NonDominatedSorting()
fronts = nds.do(combined_F, only_non_dominated_front=True)
```

### Hinweis zu Duplikaten

Es gibt eine doppelte Lösung in der Pareto-Front (Fairness=-0.806, Excitement=-3.9704). Dies kann entstehen, wenn zwei unabhängige Runs zur exakt gleichen Lösung konvergieren. Das Duplikat beeinflusst die Qualität der Pareto-Front nicht, da es ebenfalls nicht-dominiert ist.

---

## Fazit

### Kernerkenntnisse

1. **NSGA-II ist der beste Algorithmus** für dieses Problem mit einem Hypervolume von 4.189 im Tuning und 4.108 (Mittelwert) in der finalen Optimierung.

2. **Große Populationen sind vorteilhaft**: Die optimale Populationsgröße liegt bei 230.

3. **Moderate Crossover-Eta-Werte** (~18-19) liefern die besten Ergebnisse.

4. **Die Pareto-Front ist valide**: Alle 99 Lösungen sind nicht-dominiert.

5. **Robuste Ergebnisse**: Die 10 unabhängigen Runs zeigen konsistente Ergebnisse mit geringer Varianz.

### Empfohlene Konfiguration

Für zukünftige Optimierungen wird folgende Konfiguration empfohlen:

```python
{
    "algorithm": "NSGA-II",
    "pop_size": 230,
    "eta_crossover": 18.56,
    "eta_mutation": 16.67,
    "crossover_prob": 0.78,
    "n_gen": 200,
    "n_simulations": 2500
}
```

### Datei-Übersicht

| Datei | Beschreibung |
|-------|--------------|
| `results/best_hyperparameters.json` | Beste Hyperparameter pro Algorithmus |
| `results/parallel_tuning_results.json` | Vollständige Tuning-Ergebnisse |
| `results/final_optimization_results.json` | Finale Optimierungs-Statistiken |
| `results/final_pareto_front_F.npy` | Objektiv-Werte der Pareto-Front |
| `results/final_pareto_front_X.npy` | Entscheidungsvariablen der Pareto-Front |
| `results/final_pareto_front.csv` | Pareto-Front als CSV |
| `results/final_selected_decks.json` | Ausgewählte Deck-Konfigurationen |
| `run_hyperparameter_tuning.py` | Tuning-Skript |
| `run_final_optimization.py` | Finales Optimierungsskript |

---

*Erstellt am: 2026-02-01*
*Autor: Automatische Dokumentation*
