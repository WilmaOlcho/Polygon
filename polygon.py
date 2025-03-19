from __future__ import annotations
from functools import lru_cache
from math import sqrt, pi, asin, acos
from random import choice


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, value:Node):
        return self.x == value.x and self.y == value.y
        
    def __hash__(self):
        return hash((self.x, self.y))
    
    @property
    def pos(self):
        return (self.x, self.y)
    
class Line:
    def __init__(self, node1:Node, node2:Node):
        self.nodes = [node1, node2]
        self.x1 = node1.x
        self.y1 = node1.y
        self.x2 = node2.x
        self.y2 = node2.y
        a = 0
        b = 0 
        if self.x1 == self.x2:
            a = None
            b = 0
            self.length = abs(self.y1-self.y2)
        elif self.y1 == self.y2:
            b = self.y1
            self.length = abs(self.x1-self.x2)
        else:
            a = (self.y1-self.y2) / (self.x1-self.x2) # y1-y2/x1-x2
            b = self.y1-a*self.x1 # y1-a*x1
        self.a = a
        self.b = b
        self.length = sqrt((self.x1-self.x2)**2+(self.y1-self.y2)**2)

    @lru_cache(maxsize=None)
    def distance_from_endpoint(self, point:Node)->float|None:
        if self.a is None:
            return abs(point.y-self.y1)
        elif self.a == 0:
            return abs(point.x-self.x1)
        if abs(self.a*point.x+self.b-point.y) < 0.001:
            return min(sqrt((point.x-self.x1)**2+(point.y-self.y1)**2), sqrt((point.x-self.x2)**2+(point.y-self.y2)**2))
        return None

    @lru_cache(maxsize=None)
    def point_in_line(self, point:Node, endpoints=False)->bool:
        if self.a is None:
            if point.x == self.x1 and point.y >= min(self.y1, self.y2) and point.y <= max(self.y1, self.y2):
                return self.distance_from_endpoint(point) > 0.01 if not endpoints else True
            return False
        if abs(self.a*point.x+self.b-point.y) < 0.0001:
            if point.x >= min(self.x1, self.x2) and point.x <= max(self.x1, self.x2):
                return self.distance_from_endpoint(point) > 0.01 if not endpoints else True
        return False

    def __eq__(self, value:Line):
        return self.a == value.a and self.b == value.b and \
                (self.x1 == value.x1 and self.y1 == value.y1 and \
                self.x2 == value.x2 and self.y2 == value.y2) or \
                (self.x1 == value.x2 and self.y1 == value.y2 and \
                self.x2 == value.x1 and self.y2 == value.y1)
        
    def __hash__(self):
        return hash((self.a, self.b, self.x1, self.y1, self.x2, self.y2))


