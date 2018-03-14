 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#                                                                     #
#  (c) Stefano Polloni                                                #
#                                                                     #
#  Created: 08/02/2016                                                #    
#  Updated: 08/02/2016                                                #
#                                                                     #  
#  Description: Main Function.                                        #                             
#                                                                     #
 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

from workerfun import task
from datetime import datetime
from functools import partial
import csv, random, os, shutil
import sys, time, glob
import multiprocessing

##########################

y = 500  # set lenght of runs
x = 25   # set desired lenght of chunks
proj = '/Users/stefanopolloni/GoogleDrive/Year3/congestion_value'
work = '/portland/dofiles/scrape_realestate/mesh/workspace/'
path = proj + work  

##########################

#- function to split list of addresses into chunks

def chunkIt(seq, num):
  avg = num
  out = []
  last = 0.0

  while last < len(seq):
    out.append(seq[int(last):int(last + avg)])
    last += avg

  return out

#- overwrite existing files:
try:
    os.remove( path + 'retries.csv')
except OSError:
    pass


#- load file with addresses into list
with open(path + 'address_data_200_250K.csv', 'rU') as csvfile:
    lines = list(csv.reader(csvfile, delimiter=',', quotechar='|'))

#- make list of rounds
rounds = chunkIt(lines,y)
lenght  = len(rounds)

#- PROCESSING

for i in range(34,lenght):

    print '\n' * 2
    print " ******* THIS IS ROUND " + str(i+1) + " OF " + str(lenght) + " ******* "
    print '\n' * 2

    # split round into chunks
    chunks = chunkIt(rounds[i],x)

    # get current time and set # workers
    w = random.choice([6])
    h = int(datetime.now().strftime("%H")) 
    if h in range(2,10): w = random.choice([6])
    w=4

    # create partial function
    partial_task = partial(task,w)

    #- feed chunks to workers
    p = multiprocessing.Pool(processes=w)
    results = p.map(partial_task, chunks)

    #- populate retries into retry list
    retries = []
    for result in results:
        for line in result:
            retries.append(line)

    #- terminate pool        
    time.sleep(10)
    p.close()
    p.join()
    time.sleep(20)
      
    #- write retries to csv
    with open(path + 'retries.csv', 'a') as csvfile:
        wr = csv.writer(csvfile, delimiter=',')
        wr.writerows(retries)
   