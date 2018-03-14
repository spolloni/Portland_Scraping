 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#                                                                       #
#  (c) Stefano Polloni                                                  #
#                                                                       #
#  Created: 01/30/2016                                                  #    
#  Updated: 01/30/2016                                                  #
#                                                                       #  
#  Description: This function coordinates infofetch.py, salesfetch.py,  #
#               and urlfetch.py into one function. Inputs are           #
#               house adress and adress_id, output is a dictionnary     #
#               containing all relevant data                            #
#                                                                       #
 #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

from salesfetch import get_deeds
from infofetch  import get_info
from urlfetch   import get_url
import collections, re

#- list of wanted zipcodes:

zips = range(97201,97207)
zips.extend(range(97208,97222))
zips.extend([97227,97228,97232,97236,97239,97266])
zips = [str(x) for x in zips]

def get_house(line,cookie,proxy,ua):

    #- objects to populate:

    house    = collections.OrderedDict()
    assessor = collections.OrderedDict()
    characteristics = collections.OrderedDict() 
    improvements    = collections.OrderedDict()

    #- unpack line: 

    city, state, zipc, address_id = line[9].strip(), line[11].strip(), line[12].strip(), line[0].strip()

    if zipc not in zips: 
        house["NOTE"] = 'OUT_OF_BOUNDS'
        del assessor, characteristics, improvements
        return house

    try:
        # include leading zeros to house number if appplicable
        num = str(int(line[3])).strip() + str(line[1]).strip()
    except:
        # otherwise grab house number
        num = str(line[1]).strip()  

    try:
        # split unit (apt) details
        j = line[8].strip().split()
        if len(j) == 1:
            ste = j[0].strip()
            ste = ste.translate(None, '-')
            ste = ste.translate(None, '/')
            ste = ste.translate(None, '+')
            ste = ste.translate(None, '#')
        elif len(j) == 2:
            ste = j[1].strip()
        else:
            raise ValueError('')
        if not line[4].strip():
            address = num + " " + line[5].strip() + " " + line[6].strip() + " " + ste
        else:
            address = num + " " + line[4].strip() + " " + line[5].strip() + " " + line[6].strip() + " " + ste
    except:
        if not line[4].strip():
            address = num + " " + line[5].strip() + " " + line[6].strip()
        else:
            address = num + " " + line[4].strip() + " " + line[5].strip() + " " + line[6].strip() 
 
    #- step one, scrape portlandmaps.com:

    step_one = get_deeds(address_id,cookie,proxy,ua)

    if step_one in ['CONNECTION_PROBLEM','SUSPICIOUS_RESP']:
        house["NOTE"] = step_one
        del assessor, characteristics, improvements
        return house

    if step_one == 'NOT_MATCHED':
        house["NOTE"] = 'NOT_MATCHED'
        del assessor, characteristics, improvements
        return house

    if step_one == 'PREV_SUCCESS':
        house["NOTE"] = 'PREV_SUCCESS'
        del assessor, characteristics, improvements
        return house

    if step_one == 'COMM_or_IND_LAND':
        house["NOTE"] = 'COMM_or_IND_LAND'
        del assessor, characteristics, improvements
        return house

    
    prop_id = step_one[0]


    #- step two, get urls from redfin.com:

    urls = get_url(address,proxy,ua)

    if urls in ['TIMEOUT_OR_NORESULTS','NO_ADRESSES']:
        house["NOTE"] = urls+" for "+prop_id+", "+address
        return house

    if urls in ['CONNECTION_PROBLEM','SUSPICIOUS_RESP','OOPS']:
        house["NOTE"] = urls
        return house

    #- step three, scrape from redfin.com:

    step_three = get_info(urls,prop_id,proxy,ua)

    if step_three in ['CONNECTION_PROBLEM','SUSPICIOUS_RESP']:
        house["NOTE"] = step_three
        return house 

    if step_three == 'PAGE_NOT_MATCHED':
        house["NOTE"] = 'PAGE_NOT_MATCHED'+" for "+prop_id+", "+address
        return house 
    

    #- populate results into house-dict:

    for i in range(len(step_three[0])):
        characteristics[str(step_three[0][i])] = str(step_three[1][i])

    for i in range(len(step_one[5][0])):
        assessor[str(step_one[5][0][i])] = str(step_one[5][1][i])

    for i in range(len(step_one[6][0])):
        improvements[str(step_one[6][0][i])] = str(step_one[6][1][i])

    house["address"]      = address
    house["property_id"]  = prop_id
    house["adress_id"]    = address_id
    house["land_type"]    = step_one[1]
    house["city"]         = city 
    house["attributes"]   = characteristics
    house["assessor"]     = assessor
    house["improvements"] = improvements
    house["segments"]     = step_one[7]
    house["deed_info"]    = step_one[2]
    house["county"]       = line[10]
    house["state"]        = state
    house["zip_code"]     = zipc
    house["zip_four"]     = line[13]
    house["x_coord"]      = line[15]
    house["y_coord"]      = line[16]
    house["tax_info"]     = step_one[3]
    house["assmnt_info"]  = step_one[4]
    
    house["NOTE"] = 'SUCCESS'

    return house

