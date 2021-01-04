import simpy
import collections
import numpy as np
import pandas as pd
import scipy.stats as spst

from package import demand, pricing, inventory, hurricane


MAX_FRESHNESS = 100
MAX_PRICE = 130
MAX_INVENTORY = 200
CONSTANT_PRICE = 125
LINEAR_PRICE_BETA = -0.05
REFILL_UNIT = 50
STARTING_UNIT = 50

demand_attr = (-0.2, 100, 200)
arrival_attr = (30, 2, 60) #(-5, 2, 10)
total_day = 365


def get_all_default_parameters():
    global MAX_FRESHNESS
    global MAX_PRICE
    global MAX_INVENTORY
    global CONSTANT_PRICE
    global LINEAR_PRICE_BETA
    global REFILL_UNIT
    global STARTING_UNIT
    global demand_attr
    global arrival_attr
    global total_day
    return {'MAX_FRESHNESS': MAX_FRESHNESS, 'MAX_PRICE': MAX_PRICE, 
    'MAX_INVENTORY': MAX_INVENTORY, 'CONSTANT_PRICE': CONSTANT_PRICE, 
    'LINEAR_PRICE_BETA': LINEAR_PRICE_BETA, 'REFILL_UNIT': REFILL_UNIT, 
    'STARTING_UNIT': STARTING_UNIT, 'demand_attr': demand_attr, 
    'arrival_attr': arrival_attr, 'total_day': total_day}


def load_orange_price(string=None, divid=2, round_float=2):
    # return processed orange future data
    if string:
        from io import StringIO
        data = pd.read_csv(StringIO(string))
    else:
        data = pd.read_csv('Orange Juice Futures Historical Data.csv')
    data.index = pd.to_datetime(data['Date'], format='%b %d, %Y')
    data = data.sort_index()
    orange_price = data['Price'].resample('1D').ffill().div(divid).round(round_float)
    orange_price = orange_price.reset_index(drop=True)
    return orange_price


def get_orange_price(df, return_origin=False, seed=None):
    # load hurricane tuples and return processed final orange price
    hurr = hurricane.Hurricane(seed=seed)
    hurr_tuple = hurr.get_all_arrival()
    price_change = collections.defaultdict(int)
    for time, strike in hurr_tuple:
        time = int(time)
        for i in range(5):
            time += 1
            price_change[time] = strike
    price_change = pd.DataFrame.from_dict(price_change, orient='index', columns=['Strike'])
    df = pd.concat([df, price_change], axis=1).fillna(0)
    df['Final Price'] = df['Price'] * (1 + df['Strike'])
    return df['Final Price'] if not return_origin else df


def arrival(env, params, result):
    # simpy customers arrival process
    customers = demand.Customers(params['seed'], params['demand_attr'], params['arrival_attr'])
    arrival_time = customers.get_arrival()

    for a in arrival_time:
        yield env.timeout(a)
        price_kwargs = {
            'current_inventory': params['inventory_class'].get_current_volume(), 
            'constant_price': params['constant_price'], 
            'a': params['linear_price_beta']
        }
        
        if params['strategy'] == 'linear':
            current_price = params['price_strategy'].linear_price(**price_kwargs)
        else:
            current_price = params['price_strategy'].constant_price(**price_kwargs)
        
        current_freshness = params['inventory_class'].get_freshness(int(env.now))
        current_demand = customers.get_demand(current_price, current_freshness)
        current_inventory_level = params['inventory_class'].get_current_volume()

        # storing results
        result['revenueList'].append(
            min(current_demand, current_inventory_level) * current_price
        )
        result['freshList'].append(current_freshness)
        result['demandList'].append(current_demand)
        result['inventoryVolumeList'].append(current_inventory_level)
        result['fulfillList'].append(current_demand < current_inventory_level)
        
        
        params['inventory_class'].selling(current_demand)
        


