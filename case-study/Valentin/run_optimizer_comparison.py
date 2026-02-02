#!/usr/bin/env python3
"""
Parallelisierter Optimizer-Vergleich für Top Trumps Balancing
Führt 4 Algorithmen gleichzeitig auf 4 Kernen aus.

Ausführen: python run_optimizer_comparison.py
"""

import random
import time
import numpy as np
import json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

# ============================================================
# KONFIGURATION
# ============================================================

N_GEN = 200
N_SIMULATIONS = 1000
SEED = 42
K = 22  # Karten
L = 4   # Kategorien

# History speichern für Convergence-Plot (mehr Speicherverbrauch)
SAVE_HISTORY = True

RESULTS_DIR = Path("results")
PLOTS_DIR = Path("plots")

# ============================================================
# PROBLEM DEFINITION (muss im globalen Scope sein für Pickle)
# ============================================================

class TopTrumpsSimulation:
    def __init__(self, num_cards=52, num_categories=6):
        self.K = num_cards
        self.L = num_categories
        self.set_random_deck()

    def _normalize_deck(self, deck):
        min_values = [0] * self.L
        max_values = [0] * self.L
        for cat in range(self.L):
            all_values = [card[cat] for card in deck]
            min_values[cat] = min(all_values)
            max_values[cat] = max(all_values)
        normalized_deck = []
        for card in deck:
            normalized_card = [0] * self.L
            for cat in range(self.L):
                normalized_card[cat] = (card[cat] - min_values[cat]) / (max_values[cat] - min_values[cat])
            normalized_deck.append(normalized_card)
        return normalized_deck

    def set_deck(self, deck_list):
        assert len(deck_list) == self.K * self.L
        deck = np.array_split(deck_list, self.K)
        self.deck = deck
        self._normalized_deck = self._normalize_deck(deck)

    def set_random_deck(self, value_range=(1, 10)):
        deck_list = np.random.uniform(value_range[0], value_range[1], self.K * self.L)
        self.set_deck(deck_list)

    def get_p0_choice(self, card):
        return card.index(max(card))

    def get_p4_choice(self, card, remaining_cards):
        best_prob = -1
        best_cat = 0
        for cat_idx in range(self.L):
            my_val = card[cat_idx]
            wins = sum(1 for opp_card in remaining_cards if my_val > opp_card[cat_idx])
            prob = wins / len(remaining_cards)
            if prob > best_prob:
                best_prob = prob
                best_cat = cat_idx
        return best_cat

    def simulate_game(self):
        temp_deck = list(self._normalized_deck)
        random.shuffle(temp_deck)
        p4_hand = temp_deck[:self.K//2]
        p0_hand = temp_deck[self.K//2:]
        all_unplayed = list(temp_deck)
        p4_tricks = 0
        current_turn = random.choice(['p4', 'p0'])
        trick_changes = 0

        for i in range(self.K // 2):
            card_p4 = p4_hand[i]
            card_p0 = p0_hand[i]
            if current_turn == 'p4':
                category = self.get_p4_choice(card_p4, all_unplayed)
            else:
                category = self.get_p0_choice(card_p0)
            val_p4 = card_p4[category]
            val_p0 = card_p0[category]
            all_unplayed.remove(card_p0)
            all_unplayed.remove(card_p4)
            if val_p4 > val_p0:
                p4_tricks += 1
                if current_turn == 'p0':
                    current_turn = 'p4'
                    trick_changes += 1
            elif val_p0 > val_p4:
                if current_turn == 'p4':
                    current_turn = 'p0'
                    trick_changes += 1

        return {
            "p4_tricks": p4_tricks,
            "trick_changes": trick_changes,
            "p4_won": p4_tricks > (self.K / 4)
        }


def run_single_algorithm(params):
    """Führt einen einzelnen Algorithmus aus (wird in separatem Prozess ausgeführt)."""
    import numpy as np
    import random
    import time
    
    from pymoo.core.problem import ElementwiseProblem
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.algorithms.moo.nsga3 import NSGA3
    from pymoo.algorithms.moo.moead import MOEAD
    from pymoo.algorithms.moo.sms import SMSEMOA
    from pymoo.operators.crossover.sbx import SBX
    from pymoo.operators.mutation.pm import PM
    from pymoo.operators.sampling.rnd import FloatRandomSampling
    from pymoo.optimize import minimize
    from pymoo.termination import get_termination
    from pymoo.indicators.hv import HV
    from pymoo.util.ref_dirs import get_reference_directions
    
    algo_name = params['algorithm']
    seed = params['seed']
    n_gen = params['n_gen']
    n_simulations = params['n_simulations']
    k = params['K']
    l = params['L']
    save_history = params.get('save_history', False)
    
    np.random.seed(seed)
    random.seed(seed)
    
    # Problem-Klasse (muss hier definiert werden wegen Pickle)
    class TopTrumpsBalancing(ElementwiseProblem):
        def __init__(self, sim_instance, n_simulations):
            self.sim = sim_instance
            self.n_simulations = n_simulations
            n_var = self.sim.K * self.sim.L
            super().__init__(n_var=n_var, n_obj=2, n_constr=0, xl=1.0, xu=10.0)

        def _evaluate(self, x, out, *args, **kwargs):
            self.sim.set_deck(x)
            win_rates = []
            trick_changes_list = []
            for _ in range(self.n_simulations):
                res = self.sim.simulate_game()
                win_rates.append(1 if res['p4_won'] else 0)
                trick_changes_list.append(res['trick_changes'])
            out["F"] = [-np.mean(win_rates), -np.mean(trick_changes_list)]
    
    # Problem erstellen
    sim = TopTrumpsSimulation(num_cards=k, num_categories=l)
    problem = TopTrumpsBalancing(sim, n_simulations=n_simulations)
    
    # Reference directions für NSGA-III und MOEA/D
    ref_dirs = get_reference_directions("das-dennis", 2, n_partitions=99)
    
    # Algorithmus erstellen
    if algo_name == 'NSGA-II':
        algorithm = NSGA2(
            pop_size=230,
            n_offsprings=230,  # Explizit wie im Notebook
            sampling=FloatRandomSampling(),
            crossover=SBX(prob=0.781, eta=18.56),
            mutation=PM(eta=16.67),
            eliminate_duplicates=True
        )
    elif algo_name == 'NSGA-III':
        algorithm = NSGA3(
            pop_size=140,
            ref_dirs=ref_dirs,
            sampling=FloatRandomSampling(),
            crossover=SBX(prob=0.876, eta=6.38),
            mutation=PM(eta=19.86),
            eliminate_duplicates=True
        )
    elif algo_name == 'MOEA/D':
        algorithm = MOEAD(
            ref_dirs=ref_dirs,
            n_neighbors=20,
            prob_neighbor_mating=0.9,
            sampling=FloatRandomSampling(),
            crossover=SBX(prob=0.781, eta=18.56),
            mutation=PM(eta=16.67),
        )
    elif algo_name == 'SMS-EMOA':
        algorithm = SMSEMOA(
            pop_size=230,
            sampling=FloatRandomSampling(),
            crossover=SBX(prob=0.963, eta=19.14),
            mutation=PM(eta=25.86),
        )
    else:
        raise ValueError(f"Unknown algorithm: {algo_name}")
    
    termination = get_termination("n_gen", n_gen)
    
    print(f"[{algo_name}] Starting optimization...")
    start_time = time.time()
    
    res = minimize(
        problem,
        algorithm,
        termination,
        seed=seed,
        save_history=save_history,
        verbose=False
    )
    
    runtime = time.time() - start_time
    
    # Hypervolume berechnen
    hv_indicator = HV(ref_point=np.array([0.0, 0.0]))
    hv = hv_indicator(res.F)
    
    # Hypervolume-History für Convergence-Plot extrahieren
    hv_history = []
    if save_history and res.history is not None:
        for entry in res.history:
            if entry.opt is not None:
                try:
                    hv_val = hv_indicator(entry.opt.get("F"))
                    hv_history.append(float(hv_val))
                except:
                    pass
    
    print(f"[{algo_name}] Completed: {len(res.F)} solutions, HV={hv:.4f}, Time={runtime:.1f}s")
    
    return {
        'algorithm': algo_name,
        'F': res.F.tolist(),
        'X': res.X.tolist(),
        'hypervolume': float(hv),
        'n_solutions': len(res.F),
        'runtime': runtime,
        'hv_history': hv_history,
        'status': 'completed'
    }


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    PLOTS_DIR.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("PARALLEL OPTIMIZER COMPARISON")
    print("=" * 70)
    
    algorithms = ['NSGA-II', 'NSGA-III', 'MOEA/D', 'SMS-EMOA']
    n_workers = min(4, mp.cpu_count())
    
    print(f"Algorithms: {algorithms}")
    print(f"Generations: {N_GEN}")
    print(f"Simulations: {N_SIMULATIONS}")
    print(f"Workers: {n_workers}")
    print(f"Save History: {SAVE_HISTORY}")
    print("=" * 70)
    
    # Jobs vorbereiten
    jobs = []
    for algo in algorithms:
        jobs.append({
            'algorithm': algo,
            'seed': SEED,
            'n_gen': N_GEN,
            'n_simulations': N_SIMULATIONS,
            'K': K,
            'L': L,
            'save_history': SAVE_HISTORY
        })
    
    # Parallel ausführen
    print(f"\nStarting {len(jobs)} algorithms in parallel...")
    total_start = time.time()
    
    all_results = {}
    
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = {executor.submit(run_single_algorithm, job): job['algorithm'] for job in jobs}
        
        for future in as_completed(futures):
            algo_name = futures[future]
            try:
                result = future.result()
                all_results[algo_name] = result
            except Exception as e:
                print(f"[{algo_name}] FAILED: {e}")
                all_results[algo_name] = {'algorithm': algo_name, 'status': 'failed', 'error': str(e)}
    
    total_time = time.time() - total_start
    
    # ================================================================
    # IGD-Berechnung (wie im Notebook)
    # ================================================================
    from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting
    from pymoo.indicators.igd import IGD
    
    # Kombiniere alle Fronten für Referenz-Front
    completed_results = {name: r for name, r in all_results.items() if r.get('status') == 'completed'}
    all_F = np.vstack([np.array(r['F']) for r in completed_results.values()])
    
    # Non-dominated Sorting für Referenz-Front
    nds = NonDominatedSorting()
    fronts = nds.do(all_F)
    reference_front = all_F[fronts[0]]
    
    print(f"\nReference front size: {len(reference_front)} solutions")
    
    # IGD für jeden Algorithmus berechnen
    igd_indicator = IGD(reference_front)
    for name, r in completed_results.items():
        r['igd'] = float(igd_indicator(np.array(r['F'])))
    
    # ================================================================
    # Ergebnis-Ausgabe
    # ================================================================
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total Runtime: {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"Speedup vs Sequential: ~{sum(r.get('runtime', 0) for r in all_results.values()) / total_time:.1f}x")
    
    # Ranking nach Hypervolume
    ranking = sorted(
        [(name, r) for name, r in completed_results.items()],
        key=lambda x: x[1]['hypervolume'],
        reverse=True
    )
    
    print("\n" + "-" * 85)
    print(f"{'Rank':<6} {'Algorithm':<15} {'Hypervolume':>12} {'IGD':>12} {'Solutions':>12} {'Runtime':>12}")
    print("-" * 85)
    
    for i, (name, r) in enumerate(ranking, 1):
        print(f"{i:<6} {name:<15} {r['hypervolume']:>12.6f} {r['igd']:>12.6f} {r['n_solutions']:>12} {r['runtime']:>11.1f}s")
    
    print("-" * 85)
    print(f"Best Hypervolume: {ranking[0][0]} (HV={ranking[0][1]['hypervolume']:.6f})")
    print(f"Best IGD: {min(completed_results.items(), key=lambda x: x[1]['igd'])[0]}")
    print(f"Best Runtime: {min(completed_results.items(), key=lambda x: x[1]['runtime'])[0]}")
    
    # ================================================================
    # Ergebnisse speichern
    # ================================================================
    output = {
        'config': {
            'n_gen': N_GEN,
            'n_simulations': N_SIMULATIONS,
            'seed': SEED,
            'K': K,
            'L': L,
            'total_runtime': total_time
        },
        'results': {name: {k: v for k, v in r.items() if k not in ['F', 'X', 'hv_history']} 
                   for name, r in all_results.items()},
        'ranking': [name for name, _ in ranking],
        'reference_front_size': len(reference_front)
    }
    
    with open(RESULTS_DIR / 'optimizer_comparison.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    # Pareto-Fronten speichern
    for name, r in completed_results.items():
        np.save(RESULTS_DIR / f'optimizer_{name.replace("/", "_")}_F.npy', np.array(r['F']))
    
    # Referenz-Front speichern
    np.save(RESULTS_DIR / 'optimizer_reference_front.npy', reference_front)
    
    print(f"\nResults saved to {RESULTS_DIR}/")
    
    # ================================================================
    # Plots erstellen (wie im Notebook)
    # ================================================================
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        colors = plt.colormaps['tab10']
        markers = ['o', 's', '^', 'D', 'v']
        
        # ----------------------------------------------------------
        # Plot 1: Pareto Front Comparison (wie Notebook Cell 16)
        # ----------------------------------------------------------
        fig, ax = plt.subplots(figsize=(12, 8))
        
        for i, (name, r) in enumerate(completed_results.items()):
            F = np.array(r['F'])
            ax.scatter(-F[:, 0], -F[:, 1], 
                      c=[colors(i)], marker=markers[i % len(markers)],
                      s=80, alpha=0.7, edgecolors='black', linewidth=0.5,
                      label=f"{name} (HV={r['hypervolume']:.4f})")
        
        ax.set_xlabel('Fairness', fontsize=20)
        ax.set_ylabel('Excitement', fontsize=20)
        ax.set_title('Pareto Front Comparison Across Optimizers', fontsize=28)
        ax.legend(loc='best', fontsize=16)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / 'optimizer_comparison_pareto.png', dpi=150)
        plt.savefig(PLOTS_DIR / 'optimizer_comparison_pareto.svg', bbox_inches='tight')
        print(f"Plot saved: optimizer_comparison_pareto.png/svg")
        plt.close()
        
        # ----------------------------------------------------------
        # Plot 2: Convergence Analysis (wie Notebook Cell 18)
        # ----------------------------------------------------------
        if SAVE_HISTORY:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            for i, (name, r) in enumerate(completed_results.items()):
                hv_history = r.get('hv_history', [])
                if hv_history:
                    generations = range(1, len(hv_history) + 1)
                    ax.plot(generations, hv_history, color=colors(i), linewidth=2, label=name)
            
            ax.set_xlabel('Generation', fontsize=20)
            ax.set_ylabel('Hypervolume', fontsize=20)
            ax.set_title('Convergence: Hypervolume over Generations', fontsize=28)
            ax.legend(loc='lower right', fontsize=16)
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(PLOTS_DIR / 'optimizer_convergence.png', dpi=150)
            plt.savefig(PLOTS_DIR / 'optimizer_convergence.svg', bbox_inches='tight')
            print(f"Plot saved: optimizer_convergence.png/svg")
            plt.close()
        
        # ----------------------------------------------------------
        # Plot 3: Runtime Comparison (wie Notebook Cell 20)
        # ----------------------------------------------------------
        fig, ax = plt.subplots(figsize=(10, 6))
        
        names = list(completed_results.keys())
        times = [completed_results[n]['runtime'] for n in names]
        colors_list = [colors(algorithms.index(n)) for n in names]
        
        bars = ax.bar(names, times, color=colors_list, edgecolor='black', linewidth=1)
        
        for bar, t in zip(bars, times):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                   f'{t:.1f}s', ha='center', va='bottom', fontsize=10)
        
        ax.set_xlabel('Algorithm', fontsize=12)
        ax.set_ylabel('Runtime (seconds)', fontsize=12)
        ax.set_title('Runtime Comparison', fontsize=14)
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / 'optimizer_runtime.png', dpi=150)
        print(f"Plot saved: optimizer_runtime.png")
        plt.close()
        
        # ----------------------------------------------------------
        # Plot 4: Performance Summary (wie Notebook Cell 22)
        # ----------------------------------------------------------
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        names = list(completed_results.keys())
        colors_list = [colors(algorithms.index(n)) for n in names]
        
        # Hypervolume (higher is better)
        hvs = [completed_results[n]['hypervolume'] for n in names]
        axes[0].bar(names, hvs, color=colors_list, edgecolor='black')
        axes[0].set_title('Hypervolume (higher = better)', fontsize=12)
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].grid(True, alpha=0.3, axis='y')
        
        # IGD (lower is better)
        igds = [completed_results[n]['igd'] for n in names]
        axes[1].bar(names, igds, color=colors_list, edgecolor='black')
        axes[1].set_title('IGD (lower = better)', fontsize=12)
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].grid(True, alpha=0.3, axis='y')
        
        # Solutions found
        sols = [completed_results[n]['n_solutions'] for n in names]
        axes[2].bar(names, sols, color=colors_list, edgecolor='black')
        axes[2].set_title('Pareto Solutions Found', fontsize=12)
        axes[2].tick_params(axis='x', rotation=45)
        axes[2].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / 'optimizer_summary.png', dpi=150)
        print(f"Plot saved: optimizer_summary.png")
        plt.close()
        
        print(f"\nAll plots saved to {PLOTS_DIR}/")
        
    except Exception as e:
        print(f"Warning: Could not create plots: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)


if __name__ == '__main__':
    mp.set_start_method('spawn', force=True)
    main()
