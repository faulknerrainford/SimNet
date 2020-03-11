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
        self.ax1 = subplot2grid((2, 2), (0, 0))
        self.ax2 = subplot2grid((2, 2), (0, 1))
        self.ax3 = subplot2grid((2, 2), (1, 0))
        self.ax4 = subplot2grid((2, 2), (1, 1))
        self.ax1.set_title('Average falls in lifetime')
        self.ax1.set_ylabel("No. Falls")
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
        self.ax4.set_title('Population Distribution')
        self.ax4.set_ylabel("Proportion")
        self.ax4.set_xlabel("Time")
        self.ax4.set_ylim(ylims)
        self.ax4.set_xlim(xlims)
        # Set data for plot 1
        self.y11 = zeros(0)
        self.y12 = zeros(0)
        self.y13 = zeros(0)
        self.y2 = zeros(0)
        self.y3 = zeros(0)
        self.y41 = zeros(0)
        self.y42 = zeros(0)
        self.y43 = zeros(0)
        self.t = zeros(0)
        self.p11, = self.ax1.plot(self.t, self.y11, 'b-', label="Mild")
        self.p12, = self.ax1.plot(self.t, self.y12, 'g-', label="Moderate")
        self.p13, = self.ax1.plot(self.t, self.y13, 'm-', label="Severe")
        self.ax1.legend([self.p11, self.p12, self.p13], [self.p11.get_label(),
                                                         self.p12.get_label(), self.p13.get_label()])
        self.p2, = self.ax2.plot(self.t, self.y2, 'm-')
        self.p3, = self.ax3.plot(self.t, self.y3, 'g-')
        self.p41, = self.ax4.plot(self.t, self.y41, 'b-', label="Healthy")
        self.p42, = self.ax4.plot(self.t, self.y42, 'g-', label="At Risk")
        self.p43, = self.ax4.plot(self.t, self.y43, 'm-', label="Fallen")
        self.ax4.legend([self.p41, self.p42, self.p43], [self.p41.get_label(),
                                                         self.p42.get_label(), self.p43.get_label()])
        self.xmin = 0.0
        self.xmax = 20.0
        self.ymin1 = 0.0
        self.ymax1 = 12.0
        self.y = 0
        self.y4 = 0
        self.y1 = 0
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
            # Update to track average number of each type of fall for people in care.
            [mild, moderate, severe, agents_n] = txl.run("MATCH (n:Node) "
                                                         "WHERE n.name={node} "
                                                         "RETURN n.mild, n.moderate, n.severe, n.agents",
                                                         node="Care").values()[0]
            if agents_n:
                self.y11 = append(self.y11, mild / agents_n)
                self.p11.set_data(self.t, self.y11)
                self.y12 = append(self.y12, moderate / agents_n)
                self.p12.set_data(self.t, self.y12)
                self.y13 = append(self.y13, severe / agents_n)
                self.p13.set_data(self.t, self.y13)
                if max([mild / agents_n, moderate / agents_n, severe / agents_n]) > self.y1:
                    self.y1 = max([mild / agents_n, moderate / agents_n, severe / agents_n])
                    self.p11.axes.set_ylim(0.0, self.y1 + 1.0)
                    self.p12.axes.set_ylim(0.0, self.y1 + 1.0)
                    self.p13.axes.set_ylim(0.0, self.y1 + 1.0)
            else:
                self.y11 = append(self.y11, 0)
                self.p11.set_data(self.t, self.y11)
                self.y12 = append(self.y12, 0)
                self.p12.set_data(self.t, self.y12)
                self.y13 = append(self.y13, 0)
                self.p13.set_data(self.t, self.y13)
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
            # Update plot 4
            # Update plot showing distribution of well being in the general population.
            wb = txl.run("MATCH (a:Agent)-[r:LOCATED]->(n:Node) "
                         "WHERE NOT n.name={node} "
                         "RETURN a.wellbeing",
                         node="Care").values()
            wb = [val[0] for val in wb]
            healthy = wb.count("Healthy") / len(wb)
            at_risk = wb.count("At risk") / len(wb)
            fallen = wb.count("Fallen") / len(wb)
            self.y41 = append(self.y41, healthy)
            self.p41.set_data(self.t, self.y41)
            self.y42 = append(self.y42, at_risk)
            self.p42.set_data(self.t, self.y42)
            self.y43 = append(self.y43, fallen)
            self.p43.set_data(self.t, self.y43)
            if max([healthy, at_risk, fallen]) / len(wb) > self.y4:
                self.y4 = max([healthy, at_risk, fallen])
                self.p41.axes.set_ylim(0.0, self.y4 + 1.0)
                self.p42.axes.set_ylim(0.0, self.y4 + 1.0)
                self.p43.axes.set_ylim(0.0, self.y4 + 1.0)
            # Update plot axes
            if self.x >= self.xmax - 1.00:
                self.p11.axes.set_xlim(0.0, self.x + 1.0)
                self.p12.axes.set_xlim(0.0, self.x + 1.0)
                self.p13.axes.set_xlim(0.0, self.x + 1.0)
                self.p2.axes.set_xlim(0.0, self.x + 1.0)
                self.p3.axes.set_xlim(0.0, self.x + 1.0)
                self.p41.axes.set_xlim(0.0, self.x + 1.0)
                self.p42.axes.set_xlim(0.0, self.x + 1.0)
                self.p43.axes.set_xlim(0.0, self.x + 1.0)
                self.xmax = self.x
            if self.y > self.ymax1 - 1.0:
                self.p2.axes.set_ylim(0.0, self.y + 1.0)
                self.p3.axes.set_ylim(0.0, self.y + 1.0)
            plt.pause(0.0005)

    def close(self, txc):
        runtype = "scarce_contrl"
        print(self.clock)
        run = 1
        pickle_lout = open("logs_" + runtype + "_" + str(run) + ".p", "wb")
        logs = txc.run("MATCH (a:Agent) RETURN a.log").values()
        pickle.dump(logs, pickle_lout)
        pickle_lout.close()
        pickle_out = open("records_" + runtype + "_" + str(run) + ".p", "wb")
        pickle.dump(self.records, pickle_out)
        pickle_out.close()
        pickle_gout = open("graphdata_" + runtype + "_" + str(run) + ".p", "wb")
        pickle.dump([self.y11, self.y12, self.y13, self.y2, self.y3, self.y41, self.y42, self.y43, self.t], pickle_gout)
        pickle_gout.close()
        # dump graph data as strings back into the database
        # save out graph
        plt.savefig("figure_" + runtype + "_" + str(run) + "")
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
