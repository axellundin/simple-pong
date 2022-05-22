from calendar import c
import os
from unicodedata import name
import pygame
import time
import random
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

pygame.init()
pygame.mixer.init()
Loading_font = pygame.font.SysFont(None, 48)
score_font = pygame.font.SysFont(None, 30)
## SOUNDS INIT
s = 'sounds'
bounce = pygame.mixer.Sound(os.path.join(s, 'hit.wav'))
point = pygame.mixer.Sound(os.path.join(s, 'point.wav'))
soundtrack = pygame.mixer.music.load(os.path.join(s, 'soundtrack.wav'))


class Ball():
    def __init__(self, xpos, ypos, xvel, yvel, radius, color=[255, 255, 255]):
        self.x_pos = xpos
        self.y_pos = ypos    
        self.x_vel = xvel
        self.y_vel = yvel
        self.radius = radius
        self.color = color
        self.dt = 1

    def update_position(self):
        self.x_pos += self.x_vel * self.dt
        self.y_pos += self.y_vel * self.dt

    def handle_collisions(self, walls, pprs, screen): 

        # Collisions with walls

        if self.x_pos < 0:
            pygame.mixer.Sound.play(point)
            return False, (0, 1)
        if self.x_pos > walls[0]:
            pygame.mixer.Sound.play(point)
            return False, (1, 0)

        if self.y_pos - self.radius + self.y_vel * self.dt < 0 or self.y_pos + self.radius + self.y_vel * self.dt > walls[1]:
            pygame.mixer.Sound.play(bounce)
            self.y_vel = -self.y_vel

        # Collisions with ping pong rackets

        for ppr in pprs: 
            width = walls[0]
            x_bounds, y_bounds = ppr.get_hitbox_position(screen)
            if y_bounds[0] <= self.y_pos <= y_bounds[1]:
                if ppr.player == 0 and x_bounds[1] + self.radius > self.x_pos + self.x_vel * self.dt <= x_bounds[0] + self.radius:
                    pygame.mixer.Sound.play(bounce)
                    self.x_vel = -self.x_vel
                if ppr.player == 1 and x_bounds[1] + self.radius > self.x_pos + self.x_vel * self.dt >= x_bounds[0] - self.radius:
                    pygame.mixer.Sound.play(bounce)
                    self.x_vel = -self.x_vel

        return True, (0,0)

    def gen_random_pertubation(self, max_percentage):
        rand = random.Random()
        return rand.randint(0, max_percentage), rand.randint(0, max_percentage)

class PingPongRackets():
    def __init__(self, player, relative_width = 0.01, rel_padding=0.05, relative_radius=0.1, relative_pos=0.5, max_movement=0.02, color=[255, 0, 0]):
        self.rel_padding = rel_padding
        self.relative_width = relative_width
        self.relative_radius = relative_radius
        self.relative_pos = relative_pos
        self.max_movement = max_movement
        self.player = player
        self.color = color

    def move(self, direction, screen):
        x_width , y_width = screen.get_size()

        self.relative_pos += self.max_movement * direction

        if self.relative_pos - self.relative_radius <=0:
            self.relative_pos = self.relative_radius
            return
        elif self.relative_pos + self.relative_radius >= 1:
            self.relative_pos = 1-self.relative_radius
            return

    def add_element(self, screen):
        x_width , y_width = screen.get_size()

        x_top = (1-self.player) * x_width * (self.rel_padding) + self.player * x_width * (1-self.rel_padding-self.relative_width)
        y_top = y_width * (self.relative_pos - self.relative_radius) 
        bar_width = self.relative_width * x_width
        bar_length = 2 * self.relative_radius * y_width
        pygame.draw.rect(screen, self.color ,pygame.Rect(x_top,y_top, bar_width, bar_length))

    def get_hitbox_position(self, screen): 
        x_width , y_width = screen.get_size()
        x_bound_1 = (1-self.player) * x_width * (self.rel_padding + self.relative_width) + self.player * x_width * (1-self.rel_padding-self.relative_width)
        x_bound_2 = (1-self.player) * x_width * (self.rel_padding) + self.player * x_width * (1-self.rel_padding)
        x_bounds = [x_bound_1, x_bound_2]
        y_bounds = [(self.relative_pos - self.relative_radius) * y_width, (self.relative_pos + self.relative_radius) * y_width]
        return x_bounds, y_bounds

