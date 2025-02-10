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
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

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
        self.randomize_position()
        self.randomize_type()

    def randomize_type(self):
        # Randomly choose food type with different probabilities
        food_types = [
            ('square', RED, 1, 0.5),     # 50% chance for 1 point
            ('triangle', YELLOW, 2, 0.3), # 30% chance for 2 points
            ('circle', BLUE, 3, 0.2)      # 20% chance for 3 points
        ]
        
        choice = random.random()
        cumulative_prob = 0
        for shape, color, points, prob in food_types:
            cumulative_prob += prob
            if choice <= cumulative_prob:
                self.shape = shape
                self.color = color
                self.points = points
                break

    def randomize_position(self):
        self.position = (random.randint(0, GRID_COUNT-1) * GRID_SIZE,
                        random.randint(0, GRID_COUNT-1) * GRID_SIZE)

    def render(self):
        x, y = self.position
        if self.shape == 'square':
            pygame.draw.rect(screen, self.color, 
                           (x, y, GRID_SIZE, GRID_SIZE))
        elif self.shape == 'triangle':
            points = [
                (x + GRID_SIZE/2, y),
                (x, y + GRID_SIZE),
                (x + GRID_SIZE, y + GRID_SIZE)
            ]
            pygame.draw.polygon(screen, self.color, points)
        else:  # circle
            pygame.draw.circle(screen, self.color,
                             (int(x + GRID_SIZE/2), int(y + GRID_SIZE/2)),
                             GRID_SIZE//2)

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

def draw_difficulty_screen(screen):
    # Semi-transparent overlay
    overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
    overlay.fill(BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))
    
    # Title text
    font = pygame.font.Font(None, 74)
    title_text = font.render('Select Difficulty', True, WHITE)
    title_rect = title_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 100))
    screen.blit(title_text, title_rect)
    
    # Difficulty buttons
    button_font = pygame.font.Font(None, 36)
    difficulties = ['Easy', 'Medium', 'Hard']
    button_rects = []
    
    for i, diff in enumerate(difficulties):
        text = button_font.render(diff, True, WHITE)
        rect = text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 20 + i * 60))
        pygame.draw.rect(screen, WHITE, rect.inflate(20, 10), 2)
        screen.blit(text, rect)
        button_rects.append(rect.inflate(20, 10))
    
    # Exit button
    exit_text = button_font.render('Exit', True, WHITE)
    exit_rect = exit_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 180))
    pygame.draw.rect(screen, WHITE, exit_rect.inflate(20, 10), 2)
    screen.blit(exit_text, exit_rect)
    button_rects.append(exit_rect.inflate(20, 10))
    
    pygame.display.update()
    return button_rects

def draw_game_over_screen(screen, score):
    # Semi-transparent overlay
    overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
    overlay.fill(BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))
    
    # Game Over text
    font = pygame.font.Font(None, 74)
    game_over_text = font.render('GAME OVER', True, WHITE)
    score_text = font.render(f'Score: {score}', True, WHITE)
    
    # Restart button
    button_font = pygame.font.Font(None, 36)
    restart_text = button_font.render('Click to Restart', True, WHITE)
    
    # Position elements
    game_over_rect = game_over_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 50))
    score_rect = score_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 20))
    restart_rect = restart_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 80))
    
    # Draw elements
    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    screen.blit(restart_text, restart_rect)
    
    return restart_rect

def main():
    snake = Snake()
    food = Food()
    enemies = []
    running = True
    game_over = False
    restart_button_rect = None
    food_counter = 0  # Counter for spawning enemies
    
    # Initial difficulty selection
    screen.fill(BLACK)
    difficulty_buttons = draw_difficulty_screen(screen)
    difficulty = None
    
    while difficulty is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(difficulty_buttons):
                    if rect.collidepoint(event.pos):
                        if i == 3:  # Exit button
                            pygame.quit()
                            sys.exit()
                        difficulty = ['easy', 'medium', 'hard'][i]
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Return to difficulty selection
                    screen.fill(BLACK)
                    difficulty_buttons = draw_difficulty_screen(screen)
                    snake.reset()
                    food.randomize_position()
                    enemies.clear()
                    food_counter = 0
                    
                    # Wait for difficulty selection
                    waiting_for_difficulty = True
                    while waiting_for_difficulty:
                        for diff_event in pygame.event.get():
                            if diff_event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif diff_event.type == pygame.MOUSEBUTTONDOWN:
                                for i, rect in enumerate(difficulty_buttons):
                                    if rect.collidepoint(diff_event.pos):
                                        difficulty = ['easy', 'medium', 'hard'][i]
                                        waiting_for_difficulty = False
                        clock.tick(30)
                elif event.key == pygame.K_UP and snake.direction != DOWN:
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
            snake.score += food.points
            food.randomize_position()
            food.randomize_type()
            # Enemy spawning based on difficulty
            food_counter += 1
            if difficulty == 'hard':
                enemies.append(spawn_enemy(snake.get_head_position()))
            elif difficulty == 'medium' and food_counter % 2 == 0:
                enemy = spawn_enemy(snake.get_head_position())
                enemy.enemy_type = 'circle'  # Only spawn easiest enemy type
                enemies.append(enemy)

        # Update enemies
        for enemy in enemies:
            enemy.move_towards(snake.get_head_position())
            # Check collision with snake head
            ex, ey = enemy.position
            sx, sy = snake.get_head_position()
            if (abs(ex - sx) < GRID_SIZE and 
                abs(ey - sy) < GRID_SIZE):
                game_over = True

        # Draw
        screen.fill(BLACK)
        snake.render()
        food.render()
        for enemy in enemies:
            enemy.render()
        
        # Draw score and difficulty
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {snake.score}', True, WHITE)
        diff_text = font.render(f'Difficulty: {difficulty.capitalize()}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(diff_text, (WINDOW_SIZE - diff_text.get_width() - 10, 10))
        
        if game_over:
            restart_button_rect = draw_game_over_screen(screen, snake.score)
            pygame.display.update()
            
            # Wait for restart
            waiting_for_restart = True
            while waiting_for_restart:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if restart_button_rect.collidepoint(event.pos):
                            # Return to difficulty selection
                            screen.fill(BLACK)
                            difficulty_buttons = draw_difficulty_screen(screen)
                            waiting_for_difficulty = True
                            
                            while waiting_for_difficulty:
                                for diff_event in pygame.event.get():
                                    if diff_event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()
                                    elif diff_event.type == pygame.MOUSEBUTTONDOWN:
                                        for i, rect in enumerate(difficulty_buttons):
                                            if rect.collidepoint(diff_event.pos):
                                                difficulty = ['easy', 'medium', 'hard'][i]
                                                game_over = False
                                                snake.reset()
                                                food.randomize_position()
                                                enemies.clear()
                                                food_counter = 0
                                                waiting_for_restart = False
                                                waiting_for_difficulty = False
                clock.tick(30)
        else:
            pygame.display.update()
            clock.tick(10)  # Control game speed

if __name__ == '__main__':
    main()
