from aima.search import Problem, astar_search
from naoqi import ALProxy
import pygame
import time
import os

# --- IMPORTING MOVES ---
from moves import (
    stand_init, sit, sit_relax, stand, stand_zero, hello, wipe_forehead, crouch,
    arms_opening, diagonal_left, diagonal_right, double_movement, move_backward,
    move_forward, right_arm, rotation_left_foot, rotation_right_foot, union_arms,
    birthday_dance, arm_dance, blow_kisses, bow, dance_move, the_robot, come_on,
    staying_alive, rhythm, pulp_fiction, wave, glory, clap, joy
)

# --- ROBOT CONNECTION SETTINGS ---
IP, PORT = "127.0.0.1", 37995

# --- SONG CONFIGURATION (ADDED) --- 
# Setup: Put your mp3 file in the same folder as this script
SONG_FILENAME = "stayin_alive.mp3"  # <--- ADDED FOR MUSIC: Change this to your file name

# ======================================================================
#   MOVE CLASS
# ======================================================================
class Move:
    def __init__(self, name, module, execution_time=1.0):
        self.name = name
        self.module = module
        self.compatibles = set()
        self.execution_time = execution_time

    def execute(self):
        print "-> Executing: {} (Duration: {:.2f}s)".format(self.name, self.execution_time)
        try:
            self.module.main(IP, PORT)
        except:
            time.sleep(self.execution_time)

    def add_compatibles(self, move_list):
        self.compatibles.update(move_list)

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


# ======================================================================
#   SEARCH PROBLEM (THE BRAIN)
# ======================================================================
class DanceProblem(Problem):

    # --- TUNABLE CONSTANTS ---
    MAX_DURATION = 110.0    # The Robot must finish before this time
    AESTHETIC_WEIGHT = 10.0 # Higher number = Robot prefers "High" category moves more
    CLUMPING_PENALTY = 50.0 # Penalty to prevent doing Mandatories back-to-back

    def __init__(self, start_move, goal_move, mandatory_moves, all_moves_list, partitions):
        print "   [System] Initializing Search Problem..."
        self.start_move = start_move
        self.goal_move = goal_move
        self.mandatory_set = frozenset(mandatory_moves)
        self.all_mandatory_moves = set(mandatory_moves)

        # Map every move to an ID for indexing scores
        self.all_moves_list = sorted(all_moves_list, key=lambda m: m.name)
        self.move_to_index = {m: i for i, m in enumerate(self.all_moves_list)}
        self.partitions = partitions

        # Counter to track how much A* has explored
        self.nodes_explored = 0

        # Initial scores set to 0 for every move
        initial_scores = tuple([0.0] * len(self.all_moves_list))

        # Start state = (current move, pending mandatory moves, time passed, boredom scores)
        initial_state = (
            start_move,
            self.mandatory_set,
            start_move.execution_time,
            initial_scores
        )
        super(DanceProblem, self).__init__(initial_state, goal=goal_move)

    def actions(self, state):
        current_move, pending, elapsed_time, scores = state

        self.nodes_explored += 1
        if self.nodes_explored % 1000 == 0:
            print "   [Thinking] Analyzed {} partial plans...".format(self.nodes_explored)

        candidates = list(current_move.compatibles)
        valid_moves = []

        for m in candidates:
            predicted_time = elapsed_time + m.execution_time

            # Reject moves that exceed max total time
            if predicted_time > self.MAX_DURATION:
                continue

            # Reject repeating the same move twice
            if m.name == current_move.name:
                continue

            valid_moves.append(m)

        return valid_moves

    def result(self, state, action):
        current_move, pending, elapsed, current_scores = state
        next_move = action

        new_time = elapsed + next_move.execution_time

        # Update pending mandatory tasks
        if next_move in pending:
            new_pending = frozenset(x for x in pending if x != next_move)
        else:
            new_pending = pending

        new_scores_list = list(current_scores)

        for i, move_obj in enumerate(self.all_moves_list):
            if move_obj == next_move:
                new_scores_list[i] = 0.0
            else:
                rate = self.partitions.get(move_obj, 0.2)
                new_scores_list[i] += rate

        new_scores = tuple(new_scores_list)

        return (next_move, new_pending, new_time, new_scores)

    def path_cost(self, c, state1, action, state2):
        current_move = state1[0]
        current_scores = state1[3]
        next_move = action

        step_cost = next_move.execution_time

        move_index = self.move_to_index[next_move]
        aesthetic_value = current_scores[move_index]

        step_cost -= (aesthetic_value * self.AESTHETIC_WEIGHT)

        if (current_move in self.all_mandatory_moves) and (next_move in self.all_mandatory_moves):
            if current_move.name != "StandInit":
                step_cost += self.CLUMPING_PENALTY

        return c + step_cost

    def h(self, n):
        move, pending, elapsed_time, scores = n.state

        time_needed = sum(m.execution_time for m in pending)

        if self.goal_move not in pending:
            time_needed += self.goal_move.execution_time

        if elapsed_time + time_needed > self.MAX_DURATION:
            return float('inf')

        return time_needed + (len(pending) * 20.0)

    def goal_test(self, state):
        move, pending, elapsed_time, scores = state

        return (
            move == self.goal_move and
            len(pending) == 0 and
            elapsed_time <= self.MAX_DURATION
        )


