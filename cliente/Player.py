import pygame

SQUARE_SPEED = 25
PROJECTILE_SPEED = 5
WIDTH = 800
HEIGHT = 600
WHITE = (255, 255, 255)


class Player:
    def __init__(self, x, y, limit_left, limit_right, projectile_color, color):
        self.rect = pygame.Rect(x, y, 25, 25)
        self.limit_left = limit_left
        self.limit_right = limit_right
        self.projectile_color = projectile_color
        self.projectile_timer = 0
        self.projectiles = []
        self.color_original = color
        self.life = 100

    def move_up(self):
        if self.rect.y - SQUARE_SPEED >= 0:
            self.rect.y -= SQUARE_SPEED

    def move_down(self):
        if self.rect.y + SQUARE_SPEED + 25 <= HEIGHT:
            self.rect.y += SQUARE_SPEED

    def move_left(self):
        if self.rect.x - SQUARE_SPEED >= self.limit_right:
            self.rect.x -= SQUARE_SPEED

    def move_right(self):
        if self.rect.x + SQUARE_SPEED + 25 <= self.limit_left:
            self.rect.x += SQUARE_SPEED

    def shoot(self, negative):
        if negative:
            projectile_x = self.rect.x + 25
            projectile_y = self.rect.y + 10
            self.projectiles.append(pygame.Rect(projectile_x, projectile_y, 5, 5))
        else:
            projectile_x = self.rect.x - 6
            projectile_y = self.rect.y + 10
            self.projectiles.append(pygame.Rect(projectile_x, projectile_y, 5, 5))

    def update_projectiles(self, negative):
        if negative:
            self.projectiles = [projectile.move(PROJECTILE_SPEED, 0) for projectile in self.projectiles if
                                projectile.x < WIDTH]
        else:
            self.projectiles = [projectile.move(-PROJECTILE_SPEED, 0) for projectile in self.projectiles if
                                projectile.x > 0]

    def draw(self, screen):
        pygame.draw.rect(screen, self.color_original, self.rect)
        for projectile in self.projectiles:
            pygame.draw.rect(screen, self.projectile_color, projectile)

    def check_collision(self, other_player_rect):
        collision_indices = []
        for index, projectile in enumerate(self.projectiles):
            if projectile.colliderect(other_player_rect):
                collision_indices.append(index)
        return collision_indices

    def change_color(self, new_color):
        self.color_original = new_color
        pygame.time.set_timer(pygame.USEREVENT, 1000)

    def reset_color(self):
        self.color_original = WHITE
