 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#                                                                     #
#  (c) Stefano Polloni                                                #
#                                                                     #
#  Created: 01/27/2016                                                #    
#  Updated: 01/27/2016                                                #
#                                                                     #  
#  Description: This function obtains the property-specific           #
#               url from an adress search on redfin.com. The          #
#               argument returned is a list of potential urls.        #
#               It requires that the proper modules be imported       #
#               in the environment where the function is called.      #
#                                                                     #
 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as WDW 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities as DC
from datetime import datetime
import sys

def get_url(address,proxy,ua):

    urls = []

    #- path to firefox profile:
    path = '/Users/stefanopolloni/Library/Application Support/Firefox/Profiles/' + proxy

    #- set WebDriver:
    fp = webdriver.FirefoxProfile(profile_directory=path)
    fp.set_preference("general.useragent.override",ua)
    driver = webdriver.Firefox(firefox_profile=fp)
    driver.delete_all_cookies()
    driver.switch_to_default_content()

    #- access redfin page and search address

    try:
        driver.get('http://www.redfin.com') 
    except:
        driver.quit()
        return 'CONNECTION_PROBLEM'

    try:
        searchbar = driver.find_element_by_name('searchInputBox')
        searchbar.send_keys(address)
        searchbar.send_keys(Keys.ENTER)
    except:
        print str(datetime.now().strftime("%H:%M:%S")) + ' could not searchbar ' + address
        driver.quit()
        return 'SUSPICIOUS_RESP'

    #- wait for page to load and get all search results:

    try:
        srch_results = WDW(driver, 5).until(
            EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR,'a.item-title.block')))
    except:
        try:
            oups = driver.find_element_by_xpath('//div[@class="guts"]//h3').text
            if oups == "Oops!":
                msgs = driver.find_elements_by_xpath('//div[@class="guts"]//span')
                for msg in msgs:
                    if "examples" in msg.text: pass
            driver.quit()
            return 'TIMEOUT_OR_NORESULTS'     
        except:
            driver.quit()
            print str(datetime.now().strftime("%H:%M:%S")) + ' OUPS try later (?) for ' + address
            return 'OOPS'
           
    #- populate with htmls found in search results

    try:
        for srch_result in srch_results:
            if "Addresses" in srch_result.get_attribute('data-reactid'): 
                urls.append(srch_result.get_attribute('href').encode('UTF8'))

        urls = list(set(urls))
    except:
        driver.quit()
        print str(datetime.now().strftime("%H:%M:%S")) + ' could not populate ' + address
        return 'SUSPICIOUS_RESP'

    driver.quit()

    if not urls: return 'NO_ADDRESSES'
    
    return urls
