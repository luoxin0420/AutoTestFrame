#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Xuxh'

import tempfile
import re
import time
import xml.etree.cElementTree as ET

import device


class Element(object):

    def __init__(self,uid):

        self.tempFile = tempfile.gettempdir()
        self.pattern = re.compile(r"\d+")
        self.uid = uid

    def __uidump(self):

        # get control tree of current activity
        cmd = "adb -s {0} shell uiautomator dump /data/local/tmp/uidump.xml".format(self.uid)
        device.Device.shellPIPE(cmd)
        cmd = "adb -s {0} pull /data/local/tmp/uidump.xml {1}".format(self.uid,self.tempFile)
        device.Device.shellPIPE(cmd)

    def __element(self, attrib, name):

        # return single element
        self.__uidump()
        tree = ET.ElementTree(file=self.tempFile + "/uidump.xml")
        treeIter = tree.iter(tag="node")
        for elem in treeIter:
            if elem.attrib[attrib] == name:
                bounds = elem.attrib["bounds"]
                coord = self.pattern.findall(bounds)
                Xpoint = (int(coord[2]) - int(coord[0])) / 2.0 + int(coord[0])
                Ypoint = (int(coord[3]) - int(coord[1])) / 2.0 + int(coord[1])

                return Xpoint, Ypoint

    def __elements(self, attrib, name, attribute='bounds'):

        # return list with multiple same arribute
        list = []
        self.__uidump()
        tree = ET.ElementTree(file=self.tempFile + "/uidump.xml")
        treeIter = tree.iter(tag="node")
        for elem in treeIter:
            if elem.attrib[attrib] == name:
                if attribute == 'bounds':
                    bounds = elem.attrib[attribute]
                    coord = self.pattern.findall(bounds)
                    Xpoint = (int(coord[2]) - int(coord[0])) / 2.0 + int(coord[0])
                    Ypoint = (int(coord[3]) - int(coord[1])) / 2.0 + int(coord[1])
                    list.append((Xpoint, Ypoint))
                else:
                    value = elem.attrib[attribute]
                    list.append(value)
        return list

    def findElementByName(self, name):

        return self.__element("text", name)

    def findElementsByName(self, name):
        return self.__elements("text", name)

    def findElementByClass(self, className):

        return self.__element("class", className)

    def findElementsByClass(self, className):
        return self.__elements("class", className)

    def findElementById(self, id, attribute='bounds'):

        return self.__element("resource-id",id,attribute)

    def findElementsById(self, id,attribute='bounds'):
        return self.__elements("resource-id",id,attribute)


class Event(object):

    def __init__(self,uid):
        self.uid = uid
        cmd = "adb -s {0} wait-for-device ".format(self.uid)
        device.Device.shellPIPE(cmd)

    def touch(self, dx, dy):

        cmd = "adb -s {0} shell input tap {1} {2}".format(self.uid,str(dx),str(dy))
        device.Device.shellPIPE(cmd)
        time.sleep(0.5)


def click_popup_window(uid,findstr):

    element = Element(uid)
    event = Event(uid)

    for fs in findstr:
        e1 = element.findElementByName(fs)
        if e1 is not None:
            event.touch(e1[0], e1[1])
            time.sleep(1)


def click_element_by_id(uid,id,index):

    element = Element(uid)
    event = Event(uid)

    find_eles = element.findElementsById(id)
    i = 0
    for el in find_eles:
        if i == index:
            event.touch(el[0], el[1])
            time.sleep(1)
            break
        else:
            i += 1


def get_element_attribute(uid,id,index,attrib):

    element = Element(uid)

    find_eles = element.findElementsById(id,attribute=attrib)
    i = 0
    for el in find_eles:
        if i == index:
            return el
            break
        else:
            i += 1

    return ''

if __name__ == '__main__':

    click_popup_window('82e2aaad',[u"信息"])
    # print
    # e2 = element.findElementByName(u"信息")
    # evevt.touch(e2[0], e2[1])