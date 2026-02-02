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


# =============================================================================
# MULTIPLAYER EXTENSION (3+ Players)
# =============================================================================

class TopTrumpsMultiplayerSimulation:
    """
    Multiplayer Top Trumps Simulation supporting N >= 2 players.
    
    Each player can be assigned a strategy:
    - 'p0': Beginner strategy (picks category with highest normalized value on their card)
    - 'p4': Expert strategy (calculates exact win probability against remaining cards)
    
    The game proceeds in rounds. Each round:
    1. The current leader picks a category.
    2. All players compare their top card in that category.
    3. The player with the highest value wins all cards and becomes the new leader.
    4. In case of a tie, the current leader retains leadership.
    
    The game ends when all cards have been played.
    """

    def __init__(self, num_cards=22, num_categories=4, player_strategies=None):
        """
        Initialize the multiplayer simulation.
        
        Args:
            num_cards: Total number of cards in the deck (K).
            num_categories: Number of categories per card (L).
            player_strategies: List of strategies for each player, e.g., ['p4', 'p0', 'p0'].
                               Defaults to ['p4', 'p0'] for a 2-player game.
        """
        self.K = num_cards
        self.L = num_categories
        
        if player_strategies is None:
            player_strategies = ['p4', 'p0']
        
        self.player_strategies = player_strategies
        self.num_players = len(player_strategies)
        
        if self.num_players < 2:
            raise ValueError("At least 2 players are required.")
        
        if self.K % self.num_players != 0:
            raise ValueError(f"Number of cards ({self.K}) must be divisible by number of players ({self.num_players}).")
        
        self.cards_per_player = self.K // self.num_players
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
        """Beginner strategy: pick category with highest normalized value."""
        return card.index(max(card))

    def get_p4_choice(self, card, all_opponent_cards):
        """
        Expert strategy: pick category with highest win probability.
        
        In multiplayer, a 'win' in a round means having the highest value among all players.
        We calculate the probability of winning against all opponents' possible cards.
        """
        best_prob = -1
        best_cat = 0
        
        if not all_opponent_cards:
            return 0

        for cat_idx in range(self.L):
            my_val = card[cat_idx]
            # Count how many opponent cards we beat in this category
            # For multiplayer: we need to beat ALL opponents in a round to win
            # But here we estimate using pairwise dominance (simplified heuristic)
            wins = sum(1 for opp_card in all_opponent_cards if my_val > opp_card[cat_idx])
            prob = wins / len(all_opponent_cards)

            if prob > best_prob:
                best_prob = prob
                best_cat = cat_idx

        return best_cat

    def simulate_game(self):
        """
        Simulate a single multiplayer game.
        
        Returns:
            dict with:
            - 'tricks_won': list of tricks won by each player
            - 'winner_idx': index of the winning player (most tricks)
            - 'trick_changes': number of times the leader changed
            - 'is_tie': whether the game ended in a tie for first place
        """
        temp_deck = list(self._normalized_deck)
        random.shuffle(temp_deck)

        # Deal cards to each player
        hands = []
        for i in range(self.num_players):
            start = i * self.cards_per_player
            end = start + self.cards_per_player
            hands.append(temp_deck[start:end])
        
        # All unplayed cards (for p4 strategy)
        all_unplayed = list(temp_deck)
        
        tricks_won = [0] * self.num_players
        current_leader = random.randint(0, self.num_players - 1)
        trick_changes = 0
        
        for round_idx in range(self.cards_per_player):
            # Each player plays their top card
            cards_in_play = [hands[p][round_idx] for p in range(self.num_players)]
            
            # Leader picks category
            leader_card = cards_in_play[current_leader]
            leader_strategy = self.player_strategies[current_leader]
            
            if leader_strategy == 'p4':
                # Get all cards that are NOT the leader's current card
                opponent_cards_for_decision = [c for c in all_unplayed if c is not leader_card]
                category = self.get_p4_choice(leader_card, opponent_cards_for_decision)
            else:  # p0
                category = self.get_p0_choice(leader_card)
            
            # Determine winner of this round
            values = [cards_in_play[p][category] for p in range(self.num_players)]
            max_value = max(values)
            
            # Find all players with the max value (could be a tie)
            winners = [p for p, v in enumerate(values) if v == max_value]
            
            if len(winners) == 1:
                round_winner = winners[0]
            else:
                # Tie-breaker: current leader retains if among winners, else first in list
                if current_leader in winners:
                    round_winner = current_leader
                else:
                    round_winner = winners[0]
            
            tricks_won[round_winner] += 1
            
            # Remove played cards from all_unplayed
            for card in cards_in_play:
                if card in all_unplayed:
                    all_unplayed.remove(card)
            
            # Track leader changes
            if round_winner != current_leader:
                trick_changes += 1
                current_leader = round_winner
        
        # Determine overall winner
        max_tricks = max(tricks_won)
        top_players = [i for i, t in enumerate(tricks_won) if t == max_tricks]
        is_tie = len(top_players) > 1
        winner_idx = top_players[0]  # Arbitrary tie-breaker: lowest index wins
        
        return {
            "tricks_won": tricks_won,
            "winner_idx": winner_idx,
            "trick_changes": trick_changes,
            "is_tie": is_tie
        }


