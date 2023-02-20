import time
import random
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from exceptions import RequiredException, BlacklistedException, ApplyException, FinishException
import urllib.parse


class Linkedin:
    def __init__(self, config):
        options = Options()
        if config.get("headless", False):
            options.add_argument("--headless=new")
        if config.get("user_data") is not None:
            options.add_argument("user-data-dir=" + config.get("user_data"))
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager(
            chrome_type=ChromeType.CHROMIUM).install()), options=options)
        self.config = config

    def getFailed(self):
        return len(self.config.getJobsByStatus(["already", "timeout", "manual"]))

    def __del__(self):
        if self.driver is not None:
            self.driver.quit()

    def randomSleep(self, min=1, max=8.0):
        sleepTime = random.uniform(min, max)
        time.sleep(sleepTime)

    def run(self):
        self.driver.get("https://www.linkedin.com")
        try:
            WebDriverWait(self.driver, self.config.get("wait_time", 30)).until(
                EC.presence_of_element_located((By.CLASS_NAME, "global-nav__me-photo")))
        except TimeoutException:
            self.signIn()
            self.search()
        else:
            self.search()

    def signIn(self):
        email = self.config.get("email")
        password = self.config.get("password")
        if email is None or password is None:
            raise RequiredException("email and password are required")
        waitTime = self.config.get("wait_time", 30)
        self.driver.get("https://www.linkedin.com/login")
        WebDriverWait(self.driver, waitTime).until(
            EC.presence_of_element_located((By.ID, "password")))
        self.driver.find_element("id", "username").send_keys(email)
        passwordField = self.driver.find_element("id", "password")
        passwordField.send_keys(password)
        passwordField.send_keys(Keys.RETURN)
        self.randomSleep()
        if self.config.get("code") is not None:
            WebDriverWait(self.driver, waitTime).until(
                EC.presence_of_element_located((By.ID, "input__phone_verification_pin")))
        if len(self.driver.find_elements(By.ID, "input__phone_verification_pin")) > 0:
            code = self.config.get("code")
            if code is None:
                raise RequiredException(
                    "Code is required cause 2fa is enabled")
            codeField = self.driver.find_element(
                "id", "input__phone_verification_pin")
            codeField.send_keys(code)
            codeField.send_keys(Keys.RETURN)
            self.randomSleep()

    def buildSearchURL(self, start=0):
        query = self.config.get("search_query")
        if query is None:
            raise RequiredException("search_query is required")
        params = {
            'f_AL': True,
            'sortBy': "DD",
            'start': start
        }
        query.update(params)
        return "https://www.linkedin.com/jobs/search/?" + urllib.parse.urlencode(query)

    def search(self, start=0):
        waitTime = self.config.get("wait_time", 30)
        starttime = datetime.now()
        url = self.buildSearchURL(start)
        self.driver.get(url)
        WebDriverWait(self.driver, waitTime).until(
            EC.visibility_of_all_elements_located((By.CLASS_NAME, "jobs-search-results-list")))
        self.randomSleep()
        total_height = int(self.driver.execute_script(
            "return document.getElementsByClassName(\"jobs-search-results-list\")[0].scrollHeight"))
        for i in range(1, total_height, 50):
            self.driver.execute_script(
                "document.getElementsByClassName(\"jobs-search-results-list\")[0].scroll(0, {});".format(i))
        jobs = self.driver.find_elements(
            By.XPATH, '//li[@data-occludable-job-id]')
        bl_logger = self.config.getLogger("blacklist")
        pageJobList = []
        for job in jobs:
            try:
                try:
                    company = job.find_element(
                        By.CLASS_NAME, "job-card-container__company-name").text
                    if self.config.checkBlacklist("company", company.lower()):
                        raise BlacklistedException(
                            "Company", company, job.get_attribute("data-occludable-job-id"))
                except NoSuchElementException:
                    pass
                title = self.driver.find_element(
                    By.CLASS_NAME, "job-card-list__title").text
                if self.config.checkBlacklist("title", title.lower()):
                    raise BlacklistedException(
                        "Title", title, job.get_attribute("data-occludable-job-id"))
                pageJobList.append(job.get_attribute("data-occludable-job-id"))
            except BlacklistedException as e:
                bl_logger.info(e)
                pass
        maxHours = self.config.get("max_hours", 2)
        maxFailed = self.config.get("max_failed", 20)
        ap_logger = self.config.getLogger("apply")
        question_logger = self.config.getLogger("questions")
        for j in pageJobList:
            if starttime < datetime.now() - timedelta(hours=maxHours):
                raise FinishException("Ran %d Hours" % maxHours)
            if self.getFailed() >= maxFailed:
                raise FinishException("%d Failed Applications" % maxFailed)
            try:
                if self.config.getJob(j) is not None:
                    raise ApplyException(j, "Job Already Applied")
                self.apply(j)
            except ApplyException as e:
                ap_logger.info(e)
                for q in e.getQuestions():
                    question_logger.info(q)
                pass
        if len(jobs) == 25:
            self.search(start+25)
        else:
            raise FinishException(
                "%d Jobs on page. Assuming Last Page" % len(jobs))

    def apply(self, jobid):
        waitTime = self.config.get("wait_time", 30)
        self.driver.get("https://www.linkedin.com/jobs/view/"+str(jobid)+"/")
        self.randomSleep()
        try:
            WebDriverWait(self.driver, waitTime).until(EC.presence_of_element_located(
                (By.XPATH, '//button[contains(@class, "jobs-apply-button")]')))
            button = self.driver.find_element(
                By.XPATH, '//button[contains(@class, "jobs-apply-button")]')
            button.click()
            self.randomSleep()
        except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
            self.config.saveJob(jobid, "already")
            raise ApplyException(jobid, "Job Already Applied")
        starttime = datetime.now()
        ae = ApplyException(jobid, "Input Field Required")
        while starttime > datetime.now() - timedelta(minutes=self.config.get("timeout", 5)):
            # TODO: look for empty inputs and pull value from extendable config function
            fieldErrors = self.driver.find_elements(
                By.CLASS_NAME, "fb-dash-form-element__error-field")
            if len(fieldErrors) > 0:
                for fieldError in fieldErrors:
                    fieldId = fieldError.get_attribute("id")
                    question = self.driver.find_element(
                        By.CSS_SELECTOR, "label[for='"+fieldId+"']").text
                    ae.addQuestion(question)
                self.config.saveJob(jobid, "manual")
                raise ae
            unknownError = self.driver.find_elements(
                By.CLASS_NAME, "artdeco-inline-feedback__message")
            if len(unknownError) > 0:
                self.config.saveJob(jobid, "manual")
                raise ApplyException(jobid, "Input Field Required")
            if self.buttonExist('Continue to next step'):
                self.clickButton('Continue to next step')
                self.randomSleep()
            if self.buttonExist('Choose Resume'):
                self.clickButton('Choose Resume')
                self.randomSleep()
            if self.buttonExist('Review your application'):
                self.clickButton('Review your application')
                self.randomSleep()
            if self.checkboxExist('follow-company-checkbox'):
                self.clickCheckbox('follow-company-checkbox')
                self.randomSleep()
            if self.buttonExist('Submit application'):
                self.clickButton('Submit application')
                self.config.saveJob(jobid, "applied")
                return
            self.randomSleep()
        self.config.saveJob(jobid, "timeout")
        raise ApplyException(jobid, "Job Timed Out")

    def clickCheckbox(self, fortag):
        self.driver.find_element(
            By.CSS_SELECTOR, "label[for='"+fortag+"']").click()

    def checkboxExist(self, fortag):
        return len(self.driver.find_elements(By.CSS_SELECTOR, "label[for='"+fortag+"']")) > 0

    def buttonExist(self, label):
        return len(self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label='"+label+"']")) > 0

    def clickButton(self, label):
        self.driver.find_element(
            By.CSS_SELECTOR, "button[aria-label='"+label+"']").click()