def refill(env, params, result):
    # simpy inventory refill process
    params['inventory_class'].refill(0, params['starting_units'])
    result['refillTimeList'].append(0)
    result['costList'].append(params['orange_price'].loc[0] * params['starting_units'])
    
    
    while True:
        yield env.timeout(1)
        if params['inventory_class'].get_current_volume() <= params['inventory_class'].size * params['refill_percentage']:
            params['inventory_class'].refill(env.now, params['refill_units'])
            result['costList'].append(params['orange_price'].loc[int(env.now)] * params['refill_units'])
            result['refillTimeList'].append(env.now)


def system(orange_price, strategy='constant', refill_percentage=0.08, seed=None):
    # main simpy system environment
    global MAX_FRESHNESS
    global MAX_PRICE
    global MAX_INVENTORY
    global CONSTANT_PRICE
    global LINEAR_PRICE_BETA
    global REFILL_UNIT
    global STARTING_UNIT
    global demand_attr
    global arrival_attr
    global total_day
    
    inventory_class = inventory.Inventory(size=MAX_INVENTORY)
    price_strategy = pricing.Price(MAX_PRICE)
    arrival_params = {
        'strategy': strategy,
        'price_strategy': price_strategy,
        'inventory_class': inventory_class,
        'demand_attr': demand_attr,
        'arrival_attr': arrival_attr,
        'linear_price_beta': LINEAR_PRICE_BETA,
        'constant_price': CONSTANT_PRICE,
        'seed': seed
    }
    refill_params = {
        'inventory_class': inventory_class, 
        'refill_percentage': refill_percentage, 
        'orange_price': orange_price, 
        'refill_units': REFILL_UNIT, 
        'starting_units': STARTING_UNIT
    }


    result = collections.defaultdict(list)
    
    env = simpy.Environment()
    env.process(arrival(env, arrival_params, result))
    env.process(refill(env, refill_params, result))
    env.process(inventory_class.inventory_process(env, result))
    env.run(until=total_day)
    
    return result


def getAverageResult(*result_dict):
    
    result = collections.defaultdict(list)
    count = len(result_dict)
    
    for r in result_dict:
        result['Revenue'].append( sum(r['revenueList']) )
        result['Cost'].append( sum(r['costList']) )
        result['Profit'].append( sum(r['revenueList']) - sum(r['costList']) )
        result['CustomerZeroDemand'].append( sum(np.array(r['demandList']) == 0) / len(r['demandList']) )
        result['ZeroInventoryLevel'].append( sum(np.array(r['inventoryVolumeList']) == 0 ) / len(r['inventoryVolumeList']) )
        result['RefillTimes'].append( len(r['refillTimeList']) )
        result['NotFulfillRatio'].append( sum(~np.array(r['fulfillList'])) / len(r['fulfillList']) )
        result['Freshness'].append( sum(r['freshList']) / len(r['freshList']) )
        result['DecayUnits'].append( pd.DataFrame(r['decayList'], columns=['Time', 'Amount'])['Amount'].sum() )

    result['avgProfit'] = np.mean(result['Profit'])
    result['avgCost'] = np.mean(result['Cost'])
    result['avgRevenue'] = np.mean(result['Revenue'])
    result['avgCustomerZeroDemand'] = np.mean(result['CustomerZeroDemand'])
    result['avgZeroInventoryLevel'] = np.mean(result['ZeroInventoryLevel'])
    result['avgRefillTimes'] = np.mean(result['RefillTimes'])
    result['avgNotFulfillRatio'] = np.mean(result['NotFulfillRatio'])
    result['avgFreshness'] = np.mean(result['Freshness'])
    result['avgDecayUnits'] = np.mean(result['DecayUnits'])
        
    return result


def calculateConfidenceInterval(nums, names="", alpha=0.05, round_digit=3):
    mean = np.mean(nums)
    std = np.std(nums, ddof=1)
    z_score = spst.norm.ppf(1 - alpha/2)
    N = len(nums)
    
    lower = mean - z_score * std / N**0.5
    upper = mean + z_score * std / N**0.5
    print(
        '%s %.2f confidence interval: (%s, %s)' % (names, 1 - alpha, round(lower, round_digit), round(upper, round_digit))
    )