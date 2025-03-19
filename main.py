import pygame
from functools import lru_cache
from math import sqrt, pi, asin, acos
from random import choice




class Polymorph:
    def __init__(self):
        self.nodes = []
        self.lines = []
        self.polygons = []
        self.color = (255, 0, 0)
        self.closed = False

    def add_node(self, x, y):
        self.nodes.append((x, y))

    def draw(self, window):
        for line in self.lines:
            pygame.draw.line(window, (255,255,255), *line)

        for i in range(len(self.nodes)):
            if i < len(self.nodes) - 1:
                pygame.draw.line(window, self.color, self.nodes[i], self.nodes[i + 1])
            else:
                if self.closed:
                    pygame.draw.line(window, self.color, self.nodes[i], self.nodes[0])
                else:
                    pygame.draw.line(window, self.color, self.nodes[i], pygame.mouse.get_pos())

    def close(self):
        self.closed = True
        for i, node in enumerate(self.nodes):
            line = tuple([node, self.nodes[i + 1] if i < len(self.nodes) - 1 else self.nodes[0]])
            self.lines.append(line)
        for node in self.nodes:
            for second_node in self.nodes:
                if node == second_node: continue
                line = (node, second_node)
                if line not in self.lines:
                    if not any([self.lines_crossing(line, line_) for line_ in self.lines]):
                        self.lines.append(line)
        nodes = list(self.nodes)
        nodes.extend(self.nodes[:2])

        for line in self.lines:
            line_node1, line_node2 = line
            for i, node in enumerate(self.nodes):
                if node == line_node1:
                    break
            for i_, node in enumerate(self.nodes):
                if node == line_node2:
                    break
            start = min(i, i_)
            end = max(i, i_)
            if abs(start - end) <= 1: continue
            middle = choice(self.nodes[start+1:end])
            angle_direction = self.angle_direction(line_node1, middle, line_node2)
            
        for i, node in enumerate(nodes):
            if i == len(nodes) - 2:
                break
            second_node = nodes[i + 1]
            third_node = nodes[i + 2]
            angle = self.angle(node, second_node, third_node)
            print (angle, self.angle_direction(node, second_node, third_node))


                

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
    def angle(self, node1, node2, node3):
        A = self.basic_line(*node1, *node2).length
        B = self.basic_line(*node2, *node3).length
        C = self.basic_line(*node1, *node3).length
        cosc = (A**2 + B**2 - C**2)/(2*A*B)
        return acos(cosc) * 180/pi
    
    @lru_cache(maxsize=None)
    def angle_direction(self, node1, node2, node3) -> bool: # True = CW, False = CCW
        vector1 = node1[0]-node2[0], node1[1]-node2[1]
        vector2 = node3[0]-node2[0], node3[1]-node2[1]
        cross = vector1[0]*vector2[1]-vector1[1]*vector2[0]
        if cross > 0:
            return True
        return False



    class basic_line:
        def __init__(self, x1, y1, x2, y2):
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
            if x1 == x2:
                self.a = None
                self.b = x1
                self.length = abs(y1-y2)
                return
            a = (y1-y2) / (x1-x2) # y1-y2/x1-x2
            b = y1-a*x1 # y1-a*x1
            self.a = a
            self.b = b
            self.length = sqrt((x1-x2)**2+(y1-y2)**2)


    @lru_cache(maxsize=None)
    def lines_crosspoint(self, line1, line2):
        line1 = self.basic_line(*line1[0], *line1[1])
        line2 = self.basic_line(*line2[0],*line2[1])
        if line1.a == line2.a:
            return None
        x = (line2.b-line1.b)/(line1.a-line2.a)
        y = line1.a*x+line1.b
        return x, y
    
    def lines_crossing(self, line1, line2):
        line1 = tuple(line1)
        line2 = tuple(line2)
        crosspoint = self.lines_crosspoint(line1, line2)
        if crosspoint is None:
            return False
        x, y = crosspoint

        if (min(line1[0][0],line1[1][0])+1 < x < max(line1[0][0],line1[1][0])-1) and \
           (min(line2[0][0],line2[1][0])+1 < x < max(line2[0][0],line2[1][0])-1) and \
            (min(line1[0][1],line1[1][1])+1 < y < max(line1[0][1],line1[1][1])-1) and \
            (min(line2[0][1],line2[1][1])+1 < y < max(line2[0][1],line2[1][1])-1):
            if x in [line1[0][0], line1[1][0]] and y in [line1[0][1], line1[1][1]]:
                return False
            if x in [line2[0][0], line2[1][0]] and y in [line2[0][1], line2[1][1]]:
                return False
            return True
        return False
    




    def fill(self):
        pass

    def is_inside(self, x, y):
        pass


class Window:
    def __init__(self):
        self.width = 800
        self.height = 600
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
                        window.polygons.append(Polymorph())
                    window.polygons[-1].add_node(event.pos[0], event.pos[1])
                if event.button == 3:
                    if len(window.polygons) > 0:
                        window.polygons[-1].add_node(event.pos[0], event.pos[1])
                        window.polygons[-1].close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        pygame.time.delay(100)