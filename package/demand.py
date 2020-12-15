'''
Customer arrival simulation: nonhomogeneous poisson process
Customer arrival follows a nonhomogeneous poisson process for each day, and we know that customers are likely to purchase more orange in winter and purchase less in summer.  
lambda(t) = -5*sin(2*pi*x/365) + 10

Each arrival is willing to buy x units of orange, which follows a discrete uniform distribution 
U(0,  int(-price*0.05 + freshness*(50-price)/300))
'''

def get_demand():
    pass


def get_arrival():
    pass