# ======================================================================
#   SETUP
# ======================================================================

print "1. Loading Moves and Durations..."
StandInit = Move("StandInit", stand_init, 1.80)
Sit = Move("Sit", sit, 10.20)
SitRelax = Move("SitRelax", sit_relax, 6.50)
Stand = Move("Stand", stand, 2.70)
StandZero = Move("StandZero", stand_zero, 1.60)
Crouch = Move("Crouch", crouch, 1.70)

Hello = Move("Hello", hello, 4.60)
WipeForehead = Move("WipeForehead", wipe_forehead, 4.80)
BlowKisses = Move("BlowKisses", blow_kisses, 4.70)
Bow = Move("Bow", bow, 4.30)
ComeOn = Move("ComeOn", come_on, 4.00)
Wave = Move("Wave", wave, 3.70)
Glory = Move("Glory", glory, 3.45)
Clap = Move("Clap", clap, 4.30)
Joy = Move("Joy", joy, 5.00)

ArmsOpening = Move("ArmsOpening", arms_opening, 4.30)
DiagonalLeft = Move("DiagonalLeft", diagonal_left, 2.95)
DiagonalRight = Move("DiagonalRight", diagonal_right, 2.95)
DoubleMovement = Move("DoubleMovement", double_movement, 3.70)
MoveBackward = Move("MoveBackward", move_backward, 4.00)
MoveForward = Move("MoveForward", move_forward, 4.00)
RightArm = Move("RightArm", right_arm, 9.19)
RotationLeftFoot = Move("RotationLeftFoot", rotation_left_foot, 6.10)
RotationRightFoot = Move("RotationRightFoot", rotation_right_foot, 6.10)
UnionArms = Move("UnionArms", union_arms, 9.10)

BirthdayDance = Move("BirthdayDance", birthday_dance, 5.0)
ArmDance = Move("ArmDance", arm_dance, 10.42)
DanceMove = Move("DanceMove", dance_move, 6.50)
TheRobot = Move("TheRobot", the_robot, 6.10)
StayingAlive = Move("StayingAlive", staying_alive, 5.90)
Rhythm = Move("Rhythm", rhythm, 3.20)
PulpFiction = Move("PulpFiction", pulp_fiction, 5.90)

print "2. Categorizing Moves (High/Mid/Low Impact)..."

SET_HIGH = [
    ArmDance, TheRobot, StayingAlive, PulpFiction,
    BirthdayDance, DanceMove, DoubleMovement, Rhythm
]

SET_MID = [
    Hello, Wave, ComeOn, BlowKisses, ArmsOpening,
    DiagonalLeft, DiagonalRight, MoveForward, MoveBackward,
    RightArm, UnionArms, Joy, Glory, Clap,
    RotationLeftFoot, RotationRightFoot
]

SET_LOW = [
    StandInit, Stand, StandZero, Sit, SitRelax,
    Crouch, WipeForehead, Bow
]

PARTITION_MAP = {}
ALL_MOVES = []

for m in SET_HIGH:
    PARTITION_MAP[m] = 1.5
for m in SET_MID:
    PARTITION_MAP[m] = 0.5
for m in SET_LOW:
    PARTITION_MAP[m] = 0.2

ALL_MOVES = SET_HIGH + SET_MID + SET_LOW

ADD_CONSTANT = 0.0
for m in ALL_MOVES:
    m.execution_time += ADD_CONSTANT

print "3. Building Connection Graph..."

StandInit.add_compatibles([Stand, StandZero, Sit])
Sit.add_compatibles([SitRelax, Stand, StandZero])
SitRelax.add_compatibles([Sit, Stand, StandZero])

hub_destinations = [
    StandZero, Sit, Crouch, Hello, WipeForehead,
    ArmsOpening, UnionArms, RightArm, MoveForward,
    MoveBackward, RotationLeftFoot, RotationRightFoot,
    DiagonalLeft, DiagonalRight, BirthdayDance,
    Wave, Clap, Glory, Joy, Bow, BlowKisses,
    ComeOn, Rhythm, TheRobot, StayingAlive,
    PulpFiction, ArmDance, DanceMove
]

