"""
An example that shows how to draw tracked skeletons
It also use joint filtering
"""

import itertools
import pygame
import pygame.color
import pykinect
import time
from time import sleep
import re
import math

from pygame.color import THECOLORS
from pykinect import nui
from pykinect.nui import JointId
from pykinect.nui import SkeletonTrackingState
from pykinect.nui.structs import TransformSmoothParameters

KINECTEVENT = pygame.USEREVENT
WINDOW_SIZE = 640, 480

SKELETON_COLORS = [THECOLORS["red"], 
                   THECOLORS["blue"], 
                   THECOLORS["green"], 
                   THECOLORS["orange"], 
                   THECOLORS["purple"], 
                   THECOLORS["yellow"], 
                   THECOLORS["violet"]]

LEFT_ARM = (JointId.ShoulderCenter, 
            JointId.ShoulderLeft, 
            JointId.ElbowLeft, 
            JointId.WristLeft, 
            JointId.HandLeft)
RIGHT_ARM = (JointId.ShoulderCenter, 
             JointId.ShoulderRight, 
             JointId.ElbowRight, 
             JointId.WristRight, 
             JointId.HandRight)
LEFT_LEG = (JointId.HipCenter, 
            JointId.HipLeft, 
            JointId.KneeLeft, 
            JointId.AnkleLeft, 
            JointId.FootLeft)
RIGHT_LEG = (JointId.HipCenter, 
             JointId.HipRight, 
             JointId.KneeRight, 
             JointId.AnkleRight, 
             JointId.FootRight)
SPINE = (JointId.HipCenter, 
         JointId.Spine, 
         JointId.ShoulderCenter, 
         JointId.Head)

SMOOTH_PARAMS_SMOOTHING = 0.7
SMOOTH_PARAMS_CORRECTION = 0.4
SMOOTH_PARAMS_PREDICTION = 0.7
SMOOTH_PARAMS_JITTER_RADIUS = 0.1
SMOOTH_PARAMS_MAX_DEVIATION_RADIUS = 0.1
SMOOTH_PARAMS = TransformSmoothParameters(SMOOTH_PARAMS_SMOOTHING,
                                          SMOOTH_PARAMS_CORRECTION,
                                          SMOOTH_PARAMS_PREDICTION,
                                          SMOOTH_PARAMS_JITTER_RADIUS,
                                          SMOOTH_PARAMS_MAX_DEVIATION_RADIUS)

skeleton_to_depth_image = nui.SkeletonEngine.skeleton_to_depth_image

def post_frame(frame):
    """Get skeleton events from the Kinect device and post them into the PyGame
    event queue."""
    try:
        pygame.event.post(
            pygame.event.Event(KINECTEVENT, skeleton_frame=frame)
        )
    except:
        # event queue full
        pass

def draw_skeleton_data(dispInfo, screen, pSkelton, index, positions, width = 4):
    start = pSkelton.SkeletonPositions[positions[0]]
       
    for position in itertools.islice(positions, 1, None):
        next = pSkelton.SkeletonPositions[position.value]
        
        curstart = skeleton_to_depth_image(start, dispInfo.current_w, dispInfo.current_h) 
        curend = skeleton_to_depth_image(next, dispInfo.current_w, dispInfo.current_h)

        pygame.draw.line(screen, SKELETON_COLORS[index], curstart, curend, width)
        
        start = next

