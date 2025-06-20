from typing import List, Dict, Optional

class YahtzeeScorecard:
    """
    Manages a single player's Yahtzee scorecard.
    Handles scoring calculations and category validation.
    """
    
    def __init__(self):
        """Initialize empty scorecard with all categories available"""
        # Upper section categories (score = sum of matching dice)
        self.upper_scores = {
            'ones': None,
            'twos': None, 
            'threes': None,
            'fours': None,
            'fives': None,
            'sixes': None
        }
        
        # Lower section categories (fixed point values)
        self.lower_scores = {
            'three_of_kind': None,      # Sum of all dice if 3+ match
            'four_of_kind': None,       # Sum of all dice if 4+ match
            'full_house': None,         # 25 points for 3+2 combo
            'small_straight': None,     # 30 points for 4 consecutive
            'large_straight': None,     # 40 points for 5 consecutive  
            'yahtzee': None,           # 50 points for all 5 match
            'chance': None             # Sum of all dice (any combo)
        }
        
        # Bonus tracking
        self.yahtzee_bonus_count = 0  # Additional Yahtzees after first
        
    def get_all_scores(self) -> Dict[str, Optional[int]]:
        """Get all scores combined in one dictionary"""
        all_scores = {}
        all_scores.update(self.upper_scores)
        all_scores.update(self.lower_scores)
        return all_scores
        
    def is_category_available(self, category: str) -> bool:
        """Check if a category is still available for scoring"""
        all_scores = self.get_all_scores()
        return category in all_scores and all_scores[category] is None
        
    def calculate_possible_scores(self, dice: List[int]) -> Dict[str, int]:
        """
        Calculate all possible scores for the given dice roll.
        Only returns scores for categories that haven't been used yet.
        """
        if len(dice) != 5:
            raise ValueError("Must have exactly 5 dice")
            
        # Count occurrences of each die value (1-6)
        counts = [0] + [dice.count(i) for i in range(1, 7)]
        dice_sum = sum(dice)
        possible_scores = {}
        
        # Upper section - sum of matching dice
        for value in range(1, 7):
            category = ['', 'ones', 'twos', 'threes', 'fours', 'fives', 'sixes'][value]
            if self.is_category_available(category):
                possible_scores[category] = value * counts[value]
                
        # Lower section - check each category
        if self.is_category_available('three_of_kind'):
            # Three of a kind: sum of all dice if at least 3 match
            has_three_of_kind = any(count >= 3 for count in counts[1:])
            possible_scores['three_of_kind'] = dice_sum if has_three_of_kind else 0
            
        if self.is_category_available('four_of_kind'):
            # Four of a kind: sum of all dice if at least 4 match
            has_four_of_kind = any(count >= 4 for count in counts[1:])
            possible_scores['four_of_kind'] = dice_sum if has_four_of_kind else 0
            
        if self.is_category_available('full_house'):
            # Full house: exactly 3 of one number and 2 of another
            counts_only = counts[1:]
            has_three = 3 in counts_only
            has_two = 2 in counts_only
            valid_full_house = has_three and has_two and counts_only.count(3) == 1 
            possible_scores['full_house'] = 25 if valid_full_house else 0
            
        if self.is_category_available('small_straight'):
            # Small straight: 4 consecutive numbers
            unique_dice = set(dice)
            small_straights = [
                {1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}
            ]
            has_small_straight = any(straight.issubset(unique_dice) for straight in small_straights)
            possible_scores['small_straight'] = 30 if has_small_straight else 0
            
        if self.is_category_available('large_straight'):
            # Large straight: 5 consecutive numbers
            unique_dice = set(dice)
            large_straights = [{1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}]
            has_large_straight = any(straight == unique_dice for straight in large_straights)
            possible_scores['large_straight'] = 40 if has_large_straight else 0
            
        if self.is_category_available('yahtzee'):
            # Yahtzee: all 5 dice the same
            has_yahtzee = any(count == 5 for count in counts[1:])
            possible_scores['yahtzee'] = 50 if has_yahtzee else 0
            
        if self.is_category_available('chance'):
            # Chance: sum of all dice (always possible)
            possible_scores['chance'] = dice_sum
            
        return possible_scores
        
    def score_category(self, category: str, dice: List[int]) -> bool:
        """
        Score a category with the given dice.
        Returns True if successful, False if category already used.
        """
        if not self.is_category_available(category):
            return False
            
        possible_scores = self.calculate_possible_scores(dice)
        if category not in possible_scores:
            return False
            
        # Score the category
        if category in self.upper_scores:
            self.upper_scores[category] = possible_scores[category]
        else:
            self.lower_scores[category] = possible_scores[category]
            
        # Check for Yahtzee bonus
        if category != 'yahtzee':
            counts = [dice.count(i) for i in range(1, 7)]
            if max(counts) == 5 and self.lower_scores['yahtzee'] == 50:
                # This is an additional Yahtzee after scoring the first one
                self.yahtzee_bonus_count += 1
                
        return True
        
    def calculate_upper_total(self) -> int:
        """Calculate upper section total (before bonus)"""
        return sum(score for score in self.upper_scores.values() if score is not None)
        
    def calculate_upper_bonus(self) -> int:
        """Calculate upper section bonus (35 points if total >= 63)"""
        return 35 if self.calculate_upper_total() >= 63 else 0
        
    def calculate_lower_total(self) -> int:
        """Calculate lower section total"""
        return sum(score for score in self.lower_scores.values() if score is not None)
        
    def calculate_yahtzee_bonus(self) -> int:
        """Calculate Yahtzee bonus points (100 per additional Yahtzee)"""
        return self.yahtzee_bonus_count * 100
        
    def calculate_grand_total(self) -> int:
        """Calculate total score including all bonuses"""
        return (self.calculate_upper_total() + 
                self.calculate_upper_bonus() + 
                self.calculate_lower_total() + 
                self.calculate_yahtzee_bonus())
                
    def is_complete(self) -> bool:
        """Check if all categories have been scored"""
        all_scores = self.get_all_scores()
        return all(score is not None for score in all_scores.values())
        
    def get_available_categories(self) -> List[str]:
        """Get list of categories still available for scoring"""
        all_scores = self.get_all_scores()
        return [category for category, score in all_scores.items() if score is None]

# Test the scorecard functionality
if __name__ == "__main__":
    # Create a new scorecard
    scorecard = YahtzeeScorecard()
    
    # Test with some example dice rolls
    print("Testing YahtzeeScorecard class...")
    print()
    
    # Test 1: Roll with three 4s
    test_dice = [4, 4, 4, 2, 6]
    print(f"Test dice: {test_dice}")
    possible = scorecard.calculate_possible_scores(test_dice)
    print("Possible scores:")
    for category, score in possible.items():
        print(f"  {category}: {score}")
    print()
    
    # Score the fours
    success = scorecard.score_category('fours', test_dice)
    print(f"Scored 'fours': {success}")
    print(f"Fours score: {scorecard.upper_scores['fours']}")
    print()
    
    # Test 2: Full house
    test_dice = [3, 3, 3, 6, 6]
    print(f"Test dice: {test_dice}")
    possible = scorecard.calculate_possible_scores(test_dice)
    print(f"Full house possible: {possible.get('full_house', 0)}")
    
    scorecard.score_category('full_house', test_dice)
    print(f"Full house scored: {scorecard.lower_scores['full_house']}")
    print()
    
    # Show current scorecard
    print(scorecard.display_scorecard())
