 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#                                                                     #
#  (c) Stefano Polloni                                                #
#                                                                     #
#  Created: 03/02/2016                                                #    
#  Updated: 03/02/2016                                                #
#                                                                     #  
#  Description: This function and retrieves the cookie                #
#				necessary to make successful requests on              #
#				multcoproptax.org                                     #
#                                                                     #
 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as WDW 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities as DC

def make_cookie(proxy,ua):

	try:

		#- path to firefox profile:
		path = '/Users/stefanopolloni/Library/Application Support/Firefox/Profiles/' + proxy

		#- set WebDriver:
		fp = webdriver.FirefoxProfile(profile_directory=path)
		fp.set_preference("general.useragent.override",ua)
		driver = webdriver.Firefox(firefox_profile=fp)
		driver.delete_all_cookies()
		driver.switch_to_default_content()

		#- acess site and click on guest login
		driver.get('http://www.multcoproptax.org') 
		driver.find_element_by_xpath('//input[@value="Guest Login"]').click()

		#- save cookie
		cookies = driver.get_cookies()
		multco = {}
		multco[cookies[0]['name']] = cookies[0]['value']

		#- quit driver
		driver.quit()

		return multco

	except:
		driver.quit()
		return "NO_COOKIE"

