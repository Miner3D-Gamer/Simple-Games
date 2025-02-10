from typing import Tuple, Optional, Any, Union, List
from custom_typing import (
    ExtraInfo,
    MainReturn,
    SetupInput,
    GameInfo,
    Action,
    AdvancedInputs,
)
import random

# ChatGPT impressively generated this with just 5 or so prompts (I still had to fix some stuff but it was mostly working)

class Game:
    def __init__(self) -> None:
        """
        The logic that would usually go here is moved to the 'setup' function.
        """
        
    def setup(self, info: SetupInput) -> Tuple[str, list[str], Optional[Union[Action, List[Action]]]]:
        """
        Initializes the game state.
        """
        self.hp = 10
        self.score = 0
        self.enemy_hp = random.randint(3, 7)
        return (f"HP: {self.hp} | Enemy HP: {self.enemy_hp}\nPress 'w' to attack or 's' to defend/heal", ["w", "s"], None)
    
    def main(self, input: int, info: Optional[ExtraInfo]) -> Optional[MainReturn]:
        """
        Handles combat and random events.
        """
        action_result = ""
        
        if input == 0:  # Attack
            damage = random.randint(1, 3)
            self.enemy_hp -= damage
            action_result = f"You hit the enemy for {damage} damage!"
        elif input == 1:  # Defend
            if random.random() < 0.5:
                self.hp += 1
                self.enemy_hp -= 1
                action_result = "You successfully defended against the enemy's attack!"
            else:
                self.hp -= 1
                action_result = "You failed to defend and took 1 damage."
        
        # Enemy attacks if it's still alive
        if self.enemy_hp > 0 and input == 0:
            enemy_damage = random.randint(1, 2)
            self.hp -= enemy_damage
            action_result += f" The enemy hit you for {enemy_damage} damage!"
        
        # Check for game over
        if self.hp <= 0:
            return {"frame": f"HP: 0 | Game Over! Score: {self.score}", "action": {"action": "end"}} # type: ignore
        
        # Check if enemy is defeated
        if self.enemy_hp <= 0:
            self.score += 1
            self.hp += 2  # Heal after victory
            self.enemy_hp = random.randint(3, 7)
            action_result += " You defeated the enemy! A new one appears."
        
        return {"frame": f"HP: {self.hp} | Enemy HP: {self.enemy_hp}\n{action_result}", "action": None}
    
    def info(self) -> GameInfo:
        """
        Provides game metadata.
        """
        return {
            "name": "Dungeon Brawler",
            "id": "dungeon_brawler",
            "description": "Fight enemies in turn-based combat! Attack or defend strategically to survive as long as possible."
        }
