#!/usr/bin/env python3

import rospy
import math
import matplotlib.pyplot as plt
from std_msgs.msg import Float64
from apex_controller.inverse_kinematics import InverseKinematics,ForwardKinematics2D, interpolate, KeyframeKinematics

class locomotion_controller(object):

    def __init__(self):

        self.rate = rospy.Rate(200)
        #self.gaits = [[100,750,160], [100,550,160], [-100,550,160], [-100,750,160],[-40,750,160],[40,750,160]]
        self.gaits = [[-60,750,160], [-60,650,160], [60,650,160], [60,750,160],[36,750,160],[12,750,160],[-12,750,160],[-36,750,160]]
        self.trotGait = [[100,750,160], [100,650,160], [-100,650,160], [-100,750,160],[-40,750,160],[40,750,160]]
        self.lastGaitIndex = 0
        self.lastElapsedTime = 0

        self.forward_factor = 1.2
        self.height_factor = -50
        self.rotation_factor = 0
        self.lean = 0
        self.sidelean = 0

        self.keyframesFrontLeftLeg = [[-50,800, 160], [-50,800, 160]]
        self.keyframesBackLeftLeg = [[-50,800, 160], [-50,800, 160]]
        self.keyframesFrontRightLeg = [[-50,800, 160], [-50,800, 160]]
        self.keyframesBackRightLeg = [[-50,800, 160], [-50,800, 160]]

        self.keyframesFrontLeftLegHist = [[],[]]
        self.keyframesFrontRightLegHist = [[],[]]
        self.keyframesBackLeftLegHist = [[],[]]
        self.keyframesBackRightLegHist = [[],[]]
        self.jointsPositionFL = [[0,0],[0,0]]
        self.jointsPositionFR = [[0,0],[0,0]]
        self.jointsPositionBL = [[0,0],[0,0]]
        self.jointsPositionBR = [[0,0],[0,0]]

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

        self.cretaGaitGraphPlot()

    def cretaGaitGraphPlot(self):
        plt.ion() # Turn on interactive mode

        self.fig, self.ax = plt.subplots(2,2)
        self.FrontLeftLegPlot, = self.ax[0][0].plot(self.keyframesFrontLeftLegHist[0], self.keyframesFrontLeftLegHist[1])
        self.FrontRightLegPlot, = self.ax[0][1].plot(self.keyframesFrontRightLegHist[0], self.keyframesFrontRightLegHist[1])
        self.BackLeftLegPlot, = self.ax[1][0].plot(self.keyframesBackLeftLegHist[0], self.keyframesBackLeftLegHist[1])
        self.BackRightLegPlot, = self.ax[1][1].plot(self.keyframesBackRightLegHist[0], self.keyframesBackRightLegHist[1])
    
    def setPlotJointsPosition(self, foot,leg, legKeyFramesHist, legJointsPosition):
        jointsPosition = ForwardKinematics2D(foot,leg)
        legKeyFramesHist[0].append(jointsPosition[0][0])
        legKeyFramesHist[1].append(jointsPosition[1][0])
        legJointsPosition[0][0] = jointsPosition[0][1]
        legJointsPosition[1][0] = jointsPosition[1][1]
    def gaitGraph(self):
        #self.line.set_data(self.keyframesFrontLeftLegHist[0], self.keyframesFrontLeftLegHist[1])
        self.FrontLeftLegPlot.set_data(self.keyframesFrontLeftLegHist[0] + self.jointsPositionFL[0], self.keyframesFrontLeftLegHist[1] + self.jointsPositionFL[1])
        self.ax[0][0].relim()
        self.ax[0][0].autoscale_view()

        self.FrontRightLegPlot.set_data(self.keyframesFrontRightLegHist[0] + self.jointsPositionFR[0], self.keyframesFrontRightLegHist[1] + self.jointsPositionFR[1])
        self.ax[0][1].relim()
        self.ax[0][1].autoscale_view()

        self.BackLeftLegPlot.set_data(self.keyframesBackLeftLegHist[0] + self.jointsPositionBL[0], self.keyframesBackLeftLegHist[1] + self.jointsPositionBL[1])
        self.ax[1][0].relim()
        self.ax[1][0].autoscale_view()

        self.BackRightLegPlot.set_data(self.keyframesBackRightLegHist[0] + self.jointsPositionBR[0], self.keyframesBackRightLegHist[1] + self.jointsPositionBR[1])
        self.ax[1][1].relim()
        self.ax[1][1].autoscale_view()

        plt.draw()
        plt.pause(0.01) # Pause

    def clearGaitGraph(self):
        self.keyframesFrontLeftLegHist.clear()
        self.keyframesFrontRightLegHist.clear()
        self.keyframesBackLeftLegHist.clear()
        self.keyframesBackRightLegHist.clear()
        self.keyframesFrontLeftLegHist = [[],[]]
        self.keyframesFrontRightLegHist = [[],[]]
        self.keyframesBackLeftLegHist = [[],[]]
        self.keyframesBackRightLegHist = [[],[]]

    def TrotGaitMovement(self, velMsg, elapsedSequenceTime,sequenceTime):
        if velMsg != None:
            if velMsg.linear.x > 0:
                self.forward_factor = 1
            elif velMsg.linear.x < 0:
                self.forward_factor = -1
            else:
                self.forward_factor = 0
            
            if velMsg.angular.z > 0:
                self.rotation_factor = 15
            elif velMsg.angular.z < 0:
                self.rotation_factor = -15
            else:
                self.rotation_factor = 0

        ratio = float((elapsedSequenceTime-self.lastElapsedTime)/sequenceTime)
        if(ratio >= len(self.trotGait)):
            ratio -= len(self.trotGait)
            self.lastElapsedTime += len(self.trotGait)*sequenceTime
            self.clearGaitGraph()

        gaitIndex = int(ratio)
        ratio = ratio - gaitIndex

        if(self.lastGaitIndex != gaitIndex):
            self.ShiftKeyframe()
            self.lastGaitIndex = gaitIndex

        angle = 45.0/180.0*math.pi
        x_rot = math.sin(angle) * self.rotation_factor
        z_rot = math.cos(angle) * self.rotation_factor

        angle = (45+self.trotGait[gaitIndex][0])/180.0*math.pi
        x_rotFR = x_rot-math.sin(angle) * self.rotation_factor
        z_rotFR = z_rot-math.cos(angle) * self.rotation_factor

        self.keyframesFrontRightLeg[1] = self.trotGait[gaitIndex].copy()
        self.keyframesFrontRightLeg[1][1] += self.height_factor + self.lean
        self.keyframesFrontRightLeg[1][0] = self.keyframesFrontRightLeg[1][0]*self.forward_factor + x_rotFR
        self.keyframesFrontRightLeg[1][2] += z_rotFR + self.sidelean

        self.keyframesBackLeftLeg[1] = self.trotGait[gaitIndex].copy()
        self.keyframesBackLeftLeg[1][1] += self.height_factor - self.lean
        self.keyframesBackLeftLeg[1][0] = self.keyframesBackLeftLeg[1][0]*self.forward_factor - x_rotFR
        self.keyframesBackLeftLeg[1][2] += z_rotFR - self.sidelean

        adjusted_index = gaitIndex + int(len(self.trotGait)/2)
        if(adjusted_index >= len(self.trotGait)):
            adjusted_index -= len(self.trotGait)
        
        angle = (45+self.trotGait[adjusted_index][0])/180.0*math.pi
        x_rotFL = x_rot-math.sin(angle) * self.rotation_factor
        z_rotFL = z_rot-math.cos(angle) * self.rotation_factor

        self.keyframesFrontLeftLeg[1] = self.trotGait[adjusted_index].copy()
        self.keyframesFrontLeftLeg[1][1] += self.height_factor + self.lean
        self.keyframesFrontLeftLeg[1][0] = self.keyframesFrontLeftLeg[1][0]*self.forward_factor - x_rotFL
        self.keyframesFrontLeftLeg[1][2] += -z_rotFL - self.sidelean

        self.keyframesBackRightLeg[1] = self.trotGait[adjusted_index].copy()
        self.keyframesBackRightLeg[1][1] += self.height_factor - self.lean
        self.keyframesBackRightLeg[1][0] = self.keyframesBackRightLeg[1][0]*self.forward_factor + x_rotFL
        self.keyframesBackRightLeg[1][2] += -z_rotFL + self.sidelean

        self.UpdateLegsPosition(ratio)

        self.rate.sleep()

    def UpdateMovementSequence(self,velMsg, elapsedSequenceTime,sequenceTime):        
        if velMsg != None:
            if velMsg.linear.x > 0:
                self.forward_factor = 1
            elif velMsg.linear.x < 0:
                self.forward_factor = -1
            else:
                self.forward_factor = 0
            
            if velMsg.angular.z > 0:
                self.rotation_factor = 15
            elif velMsg.angular.z < 0:
                self.rotation_factor = -15
            else:
                self.rotation_factor = 0

        ratio = float((elapsedSequenceTime-self.lastElapsedTime)/sequenceTime)
        if(ratio >= len(self.gaits)):
            ratio -= len(self.gaits)
            self.lastElapsedTime += len(self.gaits)*sequenceTime
            self.clearGaitGraph()

        gaitIndex = int(ratio)
        ratio = ratio - gaitIndex

        if(self.lastGaitIndex != gaitIndex):
            self.ShiftKeyframe()
            self.lastGaitIndex = gaitIndex

        angle = 45.0/180.0*math.pi
        x_rot = math.sin(angle) * self.rotation_factor
        z_rot = math.cos(angle) * self.rotation_factor

        angle = (45+self.gaits[gaitIndex][0])/180.0*math.pi
        x_rotFR = x_rot-math.sin(angle) * self.rotation_factor
        z_rotFR = z_rot-math.cos(angle) * self.rotation_factor

        self.keyframesFrontRightLeg[1] = self.gaits[gaitIndex].copy()
        self.keyframesFrontRightLeg[1][1] += self.height_factor + self.lean
        self.keyframesFrontRightLeg[1][0] = self.keyframesFrontRightLeg[1][0]*self.forward_factor + x_rotFR
        self.keyframesFrontRightLeg[1][2] += z_rotFR + self.sidelean

        adjusted_index2 = gaitIndex + 2
        if(adjusted_index2 >= len(self.gaits)):
            adjusted_index2 -= len(self.gaits)

        angle = (45+self.gaits[adjusted_index2][0])/180.0*math.pi
        x_rotBR = x_rot-math.sin(angle) * self.rotation_factor
        z_rotBR = z_rot-math.cos(angle) * self.rotation_factor

        self.keyframesBackRightLeg[1] = self.gaits[adjusted_index2].copy()
        self.keyframesBackRightLeg[1][1] += self.height_factor - self.lean
        self.keyframesBackRightLeg[1][0] = self.keyframesBackRightLeg[1][0]*self.forward_factor + x_rotBR
        self.keyframesBackRightLeg[1][2] += -z_rotBR + self.sidelean

        adjusted_index3 = gaitIndex + 4
        if(adjusted_index3 >= len(self.gaits)):
            adjusted_index3 -= len(self.gaits)

        angle = (45+self.gaits[adjusted_index3][0])/180.0*math.pi
        x_rotFL = x_rot-math.sin(angle) * self.rotation_factor
        z_rotFL = z_rot-math.cos(angle) * self.rotation_factor

        self.keyframesFrontLeftLeg[1] = self.gaits[adjusted_index3].copy()
        self.keyframesFrontLeftLeg[1][1] += self.height_factor + self.lean
        self.keyframesFrontLeftLeg[1][0] = self.keyframesFrontLeftLeg[1][0]*self.forward_factor - x_rotFL
        self.keyframesFrontLeftLeg[1][2] += -z_rotFL - self.sidelean
        
        adjusted_index4 = gaitIndex + 6
        if(adjusted_index4 >= len(self.gaits)):
            adjusted_index4 -= len(self.gaits)
        
        angle = (45+self.gaits[adjusted_index4][0])/180.0*math.pi
        x_rotBL = x_rot-math.sin(angle) * self.rotation_factor
        z_rotBL = z_rot-math.cos(angle) * self.rotation_factor

        self.keyframesBackLeftLeg[1] = self.gaits[adjusted_index4].copy()
        self.keyframesBackLeftLeg[1][1] += self.height_factor - self.lean
        self.keyframesBackLeftLeg[1][0] = self.keyframesBackLeftLeg[1][0]*self.forward_factor - x_rotBL
        self.keyframesBackLeftLeg[1][2] += z_rotBL - self.sidelean
        
        if(adjusted_index4 == 1 or adjusted_index3 == 1 or adjusted_index4 == 2 or adjusted_index3 == 2):
            self.keyframesBackLeftLeg[1][2] -= 30
            self.keyframesFrontLeftLeg[1][2] -= 30
            self.keyframesBackRightLeg[1][2] += 30
            self.keyframesFrontRightLeg[1][2] += 30
        else:
            self.keyframesBackLeftLeg[1][2] += 30
            self.keyframesFrontLeftLeg[1][2] += 30
            self.keyframesBackRightLeg[1][2] -= 30
            self.keyframesFrontRightLeg[1][2] -= 30

        self.UpdateLegsPosition(ratio)

        self.rate.sleep()
    
    def UpdateLegsPosition(self, ratio):
        key1 = self.keyframesFrontLeftLeg[0]
        key2 = self.keyframesFrontLeftLeg[1]

        foot, leg, shoulder = KeyframeKinematics(key1, key2, ratio)
        self.setPlotJointsPosition(foot,leg,self.keyframesFrontLeftLegHist,self.jointsPositionFL)

        self.moveFrontLeftLeg(foot, leg, shoulder)

        key1 = self.keyframesBackLeftLeg[0]
        key2 = self.keyframesBackLeftLeg[1]

        foot, leg, shoulder = KeyframeKinematics(key1, key2, ratio)
        self.setPlotJointsPosition(foot,leg,self.keyframesBackLeftLegHist,self.jointsPositionBL)

        self.moveBackLeftLeg(foot, leg, shoulder)

        key1 = self.keyframesFrontRightLeg[0]
        key2 = self.keyframesFrontRightLeg[1]

        foot, leg, shoulder = KeyframeKinematics(key1, key2, ratio)
        self.setPlotJointsPosition(foot,leg,self.keyframesFrontRightLegHist,self.jointsPositionFR)

        self.moveFrontRightLeg(foot, leg, shoulder)

        key1 = self.keyframesBackRightLeg[0]
        key2 = self.keyframesBackRightLeg[1]

        foot, leg, shoulder = KeyframeKinematics(key1, key2, ratio)
        self.setPlotJointsPosition(foot,leg,self.keyframesBackRightLegHist,self.jointsPositionBR)

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