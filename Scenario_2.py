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
floater = Floater(env)
env.run()
"""
As of now self.take_payment is raising a value error for  %
Working on fix at the moment.
"""

# Floater moving for station
# If Balking Limit reached call floater
# While balking >= 5 call floater
# 
