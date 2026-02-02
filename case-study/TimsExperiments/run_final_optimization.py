#!/usr/bin/env python3
"""
Parallelisierte Finale Optimierung für Mac/Linux
Ausführen im Terminal: python run_final_optimization.py

Nimmt die besten Hyperparameter aus dem Tuning und führt eine intensive
finale Optimierung mit mehreren Seeds parallel durch.
"""

import numpy as np
import random
import time
import json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

# ============================================================
# KONFIGURATION
# ============================================================

R_FINAL = 1000           # Hohe Anzahl Simulationen für genaue Fitness
N_GEN_FINAL = 200        # Viele Generationen für gute Konvergenz
N_SEEDS = 1             # Mehrere unabhängige Runs
FINAL_SEEDS = list(range(42, 42 + N_SEEDS))  # [42, 43, ..., 51]
N_WORKERS = min(mp.cpu_count(), N_SEEDS)     # Max so viele Worker wie Seeds

# Problem-Parameter (werden aus config.json geladen falls vorhanden)
SEED = 42
K = 22
L = 4
XL = 1.0
XU = 10.0

RESULTS_DIR = Path("results")
PLOTS_DIR = Path("plots")

# Tuning-Ergebnisse
TUNING_FILES = [
    RESULTS_DIR / 'parallel_tuning_results.json',
    RESULTS_DIR / 'best_hyperparameters.json',
    RESULTS_DIR / 'full_tuning_results.json'
]


def load_best_hyperparameters():
    """Lädt die besten Hyperparameter aus dem Tuning."""
    best_params = None
    source = None
    
    # Option 1: parallel_tuning_results.json
    try:
        with open(RESULTS_DIR / 'parallel_tuning_results.json', 'r') as f:
            data = json.load(f)
        best_params = data.get('best_per_algorithm', {})
        if best_params:
            source = 'parallel_tuning_results.json'
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    # Option 2: best_hyperparameters.json
    if not best_params:
        try:
            with open(RESULTS_DIR / 'best_hyperparameters.json', 'r') as f:
                best_params = json.load(f)
            source = 'best_hyperparameters.json'
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    
    # Option 3: full_tuning_results.json
    if not best_params:
        try:
            with open(RESULTS_DIR / 'full_tuning_results.json', 'r') as f:
                data = json.load(f)
            best_params = data.get('best_per_algorithm', {})
            if best_params:
                source = 'full_tuning_results.json'
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    
    # Fallback: Default-Parameter
    if not best_params:
        print("WARNING: No tuning results found! Using default parameters.")
        best_params = {
            'NSGA-II': {
                'pop_size': 100,
                'eta_crossover': 15.0,
                'eta_mutation': 20.0,
                'crossover_prob': 0.9
            }
        }
        source = 'defaults'
    
    return best_params, source


def get_best_algorithm(params):
    """Wählt den Algorithmus mit dem höchsten Hypervolume."""
    best_algo = None
    best_hv = -1
    
    for algo, p in params.items():
        hv = p.get('hypervolume', p.get('hypervolume_mean', 0))
        if hv and hv > best_hv:
            best_hv = hv
            best_algo = algo
    
    return best_algo if best_algo else 'NSGA-II'


