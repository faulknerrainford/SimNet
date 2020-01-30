from neo4j import GraphDatabase
from Interface import Interface
from statistics import mean


def parselog(log):
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
    print(currenttimes)
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
        if history[0] - history[-1] < 0 and history[-1] > 14:
            intf.updatenode(tx, "Intervention", "cap", intf.getnodevalue(tx, "Intervention", "cap") + 1)
            return []
        elif history[0] - history[-1] > 5 and history[-10] < 14:
            intf.updatenode(tx, "Intervention", "cap", intf.getnodevalue(tx, "Intervention", "cap") - 1)
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
    while clock < 1000:
        dri = GraphDatabase.driver(flowreaction.uri, auth=("dancer", "dancer"))
        with dri.session() as ses:
            ses.write_transaction(flowreaction.applyrules, interface)
            tx = ses.begin_transaction()
            time = interface.gettime(tx)
            while clock == time:
                time = interface.gettime(tx)
            ses.end_transaction()
        dri.close()
