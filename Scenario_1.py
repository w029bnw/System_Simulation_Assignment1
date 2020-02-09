# -*- coding: utf-8 -*-
"""
Assignment 1: Restaurant Drive-Thru
Scenario 1: Dual Order Station Drive-Thru
Authors: David Inman and Brittany Woods
Date: 13 February 2020
"""

import random
import simpy

RANDOM_SEED = 123245
NUM_STATIONS = 2
NUM_WAIT_SPOTS = 6
BALK_LIMIT = 10 / NUM_STATIONS
ARRIVAL_TIME = 0.75
ORDER_TIME = 2.0
PREP_TIME = 5.0
PAY_TIME = 2.0
SIM_TIME = 60.0 * 6.0

class DriveThru(object):
    """A Drive-Thru has 2 order stations and 1 pick-up window to take and 
    deliver customer orders.
    
    Customers have to request an order station. Once they get one, they will 
    give their orders and the Drive-Thru will automatically begin preparing
    it in parallel as the customer requests a spot at the pay window. Once
    the customer has reached the pay window and their food is ready, they will
    pay and leave the Drive-Thru forever.
    
    """
    def __init__(self, env):
        self.env = env
        self.station1 = simpy.Resource(env, 1)
        self.station2 = simpy.Resource(env, 1)
        self.window = simpy.Resource(env, 1)
        self.line = simpy.Resource(env, NUM_WAIT_SPOTS)
        self.cook = simpy.Resource(env, 1)
        
    def order(self, name, order_t):
        """The order processes. It takes a ``customer`` processes and takes 
        their order."""
        yield self.env.timeout(order_t)
        
    def prep(self, name, prep_t):
        """The prep processes. It processes the previously placed order."""
        yield self.env.timeout(prep_t)
        f.write("%7.4f: %s's order is ready for pick-up.\n" % (self.env.now, name))
        
    def pay(self, name, pay_t):
        """The pay processes. It takes a ``customer`` processes and gives 
        their order."""
        yield self.env.timeout(pay_t)
        f.write("%7.4f: %s has paid for their order and left the drive-thru.\n" % (self.env.now, name))
        
def customer(env, name, drive_thru):
    """The customer precess (each customer has a ``name``) arrives at the
    drive-thru(``drive_thru``) and requests a service station.
    
    The customer then waits for their order to complete, approaches the window,
    pays for their order, and then leaves the drive-thru forever.
    
    """
    
    # Arrives at drive-thru
    f.write("%7.4f: %s has arrived at the Drive-Thru.\n" % (env.now, name))
    
    # Decides whether to enter the drive-thru line
    if(len(drive_thru.station1.queue) < BALK_LIMIT or len(drive_thru.station2.queue) < BALK_LIMIT):
        
        # Decides which station line to enter
        if(drive_thru.station1.count == 0 or (len(drive_thru.station1.queue) <= len(drive_thru.station2.queue) and (drive_thru.station1.count == 1 and drive_thru.station2.count == 1))):
            request = drive_thru.station1.request()
            yield request
                
            f.write('%7.4f: %s places their order at station 1.\n' % (env.now, name))
            yield env.process(drive_thru.order(name, random.expovariate(1.0 / ORDER_TIME)))
                
            f.write('%7.4f: %s has finished ordering at station 1.\n' % (env.now, name))
                
            # Prep the food order
            req1 =  drive_thru.cook.request()
            yield req1
            
            f.write("%7.4f: %s's order has been received.\n" % (env.now, name))
            yield env.process(drive_thru.prep(name, random.expovariate(1.0 / PREP_TIME)))  
            drive_thru.cook.release(req1)
            
            # Move to the pick-up line if there is room
            req2 = drive_thru.line.request()
            yield req2
            f.write("%4d\n" % drive_thru.line.count)
        
            f.write("%7.4f: %s moves to the pick-up line.\n" % (env.now, name))
            drive_thru.station1.release(request)
            
            # Queue to the check-out window
            req3 = drive_thru.window.request()
            yield req3
            
            f.write("%7.4f: %s moves to the window.\n" % (env.now, name))
            drive_thru.line.release(req2)
            
            # Pay and leave
            yield env.process(drive_thru.pay(name, random.expovariate(1.0 / PAY_TIME)))
            drive_thru.window.release(req3)

                
        else:
            request = drive_thru.station2.request()
            yield request
            
            f.write('%7.4f: %s places their order at station 2.\n' % (env.now, name))
            yield env.process(drive_thru.order(name, random.expovariate(1.0 / ORDER_TIME)))
            
            f.write('%7.4f: %s has finished ordering at station 2.\n' % (env.now, name))
                
            # Prep the food order
            req1 =  drive_thru.cook.request()
            yield req1
            
            f.write("%7.4f: %s's order has been received.\n" % (env.now, name))
            yield env.process(drive_thru.prep(name, random.expovariate(1.0 / PREP_TIME))) 
            drive_thru.cook.release(req1)
            
            # Move to the pick-up line if there is room
            req2 = drive_thru.line.request()
            yield req2
            f.write("%4d\n" % drive_thru.line.count)
        
            f.write("%7.4f: %s moves to the pick-up line.\n" % (env.now, name))
            drive_thru.station2.release(request)
            
            # Queue to the check-out window
            req3 = drive_thru.window.request()
            yield req3
            
            f.write("%7.4f: %s moves to the window.\n" % (env.now, name))
            drive_thru.line.release(req2)
            
            # Pay and leave
            yield env.process(drive_thru.pay(name, random.expovariate(1.0 / PAY_TIME)))
            drive_thru.window.release(req3)
        
    else:
        f.write('%s balked.\n' % (name))
        
            
def setup(env):
    """Create the drive-thru and have cars arrive every ``t_iter`` minutes."""
    # Create the drive-thru
    drive_thru = DriveThru(env)
    
    # Create more customers while the simulation is running
    i = 0
    while env.now < SIM_TIME:
        env.process(customer(env, 'Customer%02d' % i, drive_thru))
        yield env.timeout(random.expovariate(1.0 / ARRIVAL_TIME))
        i += 1

# Setup and start the simulation
f = open("output.txt", "w")
f.write('Scarnario 1\n')
random.seed(RANDOM_SEED)

# Create an environment and start the setup process
env = simpy.Environment()
env.process(setup(env))

# Execute!
env.run()
f.close()