def run_single_optimization(params):
    """Führt eine einzelne Optimierung mit gegebenem Seed aus."""
    import numpy as np
    import random
    import time
    
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.algorithms.moo.nsga3 import NSGA3
    from pymoo.algorithms.moo.sms import SMSEMOA
    from pymoo.operators.crossover.sbx import SBX
    from pymoo.operators.mutation.pm import PM
    from pymoo.operators.sampling.rnd import FloatRandomSampling
    from pymoo.optimize import minimize
    from pymoo.termination import get_termination
    from pymoo.indicators.hv import HV
    from pymoo.util.ref_dirs import get_reference_directions
    from simulation import TopTrumpsSimulation, TopTrumpsBalancing
    
    seed = params['seed']
    algorithm_name = params['algorithm']
    pop_size = int(params['pop_size'])
    eta_crossover = float(params['eta_crossover'])
    eta_mutation = float(params['eta_mutation'])
    crossover_prob = float(params['crossover_prob'])
    
    np.random.seed(seed)
    random.seed(seed)
    
    start_time = time.time()
    
    try:
        # Problem erstellen
        sim = TopTrumpsSimulation(num_cards=params['K'], num_categories=params['L'])
        problem = TopTrumpsBalancing(sim, n_simulations=params['R'], xl=params['XL'], xu=params['XU'])
        
        # Termination für JEDEN Run neu erstellen!
        termination = get_termination("n_gen", params['N_GEN'])
        
        # Algorithmus erstellen
        if algorithm_name == 'NSGA-II':
            algorithm = NSGA2(
                pop_size=pop_size,
                sampling=FloatRandomSampling(),
                crossover=SBX(prob=crossover_prob, eta=eta_crossover),
                mutation=PM(eta=eta_mutation),
                eliminate_duplicates=True
            )
        elif algorithm_name == 'SMS-EMOA':
            algorithm = SMSEMOA(
                pop_size=pop_size,
                sampling=FloatRandomSampling(),
                crossover=SBX(prob=crossover_prob, eta=eta_crossover),
                mutation=PM(eta=eta_mutation),
                eliminate_duplicates=True
            )
        elif algorithm_name == 'NSGA-III':
            n_partitions = int(params.get('n_partitions', 12))
            ref_dirs = get_reference_directions("das-dennis", 2, n_partitions=n_partitions)
            algorithm = NSGA3(
                pop_size=pop_size,
                ref_dirs=ref_dirs,
                sampling=FloatRandomSampling(),
                crossover=SBX(prob=crossover_prob, eta=eta_crossover),
                mutation=PM(eta=eta_mutation),
                eliminate_duplicates=True
            )
        else:
            raise ValueError(f"Unknown algorithm: {algorithm_name}")
        
        # Optimierung durchführen
        res = minimize(problem, algorithm, termination, seed=seed, verbose=False)
        
        runtime = time.time() - start_time
        
        # Hypervolume berechnen
        hv = HV(ref_point=np.array([0.0, 0.0]))(res.F)
        
        return {
            'seed': seed,
            'hypervolume': float(hv),
            'n_solutions': len(res.F),
            'runtime_seconds': runtime,
            'F': res.F.tolist(),
            'X': res.X.tolist(),
            'status': 'completed'
        }
        
    except Exception as e:
        runtime = time.time() - start_time
        return {
            'seed': seed,
            'hypervolume': 0.0,
            'n_solutions': 0,
            'runtime_seconds': runtime,
            'F': [],
            'X': [],
            'status': 'failed',
            'error': str(e)[:200]
        }


def combine_pareto_fronts(all_F, all_X):
    """Kombiniert alle Fronts und extrahiert die non-dominated Lösungen."""
    import numpy as np
    from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting
    from pymoo.indicators.hv import HV
    
    combined_F = np.vstack(all_F)
    combined_X = np.vstack(all_X)
    
    # Non-dominated Sorting
    nds = NonDominatedSorting()
    fronts = nds.do(combined_F, only_non_dominated_front=True)
    
    best_F = combined_F[fronts]
    best_X = combined_X[fronts]
    
    # Nach Fairness sortieren (absteigend)
    sort_idx = np.argsort(best_F[:, 0])[::-1]
    best_F = best_F[sort_idx]
    best_X = best_X[sort_idx]
    
    # Hypervolume der kombinierten Front
    combined_hv = HV(ref_point=np.array([0.0, 0.0]))(best_F)
    
    return best_F, best_X, combined_hv


