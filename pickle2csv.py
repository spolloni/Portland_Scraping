import glob, random, os
import pickle, csv, time

path = '/Users/stefanopolloni/GoogleDrive/Year3/'

try:
    os.remove('pickles.csv')
except:
    pass

pickles = glob.glob(path+'pickles_leg/*.p')
#pickles = random.sample(pickles, 100)
lenght = len(pickles)

head = ['address', 'prop_id', 'addr_id', 'city', 'county', 'zipc', 'zipf', 'x', 'y']
head.extend(['lnd_type', 'lnd_area', 'int_area','is_condo', 'yr_built', 'floor']) 
head.extend(['roof_cov', 'roof_sty', 'bu_class', 'bu_hvac', 'foun_ty', 'interior'])
head.extend(['firepl','bath','cnst_sty','rm_desc', 'garage', 'pool', 'patio', 'shed'])

head.extend(['date_sold','pr_sold','instrmnt'])

with open('pickles.csv', 'a') as csvfile:
    wr = csv.writer(csvfile, delimiter=',')
    wr.writerow(head)

i = 0
for pickl in pickles:

    i += 1

    # load pickle:
    house  = pickle.load( open( pickl, "rb" ) )
    home   = {}

    #filter:
    try:
        ltype = house['general']['land_type']
    except: 
        continue 
    if 'RESIDENTIAL' not in ltype: continue
    try:
        temp = house['imprvmnts']['details']
    except:
        continue
    if house['sales_hist'] == []: continue

    #simple info:
    home['address'] = house['address']
    home['prop_id'] = house['property_id']
    home['addr_id'] = house['adress_id']
    home['city']    = house['city']
    home['county']  = house['county']
    home['state']   = house['state']
    home['zipc']    = house['zip_code']
    home['zipf']    = house['zip_four']
    home['x']       = house['x_coord']
    home['y']       = house['y_coord']

    #info from general and imprvmnts:
    try: 
        home['lnd_type'] = str(house['general']['land_type'])
    except:
        home['lnd_type']= ''
    try: 
        home['lnd_area'] = str(house['general']['total_land_area']).strip()
    except:
        home['lnd_area'] = ''
    try:
        home['is_condo'] = str(house['general']['is_condo'])
    except:
        home['is_condo'] = ''
    try:
        home['yr_built'] = str(house['imprvmnts']['actual_year_built'])
    except:
        home['yr_built'] = ''
    try:
        home['floor']    = str(house['imprvmnts']['flooring_type'])
    except:
        home['floor']    = ''
    try:
        home['roof_cov'] = str(house['imprvmnts']['roof_cover_type'])
    except:
        home['roof_cov'] = ''
    try:
        home['roof_sty'] = str(house['imprvmnts']['roof_style'])
    except:
        home['roof_sty'] = ''
    try:
        home['bu_class'] = str(house['imprvmnts']['building_class'])
    except:
        home['bu_class'] = ''
    try:
        home['bu_hvac']  = str(house['imprvmnts']['heating_ac_type'])
    except:
        home['bu_hvac']  = ''
    try:
        home['foun_ty']  = str(house['imprvmnts']['foundation_type'])
    except: 
        home['foun_ty']  = ''
    try:
        home['interior'] = str(house['imprvmnts']['interior_finish'])
    except: 
        home['interior'] = ''
    try:
        home['firepl']   = str(house['imprvmnts']['fireplace_type'])
    except: 
        home['firepl']   = ''
    try:
        home['bath']     = str(house['imprvmnts']['plumbing'])
    except: 
        home['bath']     = ''
    try:
        home['cnst_sty'] = str(house['imprvmnts']['construction_style'])
    except: 
        home['cnst_sty'] = ''
    try:
        home['rm_desc']  = str(house['imprvmnts']['room_descriptions'])
    except: 
        home['rm_desc']  = ''

    #improvement details: 
    gar      = 0
    pool     = 0
    patio    = 0 
    basement = 0
    footage  = 0
    shed     = 0 
    for detail in house['imprvmnts']['details']:
        if not detail['area_sq_ft']: continue
        #print detail
        if not any( seg in detail['segment_type'] for seg in ['CONCRETE','PORCH','DECK','PATIO','SHED','GAR','CARPORT','POOL','BLACKTOP']):
            footage += int(detail['area_sq_ft'])
        if 'GAR'  in detail['segment_type']: gar +=1
        if 'POOL' in detail['segment_type']: pool +=1
        if 'SHED' in detail['segment_type']: shed +=1
        if any( seg in detail['segment_type'] for seg in ['PORCH','DECK','PATIO']): patio +=1
    home['garage'] = '0'
    if gar > 0 : home['garage'] = '1'
    home['pool'] = '0'
    if pool > 0 : home['pool'] = '1'
    home['patio'] = '0'
    if patio > 0 : home['patio'] = '1'
    home['shed'] = '0'
    if shed > 0 : home['shed'] = '1'
    home['int_area'] = str(footage)

    #sales info:
    print
    if type(house['sales_hist']) is dict: house['sales_hist'] = [house['sales_hist']]
    for sale in house['sales_hist']:
        if not sale['sale_date']: continue
        if sale['sale_price'] == '$0.00': continue
        if 'DEED' not in sale['type']: continue
        home['date_sold']  = sale['sale_date']
        home['pr_sold']  = sale['sale_price']
        home['instrmnt'] = sale['type']
        row = []
        for var in head:
            row.append(home[var].encode('ascii'))
        with open('pickles.csv', 'a') as csvfile:
            wr = csv.writer(csvfile, delimiter=',')
            wr.writerow(row)

    print 'exported house '+str(i)+' of '+str(lenght)

