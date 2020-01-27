import Node
from numpy import exp, log
from random import random
from numpy.random import poisson, normal
from Fall_agent import FallAgent


class FallNode(Node):

    def __init__(self, name, capacity=None, duration=None, queue=None):
        super(FallNode, self).__init__(self, name, capacity, duration, queue)

    def agentsready(self, tx, intf):
        super(FallNode, self).agentsready(tx, intf, FallAgent)

    def agentperception(self, tx, agent, intf, dest=None, waittime=None):
        view = super(FallNode, self).agentperception(tx, agent, intf, dest, waittime)
        destinations = [edge.end_node["name"] for edge in view]
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
                ag.log(tx, intf, "Sever Fall, " + str(intf.gettime()))
            elif r < exp(-3 * (agent["mob"] - 0.1 * agent["mob"])):
                view = [edge for edge in view if edge.end_node["name"] == "GP"]
                # Mark a moderate fall has happened in agent log
                ag = FallAgent(agent["id"])
                ag.log(tx, intf, "Moderate Fall, " + str(intf.gettime()))
            elif r < exp(-3 * (agent["mob"] - 0.3 * agent["mob"])):
                # Mark a mild fall has happened in agent log
                ag = FallAgent(agent["id"])
                ag.log(tx, intf, "Mild Fall, " + str(intf.gettime()))
                return view
        return view

    def agentprediction(self, tx, agent, intf):
        super(FallNode, self).agentprediction(tx, agent, intf)
        # Node specific only, no general node prediction assume no queue as default, thus no prediction needed


class HomeNode(FallNode):

    def __init__(self, name="Home", mc=-0.015, recoverrate=0.3):
        super(HomeNode, self).__init__(self, name)
        self.mobchange = mc
        self.recoverrate = recoverrate

    def agentsready(self, tx, intf):
        # Apply changes from waittime not dest
        agents = intf.getnodeagents(tx, self)
        clock = intf.gettime(tx)
        if self.queue[clock]:
            for ag in agents:
                if ag["id"] in self.queue[clock].keys() and self.queue[clock][ag["id"]][1]:
                    intf.updateagent(ag["id"], "mobility",
                                     normal((self.queue[clock][ag["id"]][1] * self.mobchange), 1, 1))
        super(HomeNode, self).agentsready(tx, intf)

    def agentperception(self, tx, agent, intf, dest=None, waittime=None):
        return super(HomeNode, self).agentperception(tx, agent, intf, dest, waittime)

    def agentprediction(self, tx, agent, intf):
        view = intf.perception(tx, agent)[1:]
        minenergy = min([edge["energy"] for edge in view])
        recoverytime = (minenergy - agent["energy"]) / self.recoverrate
        if agent["energy"] < minenergy:
            (falltime, falltype) = self.predictfall(agent["mobility"])
            t = 1
            mob = agent["mobility"]
            while t < falltime:
                mob = mob + self.mobchange
                (nfalltime, nfalltype) = self.predictfall(mob)
                if nfalltime + t < falltime:
                    (falltime, falltype) = (nfalltime + t, nfalltype)
                t = t + 1
            if falltime < recoverytime:
                # Add agent to queue with fall
                queuetime = falltime + intf.gettime()
                if falltype == "Sever":
                    self.queue[queuetime][agent["id"]] = ("Hos", falltime)
                elif falltype == "Moderate":
                    self.queue[queuetime][agent["id"]] = ("GP", falltime)
                elif falltype == "Mild":
                    self.queue[queuetime][agent["id"]] = (None, falltime)
            else:
                # Add agent to queue with recovery
                self.queue[recoverytime + intf.gettime()][agent["id"]] = ("Hos", recoverytime)
        else:
            # Add agent to next time step - no waittime or dest
            self.queue[intf.gettime() + 1][agent["id"]] = (None, None)

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

    def __init__(self, name="Hos"):
        super(HosNode, self).__init__(self, name)

    def agentsready(self, tx, intf):
        super(HosNode, self).agentsready(tx, intf)

    def agentperception(self, tx, agent, intf, dest=None, waittime=None):
        return super(HosNode, self).agentperception(tx, agent, intf, dest, waittime)

    def agentprediction(self, tx, agent, intf):
        clock = intf.gettime(tx)
        mean = min(-9 * agent["mobility"] + 14, -9 * (agent["confres"] + agent["mobres"] + 14))
        time = poisson(mean, 1)
        self.queue[clock + time][agent["id"]] = ("Home", time)


class GPNode(FallNode):

    def __init__(self, name="GP"):
        super(FallNode, self).__init__(self, name)

    def agentsready(self, tx, intf):
        super(FallNode, self).agentsready(self, tx, intf)

    def agentperception(self, tx, agent, intf, dest=None, waittime=None):
        view = super(GPNode, self).agentperception(tx, agent, intf, dest, waittime)
        if agent["mob"] < 0.6:
            view = [edge for edge in view if edge.end_node["name"] == "Hos"]
        elif agent["mob"] > 0.85:
            view = [edge for edge in view if edge.end_node["name"] == "Home"]
        else:
            view = [edge for edge in view if edge.end_node["name"] == "PT"]
        return view

    def agentprediction(self, tx, agent, intf):
        return None
        # No queue so prediction not needed


class SocialNode(FallNode):

    def __init__(self, name="Social"):
        super(FallNode, self).__init__(self, name)

    def agentsready(self, tx, intf):
        super(FallNode, self).agentsready(self, tx, intf)

    def agentperception(self, tx, agent, intf, dest=None, waittime=None):
        view = super(SocialNode, self).agentperception(tx, agent, intf, dest, waittime)
        return view

    def agentprediction(self, tx, agent, intf):
        return None
        # No queue so prediction not needed


class InterventionNode(FallNode):

    def __init__(self, name="Intervention"):
        super(FallNode, self).__init__(self, name)

    def agentsready(self, tx, intf):
        super(FallNode, self).agentsready(self, tx, intf)

    def agentperception(self, tx, agent, intf, dest=None, waittime=None):
        view = super(InterventionNode, self).agentperception(tx, agent, intf, dest, waittime)
        return view

    def agentprediction(self, tx, agent, intf):
        return None
        # No queue so prediction not needed


class CareNode():
