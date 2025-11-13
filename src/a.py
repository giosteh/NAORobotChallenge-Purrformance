import heapq
import time
from naoqi import ALProxy

# Import modules for robot movements.
# in the same directory, and each must contain a 'main(ip, port)' function.
try:
    import stand_init, stand_zero, stand, crouch, sit, sit_relax
    import rotation_right_foot, rotation_left_foot, rotation_handgun_object
    import arms_opening, union_arms, move_forward, move_backward
    import diagonal_left, diagonal_right
    #import happy_birthday, guitar, sprinkler_left, sprinkler_right, wipe_forehead, hello, workout, doublemovement, rotation_right_arm
except ImportError as e:
    print "WARNING: One or more movement modules failed to import (e.g., sit.py, hello.py)."
    print "Error: {}".format(e)
    # Define placeholder modules to prevent crash if running without NAO modules
    class PlaceholderMove:
        def main(self, ip, port): pass
    stand_init = stand_zero = stand = crouch = sit = sit_relax = PlaceholderMove()
    wipe_forehead = hello = workout = doublemovement = rotation_right_foot = PlaceholderMove()
    rotation_left_foot = rotation_handgun_object = rotation_right_arm = arms_opening = PlaceholderMove()
    union_arms = move_forward = move_backward = diagonal_left = diagonal_right = PlaceholderMove()
    sprinkler_left = sprinkler_right = happy_birthday = guitar = PlaceholderMove()


# --- ROBOT CONNECTION SETTINGS ---
# Change to your actual NAO robot IP if not using the local virtual robot
ip = "127.0.0.1"
port = 45459 # Default virtual robot port (NAOsim)


# --- 1. PROBLEM DEFINITION (The Move Graph) ---

ALL_POSITIONS = {
    "StandInit", "StandZero", "Stand", "Crouch", "Sit", "SitRelax",
    "WipeForehead", "Hello", "Workout", "DoubleMovement",
    "RotationRightFoot", "RotationLeftFoot", "RotationHandgunObject",
    "RotationRightArm", "ArmsOpening", "UnionArms", "MoveForward",
    "MoveBackward", "DiagonalLeft", "DiagonalRight", "SprinklerLeft",
    "SprinklerRight", "HappyBirthday", "Guitar"
}

COMPATIBILITIES = {
    # --- CORE POSITIONS ---
    "StandInit": {"StandZero", "Crouch", "Hello", "Workout", "DiagonalRight", "ArmsOpening"},
    "StandZero": {"Stand", "Crouch", "SitRelax", "DoubleMovement", "RotationRightFoot", "MoveBackward"},
    "Stand": {"StandZero", "WipeForehead", "DiagonalLeft", "RotationLeftFoot", "UnionArms", "RotationRightArm"},
    "Crouch": {"StandInit", "Sit", "WipeForehead", "UnionArms"},
    "Sit": {"Stand", "SitRelax", "DiagonalRight", "RotationHandgunObject", "ArmsOpening"},
    "SitRelax": {"StandZero", "WipeForehead", "Sit"},
    "WipeForehead": {"Hello", "Stand", "Guitar", "SprinklerLeft"},
    "Hello": {"StandInit", "WipeForehead", "HappyBirthday"},

    # --- INTERMEDIATE MOVES ---
    "RotationRightFoot": {"Stand", "RotationLeftFoot", "DiagonalRight"},
    "RotationLeftFoot": {"Stand", "RotationRightFoot", "DiagonalLeft"},
    "RotationHandgunObject": {"Stand", "RotationRightArm", "DoubleMovement"},
    "RotationRightArm": {"Stand", "ArmsOpening", "RotationHandgunObject"},
    "DoubleMovement": {"RotationRightFoot", "Stand", "RotationHandgunObject", "UnionArms"},
    "ArmsOpening": {"Stand", "UnionArms", "RotationRightArm"},
    "UnionArms": {"StandZero", "ArmsOpening", "MoveForward"},
    "MoveForward": {"Stand", "MoveBackward", "DiagonalRight"},
    "MoveBackward": {"Stand", "MoveForward", "DiagonalLeft"},
    "DiagonalLeft": {"StandZero", "RotationRightFoot", "RotationLeftFoot", "MoveBackward"},
    "DiagonalRight": {"StandZero", "RotationLeftFoot", "RotationRightFoot", "MoveForward"},

    # --- CRG MOVES ---
    "Workout": {"Stand", "SprinklerRight", "DoubleMovement"},
    "SprinklerLeft": {"Stand", "WipeForehead", "SprinklerRight"},
    "SprinklerRight": {"Stand", "SprinklerLeft", "Workout"},
    "HappyBirthday": {"StandInit", "StandZero", "ArmsOpening"},
    "Guitar": {"SitRelax", "WipeForehead", "RotationHandgunObject"},
}

