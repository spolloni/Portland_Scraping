 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#                                                                     #
#  (c) Stefano Polloni                                                #
#                                                                     #
#  Created: 04/02/2016                                                #    
#  Updated: 04/02/2016                                                #
#                                                                     #  
#  Description: This function takes as an argument a list of lines    #
#               from the adress_data.csv, sets up a proxy connexion,  #
#               gets a cookie, and retrieves data for that list.      #
#               The dictionary containing the data is then pickled.   #                             
#                                                                     #
 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

from housetask import get_house
from cookiemaker import make_cookie
from chooseproxy import match_id
from numpy.random import lognormal, seed
from datetime import datetime
import time, pickle, multiprocessing, os, sys, random

proj = '/Users/stefanopolloni/GoogleDrive/Year3'
work = '/congestion_value/portland/data/real_estate/pickles_nrf/'
path = proj + work

def task(w,lines):

    #- error catcher
    retries = []
    flag = 0

    #- retrieve worker id:
    w_id = int(multiprocessing.current_process().name[-2:].lstrip("-"))

    #- randomly select connection and user agent:
    proxy, ua, ua_ind  = match_id(w_id,w) 

    #- message:
    print 
    print "HELLO I AM WORKER #" + str(w_id)+" WORKING WITH "+proxy+" AND UA #"+ua_ind
    print "time: " + str(datetime.now().strftime("%H:%M:%S"))
    print 

    #- random big nap
    seed(w_id+random.randint(0,1000))
    time.sleep(min(14.3/w,lognormal(1.8/w,1.5)))

    #- get a cookie for multoproptax.com:
    cookie = make_cookie(proxy,ua)
    if cookie == "NO_COOKIE":
        print
        print "I DIDN'T GET A COOKIE :( GOODBYE!"
        print
        retries.extend(lines)
        return retries
  
    #- iterate through houses:
    for line in lines:

        #- random little nap
        time.sleep(min(7.4/w,lognormal(0.9/w,1.05)))

        house = get_house(line,cookie,proxy,ua)

        if house["NOTE"] == 'SUCCESS':
            filename = path + house["property_id"] + '.p'
            pickle.dump( house, open( filename, "wb" ) )
            print 'house #'+str(line[17])+': '+house["NOTE"]

        elif house["NOTE"] in ['CONNECTION_PROBLEM','SUSPICIOUS_RESP','OOPS']:
            retries.append(line)
            print 'house #'+str(line[17])+': '+house["NOTE"]+' with proxy'+proxy
            flag +=1
            if flag > 7: return retries

        else:
            print 'house #'+str(line[17])+' with id '+str(line[0])+' : '+house["NOTE"]

    return retries
