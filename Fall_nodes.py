from SN_Node import Node
from numpy import exp, log
from random import random
from numpy.random import poisson, normal
from Fall_agent import FallAgent
import pickle
from Fall_Balancer import parselog


class FallNode(Node):

    def __init__(self, name, capacity=None, duration=None, queue=None):
        super(FallNode, self).__init__(name, capacity, duration, queue)

    def agentsready(self, tx, intf, agentclass="FallAgent"):
        super(FallNode, self).agentsready(tx, intf, agentclass)

    def agentperception(self, tx, agent, intf, dest=None, waittime=None):
        view = super(FallNode, self).agentperception(tx, agent, intf, dest, waittime)
        if type(view) == list:
            for edge in view:
                if "allowed" in edge.keys():
                    if not agent["referal"]:
                        view.remove(edge)
                    else:
                        allowed = edge["allowed"].split(',')
                        if not agent["wellbeing"] in allowed:
                            view.remove(edge)
            destinations = [edge.end_node["name"] for edge in view]
        else:
            destinations = [view.end_node["name"]]
            if "allowed" in view.keys():
                if not agent["referal"]:
                    view = []
                else:
                    allowed = view["allowed"].split(',')
                    if not agent["wellbeing"] in allowed:
                        view = []

        # If Care in options check for zero mobility
        if "Care" in destinations and agent["mob"] <= 0:
            view = [edge for edge in view if edge.end_node["name"] == "Care"]
        # If Hos and GP in options check for fall and return hos or GP,
        #  no prediction just straight check based on  mobility
        elif "Hos" in destinations and "GP" in destinations:
            if (r := random()) < exp(-3 * agent["mob"]):
                view = [edge for edge in view if edge.end_node["name"] == "Hos"]
                # Mark a sever fall has happened in agent log
                ag = FallAgent(agent["id"])
                ag.logging(tx, intf, "Sever Fall, " + str(intf.gettime(tx)))
                intf.updateagent(tx, agent["id"], "wellbeing", "Fallen")
            elif r < exp(-3 * (agent["mob"] - 0.1 * agent["mob"])):
                view = [edge for edge in view if edge.end_node["name"] == "GP"]
                # Mark a moderate fall has happened in agent log
                ag = FallAgent(agent["id"])
                ag.logging(tx, intf, "Moderate Fall, " + str(intf.gettime(tx)))
                intf.updateagent(tx, agent["id"], "wellbeing", "Fallen")
            elif r < exp(-3 * (agent["mob"] - 0.3 * agent["mob"])):
                # Mark a mild fall has happened in agent log
                ag = FallAgent(agent["id"])
                ag.logging(tx, intf, "Mild Fall, " + str(intf.gettime(tx)))
                intf.updateagent(tx, agent["id"], "wellbeing", "Fallen")
        return view

    def agentprediction(self, tx, agent, intf):
        return super(FallNode, self).agentprediction(tx, agent, intf)
        # Node specific only, no general node prediction assume no queue as default, thus no prediction needed