def draw_skeletons(dispInfo, screen, skeletons):
    # clean the screen
    screen.fill(pygame.color.THECOLORS["black"])


    for index, skeleton_info in enumerate(skeletons):
        # test if the current skeleton is tracked or not
        if skeleton_info.eTrackingState == SkeletonTrackingState.TRACKED:
            # draw the Head
            HeadPos = skeleton_to_depth_image(skeleton_info.SkeletonPositions[JointId.Head], dispInfo.current_w, dispInfo.current_h)
            #print skeleton_info.SkeletonPositions[JointId.ShoulderLeft],skeleton_info.SkeletonPositions[JointId.ElbowLeft],skeleton_info.SkeletonPositions[JointId.WristLeft]

            draw_skeleton_data(dispInfo, screen, skeleton_info, index, SPINE, 10)
            pygame.draw.circle(screen, SKELETON_COLORS[index], (int(HeadPos[0]), int(HeadPos[1])), 20, 0)
    
            # drawing the limbs
            draw_skeleton_data(dispInfo, screen, skeleton_info, index, LEFT_ARM)
            draw_skeleton_data(dispInfo, screen, skeleton_info, index, RIGHT_ARM)
            draw_skeleton_data(dispInfo, screen, skeleton_info, index, LEFT_LEG)
            draw_skeleton_data(dispInfo, screen, skeleton_info, index, RIGHT_LEG)
            ############################################################
            sle=str(skeleton_info.SkeletonPositions[JointId.ShoulderLeft])
            sle = re.findall("-?\d+.\d+.\d+",sle)
            sle=map(float,sle)
            #print sle
            ele=str(skeleton_info.SkeletonPositions[JointId.ElbowLeft])
            ele= re.findall("-?\d+.\d+.\d+",ele)
            ele=map(float,ele)
            #print ele
            wle=str(skeleton_info.SkeletonPositions[JointId.WristLeft])
            wle= re.findall("-?\d+.\d+.\d+",wle)
            wle=map(float,wle)
            #print wle
            vec1=map(float.__sub__, ele, sle)
            #print vec1
            vec2=map(float.__sub__, wle, ele)
            #print vec2
            dotproduct=(vec1[0]*vec2[0])+(vec1[1]*vec2[1])+(vec1[2]*vec2[2])
            #print dotproduct
            mag=math.sqrt((vec1[0]*vec1[0])+(vec1[1]*vec1[1])+(vec1[2]*vec1[2]))*math.sqrt((vec2[0]*vec2[0])+(vec2[1]*vec2[1])+(vec2[2]*vec2[2]))
            #print mag
            ang=math.acos(dotproduct/mag)
            print "angle at elbow joint = ",(180-math.degrees(ang))
            #################################################################
            elw=str(skeleton_info.SkeletonPositions[JointId.ElbowLeft])
            elw = re.findall("-?\d+.\d+.\d+",elw)
            elw=map(float,elw)
            #print elw
            wlw=str(skeleton_info.SkeletonPositions[JointId.WristLeft])
            wlw= re.findall("-?\d+.\d+.\d+",wlw)
            wlw=map(float,wlw)
            #print wlw
            hlw=str(skeleton_info.SkeletonPositions[JointId.HandLeft])
            hlw= re.findall("-?\d+.\d+.\d+",hlw)
            hlw=map(float,hlw)
            #print hlw
            vec3=map(float.__sub__, wlw, elw)
            #print vec3
            vec4=map(float.__sub__, hlw, wlw)
            #print vec4
            dotproduct1=(vec3[0]*vec4[0])+(vec3[1]*vec4[1])+(vec3[2]*vec4[2])
            #print dotproduct1
            mag1=math.sqrt((vec3[0]*vec3[0])+(vec3[1]*vec3[1])+(vec3[2]*vec3[2]))*math.sqrt((vec4[0]*vec4[0])+(vec4[1]*vec4[1])+(vec4[2]*vec4[2]))
            #print mag1
            ang1=math.acos(dotproduct1/mag1)
            print "angle at wrist joint = ",(180-math.degrees(ang1))
            #####################################################################
            scs=str(skeleton_info.SkeletonPositions[JointId.ShoulderCenter])
            scs = re.findall("-?\d+.\d+.\d+",scs)
            scs=map(float,scs)
            #print scs
            sls=str(skeleton_info.SkeletonPositions[JointId.ShoulderLeft])
            sls= re.findall("-?\d+.\d+.\d+",sls)
            sls=map(float,sls)
            #print sls
            els=str(skeleton_info.SkeletonPositions[JointId.ElbowLeft])
            els= re.findall("-?\d+.\d+.\d+",els)
            els=map(float,els)
            #print els
            vec5=map(float.__sub__, sls, scs)
            #print vec5
            vec6=map(float.__sub__, els, sls)
            #print vec6
            dotproduct2=(vec5[0]*vec6[0])+(vec5[1]*vec6[1])+(vec5[2]*vec6[2])
            #print dotproduct2
            mag2=math.sqrt((vec5[0]*vec5[0])+(vec5[1]*vec5[1])+(vec5[2]*vec5[2]))*math.sqrt((vec6[0]*vec6[0])+(vec6[1]*vec6[1])+(vec6[2]*vec6[2]))
            #print mag2
            ang2=math.acos(dotproduct2/mag2)
            print "angle at shoulder joint = ",(180-math.degrees(ang2))
        
                     
            
            
def main():
    """Initialize and run the game."""
    pygame.init()

    # Initialize PyGame
    screen = pygame.display.set_mode(WINDOW_SIZE, 0, 16)
    pygame.display.set_caption('PyKinect Skeleton Example')
    screen.fill(pygame.color.THECOLORS["black"])

    with nui.Runtime() as kinect:
        kinect.skeleton_engine.enabled = True
        kinect.skeleton_frame_ready += post_frame

        # Main game loop
        while True:
            event = pygame.event.wait()

            if event.type == pygame.QUIT:
                break
            elif event.type == KINECTEVENT:
                # apply joint filtering
                kinect._nui.NuiTransformSmooth(event.skeleton_frame, SMOOTH_PARAMS)

                draw_skeletons(pygame.display.Info(), screen, event.skeleton_frame.SkeletonData)
                pygame.display.update()
                pass

if __name__ == '__main__':
    main()