# Estimated time cost for each transition (Time in seconds)
# You MUST verify these times using the simulator!
MOVE_TIMES = {
    ("StandInit", "StandZero"): 1.5, ("StandInit", "Crouch"): 2.0, ("StandInit", "Hello"): 1.0, ("StandInit", "Workout"): 3.0,
    ("StandInit", "DiagonalRight"): 1.5, ("StandInit", "ArmsOpening"): 2.0,
    ("StandZero", "Stand"): 0.5, ("StandZero", "Crouch"): 1.8, ("StandZero", "SitRelax"): 2.5, ("StandZero", "DoubleMovement"): 1.5,
    ("StandZero", "RotationRightFoot"): 1.2, ("StandZero", "MoveBackward"): 1.0,
    ("Stand", "StandZero"): 0.5, ("Stand", "WipeForehead"): 1.0, ("Stand", "DiagonalLeft"): 1.2, ("Stand", "RotationLeftFoot"): 1.2,
    ("Stand", "UnionArms"): 1.5, ("Stand", "RotationRightArm"): 1.0,
    ("Crouch", "StandInit"): 2.0, ("Crouch", "Sit"): 1.5, ("Crouch", "WipeForehead"): 3.0, ("Crouch", "UnionArms"): 2.5,
    ("Sit", "Stand"): 1.5, ("Sit", "SitRelax"): 1.0, ("Sit", "DiagonalRight"): 1.2, ("Sit", "RotationHandgunObject"): 2.0,
    ("Sit", "ArmsOpening"): 1.5,
    ("SitRelax", "StandZero"): 2.5, ("SitRelax", "WipeForehead"): 1.5, ("SitRelax", "Sit"): 1.0,
    ("WipeForehead", "Hello"): 1.0, ("WipeForehead", "Stand"): 1.0, ("WipeForehead", "Guitar"): 2.0, ("WipeForehead", "SprinklerLeft"): 1.5,
    ("Hello", "StandInit"): 1.0, ("Hello", "WipeForehead"): 1.0, ("Hello", "HappyBirthday"): 2.5,
    ("RotationRightFoot", "Stand"): 1.0, ("RotationRightFoot", "RotationLeftFoot"): 0.8, ("RotationRightFoot", "DiagonalRight"): 1.0,
    ("RotationLeftFoot", "Stand"): 1.0, ("RotationLeftFoot", "RotationRightFoot"): 0.8, ("RotationLeftFoot", "DiagonalLeft"): 1.0,
    ("RotationHandgunObject", "Stand"): 1.5, ("RotationHandgunObject", "RotationRightArm"): 1.0, ("RotationHandgunObject", "DoubleMovement"): 1.2,
    ("RotationRightArm", "Stand"): 1.0, ("RotationRightArm", "ArmsOpening"): 1.0, ("RotationRightArm", "RotationHandgunObject"): 1.0,
    ("DoubleMovement", "RotationRightFoot"): 1.5, ("DoubleMovement", "Stand"): 1.0, ("DoubleMovement", "RotationHandgunObject"): 1.2,
    ("DoubleMovement", "UnionArms"): 1.5,
    ("ArmsOpening", "Stand"): 1.0, ("ArmsOpening", "UnionArms"): 1.0, ("ArmsOpening", "RotationRightArm"): 1.0,
    ("UnionArms", "StandZero"): 1.5, ("UnionArms", "ArmsOpening"): 1.0, ("UnionArms", "MoveForward"): 1.2,
    ("MoveForward", "Stand"): 1.0, ("MoveForward", "MoveBackward"): 1.0, ("MoveForward", "DiagonalRight"): 1.0,
    ("MoveBackward", "Stand"): 1.0, ("MoveBackward", "MoveForward"): 1.0, ("MoveBackward", "DiagonalLeft"): 1.0,
    ("DiagonalLeft", "StandZero"): 1.2, ("DiagonalLeft", "RotationRightFoot"): 1.0, ("DiagonalLeft", "RotationLeftFoot"): 1.0,
    ("DiagonalLeft", "MoveBackward"): 1.0,
    ("DiagonalRight", "StandZero"): 1.2, ("DiagonalRight", "RotationLeftFoot"): 1.0, ("DiagonalRight", "RotationRightFoot"): 1.0,
    ("DiagonalRight", "MoveForward"): 1.0,
    ("Workout", "Stand"): 2.5, ("Workout", "SprinklerRight"): 1.5, ("Workout", "DoubleMovement"): 2.0,
    ("SprinklerLeft", "Stand"): 1.5, ("SprinklerLeft", "WipeForehead"): 1.5, ("SprinklerLeft", "SprinklerRight"): 0.8,
    ("SprinklerRight", "Stand"): 1.5, ("SprinklerRight", "SprinklerLeft"): 0.8, ("SprinklerRight", "Workout"): 1.5,
    ("HappyBirthday", "StandInit"): 2.5, ("HappyBirthday", "StandZero"): 2.0, ("HappyBirthday", "ArmsOpening"): 1.5,
    ("Guitar", "SitRelax"): 2.0, ("Guitar", "WipeForehead"): 2.0, ("Guitar", "RotationHandgunObject"): 1.5,
}

