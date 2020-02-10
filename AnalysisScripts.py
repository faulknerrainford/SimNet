from matplotlib.pylab import *
from matplotlib import pyplot as plt
import pickle

histdata = []

for i in range(1, 6):
    # Set up plots
    fig = figure()
    fig.suptitle("Network Stats over Time")
    # Set up subplots with titles and axes
    ax1 = subplot2grid((1, 3), (0, 0))
    ax2 = subplot2grid((1, 3), (0, 1))
    ax3 = subplot2grid((1, 3), (0, 2))
    ax1.set_title('Intervention Capacity')
    ax1.set_ylabel("No. Agents")
    ax1.set_xlabel("Time")
    ax2.set_title('Intervention Interval')
    ax2.set_ylabel("Interval")
    ax2.set_xlabel("Time")
    ax3.set_title('System Interval')
    ax3.set_ylabel("Interval")
    ax3.set_xlabel("Time")
    pickle_gin = open("graphdata_pset_" + str(i) + ".p", "rb")
    [cap, interval, lifetime, t] = pickle.load(pickle_gin)
    histdata = append(histdata, cap)
    p1, = ax1.plot(t, cap, 'b-', label="Max capacity of Intervention")
    p2, = ax2.plot(t, interval, 'm-', label="Interval from Hospital to Intervention")
    p3, = ax3.plot(t, lifetime, 'g-', label="Interval from Start to Care")
    ax1.set_ylim((0, 10))
    ax1.set_xlim((0, max(t)))
    ax2.set_ylim((0, 10))
    ax2.set_xlim((0, max(t)))
    ax3.set_ylim((0, max(lifetime)))
    ax3.set_xlim((0, max(t)))
    plt.savefig("figure_pset_" + str(i))
    pickle_gin.close()
# # Generate histograms
# fig = figure()
# plt.hist(histdata, bins=7, range=(0.5, 7.5), density=True)
# plt.title("Frequency of capacity settings for interval")
# plt.savefig("histogram.png")
# plt.show()
