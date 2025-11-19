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


class Move:
    """
    Wrapper class of a NAO robot move along with its properties
    """

    def __init__(self, name, module, compatibles={}, execution_time=1, aesthetic_score=0):
        self.name = name
        self.module = module
        self.compatibles = compatibles
        self.execution_time = execution_time
        self.aesthetic_score = aesthetic_score
    
    def execute(self):
        self.module.main(IP, PORT)
    
    def add_compatibles(self, moves_dict):
        self.compatibles.update(moves_dict)


class DanceProblem(Problem):
    """
    A* planning problem for generating a NAO dance choreography
    """

    AESTHETIC_WEIGHT = 0.1
    MAX_TIME = 120.0
    TIME_TOL = 3.0

    def __init__(self,
                 start_move,
                 goal_move,
                 mandatory_moves):
        """
        start_move: Move instance (e.g., stand_init)
        goal_move: Move instance (e.g., crouch)
        mandatory_moves: list of Move instances that must appear in the plan
        all_moves: list or dict of all Move instances
        """
        self.start_move = start_move
        self.goal_move = goal_move
        # The set of mandatory moves still required to hit
        self.mandatory_set = frozenset(mandatory_moves)
        
        # State has shape: ([current_move], [remaining_mandatory_moves], [elapsed_time])
        initial = (start_move, self.mandatory_set, 0.0)

        super().__init__(initial, goal=goal_move)

    def actions(self, state):
        """
        Returns which Move instances can follow from the current move
        without exceeding the 120s pure time limit.
        """
        current_move, pending, elapsed = state

        valid = []
        for next_move, transition_time in current_move.compatibles.items():
            if elapsed + transition_time <= self.MAX_TIME:
                valid.append(next_move)

        return valid

    def result(self, state, action):
        """
        Returns new (move, pending_mandatories, new_elapsed_time)
        """
        current_move, pending, elapsed = state
        next_move = action

        transition_time = current_move.compatibles[next_move]
        new_elapsed = elapsed + transition_time

        # Remove from pending if this move satisfies a mandatory one
        if next_move in pending:
            new_pending = set(pending)
            new_pending.remove(next_move)
            new_pending = frozenset(new_pending)
        else:
            new_pending = pending

        return (next_move, new_pending, new_elapsed)

    def goal_test(self, state):
        """
        We reach the goal only if:
        - current move == goal move
        - all mandatory moves have been executed
        - time <= 120s and time >= 120s - TIME_TOL
        """
        move, pending, elapsed = state
        return (
            move == self.goal and
            len(pending) == 0 and
            elapsed <= self.MAX_TIME and
            elapsed >= (self.MAX_TIME - self.TIME_TOL)
        )

    def path_cost(self, c, state1, action, state2):
        """
        Computes cost = previous_cost + transition_time - aesthetic_weight * score
        """
        current_move = state1[0]
        next_move = action

        transition_time = current_move.compatibles[next_move]
        aesthetic = next_move.aesthetic_score
        return c + transition_time - aesthetic * self.AESTHETIC_WEIGHT

    def h(self, n):
        """
        Admissible heuristic that combines:
        - optimistic minimal time needed to finish pending mandatory moves
        - minimal outgoing transition time
        """
        move, pending, elapsed = n.state

        if elapsed > self.MAX_TIME:
            return float('inf')
        # Computing the actual h
        min_out = min(move.compatibles.values())
        missing = len(pending)
        return missing * min_out


