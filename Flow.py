from neo4j import GraphDatabase
from Fall_nodes import *
from Interface import Interface

if __name__ == '__main__':
    verbose = False
    uri = "bolt://localhost:7687"
    dri = GraphDatabase.driver(uri, auth=("dancer", "dancer"))
    nuid = "name"
    intf = Interface()
    nodes = [HomeNode(), HosNode(), InterventionNode(), SocialNode(), GPNode()]
    with dri.session() as ses:
        clock = 0
        while clock < 40:
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
    dri.close()
