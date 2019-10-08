from neo4j import GraphDatabase
from Toy_Agent import ToyAgent
from Interface import Interface

if __name__ == '__main__':
    verbose = False
    uri = "bolt://localhost:7687"
    dri = GraphDatabase.driver(uri, auth=("dancer", "dancer"))
    intf = Interface()
    with dri.session() as ses:
        tx = ses.begin_transaction()
        res = tx.run("MATCH (a:Node) "
                     "RETURN a.id")
        tx.close()
        nodes = [v[0] for v in res.values()]
        print(nodes)
        clock = 0
        while clock < 20:
            for node in nodes:
                agents = ses.run("MATCH (n:Dancer)-[r:LOCATED]->(a:Node) "
                                 "WHERE a.id={id} "
                                 "RETURN n.id, n.switch", id=node).values()
                print(agents)
                agents = [ToyAgent(ag[0], [ag[1]]) for ag in agents]
                for agent in agents:
                    ses.write_transaction(agent.move, intf)
            res = ses.run("MATCH (a:Clock) "
                          "SET a.time = a.time + 1 "
                          "RETURN a.time")
            temp = res.values()
            clock = temp[0][0]
            print("T: " + clock.__str__())
    dri.close()