# --- 2. THE PLANNING ALGORITHM (A* Search) ---

def a_star_planner(start, goal):
    """Finds the path from start to goal with the minimum time cost."""

    # Priority queue: (f_cost, g_cost, current_node, path_list)
    # g_cost = actual time cost from start to current_node
    queue = [(0, 0, start, [start])]

    min_cost_to_node = {pos: float('inf') for pos in ALL_POSITIONS}
    min_cost_to_node[start] = 0

    while queue:
        f_cost, g_cost, current, path = heapq.heappop(queue)

        if current == goal:
            return path, g_cost

        for neighbor in COMPATIBILITIES.get(current, set()):
            transition_cost = MOVE_TIMES.get((current, neighbor), float('inf'))
            new_g_cost = g_cost + transition_cost

            if new_g_cost < min_cost_to_node[neighbor]:
                min_cost_to_node[neighbor] = new_g_cost
                new_path = path + [neighbor]
                # h(n) = 0 for shortest-time path (Dijkstra's equivalent)
                h_cost = 0
                f_cost = new_g_cost + h_cost

                heapq.heappush(queue, (f_cost, new_g_cost, neighbor, new_path))

    return None, 0 # No path found

# --- 3. CHOREOGRAPHY GENERATION (Algorithm A) ---

def generate_full_choreography(mandatory_goals):
    """Generates the full plan by chaining A* results between mandatory positions."""

    full_sequence = []
    total_time = 0.0

    if mandatory_goals[-1] != "Crouch":
        print "ERROR: The final mandatory position must be 'Crouch'."
        return [], 0

    current_start = "StandInit"
    all_segments = [current_start] + mandatory_goals

    for i in range(len(all_segments) - 1):
        start = all_segments[i]
        goal = all_segments[i+1]

        print "Planning segment {}: {} -> {}...".format(i + 1, start, goal)

        path_segment, time_segment = a_star_planner(start, goal)

        if path_segment is None:
            print "Could not find a path from {} to {}. Aborting.".format(start, goal)
            return [], 0

        # Append path, excluding the start position (if it's not the first segment)
        if i == 0:
            full_sequence.extend(path_segment)
        else:
            full_sequence.extend(path_segment[1:])

        total_time += time_segment
        current_start = goal

    return full_sequence, total_time

