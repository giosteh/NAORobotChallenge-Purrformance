# NAO Robot Choreography Generator using A* Search

This project uses Artificial Intelligence (the A* Search Algorithm) to generate an optimal dance choreography for a NAO robot. The system calculates a sequence of moves that fits within the song duration, ensures mandatory moves are included, and optimizes for aesthetic variety using a custom cost function.

---

## Group Members

**Group Name:** Purrformance

- Giovanni Stea – giovanni.stea@studio.unibo.it  
- Şimal Yücel – simal.yucel@studio.unibo.it

---

## Project Repository

https://github.com/giosteh/NAORobotChallenge-Purrformance

---

## Requirements & Libraries

IMPORTANT: This project requires **Python 2.7** because the **naoqi SDK is not compatible with Python 3**.

Required modules:
- naoqi (Aldebaran SDK)
- pygame
- aima-python (included in the project under the “aima” folder)

To install pygame:
pip install pygame

---

## Project Structure

LICENSE  
README.md  
presentation.pdf  
src/  
• dance.py — main script containing A*, cost function, and choreography execution  
• moves/ — folder with NAO motion primitives  
• aima/ — AIMA search library  
• passin_me_by.mp3 — audio file used for choreography  
• requirements.txt — dependency list

---

## How to Run on a Simulated NAO Robot

1. Launch the Choregraphe application.  
2. Connect to a virtual robot:  
   Connection → Connect to virtual robot.  
   Note the port number shown (e.g., 51346 or 37995).  
3. Ensure the file “passin_me_by.mp3” is inside the src folder.  
4. Open a terminal, navigate to the src folder, and run the script using the port number:  
   python dance.py <port_number>  
   Example:  
   python dance.py 34561
