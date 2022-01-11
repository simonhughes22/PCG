from typing import List
import numpy as np

from entities import Entrance
from utils import StringUtils

def rand(high, low=0):
    return np.random.randint(low,high+1)

def rand_float():
    return np.random.random()

class SpecialCommands(object):
    def info(self, args=None):
        self.print_output(f"Health:  {self.player.hp}")
        self.print_output(f"Magic:   {self.player.mp}")
        self.print_output(f"Attack:  {self.get_attack_points()}")
        self.print_output(f"Defense: {self.get_defense_points()}")

        self.list_inventory()

    def describe(self, args=None):
        self.print_output(self.location.describe())

    def help(self, args=None):
        self.print_output("Not implemented yet")

class Actions(object):

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
            self.print_output(
                f"The {creature_name} is already dead. You {verb} a rotting carcass. It does not strike back...")
            return

        # player attacks
        player_hits = (rand_float() <= self.player.hit_pct)
        damage = max(0, rand(high=self.get_attack_points()) - rand(creature.defense))
        if not player_hits or damage <= 0:
            self.print_output(f"You attempt to {verb} the {creature.name}, but miss spectacularly...")
        else:
            creature.hp -= damage
            if creature.hp <= 0:
                creature.is_alive = False
                self.print_output(f"You {verb} the {creature.name}, killing it.")
            else:
                self.print_output(
                    f"You {verb} the {creature.name}, doing {damage} points of damage. The {creature.name} has {creature.hp} health remaining. It is preparing to strike.")

        if creature.is_alive:
            creature_hits = (rand_float() <= creature.hit_pct)
            damage = max(0, rand(high=creature.attack) - rand(self.get_defense_points()))
            if not creature_hits or damage <= 0:
                self.print_output(
                    f"The {creature.name} attempts to {creature.attack_verb} you, but you manage to avoid the attack.")
            else:
                self.player.hp -= damage
                if self.player.hp <= 0:
                    self.print_output(
                        f"The {creature.name} tries to {creature.attack_verb} you, dealing a killing blow. Everything fades to black as you lose conciousness.")
                    self.player.is_alive = False
                    self.end_game()
                else:
                    self.print_output(
                        f"The {creature.name} tried to {creature.attack_verb} you, doing {damage} damage. You have {self.player.hp} health remaining.")

    def move(self, args: List[str]):
        direction:str = args[0][0]
        entrance: Entrance = getattr(self.location, direction, None)
        if not entrance:
            self.print_output(f"Cannot move {direction}!")
            return
        if entrance.is_locked:
            self.print_output(f"Cannot move {direction}, the {entrance.name} is locked and requires a {entrance.key_name} to unlock.")
        else:
            self.update_location(entrance.location)

class ItemActions(object):

    def pickup(self, args):
        item_name = args[0][0]
        item = self.location.remove_item(item_name)
        if not item:
            self.print_output(f"No {item_name} found in the {self.location.name}")
        else:
            existing_item = self.inventory.get_item(item_name)
            if existing_item:
                self.print_output(f"You already have {existing_item.describe()} in your inventory")
            else:
                self.inventory.add_item(item)
                item.on_pickup()
                self.print_output(f"{StringUtils.init_caps(item.describe())} was added to your inventory")
                self.list_inventory()

    def hold(self, args): # grab
        num_items = len(self.hands.get_items())
        if num_items >= 2:
            self.print_output(f"You cannot hold more than two items")
            return

        item_name = args[0][0]
        # try inventory
        item = self.inventory.remove_item(item_name)
        if not item:
            # try location
            item = self.location.remove_item(item_name)
            if not item:
                self.print_output(f"No {item_name} found.")
                return

        self.hands.add_item(item)
        self.holding()

    def drop(self, args):
        item_name = args[0][0]
        item = self.inventory.remove_item(item_name)
        if not item:
            # is item in your hands instead?
            item = self.hands.remove_item(item_name)
            if item:
                self.print_output(f"You dropped the {item}")
                self.location.add_item(item)
                item.on_drop()
                self.holding()
            else:
                self.print_output(f"No {item_name} found in your inventory")
                self.list_inventory()
        else:
            self.print_output(f"You dropped the {item}")
            self.location.add_item(item)
            item.on_drop()
            self.list_inventory()

    def consume(self, args):
        item_name = args[0][0]
        item = self.inventory.remove_item(item_name)
        if not item:
            item = self.location.remove_item(item_name)
            if not item:
                self.print_output(f"No {item_name} found.")
                return
        item.on_consume()

    def drop_all(self, args=None):
        items = self.inventory.get_items()
        items += self.hands.get_items()
        self.inventory.clear()
        self.hands.clear()

        for item in items:
            self.location.add_item(item)
        self.list_inventory()
        self.holding()

    def list_inventory(self, args=None):
        num_items = len(self.inventory.get_items())
        if num_items == 0:
            self.print_output(f"Your inventory is empty.")
        elif num_items == 1:
            self.print_output(f"Your inventory has {len(self.inventory.get_items())} item:")
        else:
            self.print_output(f"Your inventory has {len(self.inventory.get_items())} items:")

        for item in self.inventory.get_items():
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
