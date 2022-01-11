from dataclasses import dataclass
from typing import Any, List, Callable

from enums import CompassEnum, VerticalEnum
from parser import Parser
from utils import StringUtils


@dataclass
class LivingThing(object):
    name: str = "(LivingThing)"
    desc: str = ""
    hp: int = 10
    mp: int = 0
    attack: int = 10
    defense: int = 5
    hit_pct: float = 0.8
    is_alive: bool = True
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
    hp: int = 0
    mp: int = 0

    consume_fn: Callable[['Item'],None] = lambda : None
    pickup_fn: Callable[['Item'],None]  = lambda : None
    drop_fn: Callable[['Item'],None]    = lambda : None

    def on_pickup(self):
        self.pickup_fn(self)

    def on_drop(self):
        self.drop_fn(self)

    def on_consume(self):
        self.consume_fn(self)

    def __repr__(self):
        return self.name

    def describe(self):
        if self.name[0] in "aeiou":
            desc = f"an {self}"
        else:
            desc = f"a {self}"
        if self.attack > 0:
            desc += f" [atk+{self.attack}]"
        if self.defense > 0:
            desc += f" [def+{self.defense}]"
        return desc

class ItemHandler(object):
    # NOTE: requires implementation of items list - self.items = []
    def __init__(self):
        self.items = []

    def get_items(self):
        return self.items

    def get_item(self, item_name: str):
        match = [i for i in self.get_items() if i.name == item_name]
        if match:
            return match[0]
        else:
            return None

    def add_item(self, item: Item):
        parser = Parser()
        item_name = item.name.lower()
        # Allow overriding of default behavior
        if not parser.has_rule(item_name):
            parser.add_new_rule(left=item_name, right="<PickupAble>")
        self.items.append(item)

    def remove_item(self, item_name: str):
        item = self.get_item(item_name)
        if item:
            self.items.remove(item)
            return item
        else:
            return None

    def clear(self):
        self.items = []

@dataclass
class Player(LivingThing):
    hp: int = None
    max_hp: int = 100
    attack: int = 25
    defense: int = 5

    def __post_init__(self):
        if self.hp is None:
            self.hp = self.max_hp
        assert  self.hp <= self.max_hp, f"Hp:{self.hp} cannpt be greater than max_hp:{self.max_hp}"

@dataclass
class Entrance(object):
    location: 'Location'

    is_locked: bool = None
    is_visible: bool = None
    name: str = None

    # name of item needed to unlock
    key_name: str = "-"

    def __post_init__(self):
        # Implement default values
        if self.is_locked is None:
            self.is_locked = False
        if self.is_visible is None:
            self.is_visible = True
        if self.name is None:
            self.name = "passageway"

    def describe(self):
        if self.is_locked:
            return f"locked {self.name}"
        return self.name

    def unlock(self, item: Item):
        """
        Unlocks the Entrance if locked

        :param item: item used to unlock the Entrance
        :return:
        """
        if item.name == self.key_name:
            self.is_lockwd = False
            return True
        return False

    def clone(self):
        return Entrance(
            name=self.name,
            location=self.location, is_locked=self.is_locked,
            is_visible=self.is_visible, key_name=self.key_name
        )

@dataclass
class Location(ItemHandler):
    name: str = "(Name)"
    initial_desc: str = ""
    desc: str = "(Desc)"

    items = None
    creatures = None

    north: Entrance = None
    south: Entrance = None
    east: Entrance = None
    west: Entrance = None

    above: Entrance = None
    below: Entrance = None

    visited: bool = False

    @staticmethod
    def Default():
        return Location()

    def add_north(self, entrance: Entrance, two_way=True):
        self.north = entrance
        if two_way:
            cloney = entrance.clone()
            cloney.location = self
            entrance.location.south = cloney

    def add_south(self, entrance: Entrance, two_way=True):
        self.south = entrance
        if two_way:
            cloney = entrance.clone()
            cloney.location = self
            entrance.location.north = cloney

    def add_east(self, entrance: Entrance, two_way=True):
        self.east = entrance

        if two_way:
            cloney = entrance.clone()
            cloney.location = self
            entrance.location.west = cloney

    def add_west(self, entrance: Entrance, two_way=True):
        self.west = entrance

        if two_way:
            cloney = entrance.clone()
            cloney.location = self
            entrance.location.east = cloney

    def add_above(self, entrance: Entrance, two_way=True):
        self.above = entrance

        if two_way:
            cloney = entrance.clone()
            cloney.location = self
            entrance.location.below = cloney

    def add_below(self, entrance: Entrance, two_way=True):
        self.below = entrance

        if two_way:
            cloney = entrance.clone()
            cloney.location = self
            entrance.location.above = cloney

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

    def get_entrance_directions(self):
        entrances: List[Entrance] = []
        if self.north:
            entrances.append(CompassEnum.North)
        if self.south:
            entrances.append(CompassEnum.South)
        if self.west:
            entrances.append(CompassEnum.West)
        if self.east:
            entrances.append(CompassEnum.East)
        if self.above:
            entrances.append(VerticalEnum.Above)
        if self.below:
            entrances.append(VerticalEnum.Below)
        return entrances

    def describe(self):
        def describe_item_list(items):
            if len(items) == 1:
                str_items = items[0].describe()
            elif len(items) > 1:
                str_items = ", ".join([i.describe() for i in items[:-1]])
                str_items += f" and {items[-1].describe()}"
            return str_items

        # Description
        out_val = StringUtils.init_caps(self.name)
        if not self.visited:
            self.visited = True
            out_val += f"\n{self.initial_desc}"
        else:
            out_val += f"\n{self.desc}"

        # Entrances - paths into an out of location
        for direction in self.get_entrance_directions():
            # Use direction name to get correct property
            entrance: Entrance = getattr(self, direction)
            if direction in VerticalEnum.Values:
                out_val += f"\n{StringUtils.init_caps(direction)} is a {entrance.describe()}. "
            elif direction in CompassEnum.Values:
                out_val += f"\nTo the {direction} is a {entrance.describe()}. "
            else:
                raise Exception(f"Unknown location name: {direction}")

        creatures = self.creatures.get_items()
        if creatures:
            out_val += f"\nInside the {self.name} you find {describe_item_list(creatures)}"

        # Items within the location
        if len(self.get_items()) > 0:
            items = self.get_items()
            out_val += f"\nIn the {self.name} you find {describe_item_list(items)}."
        return out_val.strip()

