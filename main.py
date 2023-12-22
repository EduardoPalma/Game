import Pyro5.api
from pygame import QUIT, K_w, K_s, K_a, K_d, K_k

from cliente import Player
import pygame

# Dimensiones de la ventana del juego
WIDTH = 800
HEIGHT = 600

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)
# Velocidad de movimiento del cuadrado
SQUARE_SPEED = 5
PROJECTILE_SPEED = 6
UPDATE_FREQUENCY_BUTOONS = 250
UPDATE_FREQUENCY_PLAYER = 1000


def movement_other_player(server, hall_id, id_player, player2):
    other_player_rect, other_player_proyecil = server.get_move_and_projectiles(hall_id, id_player)
    if other_player_rect:
        player2_x = other_player_rect["x"]
        player2_y = other_player_rect["y"]
        if player2_x == 0 and player2_y == -5:
            player2.move_up()
        if player2_x == 0 and player2_y == 5:
            player2.move_down()
        if player2_x == -5 and player2_y == 0:
            player2.move_right()
        if player2_x == 5 and player2_y == 0:
            player2.move_left()

    if other_player_proyecil == 1:
        player2.shoot(False)


def player_collision(player1, player2, server, hall_id, id_player):
    collision_indices_player1 = player2.check_collision(player1.rect)
    for index in collision_indices_player1:
        server.receive_colision(hall_id, id_player)
        try:
            del player2.projectiles[index]
            player1.change_color(RED)  # Cambiar color de player1 a rojo
            pygame.time.set_timer(pygame.USEREVENT, 500)
        except:
            print("error de colision")


def write_text(screen, font, life_player_1, life_player_2):
    life_text_prefix_1 = font.render("Vida: ", True, WHITE)
    life_text_prefix_2 = font.render("Vida: ", True, WHITE)
    life_text_player1 = font.render(str(life_player_1), True, GREEN)
    life_text_player2 = font.render(str(life_player_2), True, RED)

    screen.blit(life_text_prefix_1, (50, 10))
    screen.blit(life_text_player1, (120, 10))
    screen.blit(life_text_prefix_2, (630, 10))
    screen.blit(life_text_player2, (700, 10))


def main():
    # Conexión al servidor

    uri = "PYRO:obj_41239fe0b7d4491cbe0695f82a52df11@18.231.102.150:9090"
    server = Pyro5.api.Proxy(uri)
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Juego de Cuadrados")
    clock = pygame.time.Clock()
    last_shot_time = 0
    pygame.mixer.init()  # Inicializar el módulo mixer
    shoot_sound = pygame.mixer.Sound("Music/SpaceLaserShot PE1095407.wav")
    pygame.mixer.music.load("Music/neon-gaming-128925.mp3")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5)
    # x e y
    player1 = Player.Player(50, 300, 100, 0, BLUE, WHITE)
    player2 = Player.Player(725, 300, 800, 700, RED, WHITE)
    hall_id, id_player = server.join_game()
    font = pygame.font.Font(None, 36)
    show_text = True
    blink_timer = 0
    blink_interval = 500

    running = True
    life_player_2 = 100
    life_player_1 = 100
    last_update_time = pygame.time.get_ticks()
    start_ok = False
    while running:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - last_update_time
        last_update_time = current_time

        for event in pygame.event.get():
            if event.type == QUIT:
                server.remove_players(hall_id)
                start_ok = False
            elif event.type == pygame.USEREVENT:
                player1.reset_color()
                player2.reset_color()

        screen.fill(BLACK)
        blink_timer += elapsed_time
        if blink_timer >= blink_interval:
            show_text = not show_text
            blink_timer = 0

        write_text(screen, font, life_player_1, life_player_2)

        if life_player_1 <= 0 or life_player_2 <= 0:
            start_ok = False
            finish = font.render("JUEGO TERMINADO", True, WHITE)
            server.remove_players(hall_id)
            screen.blit(finish, (300, 300))
        else:
            if start_ok is False:
                start = server.start_game(hall_id)
                if start:
                    start_ok = True
            #print(start)
            #life_player_1 = server.return_life(hall_id, id_player)

        if start_ok:
            keys = pygame.key.get_pressed()
            if keys[K_w]:
                player1.move_up()
                server.receive_move(hall_id, id_player, {"x": 0, "y": -5})
            elif keys[K_s]:
                player1.move_down()
                server.receive_move(hall_id, id_player, {"x": 0, "y": 5})
            elif keys[K_a]:
                player1.move_left()
                server.receive_move(hall_id, id_player, {"x": -5, "y": 0})
            elif keys[K_d]:
                player1.move_right()
                server.receive_move(hall_id, id_player, {"x": 5, "y": 0})
            elif keys[K_k]:
                current_time = pygame.time.get_ticks()
                if current_time - last_shot_time >= 500:
                    player1.shoot(True)
                    server.receive_proyectil(hall_id, id_player)
                    shoot_sound.play()
                    last_shot_time = current_time

            player1.update_projectiles(True)
            player2.update_projectiles(False)

            collision_indices_player2 = player1.check_collision(player2.rect)
            for index in collision_indices_player2:
                try:
                    del player1.projectiles[index]
                    player2.change_color(RED)  # Cambiar color de player2 a rojo
                    pygame.time.set_timer(pygame.USEREVENT, 500)
                except:
                    print("error de colision")

            movement_other_player(server, hall_id, id_player, player2)
            #player_collision(player1, player2, server, hall_id, id_player)
            #life_player_2 = server.return_life_player2(hall_id, id_player)

        elif not start_ok and (life_player_1 > 0 and life_player_2 > 0):
            if show_text:
                finish = font.render("ESPERANDO SEGUNDO JUGADOR", True, WHITE)
                screen.blit(finish, (200, 300))

        player1.draw(screen)
        player2.draw(screen)
        fps = clock.get_fps()
        fps_text = font.render(f"FPS: {int(fps)}", True, WHITE)
        screen.blit(fps_text, (700, 550))
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