class HomeNode(FallNode):

    def __init__(self, name="Home", mc=-0.015, rr=0.3, cc=-0.02):
        super(HomeNode, self).__init__(name, queue={})
        self.mobchange = mc
        self.recoverrate = rr
        self.confchange = cc

    def agentsready(self, tx, intf, agentclass="FallAgent"):
        # Apply changes from waittime not dest
        agents = intf.getnodeagents(tx, self.name, "name")
        clock = intf.gettime(tx)
        if clock in self.queue.keys():
            for ag in agents:
                if ag["id"] in self.queue[clock].keys() and self.queue[clock][ag["id"]][1]:
                    self.mobchange = intf.getnodevalue(tx, self.name, "modm", "Node", "name")
                    self.confchange = intf.getnodevalue(tx, self.name, "modc", "Node", "name")
                    self.recoverrate = intf.getnodevalue(tx, self.name, "energy", "Node", "name")
                    intf.updateagent(ag["id"], "mob",
                                     normal((self.queue[clock][ag["id"]][1] * self.mobchange), 1, 1))
                    intf.updateagent(ag["id"], "conf",
                                     normal((self.queue[clock][ag["id"]][1] * self.confchange), 1, 1))
                    intf.updateagent(ag["id"], "energy", self.queue[clock][ag["id"]][1] * self.recoverrate)
        super(HomeNode, self).agentsready(tx, intf)

    def agentperception(self, tx, agent, intf, dest=None, waittime=None):
        return super(HomeNode, self).agentperception(tx, agent, intf, dest, waittime)

    def agentprediction(self, tx, agent, intf):
        view = intf.perception(tx, agent["id"])[1:]
        minenergy = min([edge["energy"] for edge in view if edge["energy"]] + [edge.end_node["energy"] for edge in view
                                                                               if edge.end_node["energy"]])
        recoverytime = (minenergy - agent["energy"]) / self.recoverrate
        if agent["energy"] < minenergy:
            (falltime, falltype) = self.predictfall(agent["mob"])
            t = 1
            mob = agent["mob"]
            while t < falltime:
                mob = mob + self.mobchange
                (nfalltime, nfalltype) = self.predictfall(mob)
                if nfalltime + t < falltime:
                    (falltime, falltype) = (nfalltime + t, nfalltype)
                t = t + 1
            if falltime < recoverytime and not falltype == "Mild":
                # Add agent to queue with fall
                queuetime = falltime + intf.gettime(tx)
                intf.updateagent(tx, agent["id"], "wellbeing", "Fallen")
                if queuetime not in self.queue.keys():
                    self.queue[queuetime] = {}
                if falltype == "Sever":
                    dest = [edge for edge in view if edge.end_node["name"] == "Hos"]
                    self.queue[queuetime][agent["id"]] = (dest[0], falltime)
                    ag = FallAgent(agent["id"])
                    ag.logging(tx, intf, "Sever Fall, " + str(queuetime))
                elif falltype == "Moderate":
                    dest = [edge for edge in view if edge.end_node["name"] == "GP"]
                    self.queue[queuetime][agent["id"]] = (dest[0], falltime)
                    ag = FallAgent(agent["id"])
                    ag.logging(tx, intf, "Moderate Fall, " + str(queuetime))
            else:
                # Add agent to queue with recovery
                if falltype == "Mild":
                    queuetime = falltime + intf.gettime(tx)
                    ag = FallAgent(agent["id"])
                    ag.logging(tx, intf, "Mild Fall, " + str(queuetime))
                    intf.updateagent(tx, agent["id"], "wellbeing", "Fallen")
                if recoverytime + intf.gettime(tx) not in self.queue.keys():
                    self.queue[recoverytime + intf.gettime(tx)] = {}
                self.queue[recoverytime + intf.gettime(tx)][agent["id"]] = (None, recoverytime)
        else:
            # Add agent to next time step - no waittime or dest
            if intf.gettime(tx) + 1 not in self.queue.keys():
                self.queue[intf.gettime(tx) + 1] = {}
            self.queue[intf.gettime(tx) + 1][agent["id"]] = (None, None)

    @staticmethod
    def predictfall(mobility):
        serverfallprediction = poisson(-log(1 - mobility), 1)
        falltype = "Sever"
        falltime = serverfallprediction
        moderatefallprediction = poisson(-log(1 - (mobility - 0.1 * mobility)), 1)
        if moderatefallprediction < falltime:
            falltype = "Moderate"
            falltime = moderatefallprediction
        mildfallprediction = poisson(-log(1 - (mobility - 0.3 * mobility)), 1)
        if mildfallprediction < falltime:
            falltype = "Mild"
            falltime = mildfallprediction
        return falltime, falltype


