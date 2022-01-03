from dataclasses import dataclass
from typing import Any, List

from enums import CompassEnum, VerticalEnum

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
    hp: int = 100
    attack: int = 25
    defense: int = 5

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
    east: Any = None
    west: Any = None

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
            locn = getattr(self, name)
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