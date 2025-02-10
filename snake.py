import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 800
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
PINK = (255, 192, 203)
PURPLE = (128, 0, 128)

# Initialize screen
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('Snake Game')
clock = pygame.time.Clock()

class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [(WINDOW_SIZE//2, WINDOW_SIZE//2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = GREEN
        self.score = 0

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = ((cur[0] + (x*GRID_SIZE)) % WINDOW_SIZE, (cur[1] + (y*GRID_SIZE)) % WINDOW_SIZE)
        if new in self.positions[3:]:
            return False
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()
            return True

    def reset(self):
        self.length = 1
        self.positions = [(WINDOW_SIZE//2, WINDOW_SIZE//2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.score = 0

    def render(self):
        for p in self.positions:
            pygame.draw.rect(screen, self.color, (p[0], p[1], GRID_SIZE, GRID_SIZE))

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_COUNT-1) * GRID_SIZE,
                        random.randint(0, GRID_COUNT-1) * GRID_SIZE)

    def render(self):
        pygame.draw.rect(screen, self.color, 
                        (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE))

# Directional constants
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Enemy:
    def __init__(self, enemy_type):
        self.position = (random.randint(0, GRID_COUNT-1) * GRID_SIZE,
                        random.randint(0, GRID_COUNT-1) * GRID_SIZE)
        self.enemy_type = enemy_type
        if enemy_type == 'circle':
            self.color = WHITE
            self.speed = 0.15
        elif enemy_type == 'square':
            self.color = PINK
            self.speed = 0.25
        else:  # triangle
            self.color = PURPLE
            self.speed = 0.35
            
    def move_towards(self, target_pos):
        x, y = self.position
        tx, ty = target_pos
        
        # Add random movement
        tx += random.randint(-GRID_SIZE*3, GRID_SIZE*3)
        ty += random.randint(-GRID_SIZE*3, GRID_SIZE*3)
        
        # Calculate direction
        dx = tx - x
        dy = ty - y
        
        # Normalize and apply speed
        distance = max(abs(dx), abs(dy))
        if distance > 0:
            dx = (dx / distance) * GRID_SIZE * self.speed
            dy = (dy / distance) * GRID_SIZE * self.speed
            
        # Update position
        new_x = (x + dx) % WINDOW_SIZE
        new_y = (y + dy) % WINDOW_SIZE
        self.position = (new_x, new_y)
        
    def render(self):
        x, y = self.position
        if self.enemy_type == 'circle':
            pygame.draw.circle(screen, self.color, 
                             (int(x + GRID_SIZE/2), int(y + GRID_SIZE/2)), 
                             GRID_SIZE//2)
        elif self.enemy_type == 'square':
            pygame.draw.rect(screen, self.color, 
                           (x, y, GRID_SIZE, GRID_SIZE))
        else:  # triangle
            points = [
                (x + GRID_SIZE/2, y),
                (x, y + GRID_SIZE),
                (x + GRID_SIZE, y + GRID_SIZE)
            ]
            pygame.draw.polygon(screen, self.color, points)

def spawn_enemy(snake_pos):
    # Don't spawn within 10 grid cells of snake
    while True:
        x = random.randint(0, GRID_COUNT-1) * GRID_SIZE
        y = random.randint(0, GRID_COUNT-1) * GRID_SIZE
        sx, sy = snake_pos
        if abs(x - sx) > GRID_SIZE*10 or abs(y - sy) > GRID_SIZE*10:
            break
    
    enemy_type = random.choice(['circle', 'square', 'triangle'])
    enemy = Enemy(enemy_type)
    enemy.position = (x, y)
    return enemy

def main():
    snake = Snake()
    food = Food()
    enemies = []  # Start with no enemies
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != DOWN:
                    snake.direction = UP
                elif event.key == pygame.K_DOWN and snake.direction != UP:
                    snake.direction = DOWN
                elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                    snake.direction = LEFT
                elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                    snake.direction = RIGHT

        # Update snake
        if not snake.update():
            snake.reset()
            food.randomize_position()

        # Check for food collision
        if snake.get_head_position() == food.position:
            snake.length += 1
            snake.score += 1
            food.randomize_position()
            # Spawn new enemy when food is eaten
            enemies.append(spawn_enemy(snake.get_head_position()))

        # Update enemies
        for enemy in enemies:
            enemy.move_towards(snake.get_head_position())
            # Check collision with snake head
            ex, ey = enemy.position
            sx, sy = snake.get_head_position()
            if (abs(ex - sx) < GRID_SIZE and 
                abs(ey - sy) < GRID_SIZE):
                snake.reset()
                food.randomize_position()
                # Reset enemy positions
                for e in enemies:
                    e.position = (random.randint(0, GRID_COUNT-1) * GRID_SIZE,
                                random.randint(0, GRID_COUNT-1) * GRID_SIZE)

        # Draw
        screen.fill(BLACK)
        snake.render()
        food.render()
        for enemy in enemies:
            enemy.render()
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {snake.score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.update()
        clock.tick(10)  # Control game speed

if __name__ == '__main__':
    main()
