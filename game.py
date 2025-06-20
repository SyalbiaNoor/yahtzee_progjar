from typing import List, Dict, Optional, Tuple
from scorecard import YahtzeeScorecard
from dice import YahtzeeDice

class YahtzeeGame: 
    def __init__(self, player_name: str = "Player"):
        self.player_name = player_name
        self.scorecard = YahtzeeScorecard()
        self.dice = YahtzeeDice()
        self.current_turn = 1
        self.max_turns = 13
        self.game_complete = False
        
    def start_new_turn(self) -> None:
        if self.game_complete:
            raise ValueError("Game is already complete")
        self.dice.start_new_turn()
        self.dice.roll_all()
        
    def roll_dice(self, keep_dice: Optional[List[bool]] = None) -> List[int]:
        if self.game_complete:
            raise ValueError("Game is already complete")
            
        if keep_dice is None:
            return self.dice.roll_all()
        else:
            return self.dice.roll_with_keep(keep_dice)
            
    def get_possible_scores(self) -> Dict[str, int]:
        if self.game_complete:
            return {}
        return self.scorecard.calculate_possible_scores(self.dice.get_dice())
        
    def score_category(self, category: str) -> bool:
        if self.game_complete:
            return False
        success = self.scorecard.score_category(category, self.dice.get_dice())
        if success:
            self.current_turn += 1
            if self.current_turn > self.max_turns or self.scorecard.is_complete():
                self.game_complete = True
            else:
                self.start_new_turn()
        return success
        
    def get_available_categories(self) -> List[str]:
        return self.scorecard.get_available_categories()
        
    def is_turn_complete(self) -> bool:
        return not self.dice.can_roll()
        
    def can_roll(self) -> bool:
        return not self.game_complete and self.dice.can_roll()
        
    def get_current_score(self) -> int:
        return self.scorecard.calculate_grand_total()
        
    def get_game_state(self) -> Dict:
        return {
            'player_name': self.player_name,
            'turn': self.current_turn,
            'max_turns': self.max_turns,
            'dice': self.dice.get_dice(),
            'rolls_remaining': self.dice.get_rolls_remaining(),
            'possible_scores': self.get_possible_scores(),
            'available_categories': self.get_available_categories(),
            'current_score': self.get_current_score(),
            'game_complete': self.game_complete,
            'can_roll': self.can_roll(),
            'turn_complete': self.is_turn_complete()
        }
        
    def get_score_recommendation(self) -> Tuple[str, int, str]:
        possible = self.get_possible_scores()
        if not possible:
            return ("", 0, "No categories available")
        best_category = max(possible.items(), key=lambda x: x[1])
        category, score = best_category
        explanations = {
            'yahtzee': "YAHTZEE! Maximum points!",
            'large_straight': "Large straight - excellent score!",
            'full_house': "Full house - solid points!",
            'small_straight': "Small straight - good score!",
            'four_of_kind': "Four of a kind - high value!",
            'three_of_kind': "Three of a kind - decent points",
        }
        if score == 0:
            explanation = "Consider using this category to avoid zero elsewhere"
        elif category in explanations:
            explanation = explanations[category]
        elif score >= 20:
            explanation = "High scoring option!"
        elif score >= 10:
            explanation = "Moderate scoring option"
        else:
            explanation = "Low scoring option"            
        return (category, score, explanation)

if __name__ == "__main__":
    print("Testing YahtzeeGame class...")
    print()
    game = YahtzeeGame("Test Player")
    for turn_num in range(1, 4):
        print(f"\n{'='*20} TURN {turn_num} {'='*20}")
        if turn_num > 1:
            game.start_new_turn()
        dice_values = game.roll_dice()
        print(f"First roll: {dice_values}")
        print(game.display_game_status())
        rec_category, rec_score, rec_explanation = game.get_score_recommendation()
        print(f"Recommendation: {rec_category} for {rec_score} points - {rec_explanation}")
        success = game.score_category(rec_category)
        print(f"Scored {rec_category}: {success}")
        print(f"Current total score: {game.get_current_score()}")
        if game.game_complete:
            print("\nGame completed!")
            break
    print("\n" + "="*50)
    print("GAME TEST COMPLETE")
    print("="*50)