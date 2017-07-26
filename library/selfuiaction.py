__author__ = 'Xuxh'


from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


class SelfUIAction(object):

    def __init__(self, uid, driver):

        self.uid = uid
        self.driver = driver
        self.type = {'ID':1, 'CLASS':2, 'NAME':3, 'XPATH':4}

    def __get_element_dict(self,config_value):

        """
        config_value likes 'xx1-xx2-xx3-xx4', xx1 indicates locate method
        xx1: locate method
        xx2: group flag, if there are multiple elements with same value, it's value is 1, otherwise, it's 0
        xx3: if xx2=1, xx3 indicates index value. if xx2=0, then xx3 is empty
        xx4: value for locate elemen
        the following is example: ID:0::com.vlife:id/btn_skip
        """

        elem_dict = {}
        dict_value = config_value.split('-')
        if len(dict_value) == 4:
            try:
                typeID = self.type[str(dict_value[0]).upper()]
                dict_value[0] = typeID
                dict_key = ['Locate_Type_ID','GroupFlag','Index','Value']
                elem_dict = dict(zip(dict_key,dict_value))
            except Exception,ex:
                print ex
                return {}

        return elem_dict

    def find_element(self,config_value):

        els = None
        element = self.__get_element_dict(config_value)

        if element != {}:
            try:
                if element['GroupFlag'] != 1:

                    els={
                        1: lambda: self.driver.find_element(By.ID, element['Value']),
                        2: lambda: self.driver.find_element(By.CLASS_NAME, element['Value']),
                        3: lambda: self.driver.find_element(By.NAME, element['Value']),
                        4: lambda: self.driver.find_element(By.XPATH, element['Value'])
                   }[element['Locate_Type_ID']]()

                elif element['GroupFlag'] == 1 and element['Index'] !=999:

                    els={
                        1: lambda: self.driver.find_elements(By.ID, element['Value'])[element['index']],
                        2: lambda: self.driver.find_elements(By.CLASS_NAME, element['Value'])[element['index']],
                        3: lambda: self.driver.find_elements(By.NAME, element['Value'])[element['index']],
                        4: lambda: self.driver.find_elements(By.XPATH, element['Value'])[element['index']]
                    }[element['Locate_Type_ID']]()

                else:
                    els={
                        1: lambda: self.driver.find_elements(By.ID, element['Value']),
                        2: lambda: self.driver.find_elements(By.CLASS_NAME, element['Value']),
                        3: lambda: self.driver.find_elements(By.NAME, element['Value']),
                        4: lambda: self.driver.find_elements(By.XPATH, element['Value'])
                   }[element['Locate_Type_ID']]()
            except Exception,ex:
                print ex

        return els

    def clear_element_attribute(self,element):

        try:
            element = self.find_element(element)
            length = len(element.get_attribute("name"))
            i = 0
            while i < length:
                self.driver.press_keycode(22) #KEYCODE_DPAD_RIGHT
                i += 1
            while i >= 0:
                self.driver.press_keycode(67) #KEYCODE_DEL
                i -= 1
        except Exception, ex:
            print ex

    def get_element_attributes(self, element, attr_name):

        value = ''

        try:
            element = self.find_element(element)
            value = element.get_attribute(attr_name)
        except Exception, ex:
            print ex

        return value

    def get_element_center_location(self,element):

        try:
            element = self.find_element(element)
            x = element.location['x']
            y = element.location['y']
            width = element.size['width']
            height = element.size['height']
            x1 = x + width/2
            y1 = y + height/2
            return x1, y1
        except Exception,ex:
            return ex

    def get_screen_center_location(self):

        height = 0
        width = 0

        try:
            height = self.driver.get_window_size()['height']/2
            width = self.driver.get_window_size()['width']/2

        except Exception,ex:
            print ex

        return height, width

    def long_press_element(self, element):

        el = self.find_element(element)
        action = TouchAction(self.driver)
        action.long_press(el).wait(1000).perform()

        # the other method
        # action2 = TouchAction(self.driver)
        # el = self.driver.find_element_by_id('XXXXX2')
        # action2.moveTo(el).release().perform()

    def swipe_screen(self,value):


        x1,y1,x2,y2 = value.split(',')

        self.driver.swipe(int(x1),int(y1),int(x2),int(y2),500)

    def click_keycode(self, value):

        self.driver.press_keycode(value)

    def find_toast(message, timeout, poll_frequency, driver):

        #element = WebDriverWait(driver,timeout,poll_frequency).until(expected_conditions.presence_of_element_located((By.PARTIAL_LINK_TEXT, message)))
        element = WebDriverWait(driver,timeout,poll_frequency).until(expected_conditions.presence_of_element_located((By.XPATH, message)))
        return element

if __name__ == '__main__':

    mydriver = 0
    temp = SelfUIAction('abc',mydriver)
    value = temp.find_element('ID-0--com.android.packageinstaller:id/continue_button')
    print value
