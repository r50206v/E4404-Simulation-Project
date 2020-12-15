'''
Our inventory size is 20 units
We are also comparing the inventory level threshold to refill our orange 
(e.g. if the inventory level is lower than 5, then we will refill our orange)

also we are comparing the pricing strategy to maximize our profit
'''
import package as pkg

if __name__ == "__main__":
    print(pkg.pricing.constant_price())