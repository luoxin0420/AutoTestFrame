#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Xuxh'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import xml.etree.ElementTree as ET


class parseXml(object):

    """ Json parser reference
    https://docs.python.org/3/library/xml.etree.elementtree.html
    """
    value = ''

    def __init__(self,dataobj):

        if isinstance(dataobj,str):
            self.root = ET.fromstring(dataobj)
        else:
            self.tree = ET.parse(dataobj)
            self.root = self.tree.getroot()
                # handle with namespace "xmlns"

        # handle with namespace of xml file
        if self.root.tag.find('{http://') != -1:
            self.namespace = self.root.tag.split('}')[0] + '}'
        else:
            self.namespace = ''


    #iterate recursively over all the sub-tree below it (its children, their children, and so on).
    def find_elements(self,name):

        elements = []

        try:
            elements = self.root.iter(self.namespace + name)
        except Exception,ex:
            print ex

        return elements

    # This module only provides limited support for XPath expression
    def find_elements_by_xpath(self,xpath):

        elements = []

        try:
            elements = self.root.findall(xpath)
        except Exception,ex:
            print ex

        return elements

    def get_elements_attribute_value(self,name,attribute):

        value = []

        elements = self.find_elements(name)

        try:
            for ele in elements:
                value.append(ele.get(attribute))
        except Exception,ex:
            print ex

        return value

    def get_elements_text(self,name):

        value = []

        elements = self.find_elements(name)
        try:
            for ele in elements:
                value.append(ele.text)
        except Exception,ex:
            print ex

        return value

    def get_elements_attribute(self,name):

        value = []

        elements = self.find_elements(name)

        try:
            for ele in elements:
                value.append(ele.attrib)
        except Exception,ex:
            print ex

        return value

if __name__ == '__main__':

    xml_str ="""<query xmlns="http://jabber.com/features/iq-query/jabber:iq:auth"><uid>3568397920646752</uid><password>EoONtvLGNU</password><resource>android-2.1-pet</resource><unique>4e9ff950fcdf09acdd5f4d8f5d57d4c9</unique><platform version="7.0">android</platform><product soft="6.131" micro="6">android-ipro-magazine</product><plugin><item package="com.vlife.ipro.magazine" version="6136"/></plugin><plugin_version>140</plugin_version><promotion>2060</promotion><android_id>69287d4490f1da13</android_id><timezone>Asia/Shanghai</timezone><language>en_US</language><package>com.vlife.ipro.magazine</package><host>com.vlife.ipro.magazine:main</host><paper_id>465</paper_id><elapsed_realtime>51905</elapsed_realtime><apk_path>/system/priv-app/vlife.apk</apk_path><device>shamu</device><brand>Android</brand><board>shamu</board><display>aosp_shamu-eng 7.0 NBD90Z eng.tugang.20170117.112541 debug,test-keys</display><system_id>NBD90Z</system_id><incremental>eng.tugang.20170117.112541</incremental><manufacturer>motorola</manufacturer><model>AOSP on Shamu</model><release>7.0</release><system_product>aosp_shamu</system_product><sdk_int>24</sdk_int><user>tuganglei</user><finger_print>Android/aosp_shamu/shamu:7.0/NBD90Z/tugang01171125:eng/debug,test-keys</finger_print><manufacturer>motorola</manufacturer><tags>debug,test-keys</tags><type>eng</type><serial>ZX1G22TG4F</serial><mac>E4:90:7E:05:F0:B9</mac></query>"""
    xmlobject = parseXml(xml_str)

    # notify_data_tree = ET.fromstring(xml_str)
    # str_value = notify_data_tree.find("{http://jabber.com/features/iq-query/jabber:iq:auth}uid").text
    # print str_value
    value = xmlobject.get_elements_text('uid')
    print value
    value = xmlobject.get_elements_attribute_value('platform','version')
    print value