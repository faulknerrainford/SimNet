from neo4j import GraphDatabase
from matplotlib.pylab import *
import pickle
from matplotlib import pyplot as plt
from Fall_Balancer import timesincedischarge
from Interface import Interface
from statistics import mean


class Monitor:

    def __init__(self, xlims, ylims):
        self.uri = "bolt://localhost:7687"
        self.clock = 0
        self.records = {}
        self.orecord = None
        self.nrecord = None
        # Set up plots
        self.fig = figure()
        self.fig.suptitle("Network Stats over Time")
        # Set up subplots with titles and axes
        self.ax1 = subplot2grid((1, 3), (0, 0))
        self.ax2 = subplot2grid((1, 3), (0, 1))
        self.ax3 = subplot2grid((1, 3), (0, 2))
        self.ax1.set_title('Intervention Capacity')
        self.ax1.set_ylabel("No. Agents")
        self.ax1.set_xlabel("Time")
        self.ax1.set_ylim(ylims)
        self.ax1.set_xlim(xlims)
        self.ax2.set_title('Intervention Interval')
        self.ax2.set_ylabel("Interval")
        self.ax2.set_xlabel("Time")
        self.ax2.set_ylim(ylims)
        self.ax2.set_xlim(xlims)
        self.ax3.set_title('System Interval')
        self.ax3.set_ylabel("Interval")
        self.ax3.set_xlabel("Time")
        self.ax3.set_ylim(ylims)
        self.ax3.set_xlim(xlims)
        # Set data for plot 1
        self.y1 = zeros(0)
        self.y2 = zeros(0)
        self.y3 = zeros(0)
        self.t = zeros(0)
        self.p1, = self.ax1.plot(self.t, self.y1, 'b-', label="Max capacity of Intervention")
        self.p2, = self.ax2.plot(self.t, self.y2, 'm-', label="Interval from Hospital to Intervention")
        self.p3, = self.ax3.plot(self.t, self.y3, 'g-', label="Interval from Start to Care")
        self.xmin = 0.0
        self.xmax = 20.0
        self.ymin1 = 0.0
        self.ymax1 = 12.0
        self.y = 0
        self.x = 0
        self.y3storage = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]

    def snapshot(self, txl, ctime):
        look = txl.run("MATCH (n:Node) "
                       "WHERE n.name = {node} "
                       "RETURN n", node="Intervention")
        self.nrecord = look.values()
        if self.x != ctime:
            print(ctime)
            self.records[self.clock] = self.orecord
            self.orecord = self.nrecord
            self.clock = self.clock + 1
            # Update time
            self.t = append(self.t, ctime)
            self.x = ctime
            # Update plot 1 - Int Cap
            cap = txl.run("MATCH (n:Node) "
                          "WHERE n.name={node} "
                          "RETURN n.cap", node="Intervention").values()[0][0]
            self.y1 = append(self.y1, cap)
            self.p1.set_data(self.t, self.y1)
            if cap > self.y:
                self.y = cap
            # Update plot 2 - Hos to Int
            intf = Interface()
            gaps = timesincedischarge(txl, intf)
            if gaps:
                hiint = mean(timesincedischarge(txl, intf))
                self.y3storage = self.y3storage + [hiint]
                if len(self.y3storage) >= 10:
                    self.y3storage = self.y3storage[-10:]
            if self.y3storage:
                self.y2 = append(self.y2, mean(self.y3storage))
                if self.y < mean(self.y3storage):
                    self.y = mean(self.y3storage)
                self.p2.set_data(self.t, self.y2)
            # Update plot 3 - Start to Care
            careint = intf.getnodevalue(txl, "Care", "interval", uid="name")
            if careint:
                scint = careint
            else:
                scint = 0
            self.y3 = append(self.y3, scint)
            if self.y < scint:
                self.y = scint
            self.p3.set_data(self.t, self.y3)
            # Update plot axes
            if self.x >= self.xmax - 1.00:
                self.p1.axes.set_xlim(0.0, self.x + 1.0)
                self.p2.axes.set_xlim(0.0, self.x + 1.0)
                self.p3.axes.set_xlim(0.0, self.x + 1.0)
                self.xmax = self.x
            if self.y > self.ymax1 - 1.0:
                self.p1.axes.set_ylim(0.0, self.y + 1.0)
                self.p2.axes.set_ylim(0.0, self.y + 1.0)
                self.p3.axes.set_ylim(0.0, self.y + 1.0)
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

    def close(self, txc):
        print(self.clock)
        pickle_lout = open("logs_pset_1.p", "wb")
        logs = txc.run("MATCH (a:Agent) RETURN a.log").values()
        pickle.dump(logs, pickle_lout)
        pickle_lout.close()
        pickle_out = open("records_pset_1.p", "wb")
        pickle.dump(self.records, pickle_out)
        pickle_out.close()
        pickle_gout = open("graphdata_pset_1.p", "wb")
        pickle.dump([self.y1, self.y2, self.y3, self.t], pickle_gout)
        pickle_gout.close()
        # dump graph data as strings back into the database
        # save out graph
        plt.savefig("figure_pset_1")
        plt.show()


if __name__ == '__main__':
    monitor = Monitor((0, 12), (0, 20))
    clock = 0
    length = 2000
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
                # modifying and redrawing plot over time and saving plot rather than an animation
                session.write_transaction(monitor.snapshot, clock)
        session.write_transaction(monitor.close)
    driver.close()
