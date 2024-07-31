import pygame
import random

# Pygame initialisieren
pygame.init()

# Spiel-Fenster-Einstellungen
WIDTH, HEIGHT = 800, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Outrider")

# Farben
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Spieler Einstellungen
PLAYER_WIDTH, PLAYER_HEIGHT = 50, 40
PLAYER_SPEED = 5
MAX_HP = 20
START_HP = 10
IMMUNE_TIME = 3000  # 3 Sekunden in Millisekunden

# Schuss Einstellungen
BULLET_SPEED = 10
MAX_BULLETS = 3
SHOOT_COOLDOWN = 333  # Millisekunden zwischen Schüssen (3 Schüsse pro Sekunde)

# Hindernisse Einstellungen
OBSTACLE_SPEED = 5
OBSTACLE_FREQUENCY = 1500  # Millisekunden zwischen Hindernissen

# Initialisieren des Fonts
FONT = pygame.font.SysFont('Arial', 24)

# Spielobjekte
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (50, HEIGHT // 2)  # Startposition des Spielers
        self.hp = START_HP
        self.last_hit = 0
        self.last_shot = 0

    def update(self, keys_pressed):
        # Bewegt den Spieler basierend auf gedrückten Tasten
        if keys_pressed[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys_pressed[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += PLAYER_SPEED
        if keys_pressed[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= PLAYER_SPEED
        if keys_pressed[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += PLAYER_SPEED

    def shoot(self):
        # Feuert einen Schuss, wenn die Abklingzeit vorbei ist
        now = pygame.time.get_ticks()
        if now - self.last_shot > SHOOT_COOLDOWN:
            self.last_shot = now
            bullet = Bullet(self.rect.right, self.rect.centery)  # Schuss kommt aus der rechten Seite des Spielers
            all_sprites.add(bullet)
            bullets.add(bullet)

    def get_hit(self):
        # Reduziert HP des Spielers, wenn er getroffen wird, und aktiviert Immunität für eine kurze Zeit
        now = pygame.time.get_ticks()
        if now - self.last_hit > IMMUNE_TIME:
            self.last_hit = now
            self.hp -= 1

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))  # Horizontale Kugel
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        # Bewegt den Schuss nach rechts
        self.rect.x += BULLET_SPEED
        if self.rect.left > WIDTH:
            self.kill()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.y = random.randint(0, HEIGHT - self.rect.height)
        self.rect.x = WIDTH  # Hindernis kommt von der rechten Seite

    def update(self):
        # Bewegt das Hindernis nach links
        self.rect.x -= OBSTACLE_SPEED
        if self.rect.right < 0:
            self.kill()

def draw_health_bar(surf, x, y, hp, max_hp):
    # Zeichnet die Lebensanzeige des Spielers
    BAR_WIDTH, BAR_HEIGHT = 200, 20
    fill = (hp / max_hp) * BAR_WIDTH
    border_rect = pygame.Rect(x, y, BAR_WIDTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, RED, fill_rect)
    pygame.draw.rect(surf, WHITE, border_rect, 2)

def game_over_screen():
    # Zeigt den Gameover-Bildschirm und wartet auf Eingaben des Spielers
    WINDOW.fill(BLACK)
    game_over_text = FONT.render('GAME OVER', True, WHITE)
    retry_text = FONT.render('Press R to Retry or Q to Quit', True, WHITE)
    WINDOW.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2 - 20))
    WINDOW.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, HEIGHT // 2 - retry_text.get_height() // 2 + 20))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                    main()
                if event.key == pygame.K_q:
                    pygame.quit()

def main():
    run = True
    clock = pygame.time.Clock()
    global all_sprites, bullets, obstacles
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    obstacle_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(obstacle_timer, OBSTACLE_FREQUENCY)

    while run:
        clock.tick(60)
        keys_pressed = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()
            if event.type == obstacle_timer:
                obstacle = Obstacle()
                all_sprites.add(obstacle)
                obstacles.add(obstacle)

        player.update(keys_pressed)  # Separates the update call for Player
        bullets.update()  # Updates only bullets
        obstacles.update()  # Updates only obstacles

        # Kollision zwischen Hindernissen und Schüssen
        hits = pygame.sprite.groupcollide(obstacles, bullets, True, True)

        # Kollision zwischen Spieler und Hindernissen
        player_hits = pygame.sprite.spritecollide(player, obstacles, False)
        for hit in player_hits:
            player.get_hit()
            hit.kill()

        # Überprüfen, ob der Spieler keine HP mehr hat
        if player.hp <= 0:
            game_over_screen()
            run = False

        # Zeichnen des Bildschirms
        WINDOW.fill(BLACK)
        all_sprites.draw(WINDOW)
        draw_health_bar(WINDOW, 10, 10, player.hp, MAX_HP)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
