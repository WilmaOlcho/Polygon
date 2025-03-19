import pygame
from polygon import Polygon

class Window:
    def __init__(self):
        self.width = 800
        self.height = 600
        pygame.init()

        self.window = pygame.display.set_mode((self.width, self.height))#, pygame.FULLSCREEN)
        pygame.display.set_caption("Polygon")
        self.color = (0, 0, 255)
        self.polygons = []

    def draw(self):
        inside = False
        for polygon in self.polygons:
            self.draw_polygon(polygon)
            if polygon.closed:
                inside |= polygon.is_inside(*pygame.mouse.get_pos())
        text = "INSIDE" if inside else "OUTSIDE"
        self.window.blit(pygame.font.SysFont("Arial", 20).render(text, True, (255,255,255)), (10, 10))
        pygame.display.update()

    def draw_polygon(self,polygon):
        cursor = pygame.mouse.get_pos()
        if not polygon.closed:
            for line in polygon.lines:
                pygame.draw.line(self.window, (255,255,255), *line)
            for i in range(len(polygon.nodes)):
                if i < len(polygon.nodes) - 1:
                    pygame.draw.line(self.window, self.color, polygon.nodes[i].pos, polygon.nodes[i + 1].pos,2)
                else:
                    pygame.draw.line(self.window, self.color, polygon.nodes[i].pos, cursor, 2)
                    pygame.draw.line(self.window, self.color, polygon.nodes[0].pos, cursor, 1)
        else:
            for triangle in polygon.polygons:
                color = self.color
                if triangle == polygon.select_triangle(*cursor):
                    color = (172, 172, 0)
                triangle = [node.pos for node in triangle]
                pygame.draw.polygon(self.window, color, triangle, 0)
                pygame.draw.polygon(self.window, (172,172,0), triangle, 1)

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