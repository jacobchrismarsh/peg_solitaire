"""
graphy_utility has all utility classes for making the peg solitaire game boards.

By: Spencer Chang, Jacob Marshall

The following baseline for the following code was found at
http://interactivepython.org/courselib/static/pythonds/Graphs/Implementation.html
"""

NORTH = 0
EAST  = 1
SOUTH = 2
WEST  = 4

class Vertex:
    def __init__(self, hole: bool):
        self.hole = hole
        self.connectedTo = [None] * 4

    def addNeighbor(self, direction: int, neighbor: Vertex):
        self.connectedTo[direction] = neighbor

    def __str__(self):
        return str(self.id) + " connectedTo: " + str([x.id for x in self.connectedTo])

    def getConnections(self):
        return self.connectedTo

class Graph:
    def __init__(self):
        self.vertList = {}
        self.numVertices = 0

    def addVertex(self, key):
        self.numVertices = self.numVertices + 1
        newVertex = Vertex(key)
        self.vertList[key] = newVertex
        return newVertex

    def getVertex(self, n):
        if n in self.vertList:
            return self.vertList[n]
        else:
            return None

    def __contains__(self, n):
        return n in self.vertList

    def addEdge(self, f, t, cost=0):
        if f not in self.vertList:
            nv = self.addVertex(f)
        if t not in self.vertList:
            nv = self.addVertex(t)
        self.vertList[f].addNeighbor(self.vertList[t], cost)

    def getVertices(self):
        return self.vertList.keys()

    def __iter__(self):
        return iter(self.vertList.values())
