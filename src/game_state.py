from actions import SpecialCommands, Actions, ItemActions
from entities import ItemHandler, Player, Location
from utils import Singleton

class GameState(Singleton, SpecialCommands, Actions, ItemActions):

    def __init__(self):
        self.player = Player()
        self.location = None
        self.visited = []
        self.play = True
        # needed for ItemHandler
        # represents the inventory
        self.inventory = ItemHandler()
        self.hands = ItemHandler()

    def update_location(self, location: Location):
        self.location = location
        self.visited.append(self.location.name)
        self.describe()

    def print_output(self, s):
        print(s)

    def bad_input(self):
        self.print_output("User input not recognized")

    def get_attack_points(self):
        atk = self.player.attack
        for item in self.hands.get_items():
            atk += item.attack
        return atk

    def get_defense_points(self):
        defense = self.player.defense
        for item in self.hands.get_items():
            defense += item.defense
        return defense