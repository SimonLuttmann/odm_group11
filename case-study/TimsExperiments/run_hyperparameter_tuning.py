#!/usr/bin/env python3
"""
Parallelisiertes Hyperparameter-Tuning für Mac/Linux
Ausführen im Terminal: python run_hyperparameter_tuning.py
"""

import numpy as np
import random
import time
import pandas as pd
import matplotlib.pyplot as plt
import json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

# ============================================================
# KONFIGURATION
# ============================================================

N_TRIALS = 40                # Trials pro Algorithmus
N_GEN = 100                  # Generationen pro Trial
R_SIMULATIONS = 1000         # Simulationen pro Evaluation
EVAL_SEEDS = [42, 101, 202, 303, 404]  # 5 Seeds
N_WORKERS = mp.cpu_count()   # Alle Cores nutzen

ALGORITHMS = ['NSGA-II', 'SMS-EMOA', 'NSGA-III']

SEARCH_SPACE = {
    'pop_size': (50, 250, 10),
    'eta_crossover': (5.0, 30.0),
    'eta_mutation': (5.0, 30.0),
    'crossover_prob': (0.6, 1.0),
    'n_partitions': (6, 20),
}

# Problem-Parameter
SEED = 42
K = 22
L = 4
XL = 1.0
XU = 10.0

RESULTS_DIR = Path("results")
PLOTS_DIR = Path("plots")


def run_single_trial(params):
    """Führt einen einzelnen Hyperparameter-Trial aus."""
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
    
    trial_id = params['trial_id']
    algorithm_name = params['algorithm']
    pop_size = params['pop_size']
    eta_crossover = params['eta_crossover']
    eta_mutation = params['eta_mutation']
    crossover_prob = params['crossover_prob']
    
    sim = TopTrumpsSimulation(num_cards=params['K'], num_categories=params['L'])
    problem = TopTrumpsBalancing(sim, n_simulations=params['R_SIMULATIONS'], 
                                  xl=params['XL'], xu=params['XU'])
    termination = get_termination("n_gen", params['N_GEN'])
    
    def create_algorithm():
        if algorithm_name == 'NSGA-II':
            return NSGA2(
                pop_size=pop_size,
                sampling=FloatRandomSampling(),
                crossover=SBX(prob=crossover_prob, eta=eta_crossover),
                mutation=PM(eta=eta_mutation),
                eliminate_duplicates=True
            )
        elif algorithm_name == 'SMS-EMOA':
            return SMSEMOA(
                pop_size=pop_size,
                sampling=FloatRandomSampling(),
                crossover=SBX(prob=crossover_prob, eta=eta_crossover),
                mutation=PM(eta=eta_mutation),
                eliminate_duplicates=True
            )
        elif algorithm_name == 'NSGA-III':
            n_partitions = params.get('n_partitions', 12)
            ref_dirs = get_reference_directions("das-dennis", 2, n_partitions=n_partitions)
            return NSGA3(
                pop_size=pop_size,
                ref_dirs=ref_dirs,
                sampling=FloatRandomSampling(),
                crossover=SBX(prob=crossover_prob, eta=eta_crossover),
                mutation=PM(eta=eta_mutation),
                eliminate_duplicates=True
            )
    
    hvs = []
    start_time = time.time()
    
    for eval_seed in params['EVAL_SEEDS']:
        np.random.seed(eval_seed)
        random.seed(eval_seed)
        
        try:
            algorithm = create_algorithm()
            res = minimize(problem, algorithm, termination, seed=eval_seed, verbose=False)
            hv = HV(ref_point=np.array([0.0, 0.0]))(res.F)
            hvs.append(hv)
        except Exception as e:
            hvs.append(float('nan'))
    
    runtime = time.time() - start_time
    
    result = {
        'trial_id': trial_id,
        'algorithm': algorithm_name,
        'pop_size': pop_size,
        'eta_crossover': eta_crossover,
        'eta_mutation': eta_mutation,
        'crossover_prob': crossover_prob,
        'hypervolume_mean': float(np.nanmean(hvs)),
        'hypervolume_std': float(np.nanstd(hvs)),
        'hypervolume_min': float(np.nanmin(hvs)),
        'hypervolume_max': float(np.nanmax(hvs)),
        'runtime_seconds': runtime,
        'status': 'completed' if not np.isnan(np.nanmean(hvs)) else 'failed'
    }
    
    if algorithm_name == 'NSGA-III':
        result['n_partitions'] = params.get('n_partitions')
    
    return result


