import pandas as pd
from selenium import webdriver
from lxml import html
from getpass import getpass
from selenium.webdriver.common.keys import Keys
import time
import os
from datetime import datetime

class Wodify:

    def __init__(self, 
                 email='hasan.nagib@gmail.com', 
                 password=os.environ['wodify_password'], 
                 url='https://app.wodify.com/SignIn/', 
                 chrome_driver_path='../src/chromedriver'
                ):
        """
        :param email: Email address login for Wodify
        :param password: Wodify login password
        :param url: url for Wodify login page
        :param chrome_driver_path: path to chromedriver executable
        """
        self.email=email
        self.password=password
        self.browser = webdriver.Chrome(chrome_driver_path)
        self.url = url
        self.login()
        
    def login(self):
        """
        Sign into Wodify using self.email and self.password
        """
        self.browser.get(self.url)
        time.sleep(2)
        self.browser.find_element_by_xpath("//input[@id='Input_UserName']").send_keys(self.email)
        self.browser.find_element_by_xpath("//input[@id='Input_Password']").send_keys(self.password)
        self.browser.find_element_by_xpath("//button[@type='submit']").click()

    def pull_schedule(
        self, 
        calendar_url='https://app.wodify.com/Schedule/CalendarListViewEntry.aspx'
    ):
        """
        Get html tree for a given movement
        :param calendar url: url for class calendar
        :return:
        """
        time.sleep(2)
        self.browser.get(calendar_url)
        
    def signup_for_class(self, days_from_now=1, class_time='7:00 AM'):
        
        self.pull_schedule()
        date = (datetime.today() + pd.Timedelta(f'{days_from_now} day')).strftime('%m/%d/%Y')
        time.sleep(2)
        cal = self.browser.find_element_by_xpath("//input[@name='AthleteTheme_wt6$block$wtMainContent$wt9$W_Utils_UI_wt216$block$wtDateInputFrom']")
        cal.clear()
        cal.send_keys(date)

        time.sleep(3)
        self.browser.find_element_by_xpath(
            f"//table[@class='TableRecords']//td[normalize-space()='{class_time} Indoor Class']/following-sibling::td[@class='TableRecords_OddLine']/following-sibling::td[@class='TableRecords_OddLine']"
        ).click()