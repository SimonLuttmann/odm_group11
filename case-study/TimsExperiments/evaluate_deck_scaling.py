import numpy as np
import random
import sys
import os

# Add the directory to the path so we can import simulation
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation import TopTrumpsMultiplayerSimulation, evaluate_multiplayer_deck_detailed

def run_experiment():
    print("Running Deck Size Scaling Evaluation...")
    
    # Configuration
    n_simulations = 500
    n_decks = 20 # Average over 20 different random decks
    
    # Scenarios
    player_counts = [2, 3, 4]
    
    # 1. Fixed Deck Size (K=24)
    fixed_k = 24
    results_fixed = {}
    
    print(f"\n--- Scenario A: Fixed Deck Size (K={fixed_k}) ---")
    for n_players in player_counts:
        strategies = ['p4'] + ['p0'] * (n_players - 1)
        cards_per_player = fixed_k // n_players
        
        print(f"Players: {n_players}, Cards/Player: {cards_per_player}")
        
        metrics = {'expert_win_rate': [], 'trick_changes': [], 'tie_rate': []}
        
        for _ in range(n_decks):
            sim = TopTrumpsMultiplayerSimulation(num_cards=fixed_k, num_categories=4, player_strategies=strategies)
            # Use random deck
            sim.set_random_deck()
            
            flat_deck = [val for card in sim.deck for val in card]
            res = evaluate_multiplayer_deck_detailed(sim, flat_deck, n_simulations)
            
            metrics['expert_win_rate'].append(res['expert_win_rate'])
            metrics['trick_changes'].append(res['trick_changes'])
            metrics['tie_rate'].append(res['tie_rate'])
            
        results_fixed[n_players] = {k: np.mean(v) for k, v in metrics.items()}
        print(f"  Expert Win Rate: {results_fixed[n_players]['expert_win_rate']:.3f}")
        print(f"  Trick Changes:   {results_fixed[n_players]['trick_changes']:.3f}")
        print(f"  Tie Rate:        {results_fixed[n_players]['tie_rate']:.3f}")

    # 2. Scaled Deck Size (11 cards per player)
    cards_per_p = 11
    results_scaled = {}
    
    print(f"\n--- Scenario B: Scaled Deck Size ({cards_per_p} cards/player) ---")
    for n_players in player_counts:
        k = cards_per_p * n_players
        strategies = ['p4'] + ['p0'] * (n_players - 1)
        
        print(f"Players: {n_players}, Total Cards: {k}")
        
        metrics = {'expert_win_rate': [], 'trick_changes': [], 'tie_rate': []}
        
        for _ in range(n_decks):
            sim = TopTrumpsMultiplayerSimulation(num_cards=k, num_categories=4, player_strategies=strategies)
            sim.set_random_deck()
            
            flat_deck = [val for card in sim.deck for val in card]
            res = evaluate_multiplayer_deck_detailed(sim, flat_deck, n_simulations)
            
            metrics['expert_win_rate'].append(res['expert_win_rate'])
            metrics['trick_changes'].append(res['trick_changes'])
            metrics['tie_rate'].append(res['tie_rate'])
            
        results_scaled[n_players] = {k: np.mean(v) for k, v in metrics.items()}
        print(f"  Expert Win Rate: {results_scaled[n_players]['expert_win_rate']:.3f}")
        print(f"  Trick Changes:   {results_scaled[n_players]['trick_changes']:.3f}")
        print(f"  Tie Rate:        {results_scaled[n_players]['tie_rate']:.3f}")

if __name__ == "__main__":
    run_experiment()
