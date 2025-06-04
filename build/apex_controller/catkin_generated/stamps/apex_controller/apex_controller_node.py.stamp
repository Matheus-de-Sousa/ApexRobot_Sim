#!/usr/bin/env python3

import rospy
import numpy as np

from apex_controller.locomotion_controller import locomotion_controller

if __name__ == "__main__":
    rospy.init_node("apex_controller_node")
    apex_controller = locomotion_controller()
    rospy.sleep(4)

    while not rospy.is_shutdown():
        apex_controller.stand()
        rospy.sleep(4)
        apex_controller.moveFrontRighttLeg(100, 800, 300)
        rospy.sleep(4)