"""
Interface which provides methods to access and move the NAO robot.
"""

from naoqi import ALProxy


class NAOInterface:
    def __init__(self, ip="127.0.0.1", port=9559):
        self.motion = ALProxy("ALMotion", ip, port)
        self.posture = ALProxy("ALRobotPosture", ip, port)

    def go_to_posture(self, posture_name, speed=0.5):
        self.posture.goToPosture(posture_name, speed)

    def set_angles(self, names, angles, fraction_max_speed=0.2):
        self.motion.setAngles(names, angles, fraction_max_speed)

    def rest(self):
        self.motion.rest()

