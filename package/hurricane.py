'''
we assume the arrival of hurricane follows homogeneous poisson process
and the lambda for each month is the average occurance of each month since 1950 until 2009
'''
import requests
import numpy as np
import pandas as pd
from io import StringIO

class Hurricane(object):
    """
    this class provide all hurricane arrivals for a year, 
    acompany with the damage level as a list of tuple
    please use `get_all_arrival()` as the main function

    Args:
        seed: seed generator

    Returns:
        list of tuple: [(arrival date, damage level)]
        
        the arrival date is the time within t=0 and t=365
        the damage level represents percentage of orange selling price change
    """    

    link = 'https://psl.noaa.gov/data/timeseries/monthly/Hurricane/hurr.num.data'
    rs = requests.get(link)
    file = StringIO(str(rs.content).split("2009")[1].split("-999")[0].replace("\\n", '\n'))
    data = pd.read_table(file, sep='\s+', header=None, index_col=0)


    def __init__(self, seed=None):
        self.month_freq = self.data.mean(axis=0).div(30).to_dict()
        self.seed = seed


    @staticmethod
    def generate_arrival(lmbda, T=30, seed=None):
        random_state = np.random.RandomState(seed=seed)
        n = random_state.poisson(lam=T * lmbda, size=1)
        arrivals = random_state.uniform(0, T, size=n)
        arrivals = np.sort(arrivals)
        return arrivals


    def hurricane_simulation(self):
        result = []
        for k, v in self.month_freq.items():
            # generate arrival according to each month's lambda
            a = self.generate_arrival(v, T=30, seed=self.seed)
            # convert to our time scope, t=0 is 1/1, t=365 is 12/31
            a += 30*list(range(12))[k - 1]
            result.extend(a)
        return result


    @staticmethod
    def generate_damage_level(low=0, high=1, seed=None, size=1):
        random_state = np.random.RandomState(seed=seed)
        return random_state.uniform(low=low, high=high, size=size)


    def get_all_arrival(self):
        arrivals = self.hurricane_simulation()
        damage = self.generate_damage_level(seed=self.seed, size=len(arrivals))
        return list(zip(arrivals, damage))

    
if __name__ == "__main__":
    x = Hurricane()
    # print(x.hurricane_simulation())
    print(x.get_all_arrival())

    y = Hurricane(seed=0)
    # print(y.hurricane_simulation())
    print(y.get_all_arrival())