# --- 4. ROBOT EXECUTION ---

# Dictionary mapping planner names to imported execution modules
MOVE_MODULE_DICTIONARY = {
    "StandInit": stand_init, "StandZero": stand_zero, "Stand": stand,
    "Crouch": crouch, "Sit": sit, "SitRelax": sit_relax,
    "WipeForehead": wipe_forehead, "Hello": hello, "Workout": workout,
    "DoubleMovement": doublemovement, "RotationRightFoot": rotation_right_foot,
    "RotationLeftFoot": rotation_left_foot, "RotationHandgunObject": rotation_handgun_object,
    "RotationRightArm": rotation_right_arm, "ArmsOpening": arms_opening,
    "UnionArms": union_arms, "MoveForward": move_forward,
    "MoveBackward": move_backward, "DiagonalLeft": diagonal_left,
    "DiagonalRight": diagonal_right, "SprinklerLeft": sprinkler_left,
    "SprinklerRight": sprinkler_right, "HappyBirthday": happy_birthday,
    "Guitar": guitar
}

def execute_choreography(sequence):
    """Connects to and executes the sequence on the NAO robot/simulator."""
    print "\nAttempting to connect to NAO at {}:{}...".format(ip, port)

    try:
        # Connect to the ALMotion service
        motionProxy = ALProxy("ALMotion", ip, port)

        print "Connection successful. Waking up robot."
        motionProxy.wakeUp()
        time.sleep(1.0) # Give time for robot to stand

        for position_name in sequence:
            print "Executing move: {}".format(position_name)

            move_module = MOVE_MODULE_DICTIONARY.get(position_name)
            if move_module:
                # Call the main function of the external move script
                move_module.main(ip, port)
            else:
                print "WARNING: No execution module found for {}.".format(position_name)

        print "\nChoreography finished. Resting robot."
        motionProxy.rest()

    except Exception as e:
        print "\nERROR: Could not connect to or execute on the robot/simulator."
        print "Please ensure NAOsim is running with the correct IP/Port."
        print "Connection Error: {}".format(e)


# --- 5. MAIN EXECUTION ---

if __name__ == "__main__":

    # Mandatory positions in order (P1...P6 + Crouch)
    MANDATORY_GOALS = [
        "Sit",
        "WipeForehead",
        "Hello",
        "SitRelax",
        "Stand",
        "StandZero",
        "Crouch"
    ]

    print "--- NAO Choreography Planner (A* Search) ---"

    final_sequence, final_time = generate_full_choreography(MANDATORY_GOALS)

    print "\n--- Planning Results ---"
    if final_sequence:
        print "Plan found! Choreography meets all mandatory goals."
        print "Total time (T): {:.2f} seconds".format(final_time)
        print "Number of moves: {}".format(len(final_sequence) - 1)
        print "NAO SEQUENCE: {}".format(" -> ".join(final_sequence))

        # Check the 'at least 5 intermediate positions' constraint
        mandatory_set = set(["StandInit"] + MANDATORY_GOALS)
        intermediate_moves = [move for move in final_sequence if move not in mandatory_set]
        unique_intermediate_moves = set(intermediate_moves)

        print "\nUnique Intermediate Moves Used: {}".format(len(unique_intermediate_moves))
        status = 'SATISFIED' if len(unique_intermediate_moves) >= 5 else 'FAILED'
        print "Intermediate Moves Requirement (>= 5): {}".format(status)

        # --- ROBOT EXECUTION TRIGGER ---
        if raw_input("\nPress Enter to execute the dance on the NAO robot/simulator...") == "":
            execute_choreography(final_sequence)

    else:
        print "Choreography planning failed."