def generate_trial_params(algorithm, trial_id, seed):
    """Generiert zufällige Hyperparameter."""
    np.random.seed(seed)
    
    pop_min, pop_max, pop_step = SEARCH_SPACE['pop_size']
    
    params = {
        'trial_id': trial_id,
        'algorithm': algorithm,
        'pop_size': int(np.random.choice(range(pop_min, pop_max + 1, pop_step))),
        'eta_crossover': np.random.uniform(*SEARCH_SPACE['eta_crossover']),
        'eta_mutation': np.random.uniform(*SEARCH_SPACE['eta_mutation']),
        'crossover_prob': np.random.uniform(*SEARCH_SPACE['crossover_prob']),
        'K': K,
        'L': L,
        'XL': XL,
        'XU': XU,
        'R_SIMULATIONS': R_SIMULATIONS,
        'N_GEN': N_GEN,
        'EVAL_SEEDS': EVAL_SEEDS,
    }
    
    if algorithm == 'NSGA-III':
        params['n_partitions'] = int(np.random.randint(*SEARCH_SPACE['n_partitions']))
    
    return params


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    PLOTS_DIR.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("PARALLEL HYPERPARAMETER TUNING")
    print("=" * 70)
    print(f"Algorithms: {ALGORITHMS}")
    print(f"Trials per Algorithm: {N_TRIALS}")
    print(f"Total Trials: {len(ALGORITHMS) * N_TRIALS}")
    print(f"Workers: {N_WORKERS}")
    print(f"Generations: {N_GEN}")
    print(f"Simulations: {R_SIMULATIONS}")
    print(f"Eval Seeds: {len(EVAL_SEEDS)}")
    print("=" * 70)
    
    # Trials generieren
    all_trials = []
    trial_id = 0
    for algo in ALGORITHMS:
        for i in range(N_TRIALS):
            params = generate_trial_params(algo, trial_id, SEED + trial_id)
            all_trials.append(params)
            trial_id += 1
    
    print(f"\nGenerated {len(all_trials)} trial configurations")
    print(f"Starting parallel execution with {N_WORKERS} workers...\n")
    
    # Parallele Ausführung
    start_time = time.time()
    all_results = []
    completed = 0
    
    with ProcessPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = {executor.submit(run_single_trial, trial): trial for trial in all_trials}
        
        for future in as_completed(futures):
            trial = futures[future]
            try:
                result = future.result()
                all_results.append(result)
                completed += 1
                
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                remaining = (len(all_trials) - completed) / rate if rate > 0 else 0
                
                status = "✓" if result['status'] == 'completed' else "✗"
                print(f"[{completed:3d}/{len(all_trials)}] {status} {result['algorithm']:10s} | "
                      f"HV={result['hypervolume_mean']:.4f} | "
                      f"Elapsed: {elapsed/60:.1f}min | ETA: {remaining/60:.1f}min")
                      
            except Exception as e:
                completed += 1
                print(f"[{completed:3d}/{len(all_trials)}] ✗ Trial failed: {e}")
                all_results.append({
                    'trial_id': trial['trial_id'],
                    'algorithm': trial['algorithm'],
                    'status': 'failed',
                    'error': str(e)
                })
    
    total_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("TUNING COMPLETED!")
    print("=" * 70)
    print(f"Total Runtime: {total_time/60:.1f} minutes ({total_time/3600:.2f} hours)")
    
    # Ergebnisse analysieren
    results_df = pd.DataFrame(all_results)
    completed_df = results_df[results_df['status'] == 'completed'].copy()
    
    print(f"Completed: {len(completed_df)} / {len(all_results)}")
    
    # Beste Konfigurationen
    best_configs = {}
    print("\n" + "=" * 70)
    print("BEST CONFIGURATION PER ALGORITHM")
    print("=" * 70)
    
    for algo in ALGORITHMS:
        algo_df = completed_df[completed_df['algorithm'] == algo]
        if len(algo_df) > 0:
            best_idx = algo_df['hypervolume_mean'].idxmax()
            best = algo_df.loc[best_idx].to_dict()
            best_configs[algo] = best
            
            print(f"\n{algo}:")
            print(f"  Hypervolume: {best['hypervolume_mean']:.4f} ± {best.get('hypervolume_std', 0):.4f}")
            print(f"  pop_size: {best['pop_size']}")
            print(f"  eta_crossover: {best['eta_crossover']:.2f}")
            print(f"  eta_mutation: {best['eta_mutation']:.2f}")
            print(f"  crossover_prob: {best['crossover_prob']:.3f}")
    
    # Ergebnisse speichern
    results_export = {
        'config': {
            'N_TRIALS': N_TRIALS, 'N_GEN': N_GEN, 'R_SIMULATIONS': R_SIMULATIONS,
            'N_WORKERS': N_WORKERS, 'total_runtime_minutes': total_time / 60
        },
        'all_trials': all_results,
        'best_per_algorithm': {algo: {k: (float(v) if isinstance(v, (np.floating, np.integer)) else v) 
                                       for k, v in config.items()} 
                              for algo, config in best_configs.items()}
    }
    
    with open(RESULTS_DIR / 'parallel_tuning_results.json', 'w') as f:
        json.dump(results_export, f, indent=2, default=str)
    
    # Beste Parameter exportieren
    if best_configs:
        best_params = {}
        for algo, config in best_configs.items():
            best_params[algo] = {
                'pop_size': int(config['pop_size']),
                'eta_crossover': float(config['eta_crossover']),
                'eta_mutation': float(config['eta_mutation']),
                'crossover_prob': float(config['crossover_prob']),
                'hypervolume': float(config['hypervolume_mean'])
            }
        
        with open(RESULTS_DIR / 'best_hyperparameters.json', 'w') as f:
            json.dump(best_params, f, indent=2)
        
        print(f"\n\nResults saved to: {RESULTS_DIR}")
        print(f"Best parameters: {RESULTS_DIR / 'best_hyperparameters.json'}")
    
    # CSV für weitere Analyse
    completed_df.to_csv(RESULTS_DIR / 'parallel_tuning_trials.csv', index=False)
    
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)


if __name__ == '__main__':
    # Wichtig für macOS: spawn statt fork
    mp.set_start_method('spawn', force=True)
    main()
