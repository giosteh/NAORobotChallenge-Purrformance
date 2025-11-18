"""
Classes and algorithms to model the robot dancing behavior.
"""

from aima.search import Problem, astar_search
from naoqi import ALProxy
import time
# importing mandatory and optional moves
from moves import stand_init, sit, sit_relax, stand, stand_zero, hello, wipe_forehead, crouch
from moves import arms_opening, diagonal_left, diagonal_right, double_movement, move_backward, move_forward, right_arm
from moves import rotation_handgun_object, rotation_left_foot, rotation_right_foot, sprinkler, union_arms


# ROBOT CONNECTION SETTINGS
IP, PORT = "127.0.0.1", None



class DanceProblem(Problem):
    """Dance problem class which extends the AIMA searching problem class."""
    pass


class Move:
    """Wrapper class of a NAO robot move along with the subsequent compatible moves."""
    def __init__(self, name, time, module=None):
        self.name = name
        self.time = time
        self.module = module
        self.compatibles = {} # [move: transition_time]
    
    def execute(self):
        self.module.main(IP, PORT)
    
    def add_compatibles(self, moves_dict):
        self.compatibles.update(moves_dict)



def generate_choreography(mandatory_moves):
    """Uses the A* search algorithm to find a suitable choreography."""
    pass


def execute_choreography(sequence):
    """Connect to the NAO robot and execute the given sequence of moves."""
    try:
        motion = ALProxy("ALMotion", IP, PORT)
        motion.wakeUp()
        time.sleep(1.0)
        # loops through the moves
        for move in sequence:
            move.execute()
        motion.rest()
    except Exception as e:
        print "\nCould not connect to the robot."



if __name__ == "__main__":

    MANDATORY_MOVES = {}
    TIME_LIMIT = 120.0
