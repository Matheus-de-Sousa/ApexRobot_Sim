#!/usr/bin/env python3

import rospy
import numpy as np
from geometry_msgs.msg import Twist
from apex_controller.locomotion_controller import locomotion_controller

velMsg = None
def velCallback(msg):
    global velMsg 
    velMsg = msg
if __name__ == "__main__":
    rospy.init_node("apex_controller_node")
    apex_controller = locomotion_controller()
    vel_sub = rospy.Subscriber("apex_controller/cmd_vel", Twist, velCallback)

    '''style.use('fivethirtyeight')
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)

    ani = animation.FuncAnimation(fig, apex_controller.gaitGraph, interval=1000, fargs=(ax1,))
    plt.show(block = False)'''

    start_time = 0
    while not start_time:
        start_time = rospy.Time.now()
    step = False
    while not rospy.is_shutdown():
        currentTime = rospy.Time.now()
        deltaT = currentTime - start_time
        if velMsg != None:
            print(f"({velMsg.linear.x},{velMsg.angular.z})")
        #apex_controller.UpdateMovementSequence(velMsg, deltaT.to_sec(), 1)
        apex_controller.TrotGaitMovement(velMsg, deltaT.to_sec(), 1)
        apex_controller.gaitGraph()
        '''if step:
            apex_controller.UpdateMovementSequence(deltaT.to_sec(), 1)
        else:
            apex_controller.UpdateMovementSequence(1-deltaT.to_sec(), 1)
        if(deltaT > rospy.Duration(1)):
            start_time = rospy.Time.now()
            step = not step'''
        '''apex_controller.stand()
        rospy.sleep(4)
        apex_controller.moveFrontRighttLeg(100, 800, 300)
        rospy.sleep(4)'''