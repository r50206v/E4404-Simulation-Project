'''
Customer arrival simulation: nonhomogeneous poisson process
Customer arrival follows a nonhomogeneous poisson process for each day, and we know that customers are likely to purchase more orange in winter and purchase less in summer.  
lambda(t) = -5*sin(2*pi*x/365) + 10

Each arrival is willing to buy x units of orange, which follows a discrete uniform distribution 
U(0,  int(-price*0.05 + freshness*(50-price)/300))
'''
import numpy as np


class Customers(object):

    def __init__(self, seed=None, demand_attr=(-0.05, 50, 300), arrival_attr=(30, 2, 2)):
        self.seed = seed
        self.demand_attr = demand_attr
        self.arrival_attr = arrival_attr


    def demand_function(self):
        d, e, f = self.demand_attr
        return lambda price, freshness: np.ceil(d*price + freshness*(e-price)/f)

    
    def get_demand(self, price, freshness):
        random_state = np.random.RandomState(seed=self.seed)
        max_demand = self.demand_function()(price, freshness)
        max_demand = max_demand * (max_demand > 0)
        demand = random_state.randint(0, max_demand)
        return demand


    def arrival_function(self):
        a, b, c = self.arrival_attr
        return lambda t: a*(-np.sin(t*b*np.pi/365) + c)

    
    def get_arrival(self, T=365):
        random_state = np.random.RandomState(self.seed)
        all_time = np.linspace(0, T, 1000)
        arrival_func = self.arrival_function()
        max_lambda = max(arrival_func(all_time))

        t = -1 / max_lambda * np.log(random_state.rand())
        arrival_time = []
        while t < T:
            if random_state.rand() < arrival_func(t) / max_lambda:
                arrival_time.append(t)
            inter_arrival = -1/max_lambda * np.log(random_state.rand())
            t += inter_arrival
        
        return arrival_time


if __name__ == "__main__":
    customers = Customers(seed=0)
    price = 30
    freshness = 60
    print(customers.get_demand(price, freshness))

    print(customers.get_arrival())