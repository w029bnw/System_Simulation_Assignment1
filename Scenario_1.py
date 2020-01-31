# -*- coding: utf-8 -*-
"""
Assignment 1: Restaurant Drive-Thru
"""

import random
import simpy

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

def customer_generator(env, stations, mean_interarrival_time, operating_timespan):
    i = 0
    while (env.now <= operating_timespan):
        c = customer(env,'Customer%02d' % i, stations, mean_order_time)
        env.process(c)
        interarrival_time = random.expovariate(1.0 / mean_interarrival_time)
        yield env.timeout(interarrival_time)
        i += 1

def customer(env, name, stations, mean_order_time):
    """
    Customers arrive, order, the order is prepped, they pay, and then they leave.
    """
    arrival_time = env.now
    print("%7.4f : %s has arrived." % (arrival_time, name))
   
    # Ordering
    station_1_ordering_count = stations[0].count
    station_2_ordering_count = stations[1].count
    station_1_waiting_to_order_count = len(stations[0].queue)
    station_2_waiting_to_order_count = len(stations[1].queue)
    
    print('Station 1: ordering: %4d waiting: %4d' % (station_1_ordering_count, station_1_waiting_to_order_count))
    print('Station 2: ordering: %4d waiting: %4d' % (station_2_ordering_count, station_2_waiting_to_order_count))
        
    balk_limit = max_number_of_customers_ready_to_order / number_of_stations
    if(station_1_waiting_to_order_count < balk_limit or station_2_waiting_to_order_count < balk_limit):
        
        # Check which line is shortest and get in that line
        if(station_1_waiting_to_order_count <= station_2_waiting_to_order_count):
            req = stations[0].request()
            
            yield req
        
            wait_time = env.now - arrival_time
        
            # Arrived at an ordering station
            print('%7.4f %s arrived at Station 1 and waited %6.3f' % (env.now, name, wait_time))
            order_time = random.expovariate(1.0 / mean_order_time)
            print('%7.4f %s: service time %6.3f' % (env.now, name, order_time))
        
            yield env.timeout(order_time)
        
            # Release the station
            stations[0].release(req)
            print('%7.4f %s: Finished ordering and left Station 1' % (env.now, name))
        
        else:
            req = stations[1].request()  
            
            yield req
        
            wait_time = env.now - arrival_time
        
            # Arrived at an ordering station
            print('%7.4f %s arrived at Station 2 and waited %6.3f' % (env.now, name, wait_time))
            order_time = random.expovariate(1.0 / mean_order_time)
            print('%7.4f %s: service time %6.3f' % (env.now, name, order_time))
        
            yield env.timeout(order_time)
        
            # Release the station
            stations[1].release(req)
            print('%7.4f %s: Finished ordering and left Station 2' % (env.now, name))
    
    else:
        print('%7.4f %s: Balked' % (env.now, name)) 

# Setup and start the simulation
print("Assignment 1: Two Service Stations")
random.seed(random_seed)
env = simpy.Environment() #Starts at t=0

# Start processes and run
station_1 = simpy.Resource(env, 1)
station_2 = simpy.Resource(env, 1)
stations = [station_1, station_2]
window = simpy.Resource(env, capacity=number_of_pickup_windows)
env.process(customer_generator(env, stations, mean_interarrival_time, operating_timespan))
env.run() 
	
