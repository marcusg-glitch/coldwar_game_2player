import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge and Catch")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Fonts
font = pygame.font.SysFont("comicsans", 40)
small_font = pygame.font.SysFont("comicsans", 30)

# Player dimensions
PLAYER_WIDTH, PLAYER_HEIGHT = 50, 50

# Load images
background_img = pygame.image.load('spacebackgroundimage.png')
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
missile_img = pygame.image.load('missile.png')
missile_img = pygame.transform.scale(missile_img, (PLAYER_WIDTH, int(PLAYER_HEIGHT)))
explosion_img = pygame.image.load('nuked.png')
explosion_img = pygame.transform.scale(explosion_img, (PLAYER_WIDTH, int(PLAYER_HEIGHT * 1.5)))
migplane_img = pygame.image.load('migplane.png')
migplane_img = pygame.transform.scale(migplane_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
stealthbomber_img = pygame.image.load('stealthbomber.png')
stealthbomber_img = pygame.transform.scale(stealthbomber_img, (PLAYER_WIDTH, PLAYER_HEIGHT))

# City lists
russian_cities = ["Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg", "Nizhny Novgorod"]
usa_cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]

# Player classes
class Player:
    def __init__(self, x, y, img, name):
        self.x = x
        self.y = y
        self.img = img
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.score = 0
        self.name = name

    def draw(self, win):
        win.blit(self.img, (self.rect.x, self.rect.y))
        score_text = font.render(f"{self.name}: {self.score}", 1, RED if self.img == migplane_img else BLUE)
        win.blit(score_text, (10 if self.img == migplane_img else WIDTH - 200, 10))

    def move(self, keys, left, right, up, down):
        if keys[left] and self.rect.left > 0:
            self.rect.x -= 5
        if keys[right] and self.rect.right < WIDTH:
            self.rect.x += 5
        if keys[up] and self.rect.top > 0:
            self.rect.y -= 5
        if keys[down] and self.rect.bottom < HEIGHT:
            self.rect.y += 5

class FallingObject:
    def __init__(self):
        self.x = random.randint(0, WIDTH - PLAYER_WIDTH)
        self.y = 0
        self.width = PLAYER_WIDTH
        self.height = int(PLAYER_HEIGHT * 0.5)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = 5
        self.exploded = False
        self.explosion_time = None
        self.city = random.choice(russian_cities if random.randint(0, 1) == 0 else usa_cities)
        self.alpha = 255

    def draw(self, win):
        if self.exploded:
            self.alpha = max(0, self.alpha - 5)  # Gradually reduce alpha value
            temp_explosion_img = explosion_img.copy()
            temp_explosion_img.set_alpha(self.alpha)
            win.blit(temp_explosion_img, (self.rect.x, HEIGHT - explosion_img.get_height()))
            explosion_text = small_font.render(f"{self.city} Depleted", 1, RED)
            text_surface = explosion_text.convert_alpha()
            text_surface.set_alpha(self.alpha)
            win.blit(text_surface, (self.rect.x, HEIGHT - explosion_img.get_height() - 30))
        else:
            win.blit(missile_img, (self.rect.x, self.rect.y))

    def fall(self):
        self.rect.y += self.speed

    def explode(self):
        self.exploded = True
        self.explosion_time = pygame.time.get_ticks()

# Countdown timer before each game
def countdown():
    for i in range(3, 0, -1):
        win.blit(background_img, (0, 0))
        countdown_text = font.render(f"{i}", 1, WHITE)
        win.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2 - countdown_text.get_height() // 2))
        pygame.display.update()
        time.sleep(1)

# Main function
def main():
    run = True
    clock = pygame.time.Clock()
    
    while run:
        # Reset scores and objects
        player1 = Player(100, HEIGHT - 100, migplane_img, "The Soviets")
        player2 = Player(WIDTH - 150, HEIGHT - 100, stealthbomber_img, "USA")
        falling_objects = []
        
        # Countdown before the game starts
        countdown()
        
        start_time = time.time()
        game_time = 60  # Game duration in seconds
        
        while time.time() - start_time < game_time:
            clock.tick(30)
            win.blit(background_img, (0, 0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break
            
            keys = pygame.key.get_pressed()
            player1.move(keys, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s)
            player2.move(keys, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN)
            
            if random.randint(1, 20) == 1:
                falling_objects.append(FallingObject())
            
            for obj in falling_objects:
                if not obj.exploded:
                    obj.fall()
                obj.draw(win)
                if obj.rect.top > HEIGHT:
                    obj.explode()
                elif obj.rect.colliderect(player1.rect):
                    falling_objects.remove(obj)
                    player1.score += 1
                elif obj.rect.colliderect(player2.rect):
                    falling_objects.remove(obj)
                    player2.score += 1

            # Remove explosions that have lasted for more than 2 seconds
            current_time = pygame.time.get_ticks()
            falling_objects = [obj for obj in falling_objects if not (obj.exploded and current_time - obj.explosion_time > 2000)]
            
            player1.draw(win)
            player2.draw(win)
            
            # Display remaining time
            remaining_time = int(game_time - (time.time() - start_time))
            timer_text = font.render(f"Time: {remaining_time}", 1, WHITE)
            win.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 10))
            
            pygame.display.update()
        
        # Display winner
        win.blit(background_img, (0, 0))
        if player1.score > player2.score:
            winner_text = font.render(f"The Soviets win with {player1.score} points!", 1, RED)
        elif player2.score > player1.score:
            winner_text = font.render(f"USA wins with {player2.score} points!", 1, BLUE)
        else:
            winner_text = font.render("It's a tie!", 1, WHITE)
        
        win.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2 - winner_text.get_height() // 2))
        designer_text = small_font.render("Game designed by Marcus Granath, he's an advocator of capitalism,", 1, WHITE)
        designer_text2 = small_font.render("democracy and freedom of speech", 1, WHITE)
        win.blit(designer_text, (WIDTH // 2 - designer_text.get_width() // 2, HEIGHT // 2 + 50))
        win.blit(designer_text2, (WIDTH // 2 - designer_text2.get_width() // 2, HEIGHT // 2 + 80))
        pygame.display.update()
        time.sleep(5)
    
    pygame.quit()

if __name__ == "__main__":
    main()