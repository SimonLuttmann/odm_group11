import numpy as np
import random
from pymoo.core.problem import ElementwiseProblem

class TopTrumpsSimulation:

    def __init__(self, num_cards=22, num_categories=4):
        self.K = num_cards
        self.L = num_categories
        self.set_random_deck()

    def _normalize_deck(self, deck):
        min_values = [min(card[cat] for card in deck) for cat in range(self.L)]
        max_values = [max(card[cat] for card in deck) for cat in range(self.L)]

        normalized_deck = []
        for card in deck:
            normalized_card = [
                (card[cat] - min_values[cat]) / (max_values[cat] - min_values[cat])
                if max_values[cat] != min_values[cat] else 0.5
                for cat in range(self.L)
            ]
            normalized_deck.append(normalized_card)
        return normalized_deck

    def set_deck(self, deck_list):
        assert len(deck_list) == self.K * self.L
        deck = np.array_split(deck_list, self.K)
        self.deck = [list(card) for card in deck]
        self._normalized_deck = self._normalize_deck(self.deck)

    def set_random_deck(self, value_range=(1, 10)):
        deck_list = np.random.uniform(value_range[0], value_range[1], self.K * self.L)
        self.set_deck(deck_list)

    def get_p0_choice(self, card):
        return card.index(max(card))

    def get_p4_choice(self, card, remaining_cards):
        best_prob = -1
        best_cat = 0

        # Filter out the player's own card from the potential opponents
        # We use object identity (c is not card) to ensure we remove exactly the current card
        opponents = [c for c in remaining_cards if c is not card]
        
        if not opponents:
            return 0 # Should not happen in game loop as at least 1 opponent card exists

        for cat_idx in range(self.L):
            my_val = card[cat_idx]
            wins = sum(1 for opp_card in opponents if my_val > opp_card[cat_idx])
            prob = wins / len(opponents)

            if prob > best_prob:
                best_prob = prob
                best_cat = cat_idx

        return best_cat

    def simulate_game(self):
        temp_deck = list(self._normalized_deck)
        random.shuffle(temp_deck)

        p4_hand = temp_deck[:self.K // 2]
        p0_hand = temp_deck[self.K // 2:]
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


class TopTrumpsBalancing(ElementwiseProblem):

    def __init__(self, sim_instance, n_simulations=100, xl=1.0, xu=10.0):
        self.sim = sim_instance
        self.n_simulations = n_simulations
        
        n_var = self.sim.K * self.sim.L
        
        super().__init__(
            n_var=n_var,
            n_obj=2,
            n_constr=0,
            xl=xl,
            xu=xu
        )

    def _evaluate(self, x, out, *args, **kwargs):
        self.sim.set_deck(x)
        
        win_rates = []
        trick_changes_list = []
        
        for _ in range(self.n_simulations):
            res = self.sim.simulate_game()
            win_rates.append(1 if res['p4_won'] else 0)
            trick_changes_list.append(res['trick_changes'])
        
        out["F"] = [
            -np.mean(win_rates),
            -np.mean(trick_changes_list)
        ]

def evaluate_deck_detailed(sim, deck, R):
    """
    Evaluates a single deck with R simulations and returns detailed statistics.
    Used for validation of results.
    """
    sim.set_deck(deck)
    
    win_rates = []
    trick_changes_list = []
    p4_tricks_list = []
    
    for _ in range(R):
        result = sim.simulate_game()
        win_rates.append(1 if result['p4_won'] else 0)
        trick_changes_list.append(result['trick_changes'])
        p4_tricks_list.append(result['p4_tricks'])
    
    return {
        "win_rate": np.mean(win_rates),
        "win_rate_std": np.std(win_rates),
        "win_rate_ci": 1.96 * np.std(win_rates) / np.sqrt(R),
        "trick_changes": np.mean(trick_changes_list),
        "trick_changes_std": np.std(trick_changes_list),
        "trick_changes_ci": 1.96 * np.std(trick_changes_list) / np.sqrt(R),
        "p4_tricks_mean": np.mean(p4_tricks_list)
    }
