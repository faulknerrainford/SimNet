from matplotlib.pylab import *
from matplotlib import pyplot as plt
import pickle
from Fall_Balancer import parselog


# import scipy.stats as sps


def systeminterval(agent_log):
    # work out if care or active agent based on last entry
    if agent_log[-1][0] == "Care":
        # system interval for care based on care and create times
        return agent_log[-1][1] - agent_log[0][1]
    else:
        # system interval for active based on 2000 - create times
        return 2000 - agent_log[0][1]


# Find each hospital discharge and find the next intervention and add to list, return list
def interventioninterval(agent_log):
    times = []
    discharge_time = None
    for entry in agent_log:
        if entry[0] == "hospital discharge":
            discharge_time = entry[1]
        elif entry[0] == "intervention" and discharge_time:
            times.append(entry[1] - discharge_time)
            discharge_time = None
    return times


def counters(agent_log):
    mild = None
    moderate = None
    severe = None
    recovery = None
    for entry in agent_log:
        if entry[0] == "Mild Fall":
            mild = mild + 1
        elif entry[0] == "Moderate Fall":
            moderate = moderate + 1
        elif entry[0] == "Sever Fall":
            severe = severe + 1
        elif entry[0] == "Healthy":
            recovery = recovery + 1
    falls = mild + moderate + severe
    return [mild, moderate, severe, falls, recovery]


# Load active agents for each system run into a set for each system, use a for loop
aal_control = []
aal_at_risk = []
aal_health = []
cal_control = []
cal_at_risk = []
cal_health = []

for i in range(1, 6):
    pickle_in = open("logs_contrl_" + str(i) + ".p", "rb")
    aal_control.append(pickle.load(pickle_in))
    pickle_in.close()
    pickle_in = open("logs_atrisk_" + str(i) + ".p", "rb")
    aal_at_risk = aal_at_risk + pickle.load(pickle_in)
    pickle_in.close()
    pickle_in = open("logs_health_" + str(i) + ".p", "rb")
    aal_health = aal_health + pickle.load(pickle_in)
    pickle_in.close()
    # Load care agents for each system run into a set for each system, possibly with in the above for loop,
    # note the parsing needs to be a little different
    pickle_in_control = open("AgentLogscareag_contrl_" + str(i) + ".p", "rb")
    while True:
        try:
            cal_control.append(pickle.load(pickle_in_control))
        except EOFError:
            break
    pickle_in_control.close()
    pickle_in_at_risk = open("AgentLogscareag_atrisk_" + str(i) + ".p", "rb")
    while True:
        try:
            cal_at_risk.append(pickle.load(pickle_in_at_risk))
        except EOFError:
            break
    pickle_in_at_risk.close()
    pickle_in_health = open("AgentLogscareag_health_" + str(i) + ".p", "rb")
    while True:
        try:
            cal_health.append(pickle.load(pickle_in_health))
        except EOFError:
            break
    pickle_in_health.close()
# Parse logs of both sorts into unified format for extracting data
aal_health = [parselog(agent[0]) for agent in aal_health]
aal_at_risk = [parselog(agent[0]) for agent in aal_at_risk]
aal_control = [parselog(agent[0]) for agent in aal_control]
cal_health = [parselog(agent.split(': ')[1]) for agent in cal_health]
cal_at_risk = [parselog(agent.split(': ')[1]) for agent in cal_at_risk]
cal_control = [parselog(agent.split(': ')[1]) for agent in cal_control]


# # Compare system intervals for active, care and both
# # Calculate each agents system interval for active and care agents.
# aal_health_si = [systeminterval(agent) for agent in aal_health]
# aal_control_si = [systeminterval(agent) for agent in aal_control]
# aal_at_risk_si = [systeminterval(agent) for agent in aal_at_risk]
# cal_health_si = [systeminterval(agent) for agent in cal_health]
# cal_control_si = [systeminterval(agent) for agent in cal_control]
# cal_at_risk_si = [systeminterval(agent) for agent in cal_at_risk]
# print("System Interval Comparisons:")
# print("aal_control vs aal_health: " + str(sps.mannwhitneyu(aal_control_si, aal_health_si)[1]))
# print("aal_control vs aal_at_risk: " + str(sps.mannwhitneyu(aal_control_si, aal_at_risk_si)[1]))
# print("cal_control vs cal_health: " + str(sps.mannwhitneyu(cal_control_si, cal_health_si)[1]))
# print("cal_control vs cal_at_risk: " + str(sps.mannwhitneyu(cal_control_si, cal_at_risk_si)[1]))
# print("control vs health: " + str(sps.mannwhitneyu(aal_control_si+cal_control_si, aal_health_si+cal_health_si)[1]))
# print("control vs at_risk: " + str(sps.mannwhitneyu(aal_control_si+cal_control_si, aal_at_risk_si+cal_at_risk_si)[1]))
#
# # Compare intervention intervals for both in all
# aal_health_ii = [interventioninterval(agent) for agent in aal_health]
# aal_control_ii = [interventioninterval(agent) for agent in aal_control]
# aal_at_risk_ii = [interventioninterval(agent) for agent in aal_at_risk]
# cal_health_ii = [interventioninterval(agent) for agent in cal_health]
# cal_control_ii = [interventioninterval(agent) for agent in cal_control]
# cal_at_risk_ii = [interventioninterval(agent) for agent in cal_at_risk]
# print("Intervention Interval Comparisons:")
# print("aal_control vs aal_health: " + str(sps.mannwhitneyu(aal_control_ii, aal_health_ii)[1]))
# print("aal_control vs aal_at_risk: " + str(sps.mannwhitneyu(aal_control_ii, aal_at_risk_ii)[1]))
# print("cal_control vs cal_health: " + str(sps.mannwhitneyu(cal_control_ii, cal_health_ii)[1]))
# print("cal_control vs cal_at_risk: " + str(sps.mannwhitneyu(cal_control_ii, cal_at_risk_ii)[1]))
# print("control vs health: " + str(sps.mannwhitneyu(aal_control_ii+cal_control_ii, aal_health_ii+cal_health_ii)[1]))
# print("control vs at_risk: " + str(sps.mannwhitneyu(aal_control_ii+cal_control_ii, aal_at_risk_ii+cal_at_risk_ii)[1]))

# TODO: Compare fall numbers for care and both
# TODO: Compare "recovery" rate: number of times an agent becomes healthy
# Compare fall numbers for active (if nothing in previous)
# Compare population distribution over time


def parametersetting():
    histdata = []
    for ind in range(1, 6):
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
        pickle_gin = open("graphdata_pset_" + str(ind) + ".p", "rb")
        [cap, interval, lifetime, t] = pickle.load(pickle_gin)
        histdata = append(histdata, cap)
        ax1.plot(t, cap, 'b-', label="Max capacity of Intervention")
        ax2.plot(t, interval, 'm-', label="Interval from Hospital to Intervention")
        ax3.plot(t, lifetime, 'g-', label="Interval from Start to Care")
        ax1.set_ylim((0, 10))
        ax1.set_xlim((0, max(t)))
        ax2.set_ylim((0, 10))
        ax2.set_xlim((0, max(t)))
        ax3.set_ylim((0, max(lifetime)))
        ax3.set_xlim((0, max(t)))
        plt.savefig("figure_pset_" + str(ind))
        pickle_gin.close()
    # Generate histograms
    figure()
    plt.hist(histdata, bins=7, range=(0.5, 7.5), density=True)
    plt.title("Frequency of capacity settings for interval")
    plt.savefig("histogram.png")
    plt.show()
