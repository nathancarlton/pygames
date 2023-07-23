import pygame
from pygame.locals import *
import random
import math

# Initialize Pygame
pygame.init()

# Set up the game window
screen_width, screen_height = 1500, 1000
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Meteor Madness")

level = 1  # Set level to 1 when the game starts
score = 0  # Set score to 0 when the game starts

# Game initialization
def init_game():
    global ship, asteroids, bullets, score, game_active, lives

    # Create game objects
    ship = Ship()
    asteroids = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    lives = 3  # Set lives to 3 when the game starts
    game_active = False

    # Spawn asteroids
    spawn_asteroids()

def draw_background(color):
    screen.fill(color)

# Spawn asteroids
def spawn_asteroids():
    for _ in range(10 + 2 * (level - 1)):
        while True:
            x = random.randrange(screen_width)
            y = random.randrange(screen_height)
            if ((x - screen_width/2)**2 + (y - screen_height/2)**2)**0.5 > 100:
                break
        asteroid = Asteroid(x, y)
        asteroids.add(asteroid)

# Game objects
class Ship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # OLD Triangle 
        # self.original_image = pygame.Surface((40, 40), pygame.SRCALPHA)
        # pygame.draw.polygon(self.original_image, (255, 255, 255), [(20, 0), (0, 40), (40, 40)])
        # self.image = self.original_image.copy()
        # self.rect = self.image.get_rect(center=(screen_width/2, screen_height/2))
        # png
        self.original_image = pygame.image.load("ship2.png").convert_alpha()
        # Resize the image to your desired size (optional)
        self.original_image = pygame.transform.scale(self.original_image, (40, 40))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(screen_width/2, screen_height/2))
        self.speed = 3
        self.direction = 'UP'
        self.invincible = False  # Add this line
        self.invincible_start_time = None  # Add this line
        self.bullet_timer = pygame.time.get_ticks()  # Bullet time!
        self.rotation_angle = 0  # Attribute for rotation angle
        self.moving = False  # Track if the ship is moving

    def update(self):
        keys = pygame.key.get_pressed()
        direction = (math.cos(math.radians(self.rotation_angle)), -math.sin(math.radians(self.rotation_angle)))

        if keys[K_LEFT]:
            self.rotation_angle += 3
            self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)
            self.moving = True  # Set self.moving to True when an arrow key is pressed

        if keys[K_RIGHT]:
            self.rotation_angle -= 3
            self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)
            self.moving = True  # Set self.moving to True when an arrow key is pressed

        if keys[K_UP]:
            self.rect.x += self.speed * direction[0]
            self.rect.y += self.speed * direction[1]
            self.moving = True  # Set self.moving to True when an arrow key is pressed
        if keys[K_DOWN]:
            self.rect.x -= self.speed * direction[0]
            self.rect.y -= self.speed * direction[1]
            self.moving = True  # Set self.moving to True when an arrow key is pressed

        # Check if arrow keys are not pressed and the ship is moving
        if not any(keys):
            self.rect.x += self.speed * 0.5 * direction[0]
            self.rect.y += self.speed * 0.5 * direction[1]

        # Always update the ship's position based on its direction of movement
        self.rect.x += self.speed * direction[0]
        self.rect.y += self.speed * direction[1]
        self.moving = True

        # End invincibility after 2 seconds
        if self.invincible and pygame.time.get_ticks() - self.invincible_start_time > 2000:
            self.invincible = False

        # Keep the ship within the screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height

        # Shoot bullets
        if keys[K_SPACE]:
            self.shoot_bullet()

    def shoot_bullet(self):
        if pygame.time.get_ticks() - self.bullet_timer > 200:  # Reduced shooting interval to 150 ms
            direction = (math.cos(math.radians(self.rotation_angle)), -math.sin(math.radians(self.rotation_angle)))
            bullet = Bullet(self.rect.centerx, self.rect.centery, direction)
            bullets.add(bullet)
            self.bullet_timer = pygame.time.get_ticks()  # Reset the timer
            # Increased the distance that the ship moves when it shoots
            self.rect.x += 2 * self.speed * direction[0]
            self.rect.y += 2 * self.speed * direction[1]

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Randomly determine the size of the asteroid
        size = random.randint(30, 90)

        # Create an empty surface
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)

        # Generate random outline shapes
        points = []
        for i in range(12):  # Use more points for a more irregular shape
            angle = i * (360 / 12)
            offset = random.uniform(size * 0.3, size * 0.5)  # Randomize the distance of the points from the center
            x_point = size / 2 + offset * math.cos(math.radians(angle))
            y_point = size / 2 + offset * math.sin(math.radians(angle))
            points.append([x_point, y_point])

        pygame.draw.polygon(self.image, (255, 0, 0), points, width=1)  # Set the width to 1 for outline

        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x = self.random_direction() * level  # Speed depends on the level
        self.speed_y = self.random_direction() * level  # Speed depends on the level

    def random_direction(self):
        # Generate -1 or 1 for random direction
        return random.choice([-1, 1])

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Bounce off the screen boundaries
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speed_x *= -1
        if self.rect.top < 0 or self.rect.bottom > screen_height:
            self.speed_y *= -1

        # Keep the asteroid within the screen bounds
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(screen_width, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(screen_height, self.rect.bottom)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)  # Create a square surface
        pygame.draw.circle(self.image, (0, 255, 0), (5, 5), 5)  # Draw a green circle onto the surface
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        self.direction = direction # attribute for direction vector

    def update(self):
        self.rect.x += self.speed * self.direction[0]
        self.rect.y += self.speed * self.direction[1]

        # Remove bullets when they go off-screen
        if self.rect.bottom < 0:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Show introduction page
