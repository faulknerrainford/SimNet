class Interface:

    def __init__(self, node_vector_length, edge_vector_length):
        self.node_vector_length = node_vector_length
        self.edge_vector_length = edge_vector_length

    @staticmethod
    def perception(self, tx, agent):
        tx.run("MATCH (n)-[r:REACHES]->() "
               "WHERE n.id={agent} "
               "RETURN n, r", agent=agent)
        ######TO DO:
        # Retrieve n and r id's
        results = [getedgevector(edge) for edge in edgeids]
        results = [getnodevector(node)] + results
        ######TO DO:
        # Check vectors match expected lengths, in all functions
        return results

    @staticmethod
    def getnodevector(self, tx, node):
        return tx.run("MATCH (n) "
                      "WHERE n.id={node} "
                      "RETURN n", node=node).values()

    @staticmethod
    def getedgevector(self, tx, edge):
        return tx.run("MATCH (a)-[r:REACHES]->(b) "
                      "WHERE a.id={a} AND b.id={b} "
                      "RETURN r", a=edge[0], b=edge[1]).values()

    @staticmethod
    def changenodevector(self, tx, node, vector):
        skip

    @staticmethod
    def changeedgevector(self, tx, edge, vector):
        skip
