import time
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from linkedin import Linkedin
from config import Config
from urllib3.exceptions import ProtocolError
from selenium.common.exceptions import NoSuchWindowException, TimeoutException
from exceptions import RequiredException, FinishException
import pyotp

config = Config()
linkedin = Linkedin(config=config)
try:
    linkedin.run()
except TimeoutException:
    config.getLogger().error(
        "Element wasn't where it was supposted to be! Probably bot detection")
    exit(2)
except RequiredException as e:
    config.getLogger().error(e)
    exit(1)
except FinishException as e:
    config.getLogger().warning(e)
    config.printReport()
except (KeyboardInterrupt, ProtocolError, NoSuchWindowException):
    config.getLogger().warning("Search Interupted")
    config.printReport()
    exit(3)
