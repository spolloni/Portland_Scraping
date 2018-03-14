 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#                                                                     #
#  (c) Stefano Polloni                                                #
#                                                                     #
#  Created: 01/27/2016                                                #    
#  Updated: 01/27/2016                                                #
#                                                                     #  
#  Description: This baby obtains the property-specific county        #
#               asessor id using portlandmaps.com and scrapes         # 
#               all deed information from multcoproptex.com           #
#               the input is the adress id obtained from the          # 
#               addresses exce; file.                                 #
#                                                                     #
 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

from lxml import html
import requests, sys, os
from datetime import datetime
from selenium import webdriver

proj  = '/Users/stefanopolloni/GoogleDrive/Brown/Year3/year_III_paper'
work1 = '/congestion_value/portland/data/real_estate/pickles/'
work2 = '/congestion_value/portland/data/real_estate/pickles_nrf/'
path1 = proj + work1
path2 = proj + work2

firefox = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
    }  

def get_deeds(address_id,cookie,proxy,ua):

    segments  = []
    deed_info = []
    tax_info  = []
    ass_info  = []

    #- set proxy and identity

    if proxy != 'ri':
        proxy_host = proxy+'.proxymesh.com'
        proxy_port = "31280"  
        auth = requests.auth.HTTPProxyAuth('spolloni', 'patate45')
        proxies = {"http": "http://{}:{}/".format(proxy_host, proxy_port)} 

    pd = '/Users/stefanopolloni/Library/Application Support/Firefox/Profiles/' + proxy 

    firefox["User-Agent"] = ua

    #- set WebDriver properties:  

    fp = webdriver.FirefoxProfile(profile_directory=pd)
    fp.set_preference("general.useragent.override",ua)

    #- step one: obtain Proberty_ID through portlandmaps.com

    try:
        if proxy != 'ri':
            url = requests.get('http://www.portlandmaps.com/detail.cfm?action=Assessor&&address_id=' 
                                     + address_id, headers = firefox, proxies = proxies, auth = auth ).url
        else:
            url = requests.get('http://www.portlandmaps.com/detail.cfm?action=Assessor&&address_id=' 
                                                                     + address_id, headers = firefox ).url
    except:
        return 'CONNECTION_PROBLEM'

    try:
        prop_id = url[url.rfind("or/")+3:url.rfind("_")].encode('ascii', 'ignore')
    except:
        prop_id = 'XXXX' 

    if prop_id[0] != 'R': return 'NOT_MATCHED' 

    if os.path.isfile(path1+prop_id+'.p'): return 'PREV_SUCCESS'
    if os.path.isfile(path2+prop_id+'.p'): return 'PREV_SUCCESS'

    #- step two: scrape land type and deeds

    try:
        if proxy != 'ri':
            req  = requests.get('http://multcoproptax.org/property.asp?PropertyID=' + prop_id, 
                                    headers = firefox, proxies = proxies, auth = auth, cookies = cookie)
        else:
            req  = requests.get('http://multcoproptax.org/property.asp?PropertyID=' + prop_id, 
                                                                    headers = firefox, cookies = cookie)
    except:
        return 'CONNECTION_PROBLEM'

    try:

        tree = html.fromstring(req.content)

        land = tree.xpath('//table[descendant::td[contains(text(),"Land Information")]]' +
                                      '/tr[3]/td[2]/text()')[0].encode('ascii', 'ignore' )
        land = land[land.find("-")+1:land.find("\\")].strip()

        if "COMMERCIAL" in land: return 'COMM_or_IND_LAND'
        if "INDUSTRIAL" in land: return 'COMM_or_IND_LAND'

    except:
        print str(datetime.now().strftime("%H:%M:%S")) + 'could not retrieve land type for ' + prop_id
        return 'SUSPICIOUS_RESP'

    try:

        deed = tree.xpath('//table[descendant::td[contains(text(),"Sales Information")]]' +
                                                                   '/tr[@class="regtxt"]' )
        for row in deed:
            line = row.xpath('.//td')
            del line[1:4]
            line = [line[0].xpath('./@title')[0].encode('ascii', 'ignore' ),
                    line[1].xpath('./text()')[0].encode('ascii', 'ignore' ),
                    line[2].xpath('./text()')[0].encode('ascii', 'ignore' ).lstrip("$")]
            if line[2] == '0': continue 
            if 'DEED' not in line[0]: continue
            if 'TRUSTEE' in  line[0]: continue
            deed_info.append(line)

    except:
        print str(datetime.now().strftime("%H:%M:%S")) + 'could not retrieve deed info for ' + prop_id
        return 'SUSPICIOUS_RESP'
    
    #- step three: scrape tax summary

    try:
        if proxy != 'ri':
            req  = requests.get('http://multcoproptax.org/prop2sum.asp?PropertyID='+ prop_id, 
                                   headers = firefox, proxies = proxies, auth = auth, cookies = cookie)
        else:
            req  = requests.get('http://multcoproptax.org/prop2sum.asp?PropertyID='+ prop_id, 
                                                                   headers = firefox, cookies = cookie)
    except:
        return 'CONNECTION_PROBLEM'

    try:

        tree = html.fromstring(req.content)

        tax = tree.xpath('//table[descendant::div[contains(text(),"Tax Summary")]]' +
                                                          '/tr[@bgcolor="#FFFFFF"]' )

        for row in tax:
            line = row.xpath('.//td/text()')[:2]
            line = [ cell.encode('ascii', 'ignore') for cell in line ]
            tax_info.append(line)

    except:
        print str(datetime.now().strftime("%H:%M:%S")) + 'could not retrieve tax info for ' + prop_id
        return 'SUSPICIOUS_RESP'

    #- step four: scrape assessment history

    try:
        if proxy != 'ri':
            req  = requests.get('http://multcoproptax.org/property3.asp?PropertyID='+ prop_id, 
                                    headers = firefox, proxies = proxies, auth = auth, cookies = cookie)
        else:
            req  = requests.get('http://multcoproptax.org/property3.asp?PropertyID='+ prop_id, 
                                                                    headers = firefox, cookies = cookie)
    except:
        return 'CONNECTION_PROBLEM'

    try:

        tree = html.fromstring(req.content)

        ass = tree.xpath('//table[child::*/child::td[contains(text(),' +
                                   ' "Assessment History")]]/tr')[2:]

        for row in ass:
            line = row.xpath('.//td/text()')
            line = line[:3] + line[-1:]
            line = [ cell.encode('ascii', 'ignore').lstrip("$") for cell in line ]
            if line[-1:] == '0': continue
            ass_info.append(line)

    except:
        print str(datetime.now().strftime("%H:%M:%S")) + 'could not retrieve assessment info for ' + prop_id
        return 'SUSPICIOUS_RESP'

    #- step five: scrape info from portlandmaps.com      
    
    try:
        driver = webdriver.Firefox(firefox_profile=fp)
        driver.get(url) 
        tree = html.fromstring(driver.page_source)
        driver.quit()
    except:
        driver.quit()
        return 'CONNECTION_PROBLEM'

    try:

        cat = [x.strip().encode('ascii', 'ignore' ) for x in tree.xpath('//div[@id="general"]//dt/text()')]
        val = [x.strip().encode('ascii', 'ignore' ) for x in tree.xpath('//div[@id="general"]//dd/text()')]

        assessor = [cat,val]

        if assessor == [[], []]:
            print str(datetime.now().strftime("%H:%M:%S")) + 'could not retrieve portlandmaps for ' + prop_id
            return 'SUSPICIOUS_RESP'

        cat = [x.strip().encode('ascii', 'ignore' ) for x in tree.xpath('//div[@id="improvements"]//dt/text()')]
        val = [x.strip().encode('ascii', 'ignore' ) for x in tree.xpath('//div[@id="improvements"]//dd/text()')]

        improvements = [cat,val]

        rows = tree.xpath('//div[@id="improvements"]//table/tbody/tr')
        for row in rows:
            txt = [x.encode('ascii', 'ignore' ) for x in row.xpath('.//td/text()')]
            segments.append(txt)

    except:
        print str(datetime.now().strftime("%H:%M:%S")) + 'could not retrieve portlandmaps for  ' + prop_id
        return 'SUSPICIOUS_RESP'

    return [prop_id,land,deed_info,tax_info,ass_info,assessor,improvements,segments]



