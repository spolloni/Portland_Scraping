 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#                                                                     #
#  (c) Stefano Polloni                                                #
#                                                                     #
#  Created: 01/27/2016                                                #    
#  Updated: 01/27/2016                                                #
#                                                                     #  
#  Description: This function takes the list of plausible urls        # 
#               associated with a searched address and cross          #
#               checks with the county asessor ID to determine        #
#               which url corresponds to the right house. Once,       #
#               cross-checked, property information is taken from     #
#               the right URL.                                        #
#                                                                     #
 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

from lxml import html
import requests, sys
from datetime import datetime

#- use firefox header to avoid captcha 

firefox = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
    }  

def get_info(urls,prop_id,proxy,ua):

    def get_rdfn_prop_id(url):
    
        try:
            #- request and parse through html:
            if proxy != 'ri':
                page = requests.get(url, headers=firefox, proxies = proxies, auth = auth)
                tree = html.fromstring(page.content)
            else:
                page = requests.get(url, headers=firefox)
                tree = html.fromstring(page.content)
        except:
            return 'CONNECTION_PROBLEM'

        try: 

            #- extract prop_id on redfin page:
            rdfn_prop_id = tree.xpath('//div[@class="county-info-container"]/div[2]/span[2]/text()')[0]
            rdfn_prop_id = rdfn_prop_id.encode('ascii', 'ignore')

        except:
            rdfn_prop_id = "NULL"
            print str(datetime.now().strftime("%H:%M:%S")) + 'could not retrieve propID for ' + url
            return 'SUSPICIOUS_RESP'

        return [rdfn_prop_id,tree]

    #- set proxy:

    if proxy != 'ri':
        proxy_host = proxy+'.proxymesh.com'
        proxy_port = "31280"  
        auth = requests.auth.HTTPProxyAuth('spolloni', 'patate45')
        proxies = {"http": "http://{}:{}/".format(proxy_host, proxy_port)}  

    firefox["User-Agent"] = ua

    #- objects to be populated or used

    charact = []
    values  = []

    flag = 0

    #- collect info for redfin page with prop_id crosscheck

    for url in urls:


        result = get_rdfn_prop_id(url)

        if result == 'CONNECTION_PROBLEM': return 'CONNECTION_PROBLEM'
        if result == 'SUSPICIOUS_RESP': return 'SUSPICIOUS_RESP'

        rdfn_prop_id = result[0]
        tree = result[1]

        if rdfn_prop_id != prop_id:
            flag += 1
            continue

        try:

            #- obtain property characteristics
            columns = tree.xpath('//div[@class="median-values"][1]/table')

            #- populate into lists
            for column in columns:
                heads = column.xpath('.//td[@class="heading divider"]/text()')
                charact.extend(heads)
                data  = column.xpath('.//td[not(@class="heading divider")]/text()')
                values.extend([item.encode('ascii', 'ignore') for item in data])

        except:
            print str(datetime.now().strftime("%H:%M:%S")) + 'could not retrieve info for ' + url
            return 'SUSPICIOUS_RESP'

        try:

            #- obtain accessibility scores and populate into lists:
            types  = tree.xpath('//div[@class="viz-container"]//div[@class="iconAndLabel"]//a/text()')
            scores = tree.xpath('//div[@class="viz-container"]//div[@class="percentage"]/text()')
            charact.extend(types)
            values.extend(scores)

        except:
            print str(datetime.now().time()) + 'could not retrieve scores for ' + url
            return 'SUSPICIOUS_RESP'

        
        try:

            #- obtain school ratings and populate into lists:
            space   = " "
            ratings = []
            schools   = tree.xpath('//div[@class="schools-content"]//a[@class="school-name"]/text()')
            schools   = [space.join(school.split()[-2:]) for school in schools]
            schl_info = tree.xpath('//div[@class="schools-content"]//a[@class="school-name"]/@href')
            for link in schl_info:
                weburl = 'https://www.redfin.com'+link
                try:
                    if proxy != 'ri':
                        page = requests.get(weburl, headers=firefox, proxies = proxies, auth = auth)
                    else:
                        page = requests.get(weburl, headers=firefox)
                except:
                    return 'CONNECTION_PROBLEM'
                tree   = html.fromstring(page.content)
                rating = tree.xpath('//div[contains(@class,"inline-block badge gs-")]/@class')
                ratings.append(rating[0][-2:].lstrip("-"))
            charact.extend(schools)
            values.extend(ratings)

        except:
            print str(datetime.now().strftime("%H:%M:%S")) + 'could not retrieve schools for ' + url
            return 'SUSPICIOUS_RESP'

        charact.append("URL")
        values.append(url)

        break

    #- If no url was cross-checked:
    if flag==len(urls):
        return 'PAGE_NOT_MATCHED'

    return [charact,values]


