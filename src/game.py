import numpy as np

# # Utils
from entities import Item, Location, ItemHandler, LivingThing, Player
from parser import Parser
from utils import Singleton, StringUtils

input_list = []
def pop_from_list(s):
    global input_list
    if input_list:
        item = input_list[0]
        input_list = input_list[1:]
        print(f">>> {item}")
        return item
    return "quit"     

def rand(high, low=0):
    return np.random.randint(low,high+1)

def rand_float():
    return np.random.random()

class GameState(Singleton, ItemHandler):
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
                
    # Special Methods, defined in BNF below
    def end_game(self, args=None):
        self.print_output("Game Over")
        self.play = False        

    def fight(self, args):
        creature_name = args[0][0]
        creature = self.location.get_creature(creature_name)
        verb = args[1][0]
        
        if not creature:
            self.print_output(f"No {creature_name} exists in the {self.location.name}")
            return
        if not creature.is_alive:
            self.print_output(f"The {creature_name} is already dead. You {verb} a rotting carcass. It does not strike back...")
            return
        
        # player attacks
        player_hits = (rand_float() <= self.player.hit_pct)
        damage = max(0,rand(high=self.get_attack_points()) - rand(creature.defense))
        if not player_hits or damage <= 0:
            self.print_output(f"You attempt to {verb} the {creature.name}, but miss spectacularly...")
        else:        
            creature.hp -= damage
            if creature.hp <= 0:
                creature.is_alive = False
                self.print_output(f"You {verb} the {creature.name}, killing it.")
            else:
                self.print_output(f"You {verb} the {creature.name}, doing {damage} points of damage. The {creature.name} has {creature.hp} health remaining. It is preparing to strike.")
            
        if creature.is_alive:
            creature_hits = (rand_float() <= creature.hit_pct)
            damage = max(0,rand(high=creature.attack) - rand(self.get_defense_points()))
            if not creature_hits or damage <= 0:
                self.print_output(f"The {creature.name} attempts to {creature.attack_verb} you, but you manage to avoid the attack.")
            else:        
                self.player.hp -= damage
                if self.player.hp <= 0:
                    self.print_output(f"The {creature.name} tries to {creature.attack_verb} you, dealing a killing blow. Everything fades to black as you lose conciousness.")
                    self.player.is_alive = False
                    self.end_game()
                else:
                    self.print_output(f"The {creature.name} tried to {creature.attack_verb} you, doing {damage} damage. You have {self.player.hp} health remaining.")

    def describe(self, args=None):
        self.print_output(self.location.describe())
        
    def move(self, args):
        direction = args[0][0]
        locn = getattr(self.location, direction, None)
        if not locn:
            self.print_output(f"Cannot move {direction}!")
            return
        self.update_location(locn)

    def help(self, args=None):
        self.print_output("Not implemented yet")
    
    def pickup(self, args):
        item_name = args[0][0]
        item = self.location.remove_item(item_name)
        if not item:
            self.print_output(f"No {item_name} found in the {self.location.name}")
        else:
            existing_item = self.get_item(item_name)
            if existing_item:
                self.location.add_item(item)
                self.print_output(f"You already have {existing_item.describe()} in your inventory")
            else:
                self.add_item(item)
                self.print_output(f"{StringUtils.init_caps(item.describe())} was added to your inventory")
                
    def drop(self, args):
        item_name = args[0][0]
        item = self.remove_item(item_name)
        if not item:
            # is item in your hands instead?
            item = self.hands.remove_item(item_name)
            if item:
                self.print_output(f"You dropped the {item}")
                self.holding()
                self.location.add_item(item)                
            else:
                self.print_output(f"No {item_name} found in your inventory")
                self.inventory()
        else:
            self.print_output(f"You dropped the {item}")
            self.location.add_item(item)
            self.inventory()
            
    def hold(self, args):
        num_items = len(self.hands.get_items())
        if num_items >= 2:
            self.print_output(f"You cannot hold more than two items")
            return
        
        item_name = args[0][0]
        # try inventory
        item = self.remove_item(item_name)
        if not item:
            # try location
            item = self.location.remove_item(item_name)
            if not item:
                self.print_output(f"No {item_name} found.")
                return
            
        self.hands.add_item(item)
        self.holding()
        
    def info(self, args=None):
        self.print_output(f"Health:  {self.player.hp}")
        self.print_output(f"Magic:   {self.player.mp}")
        self.print_output(f"Attack:  {self.get_attack_points()}")
        self.print_output(f"Defense: {self.get_defense_points()}")
                
        self.inventory()
    
    def inventory(self, args=None):
        num_items = len(self.get_items())
        if num_items == 1:
            self.print_output(f"Your inventory has {len(self.get_items())} item:")
        else:
            self.print_output(f"Your inventory has {len(self.get_items())} items:")
        for item in self.get_items():
            self.print_output(f"  {item.describe()}")
        
        # print what your hands are holding also
        if len(self.hands.get_items()) > 0:        
            self.holding()
    
    def holding(self, args=None):       
        if len(self.hands.get_items()) > 0:
            self.print_output(f"You are holding:")
            for item in self.hands.get_items():
                self.print_output(f"  {item.describe()}")        
        else:
            self.print_output(f"You are holding nothing.")


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







