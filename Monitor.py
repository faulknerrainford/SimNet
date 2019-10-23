from neo4j import GraphDatabase
from matplotlib.pylab import *
import pickle
from matplotlib import pyplot as plt


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
        self.ax2 = subplot2grid((1, 2), (0, 1))
        self.ax1.set_title('Agent Strategies over Time')
        self.ax2.set_title('Agents of Nodes')
        self.ax1.ylabel("No. Agents")
        self.ax1.ylabel("No. Agents")
        self.ax1.xlabel("Time")
        self.ax2.ylabel("No. Agents")
        self.ax2.xlabel("Time")
        self.ax1.set_ylim(ylims)
        self.ax1.set_xlim(xlims)
        self.ax2.set_ylim(ylims)
        self.ax2.set_xlim(xlims)
        # Set data for plot 1
        self.y11 = zeros(0)
        self.y12 = zeros(0)
        self.t = zeros(0)
        self.p11, = self.ax1.plot(self.t, self.y11, 'b-', label="Max Benefit")
        self.p12, = self.ax1.plot(self.t, self.y12, 'g-', label="Min Cost")
        self.ax1.legend([self.p11, self.p12], [self.p11.get_label(), self.p12.get_label()])
        # Set data for plot 2
        self.y2 = {}
        self.p2 = {}
        for i in range(nodes):
            self.y2[i] = zeros(0)
            self.p2[i], = self.ax2(self.t, self.y2[i])
        self.ax2.legend()
        self.xmin = 0.0
        self.xmax = 20.0
        self.ymin1 = 0.0
        self.ymax1 = 12.0
        self.ymin2 = 0.0
        self.ymax2 = 12.0
        self.y = 0
        self.x = 0

    def snapshot(self, txl, ctime):
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
            # Update plot 1
            mb = txl.run("MATCH (n:Agent) "
                         "WHERE n.switch > 0.5 "
                         "RETURN count(*)").values()[0][0]
            tot = txl.run("MATCH (n:Agent) "
                          "RETURN count(*)").values()[0][0]
            mc = tot - mb
            self.y11 = append(self.y11, mb)
            self.y12 = append(self.y12, mc)
            self.t = append(self.t, ctime)
            self.x = ctime
            self.p11.set_data(self.t, self.y11)
            self.p12.set_data(self.t, self.y12)
            if self.x >= self.xmax - 1.00:
                self.p11.axes.set_xlim(0.0, self.x + 1.0)
                self.p12.axes.set_xlim(0.0, self.x + 1.0)
                self.xmax = self.x
            self.y = max([mb, mc])
            if self.y > self.ymax1 - 1.0 or self.y > self.ymax1 - 1.0:
                self.p11.axes.set_ylim(0.0, self.y + 1.0)
                self.p12.axes.set_ylim(0.0, self.y + 1.0)
            # Update plot 2
            mb = txl.run("MATCH (n:Agent) "
                         "WHERE n.switch > 0.5 "
                         "RETURN count(*)").values()[0][0]
            tot = txl.run("MATCH (n:Agent) "
                          "RETURN count(*)").values()[0][0]
            mc = tot - mb
            self.y11 = append(self.y11, mb)
            self.y12 = append(self.y12, mc)
            self.t = append(self.t, ctime)
            self.x = ctime
            self.p11.set_data(self.t, self.y11)
            self.p12.set_data(self.t, self.y12)
            if self.x >= self.xmax - 1.00:
                self.p11.axes.set_xlim(0.0, self.x + 1.0)
                self.p12.axes.set_xlim(0.0, self.x + 1.0)
                self.xmax = self.x
            self.y = max([mb, mc])
            if self.y > self.ymax1 - 1.0 or self.y > self.ymax1 - 1.0:
                self.p11.axes.set_ylim(0.0, self.y + 1.0)
                self.p12.axes.set_ylim(0.0, self.y + 1.0)

            plt.pause(0.005)

    def close(self):
        print(self.clock)
        pickle_out = open("records.pickle", "wb")
        pickle.dump(self.records, pickle_out)
        pickle_out.close()
        # TODO: pickle dump graph
        # TODO: save out graph
        plt.show()


if __name__ == '__main__':
    monitor = Monitor((0, 12), (0, 20), 6)
    clock = 0
    length = 2000
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("monitor", "monitor"))
    with driver.session() as session:
        # TODO: Try modifying and redrawing plot over time and saving plot rather than an animation see using
        #  plt.pause()
        while clock < length:
            tx = session.begin_transaction()
            res = tx.run("MATCH (a:Clock) "
                         "RETURN a.time")
            tx.close()
            temp = res.values()
            if temp != clock:
                clock = temp[0][0]
                print(clock)
                session.write_transaction(monitor.snapshot, clock)
    driver.close()
    monitor.close()
