'''
inventory memangement: 
Freshness = 100 if the orange is stored within 5 days, 
60 if the orange is stored between 6~10 days, 
20 if the orange is stored between 11~15 days, 
when the orange is stored over 16 days, we are not allowed to sell it.
'''
from collections import OrderedDict
from package.exception import SelfDefinedException


class Inventory(object):
    def __init__(self, size=120, debug=False):
        self.size = size
        self.inventory = OrderedDict()
        self.debug = debug


    def get_current_volume(self):
        return sum(list(self.inventory.values()))


    def _check(self):
        if self.get_current_volume() <= self.size:
            return True
        else:
            return False


    def inventory_process(self, env):
        while True:
            yield env.timeout(1)
            current_time = env.now
            self.decay(current_time)
            if not self._check:
                raise SelfDefinedException("the volume of orange is larger than our inventory size")
            if self.debug:
                print(env.now, self.inventory)


    def refill(self, time, amount):
        # the newest stocks will be the last element
        if isinstance(time, float):
            time = int(time)
        if self.get_current_volume() + amount <= self.size:
            self.inventory[time] = amount
        else:
            raise SelfDefinedException("the volume of orange will be larger than our inventory size")


    def decay(self, current_time):
        # throw away all items stored over 16 days
        # FIFO: first in first out
        keys = list(self.inventory.keys())
        if len(keys) > 0:
            while keys:
                first_key = keys.pop(0)
                if current_time - first_key > 15 :
                    if self.debug:
                        print('The orange refill at t=%.2f are decayed (over 15 days), and %.2f oranges are removed' % (first_key, self.inventory[first_key]))
                    self.inventory.popitem(last=False)


    @staticmethod
    def transfer_freshness(x):
        if x <= 5:
            return 100
        elif x <= 10:
            return 60
        elif x <= 15:
            return 20
        else:
            return 0


    def get_freshness(self, current_time):
        ans = 0
        total_amount = 0
        for t, v in self.inventory.items():
            total_amount += v
            ans += self.transfer_freshness(current_time - t) * v

        if total_amount > 0:
            return ans / total_amount
        else:
            return 0 

    
    def selling(self, amount):
        keys = list(self.inventory.keys())
        key_index = 0

        while amount and self.get_current_volume() > 0:
            first_key = keys[key_index]

            if self.inventory[first_key] > amount:
                self.inventory[first_key] -= amount
                amount = 0
            else:
                amount -= self.inventory[first_key]
                del self.inventory[first_key]
                key_index += 1

        if amount and self.debug: 
            print('The request is larger than our inventory level')
