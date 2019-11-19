# 2 rules
# Implemented through the interface for creation and deletion
# Look into passing class to interface, or creating a creation function in ToyAgent.


# 1. Delete Agents with no funds, find in pop delete using interface
#       - Find and return agents with no funds
#       - Delete agents

# 2. Add Agent to empty nodes, find nodes and create each through interface
#       - Find and return empty nodes
#       - Add an agent

# findagents

# findnodes

# main script
# agents = findagents
# for agent in agents:
#   interface.delete(agent)
# nodes = findnodes
# for node in nodes:
#   interface.addagents(nodes)

from neo4j import GraphDatabase
from Interface import Interface
from Fall_agent import FallAgent
# TODO: add nuid


def countactiveagents(tx):
    total_agents = tx.run()
    care_agents = tx.run()
    return total_agents-care_agents


def countindagents(tx):
    ind_agents = tx.run()
    return ind_agents


if __name__ == '__main__':
    verbose = False
    uri = "bolt://localhost:7687"
    dri = GraphDatabase.driver(uri, auth=("dancer", "dancer"))
    intf = Interface()
    clock = 0
    fa = FallAgent(None)
    while clock < 40:
        if clock % 2 == 0:
            with dri.session() as ses:
                active = ses.read_transaction(countactiveagents)
                ind = ses.read_transaction(countindagents)
                if ind < 10 and active - ind < 10:
                    for i in range(max(10-ind, 10-(active-ind))):
                        ses.write_transaction(fa.generator, intf, [0.8, 0.9, 1])
            clock = ses.run("MATCH (a:Clock) "
                            "RETURN a.time").values()[0][0]
        print(clock)
    dri.close()