def show_intro():
    global game_active
    intro_text = [
        "DESTROY THE ASTEROIDS BEFORE THEY REACH EARTH!",
        "",
        "LEFT or RIGHT to Turn",
        "SPACE to Shoot",
        "UP or DOWN moves Faster or Slower",
        "",
    ]

    font = pygame.font.Font(None, 28)
    text_y = screen_height // 2 - len(intro_text) * 10

    # Load the hero image and resize it to approximately 400x400 pixels
    hero = pygame.image.load("meteor_madness_hero.png").convert_alpha()
    hero = pygame.transform.scale(hero, (600, 300))

    # Calculate the position to center the hero image horizontally and place it higher on the screen
    hero_x = screen_width // 2 - hero.get_width() // 2
    hero_y = screen_height // 14

    for line in intro_text:
        text_surface = font.render(line, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen_width / 2, text_y))
        screen.blit(text_surface, text_rect)
        text_y += 30

    # Blit the centered image on the screen
    screen.blit(hero, (hero_x, hero_y))

    # Play button
    play_button = pygame.Rect(screen_width/2 - 50, screen_height/2 + 100, 100, 50)
    pygame.draw.rect(screen, (0, 255, 0), play_button)
    button_font = pygame.font.Font(None, 32)
    play_text = button_font.render("Play", True, (0, 0, 0))
    play_text_rect = play_text.get_rect(center=play_button.center)
    screen.blit(play_text, play_text_rect)

    pygame.display.flip()

    # Wait for the player to click the play button
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1 and play_button.collidepoint(event.pos):
                    waiting = False

    game_active = True

# Draw the current score
def draw_score():
    score_text = f"Score: {score}"
    font = pygame.font.Font(None, 28)
    score_surface = font.render(score_text, True, (255, 255, 255))
    score_rect = score_surface.get_rect(topleft=(10, 10))
    screen.blit(score_surface, score_rect)

# Draw the current level
def draw_level():
    level_text = f"Level: {level}"
    font = pygame.font.Font(None, 28)
    level_surface = font.render(level_text, True, (255, 255, 255))
    level_rect = level_surface.get_rect(topleft=(10, 40))  # Position it beneath the score
    screen.blit(level_surface, level_rect)

# Draw the remaining lives
def draw_lives():
    lives_text = f"Lives: {lives}"
    font = pygame.font.Font(None, 28)
    lives_surface = font.render(lives_text, True, (255, 255, 255))
    lives_rect = lives_surface.get_rect(topleft=(10, 70))  # Position it beneath the level
    screen.blit(lives_surface, lives_rect)