class HosNode(FallNode):

    def __init__(self, name="Hos", mc=-0.1, rr=0.2, cc=-0.05):
        super(HosNode, self).__init__(name, queue={})
        self.mobchange = mc
        self.recoverrate = rr
        self.confchange = cc

    def agentsready(self, tx, intf, agentclass="FallAgent"):
        # Apply changes from waittime not dest
        agents = intf.getnodeagents(tx, self.name)
        clock = intf.gettime(tx)
        if clock in self.queue.keys() and agents:
            for ag in agents:
                if ag["id"] in self.queue[clock].keys() and self.queue[clock][ag["id"]][1]:
                    self.mobchange = intf.getnodevalue(tx, self.name, "modm", "Node", "name")
                    self.confchange = intf.getnodevalue(tx, self.name, "modc", "Node", "name")
                    self.recoverrate = intf.getnodevalue(tx, self.name, "energy", "Node", "name")
                    intf.updateagent(tx, ag["id"], "mob",
                                     normal((self.queue[clock][ag["id"]][1] * self.mobchange), 1, 1)[0])
                    intf.updateagent(tx, ag["id"], "conf",
                                     normal((self.queue[clock][ag["id"]][1] * self.confchange), 1, 1)[0])
                    intf.updateagent(tx, ag["id"], "energy", self.queue[clock][ag["id"]][1] * self.recoverrate)
                    intf.updateagent(tx, ag["id"], "referal", True)
                    agent = FallAgent(ag["id"])
                    agent.logging(tx, intf, "Hos discharge, " + str(intf.gettime(tx)))
        super(HosNode, self).agentsready(tx, intf)

    def agentperception(self, tx, agent, intf, dest=None, waittime=None):
        return super(HosNode, self).agentperception(tx, agent, intf, dest, waittime)

    def agentprediction(self, tx, agent, intf):
        view = super(HosNode, self).agentprediction(tx, agent, intf)[1:]
        clock = intf.gettime(tx)
        ag = FallAgent(agent["id"])
        ag.logging(tx, intf, "Hos admitted, " + str(clock))
        mean = min(-9 * min(agent["mob"], 1) + 14, -9 * (min(agent["conf_res"], 1) + min(agent["mob_res"], 1)) + 14)
        time = poisson(mean, 1)[0]
        if clock + time not in self.queue.keys():
            self.queue[clock + time] = {}
        dest = [edge for edge in view if edge.end_node["name"] == "Home"]
        self.queue[clock + time][agent["id"]] = (dest[0], time)


class GPNode(FallNode):

    def __init__(self, name="GP"):
        super(FallNode, self).__init__(name)

    def agentsready(self, tx, intf, agentclass="FallAgent"):
        super(FallNode, self).agentsready(tx, intf, agentclass)

    def agentperception(self, tx, agent, intf, dest=None, waittime=None):
        view = super(GPNode, self).agentperception(tx, agent, intf, dest, waittime)
        if agent["mob"] < 0.6:
            view = [edge for edge in view if edge.end_node["name"] == "Hos"]
        else:
            view = [edge for edge in view if edge.end_node["name"] == "Home"]
            if agent["mob"] < 0.85:
                intf.updateagent(tx, agent["id"], "referal", True)
        return view

    def agentprediction(self, tx, agent, intf):
        return None
        # No queue so prediction not needed


class SocialNode(FallNode):

    def __init__(self, name="Social"):
        super(FallNode, self).__init__(name)

    def agentsready(self, tx, intf, agentclass="FallAgent"):
        super(FallNode, self).agentsready(tx, intf, agentclass)

    def agentperception(self, tx, agent, intf, dest=None, waittime=None):
        view = super(SocialNode, self).agentperception(tx, agent, intf, dest, waittime)
        return view

    def agentprediction(self, tx, agent, intf):
        return None
        # No queue so prediction not needed


class InterventionNode(FallNode):

    def __init__(self, name="Intervention"):
        super(FallNode, self).__init__(name)

    def agentsready(self, tx, intf, agentclass="FallAgent"):
        load = len(intf.getnodeagents(tx, self.name))
        super(FallNode, self).agentsready(tx, intf, agentclass)
        intf.updatenode(tx, self.name, "load", load, "name")

    def agentperception(self, tx, agent, intf, dest=None, waittime=None):
        view = super(InterventionNode, self).agentperception(tx, agent, intf, dest, waittime)
        ag = FallAgent(agent["id"])
        ag.logging(tx, intf, "Intervention, " + str(intf.gettime(tx)))
        if agent["mob"] > 0.6:
            intf.updateagent(tx, agent["id"], "referal", "False", "name")
        return view

    def agentprediction(self, tx, agent, intf):
        return None
        # No queue so prediction not needed


class CareNode:

    def __init__(self, rn):
        self.name = "Care"
        self.runname = rn
        self.agents = 0
        self.interval = 0

    def agentsready(self, tx, intf):
        agents = intf.getnodeagents(tx, "Care", "name")
        file = open("AgentLogs" + self.runname + ".p", 'wb')
        for agent in agents:
            agl = parselog(agent["log"])
            agint = agl[-1][1] - agl[0][1]
            self.interval = (self.interval * self.agents + agint) / (self.agents + 1)
            self.agents = self.agents + 1
            intf.updatenode(tx, "Care", "interval", self.interval, "name")
            aglog = "Agent " + str(agent["id"]) + ": " + agent["log"]
            pickle.dump(aglog, file)
            intf.deleteagent(tx, agent, "id")
        file.close()
        return None

    # While Care is not actually a node it does have an agentready function which is triggered on arrival.
    # This causes the agents log to be saved to file.
