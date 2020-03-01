from matplotlib.pylab import *
from matplotlib import pyplot as plt
import pickle
from Fall_Balancer import parselog
import scipy.stats as sps
import seaborn as sns


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
    mild = 0
    moderate = 0
    severe = 0
    recovery = 0
    for entry in agent_log:
        if entry[0] == "Mild Fall":
            mild = mild + 1
        elif entry[0] == "Moderate Fall":
            moderate = moderate + 1
        elif entry[0] == "Sever Fall":
            severe = severe + 1
        elif entry[0] == "Severe Fall":
            severe = severe + 1
        elif entry[0] == "Healthy":
            recovery = recovery + 1
    falls = mild + moderate + severe
    return [mild, moderate, severe, falls, recovery]


# function to produce box plots overlaying violin plots for set of distributions
def violinboxplots(plot_title, samples, labels):
    if len(samples) != len(labels):
        return ValueError("Samples and labels must have same length")
    x = []
    y = []
    for ind in range(len(samples)):
        x.append([labels[ind] for _ in samples[ind]])
        y.append(samples[ind])
    x = [item for sublist in x for item in sublist]
    y = [item for sublist in y for item in sublist]
    sns.violinplot(x, y, title=plot_title, palette="Pastel1")
    plt.show()


# function to produce effect size for a set of values
# none: 0.5-0.56, small: 0.56-0.64, medium: 0.64-0.71, large: >0.71
def effectsizes(sample1, sample2):
    [u1, pvalue] = sps.mannwhitneyu(sample1, sample2)
    m = len(sample1)
    n = len(sample2)
    r1 = u1 + (m * (m + 1)) / 2
    a12 = (r1 / m - (m + 1) / 2) / n
    if a12 < 0.5:
        a12 = 1 - a12
    return [pvalue, a12]


def effectsizeset(set_title, ac, ao, ah, ar, cc, co, ch, cr, c=None, o=None, h=None, r=None):
    if not c:
        c = ac + cc
    if not h:
        h = ah + ch
    if not r:
        r = ar + cr
    if not o:
        o = ao + co
    print(set_title)
    print("active control vs active open: Mann-whitey U p-value " +
          str(effectsizes(ac, ao)[0]) + " a-value " + str(effectsizes(ac, ao)[1]))
    print("active control vs active healthy: Mann-whitey U p-value " +
          str(effectsizes(ac, ah)[0]) + " a-value " + str(effectsizes(ac, ah)[1]))
    print("active control vs active at risk: Mann-whitey U p-value " +
          str(effectsizes(ac, ar)[0]) + " a-value " + str(effectsizes(ac, ar)[1]))
    print("care control vs care open: Mann-whitey U p-value " +
          str(effectsizes(cc, co)[0]) + " a-value " + str(effectsizes(cc, co)[1]))
    print("care control vs care healthy: Mann-whitey U p-value " +
          str(effectsizes(cc, ch)[0]) + " a-value " + str(effectsizes(cc, ch)[1]))
    print("care control vs care at risk: Mann-whitey U p-value " +
          str(effectsizes(cc, cr)[0]) + " a-value " + str(effectsizes(cc, cr)[1]))
    print("control vs open: Mann-whitey U p-value " +
          str(effectsizes(c, o)[0]) + " a-value " + str(effectsizes(c, o)[1]))
    print("control vs healthy: Mann-whitey U p-value " +
          str(effectsizes(c, h)[0]) + " a-value " + str(effectsizes(c, h)[1]))
    print("control vs at risk: Mann-whitey U p-value " +
          str(effectsizes(c, r)[0]) + " a-value " + str(effectsizes(c, r)[1]))


# Load active agents for each system run into a set for each system, use a for loop
aal_control = []
aal_at_risk = []
aal_health = []
aal_open = []
cal_control = []
cal_at_risk = []
cal_health = []
cal_open = []

for i in range(1, 6):
    pickle_in = open("logs_contrl_" + str(i) + ".p", "rb")
    aal_control = aal_control + pickle.load(pickle_in)
    pickle_in.close()
    pickle_in = open("logs_open_" + str(i) + ".p", "rb")
    aal_open = aal_open + pickle.load(pickle_in)
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
    pickle_in_open = open("AgentLogscareag_open_" + str(i) + ".p", "rb")
    while True:
        try:
            cal_open.append(pickle.load(pickle_in_open))
        except EOFError:
            break
    pickle_in_open.close()
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
print(len(cal_health))
print(len(cal_at_risk))
print(len(cal_open))
print(len(cal_control))
# Parse logs of both sorts into unified format for extracting data
aal_health = [parselog(agent[0]) for agent in aal_health]
aal_at_risk = [parselog(agent[0]) for agent in aal_at_risk]
aal_control = [parselog(agent[0]) for agent in aal_control]
aal_open = [parselog(agent[0]) for agent in aal_open]
cal_health = [parselog(agent.split(': ')[1]) for agent in cal_health]
cal_at_risk = [parselog(agent.split(': ')[1]) for agent in cal_at_risk]
cal_control = [parselog(agent.split(': ')[1]) for agent in cal_control]
cal_open = [parselog(agent.split(': ')[1]) for agent in cal_open]

