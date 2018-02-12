import numpy as np 
import matplotlib.pyplot as plt
import time
tick_length = .0001


client_times = np.load('client_times.npy')
server_times = np.load('server_times.npy')

time_diffs = (client_times - server_times) * tick_length
plt.plot(time_diffs)
print("average time diff: ", np.average(time_diffs))
print("sd: ", np.std(time_diffs))
print("3 sds above: ", np.average(time_diffs) + 3 * np.std(time_diffs))