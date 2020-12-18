'''
Pricing strategy:
Constant price (e.g. 20 per orange)
Linear pricing strategy: a linear equation of inventory level 
(e.g. price = -0.75*current_inventory + 30)
'''

class Price(object):

    def __init__(self, max_price=30):
        self.max_price = max_price


    def constant_price(self, constant_price=None):
        if constant_price:
            return constant_price
        else:
            return self.max_price * 2/3


    def linear_price(self, current_inventory, a=-0.25):
        return a*current_inventory + self.max_price


if __name__ == "__main__":
    import numpy as np
    price = Price(30)
    print(price.constant_price(25))
    print(price.constant_price())

    current_inventory = np.arange(0, 120, 1)
    print(price.linear_price(current_inventory))