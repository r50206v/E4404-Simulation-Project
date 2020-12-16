'''
inventory memangement: 
Freshness = 100 if the orange is stored within 5 days, 
60 if the orange is stored between 6~10 days, 
20 if the orange is stored between 11~15 days, 
when the orange is stored over 16 days, we are not allowed to sell it.
'''
from collections import OrderedDict
from exception import SelfDefinedException

class Inventory(object):
    def __init__(self, size=120):
        self.size = size
        self.inventory = OrderedDict()


    def get_current_volume(self):
        return sum(list(self.inventory.values()))


    def _check(self):
        if self.get_current_volume() <= self.size:
            return True
        else:
            return False


    def inventory_process(self, env):
        while True:
            yield env.timeout(5)
            current_time = env.now
            self.decay(current_time)
            if not self._check:
                raise SelfDefinedException("the volume of orange is larger than our inventory size")


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
            first_key = keys.pop(0)
            while keys:
                if current_time - first_key > 15 :
                    self.inventory.popitem(last=False)
                first_key = keys.pop(0)


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

    
    
if __name__ == "__main__":
    import simpy
    inv = Inventory()

    def refill_evey_ten_days(env, inv):
        while True:
            yield env.timeout(10)
            # refill the orange every 10 days with 30 volume
            inv.refill(env.now, 30)

    env = simpy.Environment()
    env.process(inv.inventory_process(env))
    env.process(refill_evey_ten_days(env, inv))
    env.run(until=365)