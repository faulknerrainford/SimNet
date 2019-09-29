class Interface:

    def __init__(self, node_vector_length=0, edge_vector_length=0):
        self.node_vector_length = node_vector_length
        self.edge_vector_length = edge_vector_length

    @staticmethod
    def perception(self, tx, agent):
        results = tx.run("MATCH (n)-[r:REACHES]->(a) "
                         "WHERE n.id={agent} "
                         "RETURN n, r, a", agent=agent).values()
        node = dict(tuple(results[0][0].items())[0])
        edges = [edge[1].items() for edge in results]
        results = [self.getedgevector(edge) for edge in edges]
        results = [self.getnodevector(node)] + results
        # TO DO:
        # Check vectors match expected lengths, in all functions
        return results

    @staticmethod
    def getnodevector(node):
        return node[:][1]

    @staticmethod
    def getedgevector(edge):
        return edge[:][1]

    @staticmethod
    def changenodevector(self, tx, node, vector):
        skip

    @staticmethod
    def changeedgevector(self, tx, edge, vector):
        skip
