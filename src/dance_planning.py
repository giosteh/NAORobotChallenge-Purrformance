from aima.search import Problem, astar_search
from naoqi import ALProxy
import time
# Importing mandatory and optional moves
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
    TIME_TOL = 5.0

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





StandInit = Move("StandInit", stand_init, execution_time=0.5, aesthetic_score=0.2)
Sit = Move("Sit", sit, execution_time=1.0, aesthetic_score=0.3)
SitRelax = Move("SitRelax", sit_relax, execution_time=1.2, aesthetic_score=0.4)
Stand = Move("Stand", stand, execution_time=0.7, aesthetic_score=0.2)
StandZero = Move("StandZero", stand_zero, execution_time=0.4, aesthetic_score=0.1)
Hello = Move("Hello", hello, execution_time=1.3, aesthetic_score=0.6)
WipeForehead = Move("WipeForehead", wipe_forehead, execution_time=1.5, aesthetic_score=0.7)
Crouch = Move("Crouch", crouch, execution_time=1.4, aesthetic_score=0.5)
ArmsOpening = Move("ArmsOpening", arms_opening, execution_time=1.8, aesthetic_score=0.8)
DiagonalLeft = Move("DiagonalLeft", diagonal_left, execution_time=1.6, aesthetic_score=0.7)
DiagonalRight = Move("DiagonalRight", diagonal_right, execution_time=1.6, aesthetic_score=0.7)
DoubleMovement = Move("DoubleMovement", double_movement, execution_time=2.0, aesthetic_score=0.9)
MoveBackward = Move("MoveBackward", move_backward, execution_time=1.3, aesthetic_score=0.5)
MoveForward = Move("MoveForward", move_forward, execution_time=1.3, aesthetic_score=0.5)
RightArm = Move("RightArm", right_arm, execution_time=1.1, aesthetic_score=0.4)
RotationHandgunObject = Move("RotationHandgunObject", rotation_handgun_object, execution_time=2.2, aesthetic_score=0.9)
RotationLeftFoot = Move("RotationLeftFoot", rotation_left_foot, execution_time=1.7, aesthetic_score=0.6)
RotationRightFoot = Move("RotationRightFoot", rotation_right_foot, execution_time=1.7, aesthetic_score=0.6)
Sprinkler = Move("Sprinkler", sprinkler, execution_time=2.5, aesthetic_score=1.0)
UnionArms = Move("UnionArms", union_arms, execution_time=1.9, aesthetic_score=0.7)



# Compatible moves specification
StandInit.add_compatibles({
    Sit: 2.0,
    Stand: 1.5,
    StandZero: 1.5,
    Hello: 2.5,
    ArmsOpening: 2.0
})

Sit.add_compatibles({
    SitRelax: 1.5,
    Stand: 2.5,
    StandZero: 2.5,
    Crouch: 3.0
})

SitRelax.add_compatibles({
    Stand: 2.5,
    StandZero: 2.5,
    WipeForehead: 2.0,
    Crouch: 3.0
})

Stand.add_compatibles({
    StandZero: 1.0,
    Hello: 2.0,
    WipeForehead: 2.5,
    ArmsOpening: 2.0,
    MoveForward: 3.0,
    MoveBackward: 3.0,
    RotationLeftFoot: 2.5,
    RotationRightFoot: 2.5,
    DiagonalLeft: 2.0,
    DiagonalRight: 2.0,
    UnionArms: 2.0,
    Crouch: 3.5
})

StandZero.add_compatibles({
    Stand: 1.0,
    Hello: 2.0,
    WipeForehead: 2.0,
    Sit: 2.0,
    SitRelax: 2.0,
    ArmsOpening: 2.0,
    Crouch: 3.0
})

Hello.add_compatibles({
    Stand: 2.0,
    StandZero: 2.0,
    WipeForehead: 2.0,
    DiagonalLeft: 2.5,
    DiagonalRight: 2.5,
    Crouch: 3.5
})

WipeForehead.add_compatibles({
    Stand: 2.0,
    StandZero: 2.0,
    Hello: 2.0,
    DiagonalLeft: 2.0,
    DiagonalRight: 2.0,
    Crouch: 3.5
})

ArmsOpening.add_compatibles({
    Stand: 2.0,
    StandZero: 2.0,
    UnionArms: 2.5,
    DiagonalLeft: 2.0,
    DiagonalRight: 2.0,
    DoubleMovement: 2.5,
    Crouch: 4.0
})

DiagonalLeft.add_compatibles({
    Stand: 2.0,
    StandZero: 2.0,
    RightArm: 2.0,
    RotationLeftFoot: 2.5,
    Sprinkler: 2.5,
    Crouch: 4.0
})

DiagonalRight.add_compatibles({
    Stand: 2.0,
    StandZero: 2.0,
    RightArm: 2.0,
    RotationRightFoot: 2.5,
    Sprinkler: 2.5,
    Crouch: 4.0
})

DoubleMovement.add_compatibles({
    Stand: 2.0,
    StandZero: 2.0,
    ArmsOpening: 2.5,
    Sprinkler: 2.5,
    Crouch: 4.0
})

MoveBackward.add_compatibles({
    Stand: 2.0,
    StandZero: 2.0,
    MoveForward: 3.0,
    RotationHandgunObject: 3.0,
    Crouch: 4.0
})

MoveForward.add_compatibles({
    Stand: 2.0,
    StandZero: 2.0,
    MoveBackward: 3.0,
    RotationHandgunObject: 3.0,
    Crouch: 4.0
})

RightArm.add_compatibles({
    Stand: 2.0,
    StandZero: 2.0,
    UnionArms: 2.0,
    Sprinkler: 3.0,
    Crouch: 4.0
})

RotationHandgunObject.add_compatibles({
    Stand: 2.0,
    StandZero: 2.0,
    MoveForward: 3.0,
    MoveBackward: 3.0,
    Crouch: 4.0
})

RotationLeftFoot.add_compatibles({
    Stand: 2.0,
    StandZero: 2.0,
    DiagonalLeft: 2.0,
    Sprinkler: 3.0,
    Crouch: 4.0
})

RotationRightFoot.add_compatibles({
    Stand: 2.0,
    StandZero: 2.0,
    DiagonalRight: 2.0,
    Sprinkler: 3.0,
    Crouch: 4.0
})

Sprinkler.add_compatibles({
    Stand: 2.0,
    StandZero: 2.0,
    RotationLeftFoot: 3.0,
    RotationRightFoot: 3.0,
    Crouch: 4.0
})

UnionArms.add_compatibles({
    Stand: 2.0,
    StandZero: 2.0,
    ArmsOpening: 2.5,
    DoubleMovement: 2.5,
    Crouch: 3.5
})


# Specifying mandatory moves
MANDATORY_MOVES = [
    Sit, SitRelax, Stand, StandZero, Hello, WipeForehead
]


def execute_choreography(choreography):
    """
    Connects to the NAO robot and execute the given moves
    """
    motion = ALProxy("ALMotion", IP, PORT)
    motion.wakeUp()
    time.sleep(1.0)

    for move in choreography:
        move.execute()
    motion.rest()



# Main execution
if __name__ == "__main__":
    problem = DanceProblem(start_move=StandInit,
                           goal_move=Crouch,
                           mandatory_moves=MANDATORY_MOVES)
    solution = astar_search(problem)
    choreography = [n.state[0] for n in solution.path()]
    total_time = solution.state[2]

    for move in choreography:
        print "-> {}".format(move.name)
    print "Total time: {}s".format(total_time)

    # Executing the choreography
    execute_choreography(choreography)
