import random
import math
import time
sim_time=30
# Set the average rate of events (e.g., cars, packets) per unit time
_lambda = 5
# Set the number of total events to generate
_num_total_arrivals = sim_time*_lambda
# Initialize the number of arrivals per unit time
_num_arrivals = 0
# Initialize the arrival time
_arrival_time = time.time()
# Initialize the list of arrivals per unit time
_num_arrivals_in_unit_time = []
# Set the time tick (i.e., the length of each unit time interval)
_time_tick = _arrival_time+1
# Generate the events and record the number of arrivals per unit time
print('RANDOM_N,INTER_ARRIVAL_TIME,EVENT_ARRIVAL_TIME')
Start_time=time.time()
t=1
for i in range(_num_total_arrivals):
    # Get the next probability value from Uniform(0,1)
    p = random.random()
    # Plug it into the inverse of the CDF of Exponential(_lambda)
    #  In other words, the inverse CDF at a specific probability p gives you the number x for which Pr(X <= x) = p.
    #F(x) = 1 – e^(–Lx)   ==>  x = –log(1–u)/L
    #  This quantile helps in understanding the distribution and can be used to generate random numbers from the distribution using a uniform random variable.
    #By knowing the cumulative distribution function (CDF) of a distribution, you can always generate a random sample from that distribution using the inverse CDF technique. 
    _inter_arrival_time = -math.log(1.0 - p)/_lambda
    # Add the inter-arrival time to the running sum
    _arrival_time = _arrival_time + _inter_arrival_time
    # Increment the number of arrivals per unit time
    _num_arrivals = _num_arrivals + 1
    # If the arrival time is greater than the time tick, reset the number of arrivals and increment the time tick
    if _arrival_time > _time_tick:
        _num_arrivals_in_unit_time.append(_num_arrivals)
        _num_arrivals = 0
        _time_tick = _time_tick + 1
    # Print the random number, inter-arrival time, and event arrival time
    while time.time()<_arrival_time:
        time.sleep(0.0000000001)
    else:
        print(str(t)+"  "+str(p)+','+str(_inter_arrival_time)+','+str(_arrival_time))
    t=t+1
Finish_time=time.time()

# Print the number of arrivals in successive unit length intervals
print('\nNumber of arrivals in successive unit length intervals ===>',(Finish_time-Start_time))
print(_num_arrivals_in_unit_time,sum(_num_arrivals_in_unit_time),len(_num_arrivals_in_unit_time))
# Calculate and print the mean arrival rate for the sample
print('Mean arrival rate for sample:' + str(sum(_num_arrivals_in_unit_time)/len(_num_arrivals_in_unit_time)))