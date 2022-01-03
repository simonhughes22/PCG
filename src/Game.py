from dataclasses import dataclass
from typing import Any, List, Iterable
import numpy as np

# # Utils

def get_members(cls):
    return set([att for att in dir(cls) if not att.startswith("_")])

def get_values(cls):
    temp = [getattr(cls, att) for att in dir(cls) if not att.startswith("_")]
    vals = set()
    for item in temp:
        if type(item) in (int,float,str):
            vals.add(item)
        elif type(item) in (set,List,tuple):
            for i in item:
                vals.add(i)
    return vals

def add_meta_data(cls):
    cls.Members = get_members(cls)
    cls.Values  = get_values(cls)
                
def to_tuples(items):
    tuples = set()
    for item in items:
        tpl = tuple(StringUtils.clean(item).split(" "))
        tuples.add(tpl)
    return tuples
    
class Singleton(object):
    __instance = None
    def __new__(cls, *args):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls, *args)
        return cls.__instance

class StringUtils(object):
    
    @staticmethod
    def init_caps(s):
        return s[0].upper() + s[1:]
    
    @staticmethod
    def clean(s):
        if not s:
            return ""
        return str(s).replace("-"," ").strip().lower()

# # Entities - Items and Locations

class CompassEnum(Singleton):
    North = "north"
    South = "south"
    East  = "east"
    West  = "west"
    
class VerticalEnum(Singleton):
    Above = "above"
    Below = "below"
        
add_meta_data(CompassEnum)
add_meta_data(VerticalEnum)

@dataclass
class LivingThing(object):  
    name: str = "(LivingThing)"
    desc: str = ""
    hp: int         = 10
    mp: int         = 0
    attack: int     = 10
    defense: int    = 5
    hit_pct: float  = 0.8
    is_alive: bool  = True
    attack_verb: str = "strike"
    
    def __repr__(self):
        return self.name
    
    def describe(self):
        # Description overrides the default behavior
        if len(self.desc) > 0:
            return self.desc
    
        if self.name[0] in "aeiou":
            return f"an {self}" 
        else:
            return f"a {self}"

@dataclass(frozen=True)
class Item(object):
    name: str = ""
    attack: int = 0
    defense: int = 0
    
    def __repr__(self):
        return self.name

    def describe(self):
        if self.name[0] in "aeiou":
            desc = f"an {self}" 
        else:
            desc = f"a {self}"
        if self.attack > 0 :
            desc += f" [atk+{self.attack}]"
        if self.defense > 0 :
            desc += f" [def+{self.defense}]"
        return desc

class ItemHandler(object):
    
    def get_items(self):
        return self.items
    
    def add_item(self, item: Item):
        self.items.append(item)
        
    def remove_item(self, item_name: str):
        item = self.get_item(item_name)
        if item:
            self.items.remove(item)
            return item
        else:
            return None
                   
    def get_item(self, item_name: str):
        match = [i for i in self.get_items() if i.name == item_name]
        if match:
            return match[0]
        else:
            return None

@dataclass
class Player(LivingThing):    
    hp: int         = 100
    attack: int     = 25
    defense: int    = 5
    
