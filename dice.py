import random
from typing import List, Optional

class YahtzeeDice:
    """
    Manages the 5 dice used in Yahtzee.
    Handles rolling, keeping specific dice, and validation.
    """
    
    def __init__(self):
        """Initialize 5 dice, all showing 1"""
        self.dice = [1, 1, 1, 1, 1]
        self.rolls_remaining = 3 
        
    def roll_all(self) -> List[int]:
        """
        Roll all 5 dice.
        Returns the new dice values.
        """
        if self.rolls_remaining <= 0:
            raise ValueError("No rolls remaining this turn")
            
        for i in range(5):
            self.dice[i] = random.randint(1, 6)
            
        self.rolls_remaining -= 1
        return self.dice.copy()
        
    def roll_with_keep(self, keep_dice: List[bool]) -> List[int]:
        """
        Roll dice, keeping the ones marked True in keep_dice.
        
        Args:
            keep_dice: List of 5 booleans, True means keep that die
            
        Returns:
            The new dice values
        """
        if len(keep_dice) != 5:
            raise ValueError("keep_dice must have exactly 5 boolean values")
            
        if self.rolls_remaining <= 0:
            raise ValueError("No rolls remaining this turn")
            
        # Only roll dice that are not being kept
        for i in range(5):
            if not keep_dice[i]:
                self.dice[i] = random.randint(1, 6)
                
        self.rolls_remaining -= 1
        return self.dice.copy()
        
    def roll_specific(self, dice_indices: List[int]) -> List[int]:
        """
        Roll only the dice at the specified indices (0-4).
        
        Args:
            dice_indices: List of dice positions to roll (0-4)
            
        Returns:
            The new dice values
        """
        if self.rolls_remaining <= 0:
            raise ValueError("No rolls remaining this turn")
            
        for index in dice_indices:
            if not (0 <= index <= 4):
                raise ValueError(f"Dice index {index} out of range (0-4)")
            self.dice[index] = random.randint(1, 6)
            
        self.rolls_remaining -= 1
        return self.dice.copy()
        
    def get_dice(self) -> List[int]:
        """Get current dice values without rolling"""
        return self.dice.copy()
        
    def get_rolls_remaining(self) -> int:
        """Get number of rolls remaining this turn"""
        return self.rolls_remaining
        
    def can_roll(self) -> bool:
        """Check if player can still roll this turn"""
        return self.rolls_remaining > 0
        
    def start_new_turn(self) -> None:
        """Start a new turn - reset rolls remaining"""
        self.rolls_remaining = 3
        
    def get_dice_summary(self) -> dict:
        """Get summary information about current dice"""
        counts = {}
        for value in range(1, 7):
            counts[value] = self.dice.count(value)
            
        return {
            'dice': self.dice.copy(),
            'rolls_remaining': self.rolls_remaining,
            'counts': counts,
            'sum': sum(self.dice)
        }


# Test the dice functionality
if __name__ == "__main__":
    print("Testing YahtzeeDice class...")
    print()
    
    # Create dice object
    dice = YahtzeeDice()
    
    # Test initial state
    print("Initial dice:")
    print(dice.display_simple())
    print()
    
    # Test rolling all dice
    print("Rolling all dice:")
    dice.roll_all()
    print(dice.display_dice())
    print()
    
    # Test keeping some dice
    print("Rolling again, keeping dice 1, 3, and 5:")
    keep = [True, False, True, False, True]
    dice.roll_with_keep(keep)
    print(dice.display_dice())
    print()
    
    # Test rolling specific dice
    print("Rolling only dice 2 and 4:")
    dice.roll_specific([1, 3])  # 0-indexed, so dice 2 and 4
    print(dice.display_dice())
    print()
    
    # Show dice summary
    summary = dice.get_dice_summary()
    print("Dice summary:")
    print(f"Values: {summary['dice']}")
    print(f"Sum: {summary['sum']}")
    print(f"Counts: {summary['counts']}")
    print(f"Rolls remaining: {summary['rolls_remaining']}")
    print()
    
    # Test turn management
    print("Starting new turn...")
    dice.start_new_turn()
    print(f"Rolls remaining: {dice.get_rolls_remaining()}")
    
    # Test error handling
    try:
        # Try to roll 4 times in one turn
        dice.roll_all()  # Roll 1
        dice.roll_all()  # Roll 2  
        dice.roll_all()  # Roll 3
        dice.roll_all()  # This should fail
    except ValueError as e:
        print(f"Expected error caught: {e}")
