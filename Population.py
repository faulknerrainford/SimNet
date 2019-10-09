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

if __name__ == '__main__':
    verbose = False
    uri = "bolt://localhost:7687"
    dri = GraphDatabase.driver(uri, auth=("dancer", "dancer"))
    intf = Interface()
    with dri.session() as ses:
        agents = ses.read_transaction(findagents)
        [ses.write_transaction(intf.delete(agent)) for agent in agents]
        nodes = ses.read_transaction(findnodes)
        [ses.write_transaction(intf.addagent(node, "Dancer", [0.5])) for node in nodes]
