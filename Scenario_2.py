# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 09:14:55 2020

@author: 597844
"""

import simpy
import random

random_seed = 12345
number_of_stations = 2
number_of_pickup_windows = 1
max_number_of_customers_ready_to_order = 10
max_number_of_customers_ready_pickup = 6
number_of_customers = 100 # total number of customers
mean_interarrival_time = 2.0 #Generate new customers roughly every x minutes
mean_prep_time = 5.0 #minutes
mean_order_time = 2.0 #minutes
mean_pay_time = 2.0 #minutes
operating_timespan = 60.0 * 6.0 #minutes - We'll also check 2 hours before/after lunch

# Floater chain of events
# Take Order
# Take Payment
# Mover to next vehicle in line
class Floater:
	def __init__(self, env):
		self.env = env
		self.take_order = env.event()
		self.take_payment = env.process(self.order())
		self.move_on = env.process(self.order_complete())
			
	def order_complete(self):
		yield self.env.timeout(10) # arbitrary timeout interval
		self.take_order.succeed()
		self.take_order = self.env.event()
		print()
			
	def order(self):
		# to add for or while loop to count remaining customers in 
		# balking limit
		print('Order #%d taken, please pull forward!' % 1)
#		yield self.take_order


#console input for test
#floater = Floater(env)
#env.run()
"""
As of now self.take_payment is raising a value error for  %
Working on fix at the moment.
"""

# Floater moving for station
# If Balking Limit reached call floater
# While balking >= 5 call floater
# 
# -*- coding: utf-8 -*-

randseed = 125346
close_time = 50

def Arrival(env, delayTime, res):
  itemNo = 1
  workTime = 3
  while (env.now <= close_time):
    print ("Arrvial occurs at time %5.3f" % (env.now))
    env.process(Unit(env, itemNo, workTime, res))
    itemNo += 1
    yield env.timeout(delayTime)
    
def Unit(env, itemNo, workTime, res):
  r1 = res[0].request()
  print ("Order %d taken from line 1 at time %5.3f" % (itemNo, env.now))
  yield r1
 
  print ("Order %d picked up from window at time %5.3f" % (itemNo, env.now))
  yield env.timeout(workTime)
  
  r2 = res[1].request()
  print("Order %d taken from line 2 at time %5.3f" % (itemNo, env.now))
  yield r2
  # 
  
  res[0].release(r1)
  print("Line 1 is now taking new orders" )
	
  print("Order %d picked up from window at time %5.3f" % (itemNo, env.now))
  yield env.timeout(workTime)
  # print("Order %d )
  res[1].release(r2)
  print ("Line 2 s now taking new orders")
  
  
random.seed(randseed)

env = simpy.Environment()
res1 = simpy.Resource(env, 1)
res2 = simpy.Resource(env, 1)
res = [res1, res2]
env.process(Arrival(env, 5.0, res))


env.run()




