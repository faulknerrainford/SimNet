from neo4j import GraphDatabase
from Fall_agent import FallAgent
from Interface import Interface

if __name__ == '__main__':
    verbose = False
    uri = "bolt://localhost:7687"
    dri = GraphDatabase.driver(uri, auth=("dancer", "dancer"))
    nuid = "name"
    intf = Interface()
    with dri.session() as ses:
        tx = ses.begin_transaction()
        res = tx.run("MATCH (a:Node) "
                     "RETURN a." + nuid + "")
        tx.close()
        nodes = [v[0] for v in res.values()]
        clock = 0
        while clock < 40:
            for node in nodes:
                agents = ses.run("MATCH (n:Agent)-[r:LOCATED]->(a:Node) "
                                 "WHERE a." + nuid + "={id} "
                                 "RETURN n.id", id=node).values()
                agents = [FallAgent(ag[0]) for ag in agents]
                # TODO: Pass in ModelAgent as class rather than hard code it. Add in check that class is a subclass of
                #  Agent
                for agent in agents:
                    ses.write_transaction(agent.move, intf)
            res = ses.run("MATCH (a:Clock) "
                          "SET a.time = a.time + 1 "
                          "RETURN a.time")
            temp = res.values()
            print(temp)
            clock = temp[0][0]
            print("T: " + clock.__str__())
    dri.close()