# Get event counts from log
aal_open_ml = [counters(agent)[0] for agent in aal_open]
aal_open_md = [counters(agent)[1] for agent in aal_open]
aal_open_sv = [counters(agent)[2] for agent in aal_open]
aal_open_fl = [counters(agent)[3] for agent in aal_open]
aal_open_rc = [counters(agent)[4] for agent in aal_open]
cal_open_ml = [counters(agent)[0] for agent in cal_open]
cal_open_md = [counters(agent)[1] for agent in cal_open]
cal_open_sv = [counters(agent)[2] for agent in cal_open]
cal_open_fl = [counters(agent)[3] for agent in cal_open]
cal_open_rc = [counters(agent)[4] for agent in cal_open]
aal_health_ml = [counters(agent)[0] for agent in aal_health]
aal_health_md = [counters(agent)[1] for agent in aal_health]
aal_health_sv = [counters(agent)[2] for agent in aal_health]
aal_health_fl = [counters(agent)[3] for agent in aal_health]
aal_health_rc = [counters(agent)[4] for agent in aal_health]
cal_health_ml = [counters(agent)[0] for agent in cal_health]
cal_health_md = [counters(agent)[1] for agent in cal_health]
cal_health_sv = [counters(agent)[2] for agent in cal_health]
cal_health_fl = [counters(agent)[3] for agent in cal_health]
cal_health_rc = [counters(agent)[4] for agent in cal_health]
aal_control_ml = [counters(agent)[0] for agent in aal_control]
aal_control_md = [counters(agent)[1] for agent in aal_control]
aal_control_sv = [counters(agent)[2] for agent in aal_control]
aal_control_fl = [counters(agent)[3] for agent in aal_control]
aal_control_rc = [counters(agent)[4] for agent in aal_control]
cal_control_ml = [counters(agent)[0] for agent in cal_control]
cal_control_md = [counters(agent)[1] for agent in cal_control]
cal_control_sv = [counters(agent)[2] for agent in cal_control]
cal_control_fl = [counters(agent)[3] for agent in cal_control]
cal_control_rc = [counters(agent)[4] for agent in cal_control]
aal_at_risk_ml = [counters(agent)[0] for agent in aal_at_risk]
aal_at_risk_md = [counters(agent)[1] for agent in aal_at_risk]
aal_at_risk_sv = [counters(agent)[2] for agent in aal_at_risk]
aal_at_risk_fl = [counters(agent)[3] for agent in aal_at_risk]
aal_at_risk_rc = [counters(agent)[4] for agent in aal_at_risk]
cal_at_risk_ml = [counters(agent)[0] for agent in cal_at_risk]
cal_at_risk_md = [counters(agent)[1] for agent in cal_at_risk]
cal_at_risk_sv = [counters(agent)[2] for agent in cal_at_risk]
cal_at_risk_fl = [counters(agent)[3] for agent in cal_at_risk]
cal_at_risk_rc = [counters(agent)[4] for agent in cal_at_risk]

# # Compare fall numbers for care and both
effectsizeset("Fall Comparisons", aal_control_fl, aal_open_fl, aal_health_fl, aal_at_risk_fl, cal_control_fl,
              cal_open_fl, cal_health_fl, cal_at_risk_fl)
effectsizeset("Mild Fall Comparisons", aal_control_ml, aal_open_ml, aal_health_ml, aal_at_risk_ml, cal_control_ml,
              cal_open_ml, cal_health_ml, cal_at_risk_ml)
effectsizeset("Moderate Fall Comparisons", aal_control_md, aal_open_md, aal_health_md, aal_at_risk_md, cal_control_md,
              cal_open_md, cal_health_md, cal_at_risk_md)
effectsizeset("Severe Fall Comparisons", aal_control_sv, aal_open_sv, aal_health_sv, aal_at_risk_sv, cal_control_sv,
              cal_open_sv, cal_health_sv, cal_at_risk_sv)
# Compare "recovery" rate: number of times an agent becomes healthy
effectsizeset("Recovery Comparisons", aal_control_rc, aal_open_rc, aal_health_rc, aal_at_risk_rc, cal_control_rc,
              cal_open_rc, cal_health_rc, cal_at_risk_rc)

# Compare system intervals for active, care and both
# Calculate each agents system interval for active and care agents.
aal_health_si = [systeminterval(agent) for agent in aal_health]
aal_control_si = [systeminterval(agent) for agent in aal_control]
aal_at_risk_si = [systeminterval(agent) for agent in aal_at_risk]
aal_open_si = [systeminterval(agent) for agent in aal_open]
cal_health_si = [systeminterval(agent) for agent in cal_health]
cal_control_si = [systeminterval(agent) for agent in cal_control]
cal_at_risk_si = [systeminterval(agent) for agent in cal_at_risk]
cal_open_si = [systeminterval(agent) for agent in cal_open]
effectsizeset("System Interval Comparisons", aal_control_si, aal_open_si, aal_health_si, aal_at_risk_si,
              cal_control_si, cal_open_si, cal_health_si, cal_at_risk_si)


# # Compare intervention intervals for both in all
# aal_health_ii = [interventioninterval(agent) for agent in aal_health]
# aal_control_ii = [interventioninterval(agent) for agent in aal_control]
# aal_at_risk_ii = [interventioninterval(agent) for agent in aal_at_risk]
# aal_open_ii = [interventioninterval(agent) for agent in aal_open]
# cal_health_ii = [interventioninterval(agent) for agent in cal_health]
# cal_control_ii = [interventioninterval(agent) for agent in cal_control]
# cal_at_risk_ii = [interventioninterval(agent) for agent in cal_at_risk]
# cal_open_ii = [interventioninterval(agent) for agent in cal_open]
# effectsizeset("Intervention Interval Comparisons", aal_control_ii, aal_open_ii, aal_health_ii, aal_at_risk_ii,
#               cal_control_ii, cal_open_ii, cal_health_ii, cal_at_risk_ii)

# violinboxplots("Recovery Comparison", [cal_control_rc, cal_open_rc], ["Control", "Open Intervention"])
print(median(cal_control_rc))
print(median(cal_open_rc))


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
