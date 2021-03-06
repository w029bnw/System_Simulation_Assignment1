#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 20:51:55 2020
@author: daveinman
"""

# -*- coding: utf-8 -*-
"""
Assignment 1: Restaurant Drive-Thru
Scenario 1: Dual Order Station Drive-Thru
Authors: David Inman and Brittany Woods
Date: 13 February 2020
"""

import random
import simpy
import matplotlib.pyplot as plt
import numpy as np

# Simulation Variables
RANDOM_SEED = 123245
NUM_STATIONS = 2
NUM_WAIT_SPOTS = 6
BALK_LIMIT = 10 / NUM_STATIONS
ARRIVAL_TIME = 1.0
PREP_TIME = 5.0
SIM_TIME = 60.0 * 12.0
ORDER_PAY_TIME = 1.0
PICKUP_TIME = 1.5

# Statistic Variables
NUM_SERVED = 0.0
TOTAL_BALKED = []
TOTAL_SERVED = []
VAR_LIST = [["Random Seed", RANDOM_SEED],
            ["Number of Stations", NUM_STATIONS],
            ["Number of Spots", NUM_WAIT_SPOTS],
            ["Balking Limit", BALK_LIMIT],
            ["Arrival Rate (minutes)", ARRIVAL_TIME],
            ["Preperation Food Rate (minutes)", PREP_TIME],
            ["Simulation Time (minutes)", SIM_TIME],
            ["Floater Interaction Time (minutes)", ORDER_PAY_TIME],
            ["Pickup Window Rate (minutes)", PICKUP_TIME]]

class DriveThru(object):

    def __init__(self, env):
        self.env = env
        self.station1 = simpy.Resource(env, BALK_LIMIT)
        self.station2 = simpy.Resource(env, BALK_LIMIT)
        self.floater1 = simpy.Resource(env, 1)
        self.floater2 = simpy.Resource(env, 1)
        self.window = simpy.Resource(env, 1)
        self.line = simpy.Resource(env, NUM_WAIT_SPOTS)
        self.cook = simpy.Resource(env, 1)

    def order_pay(self, name, order_t):
        yield self.env.timeout(order_t)
        f.write("%7.4f: %s has placed and paid for their order.\n" % (self.env.now, name))

    def prep(self, name, order_t):
        yield self.env.timeout(order_t)
        f.write("%7.4f: %s's order is ready for pick-up.\n" % (self.env.now, name))

    def pickup(self, name, pick_up_t):
        yield self.env.timeout(pick_up_t)
        f.write("%7.4f: %s has received their order and is leaving the line.\n" %(self.env.now, name))

def customer(env, name, drive_thru):
    """
    The floater process - each floater behaves like an order window that moves within
    the drive through.  The floater has the ability to both recieve and order, and recieve payment
    for that order

    The floater then moves that down from the customer to the next position in line.
    """

    # Arrives at drive-thru
    f.write("%7.4f: %s has arrived at the Drive-Thru.\n" % (env.now, name))

    # Decides whether to enter the drive-thru line
    # Balk_limit-1 because 1 of the 5 spots for each lane is the active customer
    # using the resource
    if(drive_thru.station1.count < BALK_LIMIT or drive_thru.station2.count < BALK_LIMIT):

        # Decides which station line to enter
        if(drive_thru.station1.count <= drive_thru.station2.count):
            request = drive_thru.station1.request()
            request2 = drive_thru.floater1.request()
            yield request & request2

            # Order and pay for food
            f.write('%7.4f: %s places their order with floater 1.\n' % (env.now, name))
            yield env.process(drive_thru.order_pay(name, random.expovariate(1.0 / ORDER_PAY_TIME)))

            f.write("%4d\n" % len(drive_thru.floater1.queue))
            drive_thru.floater1.release(request2)

            # Prep the food order
            req1 =  drive_thru.cook.request()
            req2 = drive_thru.line.request()
            yield req1 & req2

            f.write("%7.4f: %s's order has been received.\n" % (env.now, name))

            # Move to the pick-up line if there is room
            f.write("%7.4f: %s moves to the pick-up line.\n" % (env.now, name))
            drive_thru.station1.release(request)

            yield env.process(drive_thru.prep(name, random.expovariate(1.0 / PREP_TIME)))
            drive_thru.cook.release(req1)

            # Queue to the check-out window
            req3 = drive_thru.window.request()
            yield req3

            f.write("%7.4f: %s moves to the window.\n" % (env.now, name))
            drive_thru.line.release(req2)

            # Pickup and leave
            yield env.process(drive_thru.pickup(name, random.expovariate(1.0 / PICKUP_TIME)))
            drive_thru.window.release(req3)

            # Append value to list counter
            TOTAL_SERVED.append(name)


        else:
            request = drive_thru.station2.request()
            request2 = drive_thru.floater2.request()
            yield request & request2

            f.write('%7.4f: %s places their order with floater 2.\n' % (env.now, name))
            yield env.process(drive_thru.order_pay(name, random.expovariate(1.0 / ORDER_PAY_TIME)))

            f.write("%4d\n" % len(drive_thru.floater2.queue))
            drive_thru.floater2.release(request2)

            # Prep the food order
            req1 =  drive_thru.cook.request()
            req2 = drive_thru.line.request()
            yield req1 & req2

            f.write("%7.4f: %s's order has been received.\n" % (env.now, name))

            # Move to the pick-up line if there is room
            f.write("%7.4f: %s moves to the pick-up line.\n" % (env.now, name))
            drive_thru.station2.release(request)

            # Prep the food order
            yield env.process(drive_thru.prep(name, random.expovariate(1.0 / PREP_TIME)))
            drive_thru.cook.release(req1)

            # Queue to the check-out window
            req3 = drive_thru.window.request()
            yield req3

            f.write("%7.4f: %s moves to the window.\n" % (env.now, name))
            drive_thru.line.release(req2)

            # Pay and leave
            yield env.process(drive_thru.pickup(name, random.expovariate(1.0 / PICKUP_TIME)))
            drive_thru.window.release(req3)

            # Append value to list counter
            TOTAL_SERVED.append(name)

    else:
        f.write("%s balked.\n" % (name))

        # Append Value to list counter
        TOTAL_BALKED.append(name)


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
f.write('Scarnario 2\n')
random.seed(RANDOM_SEED)

# Create an environment and start the setup process
env = simpy.Environment()
env.process(setup(env))
# Execute!
env.run()

# Sum Results for balked customers to the output file
balked = 0
for name in TOTAL_BALKED:
    balked += 1
f.write("Total customers balked in Scenario: %d\n" % balked)

# Sum Results for served customers to output file
served = 0
for name in TOTAL_SERVED:
    served += 1
total_cust = served + balked
f.write("Total customers served in Scenario: %d\n" % served)

# Print Table of Variables Used
f.write("\n\n| Variable | Value\n")
for item in VAR_LIST:
    f.write("| %s | %d \n" % (item[0], item[1]))

# Graphic to display values from Scenario bar chart
data = [served, balked, total_cust]
x = np.arange(3)
fig, ax = plt.subplots()
plt.bar(x, data, color=['blue', 'red', 'purple'])
plt.xticks(x, ('Served', 'Balked', 'Total Customers'))
plt.title("Scenario 2 Collected Data")
plt.ylabel("# of Customers")
plt.savefig('bar_chart.pdf')

# Close file
f.close()
