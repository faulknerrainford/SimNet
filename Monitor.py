from neo4j import GraphDatabase
import pickle


class Monitor:

    def __init__(self):
        self.uri = "bolt://localhost:7687"
        self.clock = 0
        self.records = {}
        self.orecord = None
        self.nrecord = None

    def snapshot(self, txl):
        look = txl.run("MATCH (n:Node) "
                       "WITH n "
                       "ORDER BY n.id "
                       "MATCH ()-[r:LOCATED]->(n) "
                       "WITH n, count(*) as load "
                       "MATCH (n)-[r:REACHES]->() "
                       "WITH n, load, min(r.cost) as price "
                       "RETURN n.id, n.payout, n.funds, load, price")
        self.nrecord = look.values()
        if self.nrecord != self.orecord:
            self.records[self.clock] = self.orecord
            print(self.orecord)
            self.orecord = self.nrecord
            self.clock = self.clock + 1

    def close(self):
        print(self.clock)
        pickle_out = open("records.pickle", "wb")
        pickle.dump(self.records, pickle_out)
        pickle_out.close()


if __name__ == '__main__':
    monitor = Monitor()
    clock = 0
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("monitor", "monitor"))
    with driver.session() as session:
        while clock < 2000:
            session.write_transaction(monitor.snapshot)
            tx = session.begin_transaction()
            res = tx.run("MATCH (a:Clock) "
                         "RETURN a.time")
            tx.close()
            temp = res.values()
            clock = temp[0][0]
            print(clock)
    driver.close()
    monitor.close()