class TopTrumpsMultiplayerBalancing(ElementwiseProblem):
    """
    Pymoo problem wrapper for multiplayer Top Trumps optimization.
    
    Objectives (to be maximized, internally minimized):
    1. Fairness: Win-rate of the FOCUS EXPERT (first expert player, index 0 among experts)
       This ensures a clear, comparable fairness metric even with multiple experts.
    2. Excitement: Average number of trick changes per game
    """

    def __init__(self, sim_instance, n_simulations=100, xl=1.0, xu=10.0):
        self.sim = sim_instance
        self.n_simulations = n_simulations
        
        # Find indices of expert players (p4 strategy)
        self.expert_indices = [i for i, s in enumerate(self.sim.player_strategies) if s == 'p4']
        
        # Focus expert: the FIRST expert in the list (for consistent fairness measurement)
        if not self.expert_indices:
            raise ValueError("At least one expert (p4) player is required!")
        self.focus_expert_idx = self.expert_indices[0]
        
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
        
        focus_expert_wins = []
        trick_changes_list = []
        
        for _ in range(self.n_simulations):
            res = self.sim.simulate_game()
            # Fairness: Only count wins of the FOCUS EXPERT (not all experts combined)
            focus_expert_wins.append(1 if res['winner_idx'] == self.focus_expert_idx else 0)
            trick_changes_list.append(res['trick_changes'])
        
        out["F"] = [
            -np.mean(focus_expert_wins),
            -np.mean(trick_changes_list)
        ]


def evaluate_multiplayer_deck_detailed(sim, deck, R):
    """
    Evaluates a multiplayer deck with R simulations and returns detailed statistics.
    
    IMPORTANT: Fairness (focus_expert_win_rate) is measured for the FIRST expert only,
    ensuring a clear, comparable metric even when multiple experts are present.
    """
    sim.set_deck(deck)
    
    expert_indices = [i for i, s in enumerate(sim.player_strategies) if s == 'p4']
    if not expert_indices:
        raise ValueError("At least one expert (p4) player is required!")
    
    # Focus expert: the FIRST expert in the list
    focus_expert_idx = expert_indices[0]
    
    focus_expert_wins = []
    any_expert_wins = []  # For comparison: any expert winning
    trick_changes_list = []
    tricks_per_player = [[] for _ in range(sim.num_players)]
    ties = []
    
    for _ in range(R):
        result = sim.simulate_game()
        # Primary metric: Focus expert win rate
        focus_expert_wins.append(1 if result['winner_idx'] == focus_expert_idx else 0)
        # Secondary metric: Any expert winning (for comparison)
        any_expert_wins.append(1 if result['winner_idx'] in expert_indices else 0)
        trick_changes_list.append(result['trick_changes'])
        ties.append(1 if result['is_tie'] else 0)
        for p in range(sim.num_players):
            tricks_per_player[p].append(result['tricks_won'][p])
    
    return {
        # Primary fairness metric: Focus expert only
        "focus_expert_win_rate": np.mean(focus_expert_wins),
        "focus_expert_win_rate_std": np.std(focus_expert_wins),
        "focus_expert_win_rate_ci": 1.96 * np.std(focus_expert_wins) / np.sqrt(R),
        # Secondary metric for comparison
        "any_expert_win_rate": np.mean(any_expert_wins),
        "num_experts": len(expert_indices),
        # Excitement
        "trick_changes": np.mean(trick_changes_list),
        "trick_changes_std": np.std(trick_changes_list),
        "trick_changes_ci": 1.96 * np.std(trick_changes_list) / np.sqrt(R),
        # Other metrics
        "tie_rate": np.mean(ties),
        "tricks_per_player_mean": [np.mean(t) for t in tricks_per_player],
        "tricks_per_player_std": [np.std(t) for t in tricks_per_player],
        "focus_expert_idx": focus_expert_idx
    }