@dataclass
class Location(ItemHandler):
    items = None
    creatures = None
    
    initial_desc: str = ""
    desc: str = "(Desc)"
    # if specified, overrides the default descriptor
    relation_desc: str = ""
    name: str = "(Name)"
    
    north: Any = None
    south: Any = None
    east:  Any = None
    west:  Any = None

    above: Any = None
    below: Any = None
    
    visited: bool = False
        
    def add_north(self, locn):
        self.north = locn
        locn.south = self
        
    def add_south(self, locn):
        self.south = locn
        locn.north = self
        
    def add_east(self, locn):
        self.east = locn
        locn.west = self
        
    def add_west(self, locn):
        self.west = locn
        locn.east = self
        
    def add_above(self, locn):
        self.above = locn
        locn.below = self
        
    def add_below(self, locn):
        self.below = locn
        locn.above = self
        
    def add_creature(self, creature):
        self.creatures.add_item(creature)
        
    def remove_creature(self, creature_name):
        return self.creatures.remove_item(creature_name)
    
    def get_creature(self, creature_name):
        return self.creatures.get_item(creature_name)
        
    def __post_init__(self):
        self.initial_desc = self.initial_desc.strip()
        self.desc = self.desc.strip()
        if not self.initial_desc:
            self.initial_desc = self.desc
        self.name = self.name.strip()
        self.items = []
        self.creatures = ItemHandler()
        self.creatures.items = []
            
    def get_locations(self):
        locations: List[Any] = []
        if self.north:
            locations.append(CompassEnum.North)
        if self.south:
            locations.append(CompassEnum.South)
        if self.west:
            locations.append(CompassEnum.West)
        if self.east:
            locations.append(CompassEnum.East)
        if self.above:
            locations.append(VerticalEnum.Above)
        if self.below:
            locations.append(VerticalEnum.Below)
        return locations
        
    def describe(self):
        def describe_item_list(items):
            if len(items) == 1:                
                str_items = items[0].describe()
            elif len(items) > 1:                
                str_items = ", ".join([i.describe() for i in items[:-1]])
                str_items += f" and {items[-1].describe()}"  
            return str_items
        
        # Description
        if not self.visited:
            self.visited = True
            out_val = self.initial_desc
        else:
            out_val = self.desc
        
        # Locations - paths into an out of location
        for name in self.get_locations():
            locn = getattr(self,name)
            if locn.relation_desc:
                out_val += f"\n{locn.relation_desc}. "
            elif name in VerticalEnum.Values:
                out_val += f"\n{StringUtils.init_caps(name)} is a {locn.name}. "
            elif name in CompassEnum.Values:
                out_val += f"\nTo the {name} is a {locn.name}. "
            else:
                raise Exception(f"Unknown location name: {name}")
        
        creatures = self.creatures.get_items()
        if creatures:
            out_val += f"\nInside the {self.name} you find {describe_item_list(creatures)}"
        
        # Items within the location
        if len(self.get_items()) > 0:
            items = self.get_items()
            out_val += f"\nIn the {self.name} you find {describe_item_list(items)}."
        return out_val.strip()
    
loc = Location(
        initial_desc="Dazed, you awaken to find yourself in a large, dank cavern.",
        desc="You are in a large, dank cavern.",
        name="large cavern"
)
locn_west = Location(desc="a small cave .", name="dragon room")   
locn_below = Location(desc="a crater.", name="crater")   
loc.add_west(locn_west)
loc.add_below(locn_below)
loc.add_item(Item(name="torch"))
loc.describe()

# Sword().describe()
# Shield().describe()


# # Game State

# In[4]:


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
        item = self.remove_item(item_name)
        if not item:
            self.print_output(f"No {item_name} found in your inventory")
            self.inventory()
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


# # Parser + Enums

RULES = """

# group vocab items
north,south,east,west                   =><CompassDir>
above,up,climb up                       =><VerticalUp>
below,down,climb down                   =><VerticalDown>
sword,shield,torch,key,potion           =><PickUpAble>
dragon,troll,snake,rat                  =><Creature>
attack,fight,hit,punch,headbutt,headbut =><FightVerb>

# collapse different vocab
pick up,pickup,take,equip  =>get
hold,grab                  =>hold

# actions
move|go <CompassDir>       =>[move] <CompassDir>
move|go <VerticalUp>       =>[move] above
<VerticalUp>               =>[move] above
move|go <VerticalDown>     =>[move] below
<VerticalDown>             =>[move] below
<FightVerb> <Creature>     =>[fight] <Creature> <FightVerb>

get <PickUpAble>           =>[pickup] <PickUpAble>
drop <PickUpAble>          =>[drop] <PickUpAble>
hold <PickUpAble>          =>[hold] <PickUpAble>

# special commands
quit,exit                  =>[end_game]
describe                   =>[describe]
describe room|place        =>[describe]
where am i|i?              =>[describe]
help,h,?                   =>[help]
inventory                  =>[inventory]
holding|holding?           =>[holding]
what am i holding|holding? =>[holding]
info                       =>[info]

""".strip().split("\n")

@dataclass
class Token(object):
    token: str
    data: Any

@dataclass 
class ParseResult(object):
    is_valid: bool
    method: str = ""
    args: Any   = None

