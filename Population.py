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


def findagents(tx):
    results = tx.run("MATCH (n:Agent) " 
                     "WHERE n.funds=0 "
                     "RETURN n").values()
    if results:
        return results[0][0]
    else:
        return results


def findnodes(tx):
    results = tx.run("MATCH (n:Node) "
                     "WHERE NOT ()-[:LOCATED]->(n) "
                     "RETURN n").values()
    if results:
        return results[0][0]
    else:
        return results


if __name__ == '__main__':
    verbose = False
    uri = "bolt://localhost:7687"
    dri = GraphDatabase.driver(uri, auth=("dancer", "dancer"))
    intf = Interface()
    clock = 0
    while clock < 2000:
        with dri.session() as ses:
            agents = ses.read_transaction(findagents)
            if type(agents) == "list" and agents:
                [ses.write_transaction(intf.deleteagent, agent) for agent in agents]
            elif agents:
                ses.write_transaction(intf.deleteagent, agents)
            nodes = ses.read_transaction(findnodes)
            if type(nodes) == "list" and nodes:
                [ses.write_transaction(intf.addagent, node, "Agent", [("funds", 10)]) for node in nodes]
            elif nodes:
                ses.write_transaction(intf.addagent, nodes, "Agent", [("funds", 10)])
            res = ses.run("MATCH (a:Clock) "
                          "RETURN a.time")
        temp = res.values()
        clock = temp[0][0]
        print(clock)
    dri.close()