Stand.add_compatibles(hub_destinations)
StandZero.add_compatibles(hub_destinations)
Crouch.add_compatibles([Stand, StandZero])

safe_gestures = [
    Stand, StandZero, WipeForehead, RightArm, UnionArms,
    ArmsOpening, Hello, Wave, Clap, Glory,
    Joy, Bow, BlowKisses, ComeOn, Rhythm
]

for m in safe_gestures:
    if m not in (Stand, StandZero):
        m.add_compatibles(safe_gestures)
        m.add_compatibles([
            DiagonalLeft, DiagonalRight,
            MoveForward, MoveBackward
        ])

ComeOn.add_compatibles([MoveForward, ArmsOpening])
Bow.add_compatibles([Stand, StandZero, Wave])

DiagonalLeft.add_compatibles([Stand, StandZero, RightArm, RotationLeftFoot])
DiagonalRight.add_compatibles([Stand, StandZero, RightArm, RotationRightFoot])
RotationLeftFoot.add_compatibles([Stand, StandZero, DiagonalLeft])
RotationRightFoot.add_compatibles([Stand, StandZero, DiagonalRight])
MoveForward.add_compatibles([Stand, StandZero, MoveBackward, ComeOn])
MoveBackward.add_compatibles([Stand, StandZero, MoveForward, Wave])

complex_moves = [
    BirthdayDance, DoubleMovement, TheRobot,
    StayingAlive, PulpFiction, ArmDance, DanceMove
]

for m in complex_moves:
    m.add_compatibles([Stand, StandZero])

DoubleMovement.add_compatibles([ArmsOpening, Joy])


def execute_choreography(moves):
    try:
        motion = ALProxy("ALMotion", IP, PORT)
        motion.wakeUp()

        for m in moves:
            m.execute()

        motion.rest()

    except Exception as e:
        print "Error: {}".format(e)


# ======================================================================
#   MAIN EXECUTION
# ======================================================================
if __name__ == "__main__":
    print "-" * 60
    print "--- STARTING A* CHOREOGRAPHY ENGINE ---"
    print "-" * 60

    MANDATORY_MOVES = [
        Sit, Stand, Hello, WipeForehead,
        SitRelax, StandZero
    ]

    print "MANDATORY REQUIREMENTS: ", [m.name for m in MANDATORY_MOVES]

    problem = DanceProblem(
        start_move=StandInit,
        goal_move=Crouch,
        mandatory_moves=MANDATORY_MOVES,
        all_moves_list=ALL_MOVES,
        partitions=PARTITION_MAP
    )

    print "\n[Status] Starting Search Algorithm (This may take a moment)..."
    start_t = time.time()
    solution = astar_search(problem)
    end_t = time.time()

    if solution:
        print "\n[Status] SOLUTION FOUND!"
        choreography = [n.state[0] for n in solution.path()]
        total_duration = solution.state[2]

        print "Search Time: {:.4f}s".format(end_t - start_t)
        print "Total Moves: {}".format(len(choreography))
        print "Total Duration: {:.2f}s (Limit: 120s)".format(total_duration)
        print "-" * 60

        print "{:<4} {:<25} {:<10} {:<10}".format("No.", "Move Name", "Time", "Category")
        print "-" * 60
        for i, move in enumerate(choreography):
            cat = (
                "HIGH" if move in SET_HIGH else
                "MID" if move in SET_MID else
                "LOW"
            )
            print "{:<4} {:<25} {:<10.2f} {:<10}".format(
                i + 1, move.name, move.execution_time, cat
            )
        print "-" * 60

        move_names = [m.name for m in choreography]
        missing = [m.name for m in MANDATORY_MOVES if m.name not in move_names]

        if not missing:
            print "VERIFICATION: All Mandatory Moves are present."
        else:
            print "VERIFICATION FAILED: Missing", missing

        if os.path.exists(SONG_FILENAME):
            print "\n[Music] Loading: {}".format(SONG_FILENAME)
            pygame.mixer.init()
            pygame.mixer.music.load(SONG_FILENAME)
            print "[Music] Playing..."
            pygame.mixer.music.play()
        else:
            print "\n[Music] WARNING: File '{}' not found. Dancing without music.".format(
                SONG_FILENAME
            )

        execute_choreography(choreography)

        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            print "[Music] Stopped."

    else:
        print "\n[Status] FAILURE: No plan found."
        print "Possible reasons: Time limit too short or incompatible mandatory moves."
