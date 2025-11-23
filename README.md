NAO Robot Choreography Generator using A* Search

This project utilizes Artificial Intelligence (the A* Search Algorithm) to generate an optimal dance choreography for a NAO robot. The system calculates a sequence of moves that fits within a specific song duration, ensures mandatory moves are performed, and optimizes for aesthetic variety using a custom cost function.

---Group Members---

Group Name: Purrformance

Giovanni Stea - giovanni.stea@studio.unibo.it

Şimal Yücel - simal.yucel@studio.unibo.it



---Project Repository---

https://github.com/giosteh/NAORobotChallenge-Purrformance.git

---Requirements & Libraries---

!!!This project requires Python 2.7 because the naoqi SDK is not compatible with Python 3.

Required Modules:

-naoqi (Aldebaran SDK)

-pygame (Install via: pip install pygame)

-aima-python:

  The project uses the search algorithms from the aimacode/aima-python repository.
  
  Ensure the aima folder is located in the root directory of this project.

---Project Structure---

dance.py: The entry point. Defines the A* problem, heuristics, and cost functions.

moves.py: Contains the pre-programmed motion primitives for the NAO robot.

aima/: The folder containing the AIMA search library.

passin_me_by.mp3: The audio file used for the choreography.

---How to Run on Simulated NAO---

-Launch Choregraphe:
Open the Choregraphe application on your computer.

-Start the Virtual Robot:
In Choregraphe, go to Connection > Connect to virtual robot.
Note the Port number displayed in the connection window.

-Audio Setup:
Ensure a file named passin_me_by.mp3 is present in the same directory as the script.

-Run the Script:
Open your terminal/command prompt and run:
python dance.py port_number
the port_number should be your local robot's port number (ex. 34561)


