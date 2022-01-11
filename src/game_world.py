# class Player(LivingThing):
#     hp: int         = 100
#     attack: int     = 25
#     defense: int    = 5

from entities import LivingThing, Item, Location, Entrance
from game_state import GameState


def generate_world():
    dragon = LivingThing(name="dragon", hp=20, attack=35, defense=5, attack_verb="slash")
    troll = LivingThing(name="troll", hp=20, attack=15, defense=2, attack_verb="hit")
    rat = LivingThing(name="rat", hp=5, attack=12, defense=1, attack_verb="bite")
    snake = LivingThing(name="snake", hp=10, attack=12, defense=1, attack_verb="bite")

    def on_consume(self):
        gs = GameState()
        gs.player.hp = min(gs.player.max_hp, gs.player.hp + self.hp)
        gs.print_output(f"Consumed {self.name}. Heath is now: {gs.player.hp}.")

    health_potion = Item(name="potion", hp=50, consume_fn=on_consume)

    sword = Item(name="sword", attack=10)
    shield = Item(name="shield", defense=5)
    gold_key = Item(name="gold key")

    intro = Location(
        initial_desc="Dazed, you awaken to find yourself in a large, dank cavern.",
        desc="You are in a large, dank cavern.",
        name="large cavern"
    )
    intro.add_item(Item(name="torch"))
    intro.add_item(sword)
    intro.add_item(shield)
    intro.add_item(gold_key)

    locn_west = Location(desc="""
You enter a small cave with a low ceiling. Inside there is a dank smell, and a low, rumbling noise coming from one corner of the room.
Wary, you glance over a see a snout poking out from the side of a pile of rocks.
""",
                         name="dragon room")
    locn_west.add_creature(dragon)

    locn_east = Location(desc="""
You are in a room filled with treasure. Gold coins cover the floor, rubies and precious gems fill several wooden crate scattered around the room.
""",
                         name="treasure room")

    locn_east.add_item(health_potion)
    locn_east.add_creature(troll)

    locn_north = Location(
        initial_desc="You climb through a low, arrow passageway and enter a stumble onto a narrow ledge, surrounded by water.",
        desc="You are on a narrow ledge surrounded by water.",
        name="water room"
    )

    intro.add_north(Entrance(locn_north))
    intro.add_west(Entrance(locn_west))
    intro.add_east(Entrance(locn_east, is_locked=True, key_name=gold_key.name, name="wooden door"))

    return intro
