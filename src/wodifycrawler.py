import pandas as pd
from selenium import webdriver
from lxml import html
from getpass import getpass
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException 
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
        time.sleep(3)
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
        time.sleep(3)
        self.browser.get(calendar_url)
    
    def registration_xpath(self, class_time, class_type):
        xpath = f"""
        /html/body/form/div[5]/div[2]/div[2]
        /div/span/table/tbody
        /tr[1]
        //following-sibling::tr[td[1][normalize-space()='{class_time} {class_type}']]
        /td[3]/div/a
        """
        return xpath

    def attempt_signup_for_class(self, days_from_now, class_time, class_type):
        
        self.pull_schedule()
        date = (datetime.today() + pd.Timedelta(f'{days_from_now} day')).strftime('%m/%d/%Y')
        time.sleep(3)
        cal = self.browser.find_element_by_xpath("//input[@name='AthleteTheme_wt6$block$wtMainContent$wt9$W_Utils_UI_wt216$block$wtDateInputFrom']")
        cal.clear()
        cal.send_keys(date)

        time.sleep(2)
        self.browser.find_element_by_xpath(
            self.registration_xpath(class_time, class_type)+'/span[1]'
            ).click()
        
    def check_registration(self, days_from_now, class_time, class_type):
        date = (datetime.today() + pd.Timedelta(f'{days_from_now} day')).strftime('%m/%d/%Y')
        try:
            self.browser.find_element_by_xpath(
                self.registration_xpath(class_time, class_type)
                +"/div/span[1]/*[name()='svg' and contains(@class,'icon icon-ticket')]"
            )
            print(f'Found registration for {date} {class_time}!')
            return True
        
        except NoSuchElementException:
            print(f'Not signed up yet for {date} {class_time}... SAD! :(')
            return False
    
    def signup_for_class(self, days_from_now, class_time, class_type, max_attempt=15):
        attempt = 0
        while attempt < max_attempt:
            try:
                self.attempt_signup_for_class(days_from_now, class_time, class_type)
                attempt += 1
                time.sleep(1)

                signup_successful = self.check_registration(days_from_now, class_time, class_type)
                if signup_successful:
                    break

            except NoSuchElementException:
                print(f'Looks like {class_time} registration is not open yet.. tick tock..')
                pass



