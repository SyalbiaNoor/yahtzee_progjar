from typing import Dict, List

class GameState:
    def __init__(self, room_code: str):
        self.room_code = room_code
        self.players = []
        self.scores = {}
        self.turn_index = 0
        self.ready = False
        self.final_scores = {}
        self.winner = None

    def is_full(self):
        return len(self.players) == 2

    def current_player(self):
        return self.players[self.turn_index]

    def next_turn(self):
        self.turn_index = (self.turn_index + 1) % len(self.players)
