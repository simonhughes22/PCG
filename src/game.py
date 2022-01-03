# # Utils
from actions import SpecialCommands, Actions
from entities import Item, Location, ItemHandler, LivingThing, Player
from parser import Parser
from utils import Singleton

input_list = []
def pop_from_list(s):
    global input_list
    if input_list:
        item = input_list[0]
        input_list = input_list[1:]
        print(f">>> {item}")
        return item
    return "quit"

class GameState(Singleton, ItemHandler, Actions, SpecialCommands):
    def __init__(self):
        self.player = Player()
        self.location = None
        self.visited = []
        self.play = True
        # needed for ItemHandler
        # represents the inventory
        self.items = []
        self.hands = ItemHandler()
        self.hands.items = []
        
    def update_location(self, location):
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

class Game(Singleton):
            
    def __init__(self):
        self.play = True
        self.loop_num = 0
        self.gs = GameState()
        self.parser = Parser()
        
    def run(self, init_location):        
        self.gs.update_location(init_location)
        while self.gs.play:            
            self.loop()
            self.loop_num += 1
            if self.loop_num >= 1000:
                self.gs.end_game()
        
    def get_user_input(self, prompt):
        # self.gs.print_output(prompt + "\n")
        return input(prompt)

    def loop(self):
        user_input = self.get_user_input("\nWhat do you want to do?\n")

        parse_results = self.parser.parse(user_input)
        if parse_results.is_valid:
            fn = getattr(self.gs, parse_results.method)
            fn(parse_results.args)
        else:
            self.gs.bad_input()

# class Player(LivingThing):
#     hp: int         = 100
#     attack: int     = 25
#     defense: int    = 5

def generate_world():

    Dragon = LivingThing(name="dragon", hp=20, attack=35, defense=5, attack_verb="slash")
    Troll  = LivingThing(name="troll",  hp=20, attack= 15, defense=2, attack_verb="hit")
    Rat    = LivingThing(name="rat",    hp=5,  attack= 12, defense=1, attack_verb="bite")
    Snake  = LivingThing(name="snake",  hp=10, attack= 12, defense=1, attack_verb="bite")

    Sword  = Item(name="sword",  attack=10)
    Shield = Item(name="shield", defense=5)
    
    intro = Location(
        initial_desc="Dazed, you awaken to find yourself in a large, dank cavern.",
        desc="You are in a large, dank cavern.",
        name="large cavern"
    )
    intro.add_item(Item(name="torch"))
    intro.add_item(Sword)
    intro.add_item(Shield)
    intro.add_item(Item(name="key"))
    
    locn_west = Location(desc="""
You enter a small cave with a low ceiling. Inside there is a dank smell, and a low, rumbling noise coming from one corner of the room.
Wary, you glance over a see a snout poking out from the side of a pile of rocks.
""",
                        name="dragon room")
    locn_west.add_creature(Dragon)
    
    locn_east = Location(desc="""
You are in a room filled with treasure. Gold coins cover the floor, rubies and precious gems fill several wooden crate scattered around the room.
""",
                        name="treasure room")
    
    locn_east.add_creature(Troll)
    
    locn_north =  Location(
        initial_desc="You climb through a low, arrow passageway and enter a stumble onto a narrow ledge, surrounded by water.",
        desc="You are on a narrow ledge surrounded by water.",
        name="water room"
    )
    
    intro.add_north(locn_north)
    
    intro.add_west(locn_west)
    intro.add_east(locn_east)

    return intro

if __name__ == "__main__":

    game = Game()
    start_room = generate_world()
    game.run(start_room)







