import pygame, sys, random, math
from utils import load_image, load_images
from text import Text

RADIUS = 1
SCREEN_RATIO = (4,3)

WHITE = (255,255,255)
BLACK = (0,0,0)
GREY = (169,169,169)
RED = (255,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)

CLEAR_GREY = (169,169,169,128)

LINE_WIDTH = 2



class Sim:
    def __init__(self):
            pygame.init()

            pygame.display.set_caption('Monte Carlo Pi Simulation')
            self.screen = pygame.display.set_mode((SCREEN_RATIO[0] * 150, SCREEN_RATIO[1] * 150))
            self.display = pygame.Surface((SCREEN_RATIO[0] * 150 * 5, SCREEN_RATIO[1] * 150 * 5))
            self.WIDTH = SCREEN_RATIO[0] * 150 * 5
            self.HEIGHT = SCREEN_RATIO[1] * 150 * 5
            self.SQUARE_SIZE = self.HEIGHT
            self.BUFFER = self.WIDTH * (1/SCREEN_RATIO[0])

            self.assets = {
                'GO': load_image('go.png'),
                'STOP': load_image('stop.png'),
                'RESTART': load_image('restart.png'),
                'ICON': load_image('pi_icon.png'),
                'SPEED': load_images('speeds'),
                'LAG': load_images('lags')
            }

            pygame.display.set_icon(self.assets['ICON'])

            self.points = []
            self.points_within = []
            self.total_points = 0
            self.points_in = 0

            self.frame = 0

            self.clock = pygame.time.Clock()

            self.clicking = False

            self.num_click = 0
            self.num_unclick = 0

            self.current_speed = 0

            self.lag_reduction = False

            # self.calc_points(500)

            self.running = False

            self.test_press = False

            self.rate = 10

            self.text = Text(f'Total Points: {self.total_points} nl Points In: {self.points_in} nl Ratio: {0} nl PI estimation: {0} nl 0 points/s', 125, pygame.rect.Rect(0,0,self.BUFFER, self.HEIGHT))


            # self.in_text = Text(f'points in: {self.points_in}', 30, WHITE)
            # self.total_text = Text(f'points in: {self.points}', 30, WHITE)

            

    def run(self):
        while True:
            
            self.display.fill(BLUE)

            mpos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        self.num_click += 1
                        self.test_press = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                        self.num_unclick += 1
                    

            self.test_rect = pygame.surface.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
            self.test_rect.fill((255,255,255))
            self.display.blit(self.test_rect, (self.BUFFER, 0))

            self.draw_points()
            self.generate_grid()
            self.draw_objects()

            self.draw_text()

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))

            self.draw_buttons()

            if (self.start_button_rect.collidepoint(mpos[0], mpos[1]) and self.clicking):
                self.running = True

            if (self.stop_button_rect.collidepoint(mpos[0], mpos[1]) and self.clicking):
                self.running = False

            if (self.restart_button_rect.collidepoint(mpos[0], mpos[1]) and self.clicking):
                self.points = []
                self.points_within = []
                self.total_points = 0
                self.points_in = 0
                self.running = False
                self.rate = 0
                self.current_speed = 0
                self.lag_reduction = False
                self.text.update_text(f'Total Points: {0} nl Points In: {0} nl Ratio: {0} nl PI estimation: {0} nl 0 points/s')

            if (self.speed_button_rect.collidepoint(mpos[0], mpos[1]) and self.running and self.clicking and self.test_press):
                self.current_speed = (self.current_speed + 1) % 6
                self.test_press = False

            if (self.lag_button_rect.collidepoint(mpos) and self.test_press):
                self.lag_reduction = not self.lag_reduction
                self.test_press = False
                

            if self.running:
                self.calc_points(self.rate)
            else:
                self.rate = 0

            print(self.current_speed)

            if self.current_speed == 0:
                self.rate = 1
            elif self.current_speed == 1:
                self.rate = 10
            elif self.current_speed == 2:
                self.rate = 50
            elif self.current_speed == 3:
                self.rate = 100
            elif self.current_speed == 4:
                self.rate = 500
            elif self.current_speed == 5:
                self.rate = 1000

                
            
            if self.start_button_rect.collidepoint(mpos[0], mpos[1]) or self.running:
                self.assets['GO'].set_alpha(128)
            else: self.assets['GO'].set_alpha(255)

            if self.stop_button_rect.collidepoint(mpos[0], mpos[1]) or not self.running:
                self.assets['STOP'].set_alpha(128)
            else: self.assets['STOP'].set_alpha(255)

            if self.restart_button_rect.collidepoint(mpos[0], mpos[1]):
                self.assets['RESTART'].set_alpha(128)
            else: self.assets['RESTART'].set_alpha(255)

            if self.running:
                if self.speed_button_rect.collidepoint(mpos[0], mpos[1]):
                    for img in self.assets['SPEED']:
                        img.set_alpha(128)
                else: 
                    for img in self.assets['SPEED']:
                        img.set_alpha(255)

            if self.lag_button_rect.collidepoint(mpos[0], mpos[1]):
                for img in self.assets['LAG']:
                    img.set_alpha(128)
            else:
                for img in self.assets['LAG']:
                    img.set_alpha(255)

            if self.total_points > 0:
                self.text.update_text(f'Total Points: {self.total_points} nl Points In: {self.points_in} nl Ratio: {round(self.points_in / self.total_points, 5)} nl PI estimation: nl {round(self.points_in / self.total_points * 4, 9)} nl {self.rate * 60} points/s')

            # print(mpos)
            # print(self.clicking)

            self.frame += 1
            pygame.display.update()
            self.clock.tick(60)

            

    def generate_grid(self):
        for i in range(5):
                line = pygame.surface.Surface((10,self.SQUARE_SIZE))
                line.fill(CLEAR_GREY)
                self.display.blit(line, (self.BUFFER + i * ((self.SQUARE_SIZE) * 0.2), 0))

        line = pygame.surface.Surface((10,self.SQUARE_SIZE))
        line.fill(CLEAR_GREY)
        self.display.blit(line, (self.BUFFER + 5 * ((self.SQUARE_SIZE) * 0.2) - 10, 0))

        for i in range(5):
            line = pygame.surface.Surface((self.SQUARE_SIZE,10))
            line.fill(CLEAR_GREY)
            self.display.blit(line, (self.BUFFER, 0 + i * ((self.SQUARE_SIZE) * 0.2)))

        line = pygame.surface.Surface((self.SQUARE_SIZE,10))
        line.fill(CLEAR_GREY)
        self.display.blit(line, (self.BUFFER, 0 + 5 * ((self.SQUARE_SIZE) * 0.2) - 10))

    def draw_objects(self):
        pygame.draw.rect(self.display, BLACK, pygame.rect.Rect(self.BUFFER, 0, self.SQUARE_SIZE, self.SQUARE_SIZE), width=20)

        pygame.draw.circle(self.display, BLACK, (self.BUFFER + self.SQUARE_SIZE / 2, self.SQUARE_SIZE / 2), self.SQUARE_SIZE / 2, 20)

    def calc_points(self, num):
        for i in range(num):
            point = (random.random(), random.random())
            self.points.append(point)
            distance = math.sqrt((point[0]-.5)**2 + (point[1]-.5) ** 2)
            if distance <= 0.5:
                self.points_in += 1
                self.points_within.append(True)
            else:
                self.points_within.append(False)
            self.total_points += 1

    def draw_points(self):
        if not self.lag_reduction:
            for i in range(len(self.points)):
                if self.points_within[i] == True:
                    pygame.draw.circle(self.display, RED, (self.BUFFER + self.points[i][0] * self.SQUARE_SIZE, self.points[i][1] * self.SQUARE_SIZE), 10)
                else:
                    pygame.draw.circle(self.display, GREEN, (self.BUFFER + self.points[i][0] * self.SQUARE_SIZE, self.points[i][1] * self.SQUARE_SIZE), 10)
        else:
            pygame.draw.rect(self.display, GREEN, pygame.rect.Rect(self.BUFFER, 0, self.SQUARE_SIZE, self.SQUARE_SIZE))
            pygame.draw.circle(self.display, RED, (self.BUFFER + self.SQUARE_SIZE/2, self.SQUARE_SIZE/2), self.SQUARE_SIZE / 2, self.SQUARE_SIZE)


    def draw_buttons(self):
        self.screen.blit(self.assets['GO'], (0, self.screen.get_height() - 40))
        self.start_button_rect = pygame.rect.Rect(0, self.screen.get_height() - 40, 50, 40)

        self.screen.blit(self.assets['STOP'], (50, self.screen.get_height() - 40))
        self.stop_button_rect = pygame.rect.Rect(50, self.screen.get_height() - 40, 50, 40)

        self.screen.blit(self.assets['RESTART'], (100, self.screen.get_height() - 40))
        self.restart_button_rect = pygame.rect.Rect(100, self.screen.get_height() - 40, 50, 40)

        self.speed_button_rect = pygame.rect.Rect(0, self.screen.get_height() - 80, 50, 40)
        if self.running:   
            self.screen.blit(self.assets['SPEED'][self.current_speed], (0, self.screen.get_height() - 80))

        self.lag_button_rect = pygame.rect.Rect(50, self.screen.get_height() - 80, 50, 40)
        self.screen.blit(self.assets['LAG'][int(self.lag_reduction)], (50, self.screen.get_height()-80))
            

    def draw_text(self):
        self.text.render(self.display)
    
Sim().run()