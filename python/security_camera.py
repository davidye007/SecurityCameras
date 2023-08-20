import math, pygame

class SecurityCamera:
    surface = None

    def __init__(self, x, y, fov, direction, floorBitmap):
        self.x = x
        self.y = y
        self.fov = fov
        self.direction = direction
        self.floorBitmap = floorBitmap
        self.width = len(self.floorBitmap)
        self.height = len(self.floorBitmap[0])
        self.viewable = self.computeViewable()

    def inBounds(self, currX, currY):
        return 0 <= currX < self.width and 0 <= currY < self.height

    def computeViewable(self):
        viewable = [[False for y in range(self.height)] for x in range(self.width)]
        # print(self.x)
        viewable[self.x][self.y] = True
        angle = self.direction - self.fov/2
        while angle <= self.direction + self.fov/2:
            currX = self.x
            currY = self.y
            dx = math.cos(math.radians(angle))
            dy = math.sin(math.radians(angle))
            if dx == 0 or dy == 0:
                while self.inBounds(currX, currY):
                    if self.floorBitmap[int(currX)][int(currY)]:
                        break
                    viewable[int(currX)][int(currY)] = True
                    currX += dx
                    currY += dy
            elif abs(dx) < abs(dy):
                dy /= abs(dx)
                hitWall = False
                while self.inBounds(currX, currY):
                    if self.floorBitmap[int(currX)][int(currY)]:
                        break

                    nextY = currY + 0.5*dy
                    nextNextY = currY + dy
                    signX = -1 if dx < 0 else 1
                    signY = -1 if dy < 0 else 1

                    while currY*signY < nextY*signY and self.inBounds(currX, currY):
                        if self.floorBitmap[int(currX)][int(currY)]:
                            hitWall = True
                            break
                        viewable[int(currX)][int(currY)] = True
                        currY += signY

                    if hitWall:
                        break

                    currY = nextY
                    currX += signX
                    while currY*signY < nextNextY*signY and self.inBounds(currX, currY):
                        if self.floorBitmap[int(currX)][int(currY)]:
                            hitWall = True
                            break
                        viewable[int(currX)][int(currY)] = True
                        currY += signY

                    currY = nextNextY
                    if hitWall:
                        break
            else:
                dx /= abs(dy)
                hitWall = False
                while self.inBounds(currX, currY):
                    if self.floorBitmap[int(currX)][int(currY)]:
                        break

                    nextX = currX + 0.5*dx
                    nextNextX = currX + dx
                    signX = -1 if dx < 0 else 1
                    signY = -1 if dy < 0 else 1

                    while currX*signX < nextX*signX and self.inBounds(currX, currY):
                        if self.floorBitmap[int(currX)][int(currY)]:
                            hitWall = True
                            break
                        viewable[int(currX)][int(currY)] = True
                        currX += signX

                    if hitWall:
                        break

                    currX = nextX
                    currY += signY
                    while currX*signX < nextNextX*signX and self.inBounds(currX, currY):
                        if self.floorBitmap[int(currX)][int(currY)]:
                            hitWall = True
                            break
                        viewable[int(currX)][int(currY)] = True
                        currX += signX

                    currX = nextNextX
                    if hitWall:
                        break
            angle += 0.05

        return viewable

    def render(self, screen):
        if self.surface is None:
            self.surface = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA)
            for x in range(self.width):
                for y in range(self.height):
                    if self.viewable[x][y]:
                        self.surface.set_at((x,self.height-y-1), pygame.Color(255, 0, 0, 68))
                    else:
                        self.surface.set_at((x,self.height-y-1), pygame.Color(0,0,0,0))
        screen.blit(self.surface, self.surface.get_rect())