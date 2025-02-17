import pygame
import sys
import random
import sqlite3
import os


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


def get_sprite_folder():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    sprite_folder = os.path.join(current_directory, "sprites")
    if os.path.isdir(sprite_folder):
        return sprite_folder
    else:
        print("Папка со спрайтами не найдена. Пожалуйста, создайте папку с именем 'sprites' в директории скрипта.")
        sys.exit()


def load_sprites(folder, subfolder):
    sprite_folder = os.path.join(folder, subfolder)
    images = []
    try:
        for filename in os.listdir(sprite_folder):
            if filename.endswith(".png"):
                image_path = os.path.join(sprite_folder, filename)
                image = pygame.image.load(image_path).convert_alpha()
                image = pygame.transform.scale(image, (100, 100))
                images.append(image)
    except FileNotFoundError:
        print(f"Папка {sprite_folder} не найдена.")
    return images


pygame.init()
screen_width, screen_height = 1000, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Cyberbunk2077")

sprite_folder = get_sprite_folder()

images_running = load_sprites(sprite_folder, "RUN_cuts")
images_standing = load_sprites(sprite_folder, "IDLE_cuts")

background_image = pygame.image.load("1671511995_new_preview_12412412124.jpg")
platform_image = pygame.image.load("ground.png")
bomb_image = pygame.image.load("bomb.png").convert_alpha()

player_speed = 10
velocity_y = 0
gravity = 1
on_ground = True
player_pos = [200, 100]
platform_width = 100
platform_height = 10
finish_rect_1 = pygame.Rect(2000, 0, 20, 7000)
finish_rect_2 = pygame.Rect(2400, 0, 20, 7000)
current_level = 1
paused = False
elapsed_time = 0
bomb_speed = 10
last_bomb_spawn_time = 0
is_moving = False
frame_count = 0

platforms_level_1 = [
    pygame.Rect(400, 550, platform_width, platform_height),
    pygame.Rect(200, 400, platform_width, platform_height),
    pygame.Rect(550, 450, platform_width, platform_height),
    pygame.Rect(850, 400, platform_width, platform_height),
    pygame.Rect(1000, 300, platform_width, platform_height),
    pygame.Rect(1150, 200, platform_width, platform_height),
    pygame.Rect(1300, 150, platform_width, platform_height),
    pygame.Rect(1450, 100, platform_width, platform_height)
]

platforms_level_2 = [
    pygame.Rect(200, 200, platform_width, platform_height),
    pygame.Rect(600, 600, platform_width, platform_height),
    pygame.Rect(800, 400, platform_width, platform_height),
    pygame.Rect(1000, 300, platform_width, platform_height),
    pygame.Rect(1200, 250, platform_width, platform_height),
    pygame.Rect(1500, 700, platform_width, platform_height),
    pygame.Rect(1700, 600, platform_width, platform_height),
    pygame.Rect(1900, 700, platform_width, platform_height),
    pygame.Rect(2100, 550, platform_width, platform_height),
]


class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bomb_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = bomb_speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < -self.rect.width:
            self.kill()


bombs = pygame.sprite.Group()


def reset_game():
    global player_pos, velocity_y, on_ground, bombs, elapsed_time
    player_pos[0] = 200
    player_pos[1] = 100
    velocity_y = 0
    on_ground = True
    bombs.empty()
    elapsed_time = 0


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
    text_level_2 = font.render("Level 2", True, (0, 0, 0))

    while True:
        screen.fill((255, 255, 255))
        screen.blit(text_level_1, (screen_width // 2 - text_level_1.get_width() // 2, screen_height // 2 - 100))
        screen.blit(text_level_2, (screen_width // 2 - text_level_2.get_width() // 2, screen_height // 2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 1
                if event.key == pygame.K_2:
                    return 2
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


def create_bomb():
    if len(bombs) < 10:
        spawn_x = random.randint(screen_width + 200, screen_width + 900)
        spawn_y = random.randint(max(0, player_pos[1] - 100), min(screen_height, player_pos[1] + 100))
        new_bomb = Bomb(spawn_x, spawn_y)
        bombs.add(new_bomb)


def main_game():
    global player_pos, velocity_y, on_ground, paused, elapsed_time, last_bomb_spawn_time, is_moving
    global facing_right

    clock = pygame.time.Clock()
    timer_start = pygame.time.get_ticks()

    camera_x = 0
    current_frame_running = 0
    current_frame_standing = 0
    facing_right = True

    original_platform_image = pygame.image.load('ground.png').convert_alpha()
    platform_width = 100
    platform_height = 10

    if current_level == 1:
        current_platforms = platforms_level_1
        finish_rect = finish_rect_1
    else:
        current_platforms = platforms_level_2
        finish_rect = finish_rect_2

    while True:
        elapsed_time = (pygame.time.get_ticks() - timer_start) // 1000
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused

        keys = pygame.key.get_pressed()
        if not paused:
            is_moving = False
            if keys[pygame.K_a]:
                player_pos[0] -= player_speed
                is_moving = True
                facing_right = False
            if keys[pygame.K_d]:
                player_pos[0] += player_speed
                is_moving = True
                facing_right = True
            if keys[pygame.K_r]:
                reset_game()

            if on_ground and keys[pygame.K_SPACE]:
                velocity_y = -15
                on_ground = False

            velocity_y += gravity
            player_pos[1] += velocity_y

            camera_x = player_pos[0] - screen_width // 2 + 50
            camera_x = min(max(camera_x, 0), 1600)

            rect_player = pygame.Rect(player_pos[0] - camera_x, player_pos[1], 100, 100)
            on_ground = False

            screen.blit(background_image, (0, 0))

            for platform in current_platforms:
                scaled_platform_image = pygame.transform.scale(original_platform_image,
                                                               (platform_width, platform_height))
                screen.blit(scaled_platform_image, platform.move(-camera_x, 0))

            for platform in current_platforms:
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

            if current_time - last_bomb_spawn_time >= 2000:
                if player_pos[0] > screen_width / 2:
                    create_bomb()
                last_bomb_spawn_time = current_time

            global frame_count
            frame_count += 1

            if is_moving:
                if len(images_running) == 0:
                    print("Нет спрайтов для бега!")
                else:
                    if frame_count >= 10:
                        current_frame_running = (current_frame_running + 1) % len(images_running)
                        frame_count = 0
                    img_to_draw = images_running[current_frame_running]
                    if not facing_right:
                        img_to_draw = pygame.transform.flip(img_to_draw, True, False)
                    screen.blit(img_to_draw, (player_pos[0] - camera_x, player_pos[1]))
            else:
                if len(images_standing) == 0:
                    print("Нет спрайтов для стоя!")
                else:
                    if frame_count >= 10:
                        current_frame_standing = (current_frame_standing + 1) % len(images_standing)
                        frame_count = 0
                    img_to_draw = images_standing[current_frame_standing]
                    if not facing_right:
                        img_to_draw = pygame.transform.flip(img_to_draw, True, False)
                    screen.blit(img_to_draw, (player_pos[0] - camera_x, player_pos[1]))

            pygame.draw.rect(screen, (255, 0, 0), finish_rect.move(-camera_x, 0))

            font = pygame.font.Font(None, 36)
            text_timer = font.render(f'Time: {elapsed_time}', True, (255, 255, 255))
            screen.blit(text_timer, (10, 10))

            for bomb in bombs:
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
        print(f"Загружено спрайтов для бега: {len(images_running)}")
        print(f"Загружено спрайтов для стоя: {len(images_standing)}")
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
