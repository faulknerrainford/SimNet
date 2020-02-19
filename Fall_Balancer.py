from neo4j import GraphDatabase
from Interface import Interface
from statistics import mean


def parselog(log):
    while isinstance(log, list):
        log = log[0]
    log = log.split("), (")
    log[0] = log[0].replace("(", "")
    log[-1] = log[-1].replace(")", "")
    log = [entry.split(",") for entry in log]
    log = [(entry[0], int(entry[1])) for entry in log]
    return log


def timesincedischarge(tx, intf):
    times = []
    agents = intf.getnodeagents(tx, "Intervention", "name")
    for agent in agents:
        log = parselog(agent["log"])
        log.reverse()
        lasthosdis = [entry for entry in log if entry[0] == "Hos discharge"]
        if lasthosdis:
            lasthosdis = lasthosdis[0]
            times = times + [intf.gettime(tx) - lasthosdis[1]]
    return times


def adjustcapasity(tx, intf, history):
    currenttimes = timesincedischarge(tx, intf)
    if not currenttimes and history:
        currentav = history[-1]
    elif not currenttimes:
        currentav = 14
    else:
        currentav = mean(currenttimes)
    history = history + [currentav]
    # If it has been less than 20 time steps since last change do nothing
    if len(history) < 20:
        return history
    else:
        if history[-5] - history[-1] < -1 and history[-1] > 5:
            intf.updatenode(tx, "Intervention", "cap", intf.getnodevalue(tx, "Intervention", "cap", uid="name") + 1,
                            "name")
            return []
        elif history[-5] - history[-1] > 0 and history[-1] < 5:
            cap = max(1, intf.getnodevalue(tx, "Intervention", "cap", uid="name") - 1)
            intf.updatenode(tx, "Intervention", "cap", cap, "name")
            return []
        else:
            return history


class FallFlowReaction:

    def __init__(self):
        self.uri = "bolt://localhost:7687"
        self.storage = []

    def applyrules(self, tx, intf):
        self.storage = adjustcapasity(tx, intf, self.storage)


if __name__ == '__main__':
    flowreaction = FallFlowReaction()
    interface = Interface()
    clock = 0
    dri = GraphDatabase.driver(flowreaction.uri, auth=("dancer", "dancer"))
    while clock < 2000:
        with dri.session() as ses:
            ses.write_transaction(flowreaction.applyrules, interface)
            tx = ses.begin_transaction()
            time = interface.gettime(tx)
            while clock == time:
                clock = interface.gettime(tx)
    dri.close()
