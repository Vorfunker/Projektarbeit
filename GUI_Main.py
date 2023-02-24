from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import networkx as nx
import random
import time
import Beispiel1_schrittweise as bsp
import copy as copy
from PyQt5 import QtWidgets

class PrettyWidget(QWidget):

    #NumButtons = ['plot1','bsp1', 'plot3', 'forward', 'backward']
    NumButtons = ['Beispiel1','Beispiel2', 'EigenerGraph', 'Einzelschritt']

    #controlButtons = ['forward', 'backward']
    controlButtons = ['Einzelschritt']

    def __init__(self):


        super(PrettyWidget, self).__init__()        
        font = QFont()
        font.setPointSize(16)
        self.graphHistory = []
        self.initUI()

    def initUI(self):
        self.l = QLabel("Start")

        self.setGeometry(100, 100, 800, 600)
        self.center()
        self.setWindowTitle('S Plot')

        grid = QGridLayout()
        self.setLayout(grid)
        self.createVerticalGroupBox()

        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(self.verticalGroupBox)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)        
        grid.addWidget(self.canvas, 0, 1, 9, 9)          
        grid.addLayout(buttonLayout, 0, 0)

        self.show()

        self.threadpool = QThreadPool()

        self.counter = 0
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.drawQT)
        self.timer.start()


    def createVerticalGroupBox(self):
        self.verticalGroupBox = QGroupBox()

        layout = QVBoxLayout()

        layout.addWidget(self.l)
        for i in  self.NumButtons:
                button = QPushButton(i)
                button.setObjectName(i)
                layout.addWidget(button)
                layout.setSpacing(10)
                button.clicked.connect(self.submitCommand)

        self.verticalGroupBox.setLayout(layout)

    def submitCommand(self):
        eval('self.' + str(self.sender().objectName()) + '()')



    def Beispiel1(self):
        self.figure.clf()
        self.canvas.draw_idle()

    def Beispiel2(self):
        # self.thread_bsp1()
        self.threadpool.start(self.thread_bsp1)

    def thread_bsp1(self):
        self.figure.clf()
        self.Graph = nx.Graph()
        self.Graph.add_weighted_edges_from([(1, 2, 8), (1, 3, 10), (1, 4, 5), (1, 5, 9), (2, 3, 9), (2, 4, 7), (2, 5, 9), (3, 4, 7), (3, 5, 1), (4, 5, 6)])
        self.Graph.nodes(data=True)
        self.startSolution = [2, 3, 5]

        self.Loesung = bsp.BspGraph(self.Graph, self.startSolution, self.figure, self.canvas)

        # self.Loesung.color_graph()
        self.Loesung.drawGraph()

        self.canvas.draw_idle()

    def EigenerGraph(self):
        self.figure.clf()
        #User gibt Größe der Lösung ein
        numberNodesSolution, doneNumber = QtWidgets.QInputDialog.getInt(
             self, 'Bitte Anzahl an Knoten der Lösung eingeben', 'Anzahl Knoten der Lösung: ')
        #User gibt Graph ein
        UserGraph, doneGraph = QtWidgets.QInputDialog.getText(
             self, 'Bitte Graph als Liste eingeben', 'Bitte Graph als Liste eingeben:')
        
        outer_list = UserGraph.split(";")
        inner_list = []
        for inner_string in outer_list:
            inner_list.append(tuple(map(int, inner_string.split())))
        #self.threadpool.start(self.thread_plot3(inner_list, numberNodesSolution))
        self.thread_plot3(inner_list, numberNodesSolution)
        

#wird doch nicht als thread aufgerufen
    def thread_plot3(self, inner_list, numberNodesSolution):
        self.figure.clf()

        #Graph mit UserEingaben erzeugen
        self.Graph = nx.Graph()
        self.Graph.add_weighted_edges_from(inner_list)
        self.Graph.nodes(data=True)
        self.startSolution = []
        for i in range(numberNodesSolution):
            self.startSolution.append(i + 1)

        print(self.startSolution)
        self.Loesung = bsp.BspGraph(self.Graph, self.startSolution, self.figure, self.canvas)

        self.Loesung.drawGraph()

        self.canvas.draw_idle()
        screen.show()

#funktioniert noch nicht
    def greyedForward(self):
        # if self.verticalGroupBox.layout():
        #     QWidget().setLayout(self.verticalGroupBox.layout())

        layout = QVBoxLayout()
        for buttonName in  self.NumButtons:
                button = QPushButton(buttonName)
                button.setObjectName(buttonName)
                layout.addWidget(button)
                layout.setSpacing(10)
                button.clicked.connect(self.submitCommand)

                if buttonName == "forward":
                    button.setDisabled(True)

        #self.verticalGroupBox.setLayout(layout)

    def Einzelschritt(self):
        # self.thread_forward()
        self.threadpool.start(self.thread_forward) #neuer Thread um Anzeige in der UI zu ermöglichen

    def thread_forward(self):
        self.figure.clf()

        # lsg_copy = copy.deepcopy(self.Loesung)
        # self.graphHistory.append(lsg_copy)
        algoFertig = self.Loesung.algo(self.figure, self.canvas, self)

        if algoFertig == True:
            self.greyedForward() #TODO klappt nicht wegen Threads
        self.canvas.draw_idle()

#erstmal nicht implementiert
    def backward(self):
        self.threadpool.start(self.thread_backward)
        # self.thread_backward()

#erstmal nicht implementiert
    def thread_backward(self):
        self.figure.clf()

        self.Loesung = self.graphHistory.pop(-1)

        # self.Loesung.color_graph()
        self.Loesung.drawGraph()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def drawQT(self):
        self.counter +=1
        self.l.setText("Counter: %d" % self.counter)
        self.canvas.draw_idle()
        screen.show()

if __name__ == '__main__':

    import sys  
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    app.setStyle(QStyleFactory.create("gtk"))
    screen = PrettyWidget() 
    screen.show()   
    sys.exit(app.exec_())
