from random import random


class Interface:

    def __init__(self, node_vector_length=0, edge_vector_length=0):
        self.node_vector_length = node_vector_length
        self.edge_vector_length = edge_vector_length

    @staticmethod
    def perception(tx, agent):
        results = tx.run("MATCH (m:Dancer)-[s:LOCATED]->(n:Node) "
                         "WITH n, m "
                         "WHERE m.id={agent} "
                         "MATCH (n)-[r:REACHES]->(a) "
                         "RETURN n, r, a", agent=agent).values()
        node = results[0][0]
        edges = [edge[1]for edge in results]
        results = [node] + edges
        # TO DO:
        # Check vectors match expected lengths, in all functions
        return results

    @staticmethod
    def getnode(tx, nodeid, label=None):
        if label == "Dancer":
            results = tx.run("MATCH (n:Dancer) "
                             "WHERE n.id = {id} "
                             "RETURN n", id=nodeid, lab=label).values()
        else:
            results = tx.run("MATCH (n) "
                             "WHERE n.id = {id} "
                             "RETURN n", id=nodeid).values()
        node = results[0][0]
        return node

    @staticmethod
    def getnodevector(node):
        return dict(list(tuple(node.items())))

    @staticmethod
    def getedgevector(edge):
        return dict([tuple(edge.items())[0]])

    @staticmethod
    def updateedge(tx, edge, prop, value):
        start = edge.start_node
        end = edge.end_node
        query = "MATCH (a:Node)-[r:REACHES]->(b:Node) ""WHERE a.id={start} AND b.id={end} ""SET r." + prop + "={val}"
        tx.run(query, start=start["id"], end=end["id"], val=value)

    @staticmethod
    def updatenode(tx, node, prop, value):
        query = "MATCH (a) ""WHERE a.id={node} ""SET a." + prop + "={value}"
        print(prop)
        print(value)
        tx.run(query, node=node["id"], value=value)

    @staticmethod
    def deleteagent(tx, agent):
        tx.run("MATCH (n:Agent)-[r:LOCATED]->() ""WHERE n.id={ID} ""DELETE r", ID=agent["id"])
        tx.run("MATCH (n:Agent) ""WHERE n.id={ID} ""DELETE n", ID=agent["id"])

    @staticmethod
    def addagent(tx, node, label, params):
        query = "MATCH (n:"+label+") ""WITH n ""ORDER BY n.id DESC ""RETURN n.id"
        highestid = tx.run(query).values()[0][0]
        agentid = highestid + 1
        switch = random()
        values = ""
        for val in params:
            values = values +", "+ val[0] + ":"+str(val[1])+" "
        query = "CREATE (a:"+label+" {id:{aID}, switch:{SWITCH}"+values+"})-[r:LOCATED]->(n)"
        tx.run("MATCH (n) ""WHERE n.id={nID} "+query, aID=agentid, SWITCH=switch, nID=node["id"])
