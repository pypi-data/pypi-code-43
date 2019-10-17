from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
#from selenium import webdriver
#from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
#import selenium.webdriver as driver

class Agile:

    def __init__(self,driver):
        """
        This specially designed for Automating the Agile PLM Web application.
        developed by GBS EQ Automation Team.

        :Features:
         - login(*url,*User_Name,*Password)
         - quick_search_part(*Part_Number)
         - part_rev_selection(*Part_Number_Revision)

        Note: All (*) as arguments need to pass to functions.
        
        For Additional Modules: Contact - harishkumar.k@flex.com

        
        """
        self.WebDriverWait=WebDriverWait
        self.EC=EC
        self.driver=driver
        self.By=By

    def login(self,url,user_name,Password):
        """
        It will navigate to the Agile page and Login with the credential ID & switch to main window.
        
        :Args:
         - url: hyper link on Test or Live Environment of Agile 9.3.6
         - user_name: Login user_name(Mostly ADID)
         - Password: password for login

        :Usage:
            agile.login(
                url,
                user_name,
                password)

        Note: After the login, existing window will be closed default and new window will be enabled.
        """
        self.driver.get(url)
        window_before = self.driver.window_handles[0]
        self.driver.find_element_by_id("j_username").send_keys(user_name)
        self.driver.find_element_by_id("j_password").send_keys(Password)
        self.driver.find_element_by_id("loginspan").click()
        self.WebDriverWait(self.driver, 120).until(self.EC.number_of_windows_to_be(2))
        newWindow = [window for window in self.driver.window_handles if window != window_before][0]
        self.driver.close()
        self.driver.switch_to.window(newWindow)
        self.WebDriverWait(self.driver, 120).until(self.EC.visibility_of_element_located((self.By.ID, "preferences")))
        self.driver.maximize_window()

    def quick_search_part(self,part_number):
        """
        To search the part or document number and navigate in the Agile.
        
        :Args:
         - part_number: Part Number

        :Usage:
            quick_search_part(part_number)

        Note: No return arguments.
        """
        self.driver.find_element_by_id('QUICKSEARCH_STRING').send_keys(part_number)
        while self.driver.find_element_by_id('QUICKSEARCH_STRING').get_attribute('value')!=part_number:
            self.driver.find_element_by_id('QUICKSEARCH_STRING').clear()
            self.driver.find_element_by_id('QUICKSEARCH_STRING').send_keys(part_number)
        self.driver.find_element_by_id('top_simpleSearchspan').click()
        while True:
            try:
                if self.driver.find_element_by_id('treegrid_QUICKSEARCH_TABLE').is_displayed() is True:
                    self.driver.find_element_by_id('top_simpleSearchspan').click()
                    self.WebDriverWait(self.driver, 120).until(self.EC.visibility_of_element_located((self.By.ID, "searchResult")))
                    for i in range(len(self.driver.find_elements_by_class_name('GMBodyMid')[0].find_elements_by_class_name('GMDataRow'))):
                        text1=self.driver.find_elements_by_class_name('GMBodyMid')[0].find_elements_by_class_name('GMDataRow')[i].find_elements_by_tag_name('td')[3].text
                        if text1.strip()==part_number:
                            self.driver.find_elements_by_class_name('GMBodyMid')[0].find_elements_by_class_name('GMDataRow')[i].find_elements_by_tag_name('td')[3].click()
                            try:
                                self.driver.find_elements_by_class_name('GMBodyMid')[0].find_elements_by_class_name('GMDataRow')[i].find_elements_by_tag_name('td')[3].find_elements_by_tag_name('a')[0].click()
                            except:
                                pass
                            break
                    self.WebDriverWait(self.driver, 120).until(self.EC.visibility_of_element_located((self.By.ID, "selectedTab")))
                    break
                elif self.driver.find_element_by_id('selectedTab').is_displayed() is True:
                    break
            except:
                try:
                    if self.driver.find_element_by_id('selectedTab').is_displayed() is True:
                        break
                except:
                    continue
    
    def part_rev_selection(self,rev):
        [ele.click() for ele in self.driver.find_element_by_id('revSelectName').find_elements_by_tag_name('option') if rev in ele.text]
        while True:
            visible=self.driver.find_element_by_id('progress_indicator_global').value_of_css_property('visibility')
            if visible=="hidden":
                break
    #def remove_attachment_by_file_desc(desc_name):





        