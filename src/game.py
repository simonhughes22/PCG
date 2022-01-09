# # Utils
from game_state import GameState
from game_world import generate_world
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

if __name__ == "__main__":

    game = Game()
    start_room = generate_world()
    game.run(start_room)







