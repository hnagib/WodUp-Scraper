#!/usr/bin/python3
import os
import sys
from wodifycrawler import Wodify

# Log into Wodify
w = Wodify(
    email='hasan.nagib@gmail.com',
    password=os.environ['wodify_password']
)

# Sign up for class
w.signup_for_class(
    days_from_now=2, 
    class_time='7:00 AM',
    class_type='Indoor Class',
    max_attempt=20
)

w.browser.close()