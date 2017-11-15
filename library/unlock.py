#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Xuxh'

import device


class unlockScreen(object):

    def __init__(self,uid):

        self.device = device.Device(uid)
        self.uid = uid
        self.width, self.height = self.device.get_screen_size()

    def convert_coordinate(self, x, y, re_x, re_y):

        actual_w = (x * self.width)/re_x
        actual_h = (y * self.height)/re_y

        return int(actual_w), int(actual_h)

    # orig is start_point coordinate [x,y]
    def right_slide(self, orig, dest, distance=200, duration=300):

        if orig[0] == 0 and orig[1] == 0:
            cmd = "adb -s {0} shell input swipe {1} {2} {3} {4} {5}".format \
                (self.uid,int(self.width/5),int(self.height/6*5),int(self.width/6*5),int(self.height/6*5), duration)
        if orig[0] != 0 and dest[0] == 0:
            cmd = "adb -s {0} shell input swipe {1} {2} {3} {4} {5}".format \
                (self.uid,int(orig[0]),int(orig[1]),int(orig[0] + distance), int(orig[1]), duration)
        if orig[0] != 0 and dest[0] != 0:
            cmd = "adb -s {0} shell input swipe {1} {2} {3} {4} {5}".format \
                (self.uid,int(orig[0]),int(orig[1]),int(dest[0]), int(dest[1]), duration)

        self.device.shellPIPE(cmd)

    def up_slide(self, orig, dest, distance=200, duration=300):

        if orig[0] == 0 and orig[1] == 0:
            cmd = "adb -s {0} shell input swipe {1} {2} {3} {4} {5}".format \
                (self.uid,int(self.width/2),int(self.height/6*5),int(self.width/2),int(self.height/2), duration)
        if orig[0] != 0 and dest[0] == 0:
            cmd = "adb -s {0} shell input swipe {1} {2} {3} {4} {5}".format \
                (self.uid,int(orig[0]),int(orig[1]),int(orig[0]), int(orig[1]-distance), duration)
        if orig[0] != 0 and dest[0] != 0:
            cmd = "adb -s {0} shell input swipe {1} {2} {3} {4} {5}".format \
                (self.uid,int(orig[0]),int(orig[1]),int(dest[0]), int(dest[1]), duration)

        self.device.shellPIPE(cmd)

    def down_slide(self, orig, dest, distance=200, duration=300):

        if orig[0] == 0 and orig[1] == 0:
            cmd = "adb -s {0} shell input swipe {1} {2} {3} {4} {5}".format \
                (self.uid,int(self.width/2),int(self.height/2),int(self.width/2),int(self.height/4*3), duration)
        if orig[0] != 0 and dest[0] == 0:
            cmd = "adb -s {0} shell input swipe {1} {2} {3} {4} {5}".format \
                (self.uid,int(orig[0]),int(orig[1]),int(orig[0]), int(orig[1]+distance), duration)
        if orig[0] != 0 and dest[0] != 0:
            cmd = "adb -s {0} shell input swipe {1} {2} {3} {4} {5}".format \
                (self.uid,int(orig[0]),int(orig[1]),int(dest[0]), int(dest[1]), duration)

        self.device.shellPIPE(cmd)

    def left_slide(self, orig, dest, distance=200, duration=300):

        pass

    def other_slide(self, orig, dest, distance=200, duration=300):

        cmd = "adb -s {0} shell input swipe {1} {2} {3} {4} {5}".format \
                (self.uid,int(orig[0]),int(orig[1]),int(dest[0]), int(dest[1]), duration)

        self.device.shellPIPE(cmd)