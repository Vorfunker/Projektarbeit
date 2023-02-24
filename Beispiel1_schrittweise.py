import networkx as nx
import random
from matplotlib import pyplot as plt
import time
import pdb

class BspGraph(nx.Graph):

    def __init__(self, Graph, startSolution, figure, canvas):
        super().__init__()
        self.initMe(Graph, startSolution, figure, canvas)

    def initMe(self, Graph, startSolution, figure, canvas):
        self.figure = figure
        self.canvas = canvas
        self.Graph = Graph
        self.Graph.nodes(data=True)

        #merken, der bereits getauschten Knoten
        self.bereitsGetauschteKInS = []
        self.bereitsGetauschteKNotInS = []

        self.currentSolutionNodes = startSolution
        self.weights = nx.get_edge_attributes(self.Graph,'weight') #ändert sich nicht

    def get_graph_weight(self):
        kostenC = 0
        for node in self.Graph.nodes:
            if node not in self.currentSolutionNodes: #Loop über alle Knoten, die keine facility sind
                randomFacility = random.choice(self.currentSolutionNodes)
                #lowestWeightNode = int(self.Graph.adj[node].get(str(randomFacility)).get('weight')) #zufälliges, aber mögliches Gewicht auswählen
                lowestWeightNode = int(self.Graph.adj[node].get(randomFacility).get('weight')) #zufälliges, aber mögliches Gewicht auswählen
                for nbr, attr in self.Graph.adj[node].items(): #Loop über alle Nachbarn jeweils eines Knotens
                    if nbr in self.currentSolutionNodes:
                        if attr.get('weight') < lowestWeightNode:
                            lowestWeightNode = attr.get('weight')
                
                kostenC += lowestWeightNode
        return kostenC

    def color_graph(self):
        self.set_edges_blue()
        self.set_nodes_blue()
        self.color_nodes()
        return self.color_edges()

    def color_edges(self):
        dest_node = {}
        for node in self.Graph.nodes:
            if node not in self.currentSolutionNodes: #Loop über alle Knoten, die keine facility sind
                randomFacility = random.choice(self.currentSolutionNodes)
                dest_node[node] = randomFacility
                self.get_lowest_weight_edge(dest_node, node)
                self.Graph[node][dest_node[node]]['color'] = 'darkorange'
                
        return dest_node

    def get_lowest_weight_edge(self, dest_node, node):
        for nbr, attr in self.Graph.adj[node].items(): #Loop über alle Nachbarn jeweils eines Knotens
            if nbr not in self.currentSolutionNodes:
                continue
            if attr.get('weight') < self.Graph[node][dest_node[node]].get('weight'):
                dest_node[node] = nbr

    def set_edges_blue(self):
        for node in self.Graph.nodes:
            for connectedNode in self.Graph.nodes:
                if node != connectedNode:
                    self.Graph[node][connectedNode]['color'] = 'deepskyblue'

    def set_nodes_blue(self):
        for node in self.Graph.nodes:
            #self.Graph._node[str(node)]['color'] = 'darkorange'
            self.Graph._node[node]['color'] = 'darkorange'

    def color_nodes(self):
        for node in self.currentSolutionNodes:
            #pdb.set_trace()
            #self.Graph._node[str(node)]['color'] = 'mediumorchid'
            self.Graph._node[node]['color'] = 'mediumorchid'

    def algo(self, figure, canvas, gui):
        self.figure = figure
        self.canvas = canvas
        self.gui = gui
        algoFertig = self.swapEveryNodeInSolution()
        return algoFertig

    def swapEveryNodeInSolution(self):
        zuTauschendeKInS = list(set(self.currentSolutionNodes) - set(self.bereitsGetauschteKInS))
        if not zuTauschendeKInS: #Liste ist leer
            self.drawGraph()
            return True #algoFertig
        else:
            # self.currentKInS = zuTauschendeKInS[0]
            restartSwapSequenz = self.swapWithNeighbours(zuTauschendeKInS[0])
            # self.bereitsGetauschteKInS.append(zuTauschendeKInS[0])
            if restartSwapSequenz == "RestartComplete":
                self.bereitsGetauschteKInS.clear()
                self.bereitsGetauschteKNotInS.clear()
                # self.swapEveryNodeInSolution()
                return False

            elif restartSwapSequenz == "RestartNextKInS":
                return self.swapEveryNodeInSolution()
            
            return False
        # for swappedOut in list(set(self.currentSolutionNodes) - set(self.bereitsGetauschteKInS)):
        #     restartSwapSequenz = self.swapWithNeighbours(swappedOut)
        #     self.bereitsGetauschteKInS.append(swappedOut)
        #     if restartSwapSequenz == True:
        #         self.bereitsGetauschteKInS.clear()
        #         self.bereitsGetauschteKNotInS.clear()
        #         self.swapEveryNodeInSolution()
        #         break#TODO

    def swapWithNeighbours(self, swappedOut): #TODO: Typisierung?
        zuTauschendeKNotInS = list(set(self.Graph.nodes) - set(self.currentSolutionNodes) - set(self.bereitsGetauschteKNotInS))
        if not zuTauschendeKNotInS: #Liste ist leer
            self.bereitsGetauschteKInS.append(swappedOut)
            self.bereitsGetauschteKNotInS.clear()
            return "RestartNextKInS"
        else:
            restartSwapSequenz = self.swap2Nodes(swappedOut, zuTauschendeKNotInS[0])
            self.bereitsGetauschteKNotInS.append(zuTauschendeKNotInS[0])
            if restartSwapSequenz == True:
                return "RestartComplete" 
        # for swappedIn in list(set(self.Graph.nodes) - set(self.bereitsGetauschteKNotInS)):
        #     if swappedIn not in self.currentSolutionNodes:
        #         restartSwapSequenz = self.swap2Nodes(swappedOut, swappedIn)
        #         self.bereitsGetauschteKNotInS.append(swappedIn)
        #         if restartSwapSequenz == True:
        #             return True


    def swap2Nodes(self, swappedOut, swappedIn): #TODO: NAME???
        costBeforeSwap = self.get_graph_weight()
        self.swap2NodesInList(swappedOut, swappedIn)
        costAfterSwap = self.get_graph_weight()
        # self.color_graph() jetzt in drawGraph
        self.drawGraph()
        # self.gui.drawQT()
        if costAfterSwap < costBeforeSwap: #Kosten besser als vorher -> Neu alles durchtauschen
            return True
        else:
            time.sleep(1)
            self.swap2NodesInList(swappedIn, swappedOut)
            self.color_graph()
            self.drawGraph()

    def swap2NodesInList(self, swappedOut, swappedIn): #TODO: NAME???
        self.currentSolutionNodes.remove(swappedOut)
        self.currentSolutionNodes.append(swappedIn)
        self.currentSolutionNodes.sort()

    def stepBack(self):
        if self.bereitsGetauschteKNotInS:
            self.swap2NodesInList(self.bereitsGetauschteKNotInS[-1], )#TODO

    def drawGraph(self):
        self.figure.clf()

        self.color_graph()

        zuTauschendeKInS = list(set(self.currentSolutionNodes) - set(self.bereitsGetauschteKInS))
        if zuTauschendeKInS:
            plt.title('Kosten C = ' + str(self.get_graph_weight()))
            plt.suptitle('Tauschender Knoten in S: ' + str(zuTauschendeKInS[0]))

        edgeColor = nx.get_edge_attributes(self.Graph,'color').values()
        nodeColor = nx.get_node_attributes(self.Graph,'color').values()
        plt.plot()
        pos = nx.circular_layout(self.Graph)

        nx.draw_networkx_nodes(self.Graph, pos, node_color=nodeColor)
        nx.draw_networkx_labels(self.Graph, pos)
        nx.draw_networkx_edges(self.Graph, pos, edge_color=edgeColor)
        nx.draw_networkx_edge_labels(self.Graph, pos, edge_labels=self.weights)

        # plt.show()


###ab hier wird gedruckt###
# color_graph()
# drawGraph()

# algo()