class Polygon:
    def __init__(self):
        self.nodes = []
        self.lines = []
        self.edges = []
        self.polygons = []
        self.closed = False

    def add_node(self, x:float, y:float):
        """Add a node to the polygon."""
        node = Node(x, y)
        if node not in self.nodes:
            self.nodes.append(node)

    def point_in_polygon(self, x, y) -> bool:
        """Check if the point is inside the polygon."""
        for triangle in self.polygons:
            if self.point_in_triangle(x, y, triangle):
                return True
        return False
    
    def point_in_triangle(self, x, y, triangle:tuple[Node, Node, Node]) -> bool:
        """Check if the point is inside the triangle."""
        a, b, c = triangle
        point = Node(x, y)
        directions = [
            self.direction(point, a, b),
            self.direction(point, b, c),
            self.direction(point, c, a)]
        neg = not any([direction < 0 for direction in directions])
        pos = not any([direction > 0 for direction in directions])
        return neg or pos
    
    def select_triangle(self, x, y) -> tuple[Node, Node, Node]|None:
        """Select the triangle that contains the point."""
        for triangle in self.polygons:
            if self.point_in_triangle(x, y, triangle):
                return triangle
        return None

    def remove_node(self):
        """Remove the last node from the polygon."""
        if self.nodes:
            self.nodes.pop()

    def create_edges(self):
        """Create the edges of the polygon from existing nodes."""
        for i, node in enumerate(self.nodes):
            line = Line(node, self.nodes[i + 1] if i < len(self.nodes) - 1 else self.nodes[0])
            self.edges.append(line)

    def connect_nodes(self):
        """Connect the nodes with lines that do not intersect."""
        for node in self.nodes:
            nodes = self.nodes.copy()
            while nodes:
                second_node = choice(nodes)
                nodes.remove(second_node)
                if node == second_node: continue
                line = Line(node, second_node)
                if line not in [*self.lines, *self.edges]:
                    if not any([self.lines_crossing(line, line_) for line_ in [*self.lines, *self.edges]]):
                        self.lines.append(line)

    def winding_number(self, node:Node)->float:
        """Calculate the winding number."""
        winding_angle = 0
        for i in range(len(self.nodes)):
            start = i
            end = (start + 1) if i < len(self.nodes)-1 else 0
            angle = self.angle(self.nodes[start], node, self.nodes[end])
            direction = self.direction(self.nodes[start], node, self.nodes[end])
            if direction > 0: angle = -angle
            winding_angle+= angle
        return round(winding_angle, 2)

    def remove_lines_outside_polygon(self):
        """Remove lines that are outside the polygon."""
        for line in self.lines.copy():
            halfpoint = Node((line.x1+line.x2)/2, (line.y1+line.y2)/2)
            winding_number = self.winding_number(halfpoint)
            if round(abs(winding_number/360),2) < 1:
                self.lines.remove(line)
                continue
    
    def divide_to_triangles(self):
        """Divide the polygon to triangles."""
        nodes = self.nodes.copy()
        lines = [*self.lines.copy(), *self.edges.copy()]
        while len(nodes) >= 3:
            node = nodes[0]
            node_lines = []
            for line in lines:
                if node in line.nodes:
                    node_lines.append(line)
                if len(node_lines) > 2:
                    break
            if len(node_lines) == 2:
                nodes.remove(node)
                for line in node_lines:
                    lines.remove(line)
                nodeset = set()
                for line in node_lines:
                    for line_node in line.nodes:
                        nodeset.add(line_node)
                triangle = tuple(nodeset)
                self.polygons.append(triangle)
            else:
                nodes_shift = [*nodes[1:], node]
                nodes = nodes_shift

    def close(self):
        """Close the polygon."""
        assert len(self.nodes) >= 3, "Polygon must have at least 3 nodes."
        self.create_edges()
        self.connect_nodes()
        self.remove_lines_outside_polygon()
        self.divide_to_triangles()
        self.closed = True

    @lru_cache(maxsize=None)
    def angle(self, node1:Node, node2:Node, node3:Node)->float:
        """Calculate the angle between three nodes. Node2 as the vertex."""
        A = Line(node1, node2).length
        B = Line(node2, node3).length
        C = Line(node1, node3).length
        cosc = (A**2 + B**2 - C**2)/(2*A*B)
        return acos(cosc) * 180/pi
    
    @lru_cache(maxsize=None)
    def direction(self, node1:Node, node2:Node, node3:Node) -> float: # CW > 0, CCW <= 0
        """Calculate the side of node2 using nodes 1 and 3 as symmetry line points."""
        vector1 = node1.x-node2.x, node1.y-node2.y
        vector2 = node3.x-node2.x, node3.y-node2.y
        cross = vector1[0]*vector2[1]-vector1[1]*vector2[0]
        return cross

    @lru_cache(maxsize=None)
    def lines_crosspoint(self, line1:Line, line2:Line)->Node|None:
        """Calculate the crosspoint of two lines."""
        lines = [line1, line2]
        if any([line.a is None for line in lines]) and line1.a != line2.a: # one horizontal line case
            if line1.a is None: lines = lines[::-1]
            y = lines[0].b
            x = (y-lines[1].b)/lines[1].a
        elif line1.a == line2.a and line1.b == line2.b: # same line case
            halfpoint_line1 = Node((line1.x1+line1.x2)/2, (line1.y1+line1.y2)/2)
            halfpoint_line2 = Node((line2.x1+line2.x2)/2, (line2.y1+line2.y2)/2)
            intersection = Line(halfpoint_line1, halfpoint_line2)
            if line2.point_in_line(halfpoint_line1) and line1.point_in_line(halfpoint_line2):
                x, y = ((intersection.x1+intersection.x2)/2, (intersection.y1+intersection.y2)/2)
            else:
                return None
        elif line1.a == line2.a: # parallel line case
            return None
        else: # normal case
            x = (line2.b-line1.b)/(line1.a-line2.a)
            y = line1.a*x+line1.b
        return Node(x, y)
    
    def lines_crossing(self, line1:Line, line2:Line)->bool:
        """Check if two lines are crossing."""
        lines = [line1, line2]
        crosspoint = self.lines_crosspoint(*lines)
        if crosspoint is None:
            return False
        if all([line.point_in_line(crosspoint) for line in lines]):
            return True
        return False
    
    def is_inside(self, x, y):
        """Check if the point is inside the polygon."""
        return self.point_in_polygon(x, y)