class Parser(Singleton):
    StopWords = set("a,an,the".split(","))
    
    def __init__(self):
        self.build_fst(RULES)
    
    # handles | (or) tokens
    def generate_or_variants(self, tokens):
        l_toks  = [[]]
        for token in tokens:
            new_l = []
            for tok in token.split("|"):            
                for lst in l_toks:
                    new_l.append(lst + [tok])
            l_toks = new_l
        return l_toks

    def build_fst(self, rules):      
        all_tokens = set()
        fst = dict()
        for line in rules:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            left, right = line.split("=>")
            left = left.strip()
            right = right.strip()
            
            lhs_phrases = [phrase.strip().split(" ") for phrase in left.split(",")]
            assert "," not in right, "Multiple right hand phrases not supported for now"

            rhs_phrases = [t.strip() for t in right.split(" ") if len(t.strip()) > 0]
            all_tokens.update(rhs_phrases)
            for tokens in lhs_phrases:
                # remove empty tokens
                raw_tokens = [t for t in tokens if len(t.strip()) > 0]
                if not raw_tokens:
                    continue
                
                # Generate permutations of lhs rule when OR chars present
                lst_tokens = self.generate_or_variants(raw_tokens)
                for tokens in lst_tokens:
                    all_tokens.update(tokens)
                    # build dictionary for phrase
                    dct = fst
                    for tok in tokens[:-1]:
                        if tok not in dct:
                            dct[tok] = tuple([None, dict()])
                        dct = dct[tok][1]
                    # last token
                    tok = tokens[-1]
                    if tok not in dct:
                        dct[tok] = tuple([rhs_phrases, dict()])
                    else:
                        rhs_tpl = dct[tok]
                        assert rhs_tpl[0] is None, (left, right, tokens, rhs_tpl)
                        # update tuple
                        dct[tok] = tuple([rhs_phrases, rhs_tpl[1]])
                        
        self.fst = fst
        self.vocab = all_tokens
    
    def process_rules(self, tokens: List[Token])->List[Token]:
        rule_matched = True
        while rule_matched:
            tokens, rule_matched  = self.process_rules_inner(tokens)
        return tokens
    
    def process_rules_inner(self, tokens: List[Token]):
        output = []
        ix = 0
        rule_matched = False
        
        while ix < len(tokens):
            current_tok = tokens[ix]
            if current_tok.token not in self.vocab:
                ix += 1
                continue
                
            if current_tok.token not in self.fst:
                # skip unrecognized for now
                output.append(current_tok)
            else:
                best_rhs = None
                dct = self.fst
                num_tokens_matched = 0 # how long into the tokens array did we go?
                remainder = tokens[ix:] 
                for tok in remainder:
                    
                    if not tok.token in dct:
                        break
                    num_tokens_matched += 1
                    emit, dct = dct[tok.token]
                    if emit:
                        best_rhs = emit
                    # partial match only
                    if not dct:
                        break
                if not best_rhs:
                    output.append(current_tok)
                else:
                    rule_matched = True
                    matched = remainder[:num_tokens_matched]
                    diff = [t.token for t in matched if t.token not in best_rhs]                    
                    str2token = dict([(t.token, t) for t in matched])
                    # print(matched, best_rhs)
                    for str_tok in best_rhs:
                        data = diff
                        if str_tok in str2token:
                            # if token on both sides, carry over the data, e.g. move|go <CompassDir>  =>[move] <CompassDir>
                            data = str2token[str_tok].data                        
                        new_tok = Token(token=str_tok, data=data)
                        output.append(new_tok)
                    ix += num_tokens_matched - 1 # minus 1 as we are about to add one in a sec
            ix += 1
        return output, rule_matched
    
    def parse(self, s):
        tokens = [Token(data=t, token=t) for t in StringUtils.clean(s).split(" ") 
                  if t not in Parser.StopWords]
        
        if not tokens:
            return ParseResult(is_valid=False)
        
        tokens = self.process_rules(tokens)
        for i in range(len(tokens)):
            tok = tokens[i]
            if tok.token.startswith("["):
                method = tok.token[1:-1]
                args = [t.data for t in tokens[i+1:]]                
                return ParseResult(is_valid=True, method=method, args=args)
        
        return ParseResult(is_valid=False)
    
# # World Generation

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







