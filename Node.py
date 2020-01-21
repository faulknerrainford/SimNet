from abc import ABC, abstractmethod


class Node(ABC):

    def __init__(self, name, capacity=None, duration=None, queue=None, nuid="name"):
        self.name = name
        self.capacity = capacity
        self.duration = duration
        self.queue = queue
        self.nuid = nuid

    @abstractmethod
    def agentsready(self, tx, intf):
        agents = intf.getnodeagents(tx, self)
        clock = intf.gettime(tx)
        if not self.queue or self.queue[clock]:
            for ag in agents:
                if self.queue:
                    if ag["id"] in self.queue[clock].keys():
                        agper = self.agentperception(tx, ag, intf, self.queue[clock][ag["id"]][0],
                                                     self.queue[clock][ag["id"]])
                        ag.move(tx, intf, agper)
                else:
                    agper = self.agentperception(tx, ag, intf)
                    ag.move(tx, intf, agper)

    @abstractmethod
    def agentperception(self, tx, agent, intf, dest=None, waittime=None):
        if dest:
            return dest, waittime
        else:
            view = intf.perception(tx, agent)
            return view[1:], waittime

    # TODO: Add function to queue agents on arrival at node. Triggered by agent in move function.
    @abstractmethod
    def agentprediction(self, tx, agent, intf):
        view = intf.perception(tx, agent)
        return view

        # TODO:
        #  Subclass of fall nodes
        #  Takes options and checks for hospital
        #  Check for fall
        #  Check options available to agent
        #  Check for falls
        #  if fall return hos or gp
        #  return time and referrals for hos or gp
        #  Agent will check energy and return queue time based on perception or choice
        #  include how long they queued in perception
        #  return (options, wait time past, wait time future, fall, referral)
