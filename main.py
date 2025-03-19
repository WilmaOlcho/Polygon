from __future__ import annotations
import pygame
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
            b = None
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
        self.color = (255, 0, 0)
        self.closed = False

    def add_node(self, x, y):
        node = Node(x, y)
        if node not in self.nodes:
            self.nodes.append(node)

    def draw(self, window):
        if not self.closed:
            for line in self.lines:
                pygame.draw.line(window, (255,255,255), *line)
            for i in range(len(self.nodes)):
                if i < len(self.nodes) - 1:
                    pygame.draw.line(window, self.color, self.nodes[i].pos(), self.nodes[i + 1].pos(),2)
                else:
                    if self.closed:
                        pygame.draw.line(window, self.color, self.nodes[i].pos(), self.nodes[0].pos(),2)
                    else:
                        pygame.draw.line(window, self.color, self.nodes[i].pos(), pygame.mouse.get_pos(), 2)
                        pygame.draw.line(window, self.color, self.nodes[0].pos(), pygame.mouse.get_pos(), 1)
        else:
            for triangle in self.polygons:
                triangle = [node.pos() for node in triangle]
                pygame.draw.polygon(window, self.color, triangle, 0)
                pygame.draw.polygon(window, (172,172,0), triangle, 1)
            text = "INSIDE" if self.is_inside(*pygame.mouse.get_pos()) else "OUTSIDE"
            window.blit(pygame.font.SysFont("Arial", 20).render(text, True, (255,255,255)), (10, 10))

    def point_in_polygon(self, x, y):
        for triangle in self.polygons:
            if self.point_in_triangle(x, y, triangle):
                return True
    
    def point_in_triangle(self, x, y, triangle:tuple[Node, Node, Node]):
        a, b, c = triangle
        point = Node(x, y)
        d1 = self.sign(point, a, b)
        d2 = self.sign(point, b, c)
        d3 = self.sign(point, c, a)
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        return not (has_neg and has_pos)
        
    def sign(self, p1:Node, p2:Node, p3:Node):
        return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)
    
    def purge(self):
        self.lines = []
        self.edges = []
        self.closed = False

    def close(self):
        self.purge()
        self.closed = True

        for i, node in enumerate(self.nodes):
            line = Line(node, self.nodes[i + 1] if i < len(self.nodes) - 1 else self.nodes[0])
            self.edges.append(line)
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

        for line in self.lines.copy():
            halfpoint = Node((line.x1+line.x2)/2, (line.y1+line.y2)/2)
            overall_angle = 0
            for i, node in enumerate(self.nodes):
                start = i
                end = (start + 1) if i < len(self.nodes)-1 else 0
                angle = self.angle(self.nodes[start], halfpoint, self.nodes[end])
                angle_direction = self.angle_direction( self.nodes[start], halfpoint,self.nodes[end])
                if angle_direction: angle = -angle
                overall_angle+= angle
            overall_angle = round(overall_angle, 2)
            if round(abs(overall_angle/360),2) < 1:
                self.lines.remove(line)
                continue
        
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
                

    @lru_cache(maxsize=None)
    def above_line(self, node, line):
        if line.a*node[0]+line.b > node[1]:
            return True
        return False
    
    @lru_cache(maxsize=None)
    def right_of_line(self, node, line):
        if line.a*node[0]+line.b < node[1]:
            return True
        return False

    @lru_cache(maxsize=None)
    def angle(self, node1:Node, node2:Node, node3:Node)->float:
        A = Line(node1, node2).length
        B = Line(node2, node3).length
        C = Line(node1, node3).length
        cosc = (A**2 + B**2 - C**2)/(2*A*B)
        return acos(cosc) * 180/pi
    
    @lru_cache(maxsize=None)
    def angle_direction(self, node1:Node, node2:Node, node3:Node) -> bool: # True = CW, False = CCW
        vector1 = node1.x-node2.x, node1.y-node2.y
        vector2 = node3.x-node2.x, node3.y-node2.y
        cross = vector1[0]*vector2[1]-vector1[1]*vector2[0]
        if cross > 0:
            return True
        return False

    @lru_cache(maxsize=None)
    def lines_crosspoint(self, line1:Line, line2:Line)->Node|None:
        if line1.a is None and line2.a is not None:
            if line2.a is None:
                return None
            x = line1.x1
            y = line2.a*x+line2.b
        elif line2.a is None and line1.a is not None:
            x = line2.x1
            y = line1.a*x+line1.b
        elif line1.a == line2.a and line1.b == line2.b:
            halfpoint_line1 = Node((line1.x1+line1.x2)/2, (line1.y1+line1.y2)/2)
            halfpoint_line2 = Node((line2.x1+line2.x2)/2, (line2.y1+line2.y2)/2)
            intersection = Line(halfpoint_line1, halfpoint_line2)
            if line2.point_in_line(halfpoint_line1) and line1.point_in_line(halfpoint_line2):
                x, y = ((intersection.x1+intersection.x2)/2, (intersection.y1+intersection.y2)/2)
            else:
                return None
        elif line1.a == line2.a:
            return None
        else:
            x = (line2.b-line1.b)/(line1.a-line2.a)
            y = line1.a*x+line1.b
        return Node(x, y)
    
    def lines_crossing(self, line1:Line, line2:Line)->bool:
        lines = [line1, line2]
        crosspoint = self.lines_crosspoint(*lines)
        if crosspoint is None:
            return False
        if all([line.point_in_line(crosspoint) for line in lines]):
            return True
        return False
    
    def fill(self):
        pass

    def is_inside(self, x, y):
        return self.point_in_polygon(x, y)

class Window:
    def __init__(self):
        self.width = 800
        self.height = 600
        pygame.init()

        self.window = pygame.display.set_mode((self.width, self.height))#, pygame.FULLSCREEN)
        pygame.display.set_caption("Polymorph")
        self.polygons = []

    def draw(self):
        for polygon in self.polygons:
            polygon.draw(self.window)
        pygame.display.update()

    def clear(self):
        self.window.fill((0, 0, 0))


if __name__ == "__main__":
    window = Window()
    running = True
    while running:
        window.clear()
        window.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if len(window.polygons) == 0 or window.polygons[-1].closed:
                        window.polygons.append(Polygon())
                    window.polygons[-1].add_node(event.pos[0], event.pos[1])
                if event.button == 3:
                    if len(window.polygons) > 0:
                        window.polygons[-1].add_node(event.pos[0], event.pos[1])
                        window.polygons[-1].close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        pygame.time.delay(100)