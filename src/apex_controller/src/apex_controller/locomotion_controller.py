#!/usr/bin/env python3

import rospy
import math
from std_msgs.msg import Float64
from apex_controller.inverse_kinematics import InverseKinematics, interpolate, KeyframeKinematics

class locomotion_controller(object):

    def __init__(self):

        self.rate = rospy.Rate(200)
        #self.gaits = [[100,750,160], [100,550,160], [-100,550,160], [-100,750,160],[-40,750,160],[40,750,160]]
        self.gaits = [[-60,750,160], [-60,650,160], [60,650,160], [60,750,160],[36,750,160],[12,750,160],[-12,750,160],[-36,750,160]]
        self.lastGaitIndex = 0
        self.lastElapsedTime = 0

        self.forward_factor = 0
        self.height_factor = 20
        self.rotation_factor = 0

        self.keyframesFrontLeftLeg = [[-50,800, 160], [-50,800, 160]]
        self.keyframesBackLeftLeg = [[-50,800, 160], [-50,800, 160]]
        self.keyframesFrontRightLeg = [[-50,800, 160], [-50,800, 160]]
        self.keyframesBackRightLeg = [[-50,800, 160], [-50,800, 160]]

        self.back_right_thigh = rospy.Publisher('/quad_robo/brt_position_controller/command', Float64, queue_size=10)
        self.back_right_leg = rospy.Publisher('/quad_robo/brl_position_controller/command', Float64, queue_size=10)
        self.back_right_shin = rospy.Publisher('/quad_robo/brs_position_controller/command', Float64, queue_size=10)

        self.back_left_thigh = rospy.Publisher('/quad_robo/blt_position_controller/command', Float64, queue_size=10) 
        self.back_left_leg = rospy.Publisher('/quad_robo/bll_position_controller/command', Float64, queue_size=10)
        self.back_left_shin = rospy.Publisher('/quad_robo/bls_position_controller/command', Float64, queue_size=10)

        self.front_left_thigh = rospy.Publisher('/quad_robo/flt_position_controller/command', Float64, queue_size=10) 
        self.front_left_leg = rospy.Publisher('/quad_robo/fll_position_controller/command', Float64, queue_size=10)
        self.front_left_shin = rospy.Publisher('/quad_robo/fls_position_controller/command', Float64, queue_size=10)

        self.front_right_thigh = rospy.Publisher('/quad_robo/frt_position_controller/command', Float64, queue_size=10)
        self.front_right_leg = rospy.Publisher('/quad_robo/frl_position_controller/command', Float64, queue_size=10)
        self.front_right_shin = rospy.Publisher('/quad_robo/frs_position_controller/command', Float64, queue_size=10)

        self.stand()

    def LocomotionRun(self, elapsedSequenceTime,sequenceTime):
        pass
    def UpdateMovementSequence(self, elapsedSequenceTime,sequenceTime):
        ratio = float((elapsedSequenceTime-self.lastElapsedTime)/sequenceTime)
        gaitIndex = int(ratio)
        if(self.lastGaitIndex != gaitIndex):
            self.ShiftKeyframe()

        angle = 45.0/180.0*math.pi
        x_rot = math.sin(angle) * self.rotation_factor
        z_rot = math.cos(angle) * self.rotation_factor

        angle = (45+self.gaits[gaitIndex][0])/180.0*math.pi
        x_rotFR = x_rot-math.sin(angle) * self.rotation_factor
        z_rotFR = z_rot-math.cos(angle) * self.rotation_factor

        self.keyframesFrontRightLeg[1] = self.gaits[gaitIndex].copy()
        self.keyframesFrontRightLeg[1][1] += self.height_factor
        self.keyframesFrontRightLeg[1][0] = self.keyframesFrontRightLeg[1][0]*self.forward_factor + x_rotFR
        self.keyframesFrontRightLeg[1][2] += z_rotFR 

        adjusted_index2 = gaitIndex + 2
        if(adjusted_index2 >= len(self.gaits)):
            adjusted_index2 -= len(self.gaits)

        angle = (45+self.gaits[adjusted_index2][0])/180.0*math.pi
        x_rotBR = x_rot-math.sin(angle) * self.rotation_factor
        z_rotBR = z_rot-math.cos(angle) * self.rotation_factor

        self.keyframesBackRightLeg[1] = self.gaits[adjusted_index2].copy()
        self.keyframesBackRightLeg[1][1] += self.height_factor
        self.keyframesBackRightLeg[1][0] = self.keyframesBackRightLeg[1][0]*self.forward_factor + x_rotBR
        self.keyframesBackRightLeg[1][2] += -z_rotBR 

        adjusted_index3 = gaitIndex + 4
        if(adjusted_index3 >= len(self.gaits)):
            adjusted_index3 -= len(self.gaits)

        angle = (45+self.gaits[adjusted_index3][0])/180.0*math.pi
        x_rotFL = x_rot-math.sin(angle) * self.rotation_factor
        z_rotFL = z_rot-math.cos(angle) * self.rotation_factor

        self.keyframesFrontLeftLeg[1] = self.gaits[adjusted_index3].copy()
        self.keyframesFrontLeftLeg[1][1] += self.height_factor
        self.keyframesFrontLeftLeg[1][0] = self.keyframesFrontLeftLeg[1][0]*self.forward_factor - x_rotFL
        self.keyframesFrontLeftLeg[1][2] += -z_rotFL

        
        adjusted_index4 = gaitIndex + 6
        if(adjusted_index4 >= len(self.gaits)):
            adjusted_index4 -= len(self.gaits)
        
        angle = (45+self.gaits[adjusted_index4][0])/180.0*math.pi
        x_rotBL = x_rot-math.sin(angle) * self.rotation_factor
        z_rotBL = z_rot-math.cos(angle) * self.rotation_factor

        self.keyframesBackLeftLeg[1] = self.gaits[adjusted_index4].copy()
        self.keyframesBackLeftLeg[1][1] += self.height_factor
        self.keyframesBackLeftLeg[1][0] = self.keyframesBackLeftLeg[1][0]*self.forward_factor - x_rotBL
        self.keyframesBackLeftLeg[1][0] += z_rotBL
        '''self.keyframesFrontRightLeg[1] = self.gaits[gaitIndex]
        self.keyframesBackLeftLeg[1] = self.gaits[gaitIndex]

        adjusted_index = gaitIndex + int(len(self.gaits)/2)
        if(adjusted_index >= len(self.gaits)):
            adjusted_index -= len(self.gaits)
        self.keyframesFrontLeftLeg[1] = self.gaits[adjusted_index]
        self.keyframesBackRightLeg[1] = self.gaits[adjusted_index]'''
        
        if(adjusted_index4 == 1 or adjusted_index3 == 1 or adjusted_index4 == 2 or adjusted_index3 == 2):
            self.keyframesBackLeftLeg[1][2] += 35
            self.keyframesFrontLeftLeg[1][2] += 35
            self.keyframesBackRightLeg[1][2] -= 35
            self.keyframesFrontRightLeg[1][2] -= 35
        else:
            self.keyframesBackLeftLeg[1][2] += 35
            self.keyframesFrontLeftLeg[1][2] += 35
            self.keyframesBackRightLeg[1][2] -= 35
            self.keyframesFrontRightLeg[1][2] -= 35
        ratio = ratio - gaitIndex
        self.UpdateLegsPosition(ratio)

        if(gaitIndex >= len(self.gaits) - 1):
            self.lastElapsedTime = elapsedSequenceTime
        self.lastGaitIndex = gaitIndex

        self.rate.sleep()
    
    def UpdateLegsPosition(self, ratio):
        key1 = self.keyframesFrontLeftLeg[0]
        key2 = self.keyframesFrontLeftLeg[1]

        foot, leg, shoulder = KeyframeKinematics(key1, key2, ratio)
        self.moveFrontLeftLeg(foot, leg, shoulder)

        key1 = self.keyframesBackLeftLeg[0]
        key2 = self.keyframesBackLeftLeg[1]

        foot, leg, shoulder = KeyframeKinematics(key1, key2, ratio)
        self.moveBackLeftLeg(foot, leg, shoulder)

        key1 = self.keyframesFrontRightLeg[0]
        key2 = self.keyframesFrontRightLeg[1]

        foot, leg, shoulder = KeyframeKinematics(key1, key2, ratio)
        self.moveFrontRightLeg(foot, leg, shoulder)

        key1 = self.keyframesBackRightLeg[0]
        key2 = self.keyframesBackRightLeg[1]

        foot, leg, shoulder = KeyframeKinematics(key1, key2, ratio)
        self.moveBackRightLeg(foot, leg, shoulder)
    
    def ShiftKeyframe(self):
        self.keyframesFrontLeftLeg[0] = self.keyframesFrontLeftLeg[1]
        self.keyframesFrontRightLeg[0] = self.keyframesFrontRightLeg[1]
        self.keyframesBackLeftLeg[0] = self.keyframesBackLeftLeg[1]
        self.keyframesBackRightLeg[0] = self.keyframesBackRightLeg[1]
    
    def stand(self):
        self.back_right_thigh.publish(1.57)
        self.back_right_leg.publish(1.57+0.7)
        self.back_right_shin.publish(3.14-1.5)
        self.front_right_thigh.publish(1.57)
        self.front_right_leg.publish(1.57+0.7)
        self.front_right_shin.publish(3.14-1.5) 
        self.back_left_thigh.publish(1.57)
        self.back_left_leg.publish(1.57-0.7) 
        self.back_left_shin.publish(0+1.5)
        self.front_left_thigh.publish(1.57)
        self.front_left_leg.publish(1.57-0.7)
        self.front_left_shin.publish(0+1.5)
        self.rate.sleep()

    def land(self):
        self.back_right_thigh.publish(1.57)
        self.back_right_leg.publish(1.57+0.7)
        self.back_right_shin.publish(3.14-2.0)
        self.front_right_thigh.publish(1.57)
        self.front_right_leg.publish(1.57+0.7)
        self.front_right_shin.publish(3.14-2.0) 
        self.back_left_thigh.publish(1.57)
        self.back_left_leg.publish(1.57-0.7) 
        self.back_left_shin.publish(0+2.0)
        self.front_left_thigh.publish(1.57)
        self.front_left_leg.publish(1.57-0.7)
        self.front_left_shin.publish(0+2.0)
        '''self.back_right_thigh.publish(1.57)
        self.back_right_leg.publish(1.57)
        self.back_right_shin.publish(1.57)
        self.front_right_thigh.publish(1.57)
        self.front_right_leg.publish(1.57)
        self.front_right_shin.publish(1.57) 
        self.back_left_thigh.publish(1.57)
        self.back_left_leg.publish(1.57) 
        self.back_left_shin.publish(1.57)
        self.front_left_thigh.publish(1.57)
        self.front_left_leg.publish(1.57)
        self.front_left_shin.publish(1.57)'''
        self.rate.sleep()

    def up(self, angleStep):
        self.back_right_thigh.publish(1.57)
        self.back_right_leg.publish(1.57+0.7)
        self.back_right_shin.publish(3.14-angleStep)
        self.front_right_thigh.publish(1.57)
        self.front_right_leg.publish(1.57+0.7)
        self.front_right_shin.publish(3.14-angleStep) 
        self.back_left_thigh.publish(1.57)
        self.back_left_leg.publish(1.57-0.7) 
        self.back_left_shin.publish(0+angleStep)
        self.front_left_thigh.publish(1.57)
        self.front_left_leg.publish(1.57-0.7)
        self.front_left_shin.publish(0+angleStep)
        self.rate.sleep()
    
    def moveFrontLeftLeg(self, foot, leg, shoulder):
        self.front_left_thigh.publish(3.14-shoulder)
        self.front_left_leg.publish(3.14-(1.57+leg))
        self.front_left_shin.publish(3.14-foot)
        #print([3.14-foot,3.14-(1.57+leg), 3.14-shoulder])
    
    def moveBackLeftLeg(self, foot, leg, shoulder):
        self.back_left_thigh.publish(3.14-shoulder)
        self.back_left_leg.publish(3.14-(1.57+leg))
        self.back_left_shin.publish(3.14-foot)
        #print([3.14-foot,3.14-(1.57+leg), 3.14-shoulder])

    def moveFrontRightLeg(self, foot, leg, shoulder):
        self.front_right_thigh.publish(shoulder)
        self.front_right_leg.publish(3.14-(1.57-leg))
        self.front_right_shin.publish(foot)
        #print([foot,3.14-(1.57-leg), shoulder])

    def moveBackRightLeg(self, foot, leg, shoulder):
        self.back_right_thigh.publish(shoulder)
        self.back_right_leg.publish(3.14-(1.57-leg))
        self.back_right_shin.publish(foot)
        #print([foot,3.14-(1.57-leg), shoulder])