class Game:
    def __init__(self, screen, player_names, ball_initial_velocity=[5,5], ball_start_pos=[0,0]):
        self.players = player_names
        self.player_points = (0,0)
        self.screen = screen
        self.ball = Ball(ball_start_pos[0], ball_start_pos[1], ball_initial_velocity[0], ball_initial_velocity[1], 10)
        self.ppr = [PingPongRackets(0), PingPongRackets(1)]
        self.game_ongoing = True
        self.game_started = False

    def updateFrame(self):
        # Clear screen
        self.screen.fill(bg_color)
        widths = self.screen.get_size()

        for pr in self.ppr: 
            pr.add_element(self.screen)

        self.ball.update_position()
        self.game_ongoing, points_scored = self.ball.handle_collisions(widths, self.ppr, self.screen)
        pygame.draw.circle(self.screen, self.ball.color, (self.ball.x_pos, self.ball.y_pos), self.ball.radius)
        
        self.player_points = (self.player_points[0] + points_scored[0], self.player_points[1] + points_scored[1])

        pygame.display.update()
    
    def writeTextOnScreen(self, text: str, pos: tuple, color):
        img = Loading_font.render(text, True, color)
        self.screen.blit(img, pos)

    def writeScore(self): 
        width, _ = self.screen.get_size()
        positions = [ (10, 10), ((width // 2) + 10, 10) ]
        for i in range(2):
            img = score_font.render(f"{self.players[i]}: {self.player_points[i]}", True, [255, 255, 255])
            self.screen.blit(img, positions[i])

    def gameLoop(self): 
        while self.game_ongoing: 
            if self.game_started:
                self.updateFrame()
                draw_mid_line(self.screen)
            else: 
                self.screen.fill(bg_color)
                width, height = self.screen.get_size()
                self.writeTextOnScreen("Starta rundan genom att trycka på mellanslag!", (int(width/2)-350, int(height/2)-10), [0, 200, 0])
            
            self.writeScore()
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    break

                if event.type == pygame.VIDEORESIZE:
                    # There's some code to add back window content here.
                    surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                keys = pygame.key.get_pressed()

                if keys[pygame.K_w]:
                    self.ppr[0].move( -1, self.screen)
                if keys[pygame.K_s]:
                    self.ppr[0].move( 1, self.screen)
                if keys[pygame.K_o]:
                    self.ppr[1].move(-1, self.screen)
                if keys[pygame.K_l]:
                    self.ppr[1].move(1, self.screen)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE: 
                        self.game_started = True 

            pygame.display.update()
        return self.player_points

def draw_mid_line(screen):
    width, height = screen.get_size()
    width_midpoint = width // 2
    mid_line = pygame.Rect(width_midpoint, 0, 1, height)
    color = [255, 255, 255]
    pygame.draw.rect(screen, color, mid_line)

def game_setup(screen): 
    width, height = screen.get_size()
    width_midpoint = width // 2
    height_midpoint = height // 2

    names = ["", ""]
    text_color = [255, 255, 255]
    
    ready = False 

    choice = 0

    while not ready: 
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                    pygame.quit()
                    break
            
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_LEFT: 
                    choice = 0
                if event.key == pygame.K_RIGHT: 
                    choice = 1
                if event.key == pygame.K_RETURN: 
                    ready = True
                    break

                if event.key == pygame.K_BACKSPACE:
                    if len(names[choice])>0:
                        names[choice] = names[choice][:-1]
                else:
                    names[choice] += event.unicode
                    names[choice] = names[choice].strip()

        img_left = score_font.render("Namn: " + names[0], True, text_color) 
        img_right = score_font.render("Namn: " + names[1], True, text_color) 

        rects = [img_left.get_rect(), img_right.get_rect()]
        rects[0].topleft = (20, height_midpoint)
        rects[1].topleft = (width_midpoint + 20, height_midpoint)

        cursor = pygame.Rect(rects[choice].topright, (3, rects[choice].height))

        rects[0].size=img_left.get_size()
        rects[1].size=img_right.get_size()
        cursor.topleft = rects[choice].topright

        screen.fill(bg_color)
        screen.blit(img_left, rects[0])
        screen.blit(img_right, rects[1])
        if time.time() % 1 > 0.5:
            pygame.draw.rect(screen, [255, 0, 0], cursor)
        pygame.display.update()
    return names

def main():
    screen = pygame.display.set_mode()
    x_width , y_width = screen.get_size()
    x_width = int(0.8 * x_width)
    y_width = int(0.8 * y_width)
    screen = pygame.display.set_mode([x_width, y_width])
    global bg_color
    bg_color = [0, 0, 50]
    rand = random.Random()
    session_ongoing = True
    pygame.mixer.music.play(-1)
    score = (0, 0)
    names = game_setup(screen)
    pygame.mixer.music.stop()
    soundtrack = pygame.mixer.music.load(os.path.join(s, 'main_soundtrack.wav'))
    pygame.mixer.music.play(-1)
    
    while session_ongoing:
        pos_x = x_width // 2
        pos_y = rand.randint(0, y_width)

        vel_x = rand.choice([-1, 1]) * rand.randint(10, 15)
        vel_y = rand.randint(10, 15)
        game = Game(screen, names, ball_start_pos=[pos_x, pos_y], ball_initial_velocity=[vel_x,vel_y])
        game.player_points = score
        score = game.gameLoop()

if __name__=='__main__':main()