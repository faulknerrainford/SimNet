from neo4j import GraphDatabase
from matplotlib.pylab import *
import pickle
from matplotlib import pyplot as plt
from Fall_Balancer import timesincedischarge, parselog
from Interface import Interface


class Monitor:

    def __init__(self, xlims, ylims, nodes):
        self.uri = "bolt://localhost:7687"
        self.clock = 0
        self.records = {}
        self.orecord = None
        self.nrecord = None
        # Set up plots
        self.fig = figure()
        self.fig.suptitle("Network Stats over Time")
        # Set up subplots with titles and axes
        self.ax1 = subplot2grid((1, 2), (0, 0))
        self.ax1.set_title('Intervention Capacity')
        self.ax1.set_ylabel("No. Agents")
        self.ax1.set_xlabel("Time")
        self.ax1.set_ylim(ylims)
        self.ax1.set_xlim(xlims)
        # Set data for plot 1
        self.y11 = zeros(0)
        self.y12 = zeros(0)
        self.y13 = zeros(0)
        self.t = zeros(0)
        self.p11, = self.ax1.plot(self.t, self.y11, 'b-', label="Max capacity of Intervention")
        self.p12, = self.ax1.plot(self.t, self.y12, 'p-', label="Interval from Hospital to Intervention")
        self.p13, = self.ax1.plot(self.t, self.y13, 'p-', label="Interval from Start to Care")
        self.xmin = 0.0
        self.xmax = 20.0
        self.ymin1 = 0.0
        self.ymax1 = 12.0
        self.y = 0
        self.x = 0

    def snapshot(self, txl, ctime):
        look = txl.run("MATCH (n:Node) "
                       "WHERE n.name == 'Intervention' "
                       "RETURN n")
        self.nrecord = look.values()
        if self.x != ctime:
            self.records[self.clock] = self.orecord
            self.orecord = self.nrecord
            self.clock = self.clock + 1
            # Update plot 1 - Int Cap
            cap = txl.run("MATCH (n:Node) "
                          "WHERE n.name == 'Intervention' "
                          "RETURN n.cap").values()[0][0]
            self.y11 = append(self.y11, cap)
            # Update plot 2 - Hos to Int
            intf = Interface()
            HIint = mean(timesincedischarge(tx, intf))
            if HIint:
                self.y12 = append(self.y12, HIint)
            # Update plot 3 - Start to Care
            times = []
            agents = intf.getnodeagents(tx, "Care", "name")
            for agent in agents:
                log = parselog(agent["log"])
                time = log[-1][1] - log[0][1]
                times = times + [time]
            SCint = mean(times)
            if SCint:
                self.y13 = append(self.y13, SCint)
            # Update time
            self.t = append(self.t, ctime)
            self.x = ctime
            self.p11.set_data(self.t, self.y11)
            self.p12.set_data(self.t, self.y12)
            self.p13.set_data(self.t, self.y13)
            # Update plot axes
            if self.x >= self.xmax - 1.00:
                self.p11.axes.set_xlim(0.0, self.x + 1.0)
                self.xmax = self.x
            self.y = max([cap, HIint, SCint])
            if self.y > self.ymax1 - 1.0:
                self.p11.axes.set_ylim(0.0, self.y + 1.0)
            # Update plot 2
            # resl = txl.run("MATCH ()-[:LOCATED]->(n:Node) "
            #                "RETURN n.id, count(*)").values()
            # # loop assigning counts to correct data
            # for node in range(self.nodes):
            #     if node in [n[0] for n in resl]:
            #         count = [n[1] for n in resl if n[0] == node]
            #         self.y2[node] = append(self.y2[node], count[0])
            #         # loop assigning data to plots
            #         self.p2[node].set_data(self.t, self.y2[node])
            #     else:
            #         self.y2[node] = append(self.y2[node], 0)
            #         self.p2[node].set_data(self.t, self.y2[node])
            # # Update and check axis (update axis on these plots)
            # self.y = max([node[1] for node in resl])
            # if self.y > self.ymax2 - 1.0:
            #     [self.p2[node[0]].axes.set_ylim(0.0, self.y + 1.0) for node in resl]
            plt.pause(0.0005)

    def close(self):
        print(self.clock)
        pickle_out = open("records.pickle", "wb")
        pickle.dump(self.records, pickle_out)
        pickle_out.close()
        # dump graph data as strings back into the database
        # save out graph
        plt.savefig("figure4")
        plt.show()


if __name__ == '__main__':
    monitor = Monitor((0, 12), (0, 20), 6)
    clock = 0
    length = 40
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("monitor", "monitor"))
    with driver.session() as session:
        while clock < length:
            tx = session.begin_transaction()
            res = tx.run("MATCH (a:Clock) "
                         "RETURN a.time")
            tx.close()
            temp = res.values()
            if temp != clock:
                clock = temp[0][0]
                print(clock)
                # modifying and redrawing plot over time and saving plot rather than an animation
                session.write_transaction(monitor.snapshot, clock)
    driver.close()
    monitor.close()