def main():
    """Hauptfunktion für die parallelisierte finale Optimierung."""
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    print("=" * 70)
    print("PARALLELISIERTE FINALE OPTIMIERUNG")
    print("=" * 70)
    
    # Verzeichnisse erstellen
    RESULTS_DIR.mkdir(exist_ok=True)
    PLOTS_DIR.mkdir(exist_ok=True)
    
    # Problem-Parameter aus config.json laden
    global K, L, XL, XU
    try:
        with open(RESULTS_DIR / 'config.json', 'r') as f:
            config = json.load(f)
        K = config.get('K', K)
        L = config.get('L', L)
        XL = config.get('xl', XL)
        XU = config.get('xu', XU)
        print(f"Config loaded: K={K}, L={L}")
    except FileNotFoundError:
        print(f"Using defaults: K={K}, L={L}")
    
    # Beste Hyperparameter laden
    best_params, source = load_best_hyperparameters()
    print(f"\nLoaded hyperparameters from: {source}")
    
    # Besten Algorithmus wählen
    algorithm = get_best_algorithm(best_params)
    algo_params = best_params.get(algorithm, list(best_params.values())[0])
    
    print(f"\nUsing {algorithm} with:")
    for k, v in algo_params.items():
        if k not in ['hypervolume', 'hypervolume_mean', 'hypervolume_std', 'status', 'trial_id', 'algorithm']:
            print(f"  {k}: {v}")
    
    print(f"\nConfiguration:")
    print(f"  Simulations (R): {R_FINAL}")
    print(f"  Generations: {N_GEN_FINAL}")
    print(f"  Seeds: {N_SEEDS} ({FINAL_SEEDS[0]} - {FINAL_SEEDS[-1]})")
    print(f"  Workers: {N_WORKERS}")
    print("=" * 70)
    
    # Jobs vorbereiten
    jobs = []
    for seed in FINAL_SEEDS:
        job = {
            'seed': seed,
            'algorithm': algorithm,
            'pop_size': algo_params.get('pop_size', 100),
            'eta_crossover': algo_params.get('eta_crossover', 15.0),
            'eta_mutation': algo_params.get('eta_mutation', 20.0),
            'crossover_prob': algo_params.get('crossover_prob', 0.9),
            'n_partitions': algo_params.get('n_partitions', 12),
            'K': K,
            'L': L,
            'XL': XL,
            'XU': XU,
            'R': R_FINAL,
            'N_GEN': N_GEN_FINAL
        }
        jobs.append(job)
    
    # Parallel ausführen
    print(f"\nStarting {len(jobs)} parallel optimizations...")
    print("This will take a while.\n")
    
    all_results = []
    total_start = time.time()
    
    with ProcessPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = {executor.submit(run_single_optimization, job): job['seed'] for job in jobs}
        
        for future in as_completed(futures):
            seed = futures[future]
            try:
                result = future.result()
                all_results.append(result)
                
                elapsed = time.time() - total_start
                completed = len(all_results)
                remaining = len(jobs) - completed
                eta = elapsed / completed * remaining if completed > 0 else 0
                
                status = "OK" if result['status'] == 'completed' else "FAILED"
                print(f"[{completed:2d}/{len(jobs)}] Seed {seed}: HV={result['hypervolume']:.4f}, "
                      f"Solutions={result['n_solutions']}, Time={result['runtime_seconds']/60:.1f}min "
                      f"[{status}] | ETA: {eta/60:.1f}min")
                
            except Exception as e:
                print(f"[??/{len(jobs)}] Seed {seed}: EXCEPTION - {str(e)[:50]}")
    
    total_time = time.time() - total_start
    
    # Ergebnisse filtern
    successful_runs = [r for r in all_results if r['status'] == 'completed']
    failed_runs = [r for r in all_results if r['status'] != 'completed']
    
    print("\n" + "=" * 70)
    print("OPTIMIZATION COMPLETED!")
    print("=" * 70)
    print(f"Total Runtime: {total_time/60:.1f} minutes ({total_time/3600:.2f} hours)")
    print(f"Successful: {len(successful_runs)}/{len(jobs)}")
    if failed_runs:
        print(f"Failed Seeds: {[r['seed'] for r in failed_runs]}")
    
    if len(successful_runs) < 3:
        print("\nERROR: Too few successful runs!")
        return
    
    # Kombinierte Pareto-Front berechnen
    all_F = [np.array(r['F']) for r in successful_runs]
    all_X = [np.array(r['X']) for r in successful_runs]
    
    best_F, best_X, combined_hv = combine_pareto_fronts(all_F, all_X)
    
    # Statistiken
    hvs = [r['hypervolume'] for r in successful_runs]
    
    print(f"\nStatistics:")
    print(f"  Hypervolume Mean: {np.mean(hvs):.4f} ± {np.std(hvs):.4f}")
    print(f"  Hypervolume Range: [{np.min(hvs):.4f}, {np.max(hvs):.4f}]")
    print(f"  Combined Front: {len(best_F)} solutions, HV={combined_hv:.4f}")
    
    # Extrempunkte
    best_fairness_idx = np.argmax(best_F[:, 0])
    best_excitement_idx = np.argmax(best_F[:, 1])
    
    # Knee-Point
    f_norm = (best_F - best_F.min(axis=0)) / (best_F.max(axis=0) - best_F.min(axis=0) + 1e-10)
    knee_idx = np.argmax(f_norm.sum(axis=1))
    
    print(f"\nExtreme Points:")
    print(f"  Best Fairness: F={best_F[best_fairness_idx, 0]:.4f}, E={best_F[best_fairness_idx, 1]:.4f}")
    print(f"  Best Excitement: F={best_F[best_excitement_idx, 0]:.4f}, E={best_F[best_excitement_idx, 1]:.4f}")
    print(f"  Knee Point: F={best_F[knee_idx, 0]:.4f}, E={best_F[knee_idx, 1]:.4f}")
    
    # Ergebnisse speichern
    final_results = {
        'config': {
            'algorithm': algorithm,
            'hyperparameters': {k: (float(v) if isinstance(v, (np.floating, np.integer, float, int)) else v) 
                               for k, v in algo_params.items() 
                               if k not in ['hypervolume', 'hypervolume_mean', 'hypervolume_std', 'status', 'trial_id', 'algorithm']},
            'R': R_FINAL,
            'generations': N_GEN_FINAL,
            'n_seeds': N_SEEDS,
            'n_workers': N_WORKERS,
            'K': K,
            'L': L,
            'total_runtime_minutes': total_time / 60
        },
        'statistics': {
            'hypervolume_mean': float(np.mean(hvs)),
            'hypervolume_std': float(np.std(hvs)),
            'hypervolume_min': float(np.min(hvs)),
            'hypervolume_max': float(np.max(hvs)),
            'combined_hypervolume': float(combined_hv),
            'combined_n_solutions': len(best_F),
            'successful_runs': len(successful_runs),
            'failed_runs': len(failed_runs)
        },
        'runs': [{k: v for k, v in r.items() if k not in ['F', 'X']} for r in successful_runs],
        'extremes': {
            'best_fairness': {'fairness': float(best_F[best_fairness_idx, 0]), 
                              'excitement': float(best_F[best_fairness_idx, 1])},
            'best_excitement': {'fairness': float(best_F[best_excitement_idx, 0]), 
                                'excitement': float(best_F[best_excitement_idx, 1])},
            'knee_point': {'fairness': float(best_F[knee_idx, 0]), 
                           'excitement': float(best_F[knee_idx, 1])}
        }
    }
    
    with open(RESULTS_DIR / 'final_optimization_results.json', 'w') as f:
        json.dump(final_results, f, indent=2)
    
    # Pareto-Front speichern
    np.save(RESULTS_DIR / 'final_pareto_front_F.npy', best_F)
    np.save(RESULTS_DIR / 'final_pareto_front_X.npy', best_X)
    
    # CSV für einfachen Zugriff
    front_df = pd.DataFrame(best_F, columns=['Fairness', 'Excitement'])
    front_df.to_csv(RESULTS_DIR / 'final_pareto_front.csv', index=False)
    
    # Selected Decks speichern
    selected_decks = {
        'fairness_max': {
            'deck': best_X[best_fairness_idx].tolist(),
            'fairness': float(best_F[best_fairness_idx, 0]),
            'excitement': float(best_F[best_fairness_idx, 1])
        },
        'excitement_max': {
            'deck': best_X[best_excitement_idx].tolist(),
            'fairness': float(best_F[best_excitement_idx, 0]),
            'excitement': float(best_F[best_excitement_idx, 1])
        },
        'knee_point': {
            'deck': best_X[knee_idx].tolist(),
            'fairness': float(best_F[knee_idx, 0]),
            'excitement': float(best_F[knee_idx, 1])
        }
    }
    
    with open(RESULTS_DIR / 'final_selected_decks.json', 'w') as f:
        json.dump(selected_decks, f, indent=2)
    
    print(f"\nResults saved to:")
    print(f"  - {RESULTS_DIR / 'final_optimization_results.json'}")
    print(f"  - {RESULTS_DIR / 'final_pareto_front_F.npy'}")
    print(f"  - {RESULTS_DIR / 'final_pareto_front_X.npy'}")
    print(f"  - {RESULTS_DIR / 'final_pareto_front.csv'}")
    print(f"  - {RESULTS_DIR / 'final_selected_decks.json'}")
    
    # Plot erstellen
    try:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Links: Alle Runs
        colors = plt.cm.viridis(np.linspace(0, 1, len(successful_runs)))
        for i, r in enumerate(successful_runs):
            F = np.array(r['F'])
            axes[0].scatter(F[:, 0], F[:, 1], c=[colors[i]], alpha=0.5, s=20,
                           label=f"Seed {r['seed']} (HV={r['hypervolume']:.3f})")
        
        axes[0].set_xlabel('Fairness (Win Rate)')
        axes[0].set_ylabel('Excitement (Trick Changes)')
        axes[0].set_title(f'All {len(successful_runs)} Independent Runs')
        axes[0].legend(fontsize=7, loc='lower left')
        axes[0].grid(True, alpha=0.3)
        
        # Rechts: Kombinierte Front
        axes[1].scatter(best_F[:, 0], best_F[:, 1], c='blue', s=50, alpha=0.7, label='Pareto-Front')
        axes[1].scatter(best_F[best_fairness_idx, 0], best_F[best_fairness_idx, 1], 
                       c='green', s=150, marker='*', label='Best Fairness', zorder=5)
        axes[1].scatter(best_F[best_excitement_idx, 0], best_F[best_excitement_idx, 1], 
                       c='red', s=150, marker='*', label='Best Excitement', zorder=5)
        axes[1].scatter(best_F[knee_idx, 0], best_F[knee_idx, 1], 
                       c='orange', s=150, marker='*', label='Knee-Point', zorder=5)
        
        axes[1].set_xlabel('Fairness (Win Rate)')
        axes[1].set_ylabel('Excitement (Trick Changes)')
        axes[1].set_title(f'Combined Pareto-Front (HV={combined_hv:.4f})')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / 'final_optimization_fronts.png', dpi=150)
        print(f"  - {PLOTS_DIR / 'final_optimization_fronts.png'}")
        plt.close()
        
    except Exception as e:
        print(f"Warning: Could not create plot: {e}")
    
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)


if __name__ == '__main__':
    mp.set_start_method('spawn', force=True)
    main()
