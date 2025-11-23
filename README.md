NAO Robot Choreography Generator using A* Search

This project utilizes Artificial Intelligence (the A* Search Algorithm) to generate an optimal dance choreography for a NAO robot. The system calculates a sequence of moves that fits within a specific song duration, ensures mandatory moves are performed, and optimizes for aesthetic variety using a custom cost function.

---Group Members---

Group Name: Purrformance

Giovanni Stea - giovanni.stea@studio.unibo.it

Şimal Yücel - simal.yucel@studio.unibo.it

---Project Repository---

https://github.com/giosteh/NAORobotChallenge-Purrformance

---Requirements & Libraries---

!!!IMPORTANT: This project requires Python 2.7 because the naoqi SDK is not compatible with Python 3.

Required Modules:

-naoqi (Aldebaran SDK)

-pygame (Install via: pip install pygame)

aima-python (The project uses search algorithms from the aimacode/aima-python repository. The aima folder is included in the source code.)

---Project Structure---

* **LICENSE**: The license file for the project.
* **README.md**: This documentation file.
* **presentation.pdf**: The slides explaining the project logic.
* **src/**: The main source code directory containing:
    * **dance.py**: The main entry point script. It contains the A* algorithm, the cost function logic, and the choreography execution.
    * **moves/**: A folder containing the pre-programmed motion primitives for the NAO robot.
    * **aima/**: A folder containing the AIMA search library used for pathfinding.
    * **passin_me_by.mp3**: The audio file used for the choreography.
    * **requirements.txt**: A text file listing the necessary Python dependencies.


---How to Run on Simulated NAO---

-Launch Choregraphe:
Open the Choregraphe application on your computer.

-Start the Virtual Robot:
In Choregraphe, go to Connection > Connect to virtual robot.
Note the Port number displayed in the connection window (e.g., 51346 or 37995).

-Audio Setup:
Ensure the file passin_me_by.mp3 is located in the src folder alongside the script.

-Run the Script:
Open your terminal, navigate to the src folder, and run the script passing the port number as an argument:

python dance.py <port_number>

Example:

python dance.py 34561

