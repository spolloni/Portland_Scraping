 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#                                                                     #
#  (c) Stefano Polloni                                                #
#                                                                     #
#  Created: 06/02/2016                                                #    
#  Updated: 06/02/2016                                                #
#                                                                     #  
#  Description: This function takes as an argument the pool worker    #
#               ID (integer), assigns the worker-specific proxy,      #
#               and returns the proxy port to use for scraping.       #                             
#                                                                     #
 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import csv
from random import seed, randint, choice, sample

proj = '/Users/stefanopolloni/GoogleDrive/Year3/'
dirc = 'congestion_value/portland/dofiles/scrape_realestate/mesh/ua/'
path = proj + dirc

def match_id(w_id,w):

    seed(w_id*randint(1000, 1500) - randint(10, 20)*w_id**2)

    if w_id in range(1,500,4):
        proxy = choice(['ch','us-fl'])
        with open(path + 'useragents_1.csv', 'rU') as csvfile:
            lines = list(csv.reader(csvfile))
    elif w_id in range(2,500,4):
        proxy = choice(['us-dc','us'])
        with open(path + 'useragents_2.csv', 'rU') as csvfile:
            lines = list(csv.reader(csvfile))
    elif w_id in range(3,500,4):
        proxy = choice(['us-il','ri'])
        with open(path + 'useragents_3.csv', 'rU') as csvfile:
            lines = list(csv.reader(csvfile))
    else:
        proxy = choice(['us-il','ri','us-dc','us','ch','us-fl'])
        with open(path + 'useragents_4.csv', 'rU') as csvfile:
            lines = list(csv.reader(csvfile))


    ua = sample(lines, 1)[0][0]
    ua_ind = sample(lines, 1)[0][1]

    return proxy, ua, ua_ind
