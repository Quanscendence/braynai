from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium.webdriver.chrome.options import Options
from django.contrib.auth.models import User
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from django.conf import settings
from datetime import datetime
import os
from time import sleep,time
import subprocess
from os import listdir
from os.path import isfile, join
import logging
import random



class TestWebsiteIndex(StaticLiveServerTestCase):
    """Class for functional tests on the website."""

    def setUp(self):
        if os.name == 'nt':
            self.browser = webdriver.Chrome(ChromeDriverManager().install())
            self.url     = 'http://127.0.0.1:8000/'
            # self.user = User.objects.create_user(username='vishwa@therealm.in', password="someuser")
        else:
            try:
                output = subprocess.run(['geckodriver', '-V'], stdout=subprocess.PIPE, encoding='utf-8')
                version = output.stdout.splitlines()[0].split()[-1]
            except:
                version = "0.0"
            if version == "0.0":
                print("Gecko is not existing. We should try Chrome")
                print("Gecko is not existing. We should try Chrome")
            else:
                options = webdriver.FirefoxOptions()
                options.add_argument('-headless')
                self.browser = webdriver.Firefox(firefox_options=options)

    def tearDown(self):
        self.browser.close()

######### TESTING INDEX PAGE #########
#     def test_index_page_is_displayed(self):
#         self.browser.get(self.url)
#         body = self.browser.find_element_by_class_name('top-menu')
#         self.assertEquals(
#             body.find_element_by_id('header_id').text,
#             "HOME"
#         )

#     def test_index_page_onclick_signup_button_redirect_to_signup_page(self):

#         self.browser.get(self.url)

#         destination_url = self.url+'customer/signup/'

#         signup_section = self.browser.find_element_by_class_name('btn-custom')
#         self.browser.execute_script("arguments[0].click();", signup_section)
#         self.browser.implicitly_wait(10)
#         self.assertEquals(
#             self.browser.current_url,
#             destination_url
#         )

#     def test_index_page_onclick_login_button_redirect_to_login_page(self):

#         self.browser.get(self.url)
#         destination_url = self.url+'customer/login/'
#         login_section = self.browser.find_element_by_id('login_link')
#         self.browser.execute_script("arguments[0].click();", login_section)
#         self.browser.implicitly_wait(10)
#         self.assertEquals(
#             self.browser.current_url,
#             destination_url
#         )
# #########END OF TESTING INDEX PAGE #########

#     ######### TESTING LOGIN PAGE #########
#     def test_login_page_display(self):
#         self.browser.get(self.url+'customer/login')
#         body = self.browser.find_element_by_class_name('top-menu')
#         self.assertEquals(
#             body.find_element_by_id('header_id').text,
#             "HOME"
#         )

#     def test_login_page_redirect_to_home_page(self):
#         self.browser.get(self.url+'customer/login')
#         destination_url = self.url
#         index_page = self.browser.find_element_by_id('header_id')
#         self.browser.execute_script("arguments[0].click();", index_page)
#         self.browser.implicitly_wait(10)
#         self.assertEquals(
#             self.browser.current_url,
#             destination_url
#         )

#     def test_login_page_signup_link(self):
#         self.browser.get(self.url+'customer/login')
#         destination_url = self.url+'customer/signup/'
#         signup_section = self.browser.find_element_by_class_name('signup_link')
#         self.browser.execute_script("arguments[0].click();", signup_section)
#         self.browser.implicitly_wait(10)
#         self.assertEquals(
#             self.browser.current_url,
#             destination_url
#         )

#     def test_login_page_forgot_password_link(self):
#         self.browser.get(self.url+'customer/login')
#         destination_url          = self.url+'customer/password-reset/'
#         forgot_password_section  = self.browser.find_element_by_class_name('forgot_password_link')
#         self.browser.execute_script("arguments[0].click();", forgot_password_section)
#         self.browser.implicitly_wait(10)
#         self.assertEquals(
#             self.browser.current_url,
#             destination_url
#         )

#     def test_login_page_facebook_link(self):
#         self.browser.get(self.url+'customer/login')
#         destination_url = 'https://www.facebook.com/transcendbrayn/'
#         facebook_link = self.browser.find_element_by_class_name('fa-facebook-official')
#         self.browser.execute_script("arguments[0].click();", facebook_link)
#         self.browser.implicitly_wait(10)
#         self.assertEquals(
#             self.browser.current_url,
#             destination_url
#         )

#     def test_login_page_form_submission(self):
#         self.browser.get(self.url+'customer/login')
#         destination_url = 'http://127.0.0.1:8000/dashboard/'
#         self.browser.find_element_by_id('id_username').send_keys("vishwa@therealm.in")
#         self.browser.find_element_by_id('id_password').send_keys("someuser")
#         self.browser.find_element_by_id('login_submit_button').submit()
#         self.browser.implicitly_wait(10)
#         self.browser.get(destination_url)
#         form_body = self.browser.find_element_by_id('menu1')
#         self.assertEquals(
#             form_body.find_element_by_class_name('mini-click-non').text,
#             "Dashboard"
#         )

