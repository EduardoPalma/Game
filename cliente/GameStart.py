import Pyro5.api
import pygame
from pygame import QUIT, KEYDOWN, K_w, K_s, K_a, K_d, K_k
import threading
from cliente.Player import Player

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)


def star_music():
    pygame.mixer.init()
    pygame.mixer.music.load("Music/neon-gaming-128925.mp3")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.1)
    return pygame.mixer.Sound("Music/SpaceLaserShot PE1095407.wav")


def show_fps(clock, font, screen):
    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(fps)}", True, WHITE)
    screen.blit(fps_text, (700, 550))
    clock.tick(60)


def init_pygame(name):
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    pygame.display.set_caption(name)


class GameStart:
    def __init__(self, width, height, hall_id, id_player, server, start):
        self.name = "Juego"
        self.width = width
        self.height = height
        self.font = None
        self.player1 = Player(50, 300, 100, 0, BLUE, WHITE)
        self.player2 = Player(725, 300, 800, 700, RED, WHITE)
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.hall_id = hall_id
        self.id_player = id_player
        self.server = server
        self.start = start
        self.begin = False
        self.finish = 0

    def main_loop(self):
        init_pygame(self.name)
        self.font = pygame.font.Font(None, 36)
        shoot_sound = star_music()
        last_shoot_time = 0
        self.start_thread()
        while self.start:
            self.screen.fill(BLACK)
            self.finish_game()
            self.home_player_moves(shoot_sound, last_shoot_time)
            self.check_collision_local()
            self.player1.update_projectiles(True)
            self.player2.update_projectiles(False)
            self.player1.draw(self.screen)
            self.player2.draw(self.screen)
            self.write_text_life()
            show_fps(self.clock, self.font, self.screen)
            self.wait_game()
            pygame.display.flip()

    def home_player_moves(self, shoot_sound, last_shot_time):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.server.remove_players(self.hall_id)
                self.start = False
            elif event.type == pygame.USEREVENT:
                self.player1.reset_color()
                self.player2.reset_color()
            elif event.type == KEYDOWN:
                if not self.begin:
                    continue
                self.mov_player(event, last_shot_time, shoot_sound)

    def mov_player(self, event, last_shot_time, shoot_sound):
        if event.key == K_w:
            self.player1.move_up()
            self.server.receive_move(self.hall_id, self.id_player, {"x": 0, "y": -5})
        elif event.key == K_s:
            self.player1.move_down()
            self.server.receive_move(self.hall_id, self.id_player, {"x": 0, "y": 5})
        elif event.key == K_a:
            self.player1.move_left()
            self.server.receive_move(self.hall_id, self.id_player, {"x": -5, "y": 0})
        elif event.key == K_d:
            self.player1.move_right()
            self.server.receive_move(self.hall_id, self.id_player, {"x": 5, "y": 0})
        elif event.key == K_k:
            current_time = pygame.time.get_ticks()
            if current_time - last_shot_time >= 500:
                self.player1.shoot(True)
                self.server.receive_projectile(self.hall_id, self.id_player)
                shoot_sound.play()
                return current_time
        return 0

    def write_text_life(self):
        life_text_prefix_1 = self.font.render("Vida: ", True, WHITE)
        life_text_prefix_2 = self.font.render("Vida: ", True, WHITE)
        life_text_player1 = self.font.render(str(self.player1.life), True, GREEN)
        life_text_player2 = self.font.render(str(self.player2.life), True, RED)

        self.screen.blit(life_text_prefix_1, (50, 10))
        self.screen.blit(life_text_player1, (120, 10))
        self.screen.blit(life_text_prefix_2, (630, 10))
        self.screen.blit(life_text_player2, (700, 10))

    def mov_other_player(self, server):
        other_player_rect, other_player_projectile = server.get_move_and_projectiles(self.hall_id, self.id_player)
        if other_player_rect:
            player2_x = other_player_rect["x"]
            player2_y = other_player_rect["y"]
            if player2_x == 0 and player2_y == -5:
                self.player2.move_up()
            if player2_x == 0 and player2_y == 5:
                self.player2.move_down()
            if player2_x == -5 and player2_y == 0:
                self.player2.move_right()
            if player2_x == 5 and player2_y == 0:
                self.player2.move_left()

        if other_player_projectile == 1:
            self.player2.shoot(False)

    def check_collision(self, server):
        collision_indices_player1 = self.player2.check_collision(self.player1.rect)
        for index in collision_indices_player1:
            server.receive_colision(self.hall_id, self.id_player)
            try:
                del self.player2.projectiles[index]
                self.player1.change_color(RED)
                pygame.time.set_timer(pygame.USEREVENT, 500)
            except:
                print("error de colision")
                raise

    def check_collision_local(self):
        collision_indices_player2 = self.player1.check_collision(self.player2.rect)
        for index in collision_indices_player2:
            try:
                del self.player1.projectiles[index]
                self.player2.change_color(RED)
                pygame.time.set_timer(pygame.USEREVENT, 500)
            except:
                print("error de colision")
                raise

    def finish_game(self):
        if (self.player2.life <= 0 or self.player1.life <= 0) and (self.begin is True or self.start is True):
            self.begin = False
            finish = self.font.render("JUEGO TERMINADO", True, WHITE)
            self.server.remove_players(self.hall_id)
            self.screen.blit(finish, (300, 300))

    def handle_player_moves(self):
        server = Pyro5.api.Proxy("PYRO:server@18.228.154.72:9090")
        while self.start:
            if self.begin:
                self.mov_other_player(server)
                self.check_collision(server)
            pygame.time.delay(10)

    def handle_life(self):
        server = Pyro5.api.Proxy("PYRO:server@18.228.154.72:9090")
        while self.start:
            if server.start_game(self.hall_id):
                self.begin = True
            if self.begin:
                self.player1.life = server.return_life(self.hall_id, self.id_player)
                self.player2.life = server.return_life_player2(self.hall_id, self.id_player)
            pygame.time.delay(100)

    def wait_game(self):
        if not self.begin and self.player1.life > 0 and self.player2.life > 0:
            finish = self.font.render("ESPERANDO SEGUNDO JUGADOR", True, WHITE)
            self.screen.blit(finish, (200, 300))

    def start_thread(self):
        server_thread_life = threading.Thread(target=self.handle_life)
        server_thread_moves = threading.Thread(target=self.handle_player_moves)

        server_thread_life.start()
        server_thread_moves.start()
