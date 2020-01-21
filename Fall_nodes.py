import Node


class FallNode(Node):

    def __init__(self, name, capacity=None, duration=None, queue=None):
        super(FallNode, self).__init__(self, name, capacity, duration, queue)

    def agentready(self, tx, intf):
        super(FallNode, self).agentready(tx, intf)

    def agentperception(self, tx, agent, intf, dest=None, waittime=None):
        super(FallNode, self).agentperception(tx, agent, intf, dest, waittime)
        # TODO: If hos and GP in options check for fall and return hos or GP,
        #  no prediction just straight check based on  mobility

    def agentprediction(self, tx, agent, intf):
        super(FallNode, self).agentprediction(tx, agent, intf)
        # Node specific only, no general node prediction assume no queue as default, thus no prediction needed
