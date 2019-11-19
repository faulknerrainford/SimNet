

class Interface:

    def __init__(self, node_vector_length=0, edge_vector_length=0):
        self.node_vector_length = node_vector_length
        self.edge_vector_length = edge_vector_length

    @staticmethod
    def perception(tx, agent):
        results = tx.run("MATCH (m:Agent)-[s:LOCATED]->(n:Node) "
                         "WITH n, m "
                         "WHERE m.id={agent} "
                         "MATCH (n)-[r:REACHES]->(a) "
                         "RETURN n, r, a", agent=agent).values()
        if results:
            node = results[0][0]
            edges = [edge[1]for edge in results]
            results = [node] + edges
        # TODO: Check vectors match expected lengths, in all functions
        return results

    @staticmethod
    def getnode(tx, nodeid, label=None, uid=None):
        if not uid:
            uid = "id"
        if label == "Agent":
            query = "MATCH (n:Agent) ""WHERE n."+uid+" = {id} ""RETURN n"
            results = tx.run(query, id=nodeid, lab=label).values()
        else:
            query = "MATCH (n) ""WHERE n."+uid+" = {id} ""RETURN n"
            results = tx.run(query, id=nodeid).values()
        node = results[0][0]
        return node

    @staticmethod
    def getnodevalue(tx, node, value, label=None, uid=None):
        if not uid:
            uid = "id"
        if label:
            query = "MATCH (a:" + label + ") ""WHERE a." + uid + "={node} ""RETURN a." + value
        else:
            query = "MATCH (a:Node) ""WHERE a." + uid + "={node} ""RETURN a." + value
        tx.run(query, node=node, value=value)

    @staticmethod
    def getnodevector(node):
        return dict(list(tuple(node.items())))

    @staticmethod
    def getedgevector(edge):
        return dict([tuple(edge.items())[0]])

    @staticmethod
    def updateedge(tx, edge, prop, value, uid=None):
        if not uid:
            uid = "id"
        start = edge.start_node
        end = edge.end_node
        query = "MATCH (a:Node)-[r:REACHES]->(b:Node) ""WHERE a." + uid + "={start} AND b." + uid +\
                "={end} ""SET r." + prop + "={val}"
        tx.run(query, start=start[uid], end=end[uid], val=value)

    @staticmethod
    def updatenode(tx, node, prop, value, uid=None):
        if not uid:
            uid = "id"
        query = "MATCH (a:Node) ""WHERE a." + uid + "={node} ""SET a." + prop + "={value}"
        tx.run(query, node=node[uid], value=value)

    @staticmethod
    def updateagent(tx, node, prop, value, uid=None):
        if not uid:
            uid = "id"
        query = "MATCH (a:Agent) ""WHERE a." + uid + "={node} ""SET a." + prop + "={value}"
        tx.run(query, node=node[uid], value=value)
        print(node[uid])
        print(prop)
        print(node[prop])
        print(value)

    @staticmethod
    def deleteagent(tx, agent, uid=None):
        if not uid:
            uid = "id"
        tx.run("MATCH (n:Agent)-[r:LOCATED]->() ""WHERE n." + uid + "={ID} ""DELETE r", ID=agent[uid])
        tx.run("MATCH (n:Agent) ""WHERE n." + uid + "={ID} ""DELETE n", ID=agent[uid])

    @staticmethod
    def addagent(tx, node, label, params, uid=None):
        if not uid:
            uid = "id"
        query = "MATCH (n:"+label+") ""WITH n ""ORDER BY n.id DESC ""RETURN n.id"
        highest_id = tx.run(query).values()[0][0]
        agent_id = highest_id + 1
        query = "CREATE (a:"+label+" {id:"+agent_id
        for param in params:
            query = query + ", " + param.key() + ":" + param.value()
        query = query + "})-[r:LOCATED]->(n)"
        tx.run("MATCH (n:Node) ""WHERE n." + uid + "=" + node[uid] + " " + query)

        # TODO: Integrate toy functionality back in by updating toy files to use new system

        # CODE FOR TOY
        # switch = random()
        # values = ""
        # for val in params:
        #     values = values + ", " + val[0] + ":"+str(val[1])+" "
        # query = "CREATE (a:"+label+" {" + uid + ":{aID}, switch:{SWITCH}"+values+"})-[r:LOCATED]->(n)"
        # tx.run("MATCH (n:Node) ""WHERE n." + uid + "={nID} "+query, aID=agentid, SWITCH=switch, nID=node[uid])