#     def test_login_page_invalid_form_submission(self):
#         self.browser.get(self.url+'customer/login')
#         destination_url = self.url+'customer/login'
#         self.browser.find_element_by_id('id_username').send_keys("vishwa@therealm.in")
#         self.browser.find_element_by_id('id_password').send_keys("sxaoixoa")
#         self.browser.find_element_by_id('login_submit_button').submit()
#         self.browser.implicitly_wait(10)
#         form_body = self.browser.find_element_by_id('loginForm')
#         self.assertEquals(
#             form_body.find_element_by_id('login_error_message').text,
#             "Please Signup before login"
#         )
    ######### END OF TESTING LOGIN PAGE #########


    def test_project_create(self):
        '''function to test project creation  '''
        self.browser.get(self.url+'customer/login')
        destination_url = 'http://127.0.0.1:8000/dashboard/'
        self.browser.find_element_by_id('id_username').send_keys("vishwa@therealm.in")
        self.browser.find_element_by_id('id_password').send_keys("someuser")
        self.browser.find_element_by_id('login_submit_button').submit()
        self.browser.implicitly_wait(10)
        # self.browser.get(destination_url)

        new_project = self.browser.find_element_by_xpath('/html/body/div[2]/nav/div[2]/div[1]/div/nav/ul/li[1]/a')
        logging.info("Current directory: "+ str(os.getcwd()))
        folder =os.listdir('data')
        logging.info("tje BASE_DIR"+str(settings.BASE_DIR))
        path = settings.BASE_DIR+'/data\\'
        p = path.replace('\\', '/')
        logging.info("the path: "+path+p)

        for file1 in folder:
            #file1_path = p+file1
            file1_path = os.path.join(os.getcwd(), 'data', file1)
            logging.info("Checking the file: "+file1_path)
            try:
                sleep(10)
                self.browser.set_page_load_timeout(60)
                self.browser.execute_script("arguments[0].click();", new_project)

            except TimeoutException as ex:
                isrunning = 0
                pass
            self.browser.implicitly_wait(20)
            num = random.randint(1, 10)

            pro_name = f'{num}{file1}'
            logging.info(f'the randint{pro_name}')
            self.browser.find_element_by_id('id_project_title').send_keys(pro_name)

            select = Select(self.browser.find_element_by_id('id_industry'))
            select.select_by_value('34')
            self.browser.find_element_by_id('id_end_goal').send_keys("Some end goal")
            self.browser.find_element_by_id('description').send_keys("Some description")
            first_next = self.browser.find_element_by_id('first_button')
            try:
                sleep(10)
                self.browser.set_page_load_timeout(60)
                self.browser.execute_script("arguments[0].click();", first_next)
            except TimeoutException as ex:
                isrunning = 0
                pass
            logging.info(f'start of read file{file1}-{datetime.now()}')

            self.browser.find_element_by_id('id_files').send_keys(file1_path)
            second_button = self.browser.find_element_by_id('second_button')
            try:
                sleep(10)
                self.browser.set_page_load_timeout(60)
                self.browser.execute_script("arguments[0].click();", second_button)

            except TimeoutException as ex:
                isrunning = 0
                pass
            logging.info(f'end of read file{file1}-{datetime.now()}')
            logging.info(f'start nan option {file1}-{datetime.now()}')


            third_button = self.browser.find_element_by_id('third_button')
            try:
                sleep(10)
                self.browser.set_page_load_timeout(60)
                self.browser.execute_script("arguments[0].click();", third_button)

            except TimeoutException as ex:
                isrunning = 0
                pass

            logging.info(f'end of nan option {file1}-{datetime.now()}')
            logging.info(f'start time series {file1}-{datetime.now()}')
            fourth_button = self.browser.find_element_by_id('fourth_button')

            try:
                sleep(10)
                self.browser.set_page_load_timeout(60)
                self.browser.execute_script("arguments[0].click();", fourth_button)
                sleep(10)

            except TimeoutException as ex:
                isrunning = 0
                pass


            final_subbmit_button = self.browser.find_element_by_id('submit')
            logging.info(f'end time seriesn {file1}-{datetime.now()}')
            logging.info(f'start final project creation {file1}-{datetime.now()}')

            try:

                self.browser.set_page_load_timeout(60)
                self.browser.execute_script("arguments[0].click();", final_subbmit_button)
                sleep(60)

            except TimeoutException as ex:
                isrunning = 0
                pass
            logging.info(f'end final project creation {file1}-{datetime.now()}')
            try:

                self.browser.set_page_load_timeout(60)
                self.browser.get(destination_url)


            except TimeoutException as ex:
                isrunning = 0
                pass
            # element = WebDriverWait(self.browser, 20).until(
            #                 EC.element_to_be_clickable((By.XPATH, "/html/body/div/footer/div[1]/div/div[3]/div/div/a[5]")))








    def wait_for_element(self, elm, by = 'id', timeout=10):
        wait = WebDriverWait(self.browser, timeout)
        wait.until(EC.presence_of_element_located((By.XPATH, elm)))
        return self.driver.find_element_by_xpath(elm)
        wait_for_element(self,
                         "//span[@data-input-id='id_branch-autocomplete']/span[@data-value='1']",
                         "xpath").click()
