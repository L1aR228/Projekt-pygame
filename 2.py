import pygame
import sys
import random
import sqlite3


def init_db():
    conn = sqlite3.connect('highscores.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def add_score(time):
    conn = sqlite3.connect('highscores.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO scores (time) VALUES (?)', (time,))
    conn.commit()
    conn.close()


def get_high_scores():
    conn = sqlite3.connect('highscores.db')
    cursor = conn.cursor()
    cursor.execute('SELECT time FROM scores ORDER BY time ASC LIMIT 5')
    scores = cursor.fetchall()
    conn.close()
    return [score[0] for score in scores]


pygame.init()
screen_width, screen_height = 1000, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Cyberbunk2077")

background_image = pygame.image.load("1671511995_new_preview_12412412124.jpg")
platform_image = pygame.image.load("ground.png")
bomb_image = pygame.image.load("bomb.png").convert_alpha()
player_speed = 10
velocity_y = 0
gravity = 1
on_ground = True
platform_width = 100
platform_height = 10
platform_image = pygame.transform.scale(platform_image, (platform_width, platform_height))
finish_rect = pygame.Rect(2000, 450, 20, 100)
player_pos = [200, 100]
current_level = 1
paused = False
elapsed_time = 0
bomb_speed = 10
last_bomb_spawn_time = 0
speed_increase_time = 0

cube_colors = [(0, 128, 255), (255, 0, 0), (0, 255, 0), (255, 255, 0)]
current_color_index = 0
last_color_change_time = pygame.time.get_ticks()

platforms = [
    pygame.Rect(400, 550, platform_width, platform_height),
    pygame.Rect(200, 400, platform_width, platform_height),
    pygame.Rect(400, 450, platform_width, platform_height),
    pygame.Rect(550, 400, platform_width, platform_height),
    pygame.Rect(700, 350, platform_width, platform_height),
    pygame.Rect(850, 300, platform_width, platform_height),
    pygame.Rect(1000, 250, platform_width, platform_height),
    pygame.Rect(1150, 200, platform_width, platform_height),
    pygame.Rect(1300, 150, platform_width, platform_height),
    pygame.Rect(1450, 100, platform_width, platform_height)
]


class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bomb_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = bomb_speed  # Изменяем скорость бомбы(это нужно для того чтобы усложнить игру)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < -self.rect.width:
            self.kill()


bombs = pygame.sprite.Group()


def reset_game():
    global player_pos, velocity_y, on_ground, bombs, elapsed_time, bomb_speed
    player_pos[0] = 200
    player_pos[1] = 100
    velocity_y = 0
    on_ground = True
    bombs.empty()
    elapsed_time = 0
    bomb_speed = 10


def display_menu():
    font = pygame.font.Font(None, 74)
    text_play = font.render("Play", True, (0, 0, 0))
    text_exit = font.render("Exit", True, (0, 0, 0))
    scores = get_high_scores()
    text_highscores = font.render("High Scores", True, (0, 0, 0))

    while True:
        screen.fill((255, 255, 255))
        screen.blit(text_play, (screen_width // 2 - text_play.get_width() // 2, screen_height // 2 - 50))
        screen.blit(text_exit, (screen_width // 2 - text_exit.get_width() // 2, screen_height // 2 + 50))
        screen.blit(text_highscores, (screen_width // 2 - text_highscores.get_width() // 2, screen_height // 2 - 200))

        font_small = pygame.font.Font(None, 36)
        for i, score in enumerate(scores):
            text_score = font_small.render(f"{i + 1}. {score} seconds", True, (0, 0, 0))
            screen.blit(text_score,
                        (screen_width // 2 - text_score.get_width() // 2, screen_height // 2 - 150 + i * 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if text_play.get_rect(center=(screen_width // 2, screen_height // 2 - 50)).collidepoint(event.pos):
                    return
                elif text_exit.get_rect(center=(screen_width // 2, screen_height // 2 + 50)).collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        pygame.display.flip()


def display_level_selection():
    font = pygame.font.Font(None, 74)
    text_level_1 = font.render("Level 1", True, (0, 0, 0))

    while True:
        screen.fill((255, 255, 255))
        screen.blit(text_level_1, (screen_width // 2 - text_level_1.get_width() // 2, screen_height // 2 - 50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 1
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        pygame.display.flip()


def display_game_over(time):
    font = pygame.font.Font(None, 74)
    text_game_over = font.render("Level Completed", True, (0, 0, 0))
    font_timer = pygame.font.Font(None, 36)
    text_timer = font_timer.render(f'Time: {time} seconds', True, (0, 0, 0))

    screen.fill((255, 255, 255))
    screen.blit(text_game_over, (screen_width // 2 - text_game_over.get_width() // 2, screen_height // 2 - 50))
    screen.blit(text_timer, (screen_width // 2 - text_timer.get_width() // 2, screen_height // 2 + 50))
    pygame.display.flip()
    pygame.time.delay(2000)


def game_over():
    font = pygame.font.Font(None, 74)
    text_game_over = font.render("Game Over", True, (0, 0, 0))
    screen.fill((255, 255, 255))
    screen.blit(text_game_over, (screen_width // 2 - text_game_over.get_width() // 2, screen_height // 2 - 50))
    pygame.display.flip()
    pygame.time.delay(2000)


def create_bomb():  # Та самая смешная функция
    if len(bombs) < 4:
        spawn_x = random.randint(screen_width + 200, screen_width + 900)
        spawn_y = random.randint(max(0, player_pos[1] - 100),
                                 min(screen_height, player_pos[1] + 100))
        new_bomb = Bomb(spawn_x, spawn_y)
        bombs.add(new_bomb)


def main_game():
    global player_pos, velocity_y, on_ground, paused, current_color_index, last_color_change_time, elapsed_time, bomb_speed, last_bomb_spawn_time, speed_increase_time
    clock = pygame.time.Clock()
    timer_start = pygame.time.get_ticks()

    camera_x = 0

    while True:
        elapsed_time = (pygame.time.get_ticks() - timer_start) // 1000
        current_time = pygame.time.get_ticks()

        if current_time - speed_increase_time >= 5000:
            bomb_speed += 2
            speed_increase_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused

        keys = pygame.key.get_pressed()
        if not paused:
            if keys[pygame.K_a]:
                player_pos[0] -= player_speed
            if keys[pygame.K_d]:
                player_pos[0] += player_speed
            if keys[pygame.K_r]:
                reset_game()

            if on_ground and keys[pygame.K_SPACE]:
                velocity_y = -15
                on_ground = False

            velocity_y += gravity
            player_pos[1] += velocity_y

            camera_x = player_pos[0] - screen_width // 2 + 25
            camera_x = min(max(camera_x, 0), 1600)

            rect_player = pygame.Rect(player_pos[0] - camera_x, player_pos[1], 50, 50)
            on_ground = False

            for platform in platforms:
                if rect_player.colliderect(platform.move(-camera_x, 0)):
                    if velocity_y > 0:
                        if rect_player.bottom >= platform.top:
                            player_pos[1] = platform.top - rect_player.height
                            velocity_y = 0
                            on_ground = True
                            break
                    elif velocity_y < 0:
                        if rect_player.top <= platform.bottom:
                            player_pos[1] = platform.bottom
                            velocity_y = 0
                            break

            for bomb in bombs:
                if rect_player.colliderect(bomb.rect.move(-camera_x, 0)):
                    game_over()
                    return

            if rect_player.colliderect(finish_rect.move(-camera_x, 0)):
                add_score(elapsed_time)
                display_game_over(elapsed_time)
                reset_game()
                return
            if player_pos[1] > screen_height:
                game_over()
                return

            if current_time - last_bomb_spawn_time >= 1000:
                if player_pos[0] > screen_width / 2:
                    create_bomb()
                last_bomb_spawn_time = current_time

            if current_time - last_color_change_time > 500:
                current_color_index = (current_color_index + 1) % len(cube_colors)
                last_color_change_time = current_time

            screen.blit(background_image, (0, 0))
            for platform in platforms:
                screen.blit(platform_image, (platform.x - camera_x, platform.y))

            pygame.draw.rect(screen, cube_colors[current_color_index], rect_player)
            pygame.draw.rect(screen, (255, 0, 0), finish_rect.move(-camera_x, 0))

            font = pygame.font.Font(None, 36)
            text_timer = font.render(f'Time: {elapsed_time}', True, (0, 0, 0))
            screen.blit(text_timer, (10, 10))  # Отображение таймера в верхнем левом углу

            for bomb in bombs:
                bomb.speed = bomb_speed
                bomb.update()
                screen.blit(bomb.image, bomb.rect.move(-camera_x, 0).topleft)

            pygame.display.flip()
            clock.tick(30)
        else:
            font = pygame.font.Font(None, 74)
            text_pause = font.render("Paused", True, (0, 0, 0))
            screen.fill((255, 255, 255))
            screen.blit(text_pause, (screen_width // 2 - text_pause.get_width() // 2, screen_height // 2 - 50))
            pygame.display.flip()


init_db()

try:
    display_menu()
    while True:
        current_level = display_level_selection()
        reset_game()
        main_game()
except KeyboardInterrupt:
    print("Игра завершена.")
    pygame.quit()
    sys.exit()
except Exception as e:
    print(f"Произошла ошибка: {e}")
    pygame.quit()
    sys.exit()
