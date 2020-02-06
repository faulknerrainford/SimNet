from neo4j import GraphDatabase
from Fall_nodes import *
from Interface import Interface


def activeagentsave(tx, activenodes, interface, rn):
    file = open("AgentLogs" + rn + ".p", 'wb')
    for anode in activenodes:
        agents = interface.getnodeagents(tx, anode.name)
        for agent in agents:
            record = "Agent " + str(agent["id"]) + ": " + agent["log"]
            pickle.dump(record, file)
    file.close()


if __name__ == '__main__':
    verbose = False
    uri = "bolt://localhost:7687"
    dri = GraphDatabase.driver(uri, auth=("dancer", "dancer"))
    nuid = "name"
    intf = Interface()
    runname = "careag_pset_1"
    nodes = [CareNode(runname), HosNode(), SocialNode(), GPNode(), InterventionNode(), HomeNode()]
    with dri.session() as ses:
        clock = 0
        while clock < 2000:
            for node in nodes:
                ses.write_transaction(node.agentsready, intf)
            res = ses.run("MATCH (a:Clock) "
                          "SET a.time = a.time + 1 "
                          "RETURN a.time")
            clock = res.values()[0][0]
            print("T: " + clock.__str__())
        for node in nodes:
            print(node.name)
            print(node.queue)
        ses.write_transaction(activeagentsave, nodes[1:], intf, runname)
    dri.close()