# Show level over screen with two choices: play again, next level, or quit
def level_over(reason):
    global game_active, level, score

    if reason == 'game_over':
        level_message = "Game Over!"
        level = 1  # Reset the level to 1
        score = 0  # Reset the score to 0
    elif reason == 'asteroids_cleared':
        level_message = "Good Job!" if level < 15 else "Winner! All Asteroids Cleared!"
        if level < 15:  # Only increment the level if it's less than 15
            level += 1
        elif level == 15:  # If level is exactly 15
            level = 1  # Reset the level to 1
            score = 0  # Reset the score to 0
        spawn_asteroids()  # Spawn new asteroids
    else:
        level_message = "You Crashed!"
        level = 1  # Reset the level to 1
        score = 0  # Reset the score to 0

    font = pygame.font.Font(None, 72)
    level_message_surface = font.render(level_message, True, (255, 0, 0))
    level_message_rect = level_message_surface.get_rect(center=(screen_width/2, screen_height/2))
    screen.blit(level_message_surface, level_message_rect)

    # Play again or next level button
    button_text = "Start Over" if reason == 'game_over' or reason == 'ship_collided' or level == 1 else "Next Level"
    play_again_button = pygame.Rect(screen_width/2 - 100, screen_height/2 + 100, 200, 50)  # Increased width
    pygame.draw.rect(screen, (0, 255, 0), play_again_button)
    button_font = pygame.font.Font(None, 32)
    play_again_text = button_font.render(button_text, True, (0, 0, 0))
    play_again_text_rect = play_again_text.get_rect(center=play_again_button.center)
    screen.blit(play_again_text, play_again_text_rect)

    # Quit button
    quit_button = pygame.Rect(screen_width/2 - 100, screen_height/2 + 160, 200, 50)  # Increased width
    pygame.draw.rect(screen, (255, 0, 0), quit_button)
    quit_text = button_font.render("Quit", True, (0, 0, 0))
    quit_text_rect = quit_text.get_rect(center=quit_button.center)
    screen.blit(quit_text, quit_text_rect)

    pygame.display.flip()

    # Wait for the player to click the play again button or quit button
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if play_again_button.collidepoint(event.pos):
                        if reason == 'game_over' or reason == 'ship_collided':
                            level = 1  # Reset the level to 1 only when the game is over or the ship has collided
                        waiting = False
                        init_game()  # Initialize game after clicking "Play Again"
                        game_active = True  # Set game_active to True
                    elif quit_button.collidepoint(event.pos):
                        pygame.quit()
                        quit()

    init_game()
    game_active = True  # Set game_active to True

# Create game objects
init_game()

# Show the introduction page
show_intro()

clock = pygame.time.Clock()

# Main game loop
def main():
    global game_active, score, level, lives
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if not game_active:
                        level = 1  # Set level to 1 when the player chooses to play again
                        init_game()
                        game_active = True

        # Draw background
        if ship.invincible:
            time_passed = pygame.time.get_ticks() - ship.invincible_start_time
            ratio = 1 - time_passed / 2010  # Ratio of the remaining invincibility time
            red = max(0, int(255 * ratio))  # Interpolate between 255 (red) and 0 (black)
            draw_background((red, 0, 0))  # The color gradually changes from red to black
        else:
            draw_background((0, 0, 0))  # Black background otherwise

        # Update game objects
        if game_active:
            ship.update()
            asteroids.update()
            bullets.update()

            # Check for collisions
            for asteroid in asteroids:
                if pygame.sprite.spritecollide(asteroid, bullets, True):
                    asteroid.kill()
                    score += 1

        # If the player clears all asteroids
        if len(asteroids) == 0 and not ship.invincible:
            game_active = False
            level_over('asteroids_cleared')

        # If the ship collides with an asteroid
        if pygame.sprite.spritecollide(ship, asteroids, False) and not ship.invincible:
            lives -= 1  # Decrease lives by 1
            ship.rect.center = (screen_width/2, screen_height/2)  # Reset the ship's position
            ship.invincible = True  # Set the ship to invincible
            ship.invincible_start_time = pygame.time.get_ticks()  # Start the timer
            if lives <= 0:  # Check if lives is 0
                game_active = False
                level_over('game_over')  # Call game_over instead of ship_collided

        # Clear the screen
        pass

        # Draw game objects
        if game_active:
            ship.draw(screen)
            asteroids.draw(screen)
            bullets.draw(screen)
            draw_score()
            draw_level()
            draw_lives()
        else:
            if game_active:  # Check if game_active is True after level_over
                continue  # Skip the rest of the loop and start the next iteration

        # Update the display
        pygame.display.flip()
        clock.tick(60)  # Adjust the frame rate as needed (e.g., 60 frames per second)

    # Quit the game
    pygame.quit()

if __name__ == "__main__":
    main()
