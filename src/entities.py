
import pygame

from base import Sprite
from settings import *


class Bullet(Sprite):

    def __init__(
        self,
        x: float, y: float,
        speed: float,
        color: tuple,
        owner: str
    ): 
        super().__init__(x, y, 4, 12, color)
        self._vy = speed
        self._vx = 0
        self._owner = owner

    
    @property
    def owner(self) -> str:
        return self._owner
    
    def update(self, dt: float):
        self.x += self._vx * dt
        self.y += self._vy * dt
        if self.y < -20 or self.y > SCREEN_HEIGHT + 20:
            self.kill()
        if self.x < -20 or self.x > SCREEN_WIDTH + 20:
            self.kill()


class Player(Sprite):

    def __init__(self, x: float, y: float):
        x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
        y = PLAYER_START_Y

        super().__init__(x, y, PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_COLOR)
        self._speed = PLAYER_SPEED
        self._lives = PLAYER_LIVES
        self._last_shot = 0
        self._left_pressed = False
        self._right_pressed = False
        self.image = pygame.image.load("../assets/PlayerCat.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

    @property
    def vx(self) -> float:
        return self._vx
    
    @vx.setter
    def vx(self, value: float):
        self._vx = value

    @property
    def lives(self) -> int:
        return self._lives
    
    def press_left(self):
        self._left_pressed = True
        self._update_velocity()
    
    def press_right(self):
        self._right_pressed = True
        self._update_velocity()
    
    def release_left(self):
        self._left_pressed = False
        self._update_velocity()
    
    def release_right(self):
        self._right_pressed = False
        self._update_velocity()
    
    def _update_velocity(self):
        if self._left_pressed and not self._right_pressed:
            self._vx = -self._speed
        elif self._right_pressed and not self._left_pressed:
            self._vx = self._speed
        else:
            self._vx = 0
    
    def can_shoot(self) -> bool:
        now = pygame.time.get_ticks()
        return now - self._last_shot >= PLAYER_SHOOT_DELAY
    
    def shoot(self):
        self._last_shot = pygame.time.get_ticks()
        bullet_x = self.x + self.width // 2 - 2
        bullet_y = self.y - 10
        return Bullet(bullet_x, bullet_y, -PLAYER_BULLET_SPEED, WHITE, "player")
    
    def hit(self):
        self._lives -= 1
        if self._lives <= 0:
            self.kill()

    def update(self, dt: float):
        self.x += self._vx * dt
        
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width

    def draw(self, surface: pygame.Surface):
        if self.alive:
            surface.blit(self.image, self.rect)


class ShieldBlock(Sprite):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, SHIELD_BLOCK_SIZE, SHIELD_BLOCK_SIZE, SHIELD_COLOR)

    def update(self, dt: float):
        ...