import random
import pygame

from base import Sprite
from entities import Bullet
from settings import *


class Enemy(Sprite):
    TYPES = ("basic", "fast", "tough")

    def __init__(self, 
        x: float, 
        y: float, 
        width: int,
        height: int,
        color: tuple,
        hp: int,
        score: int,
        image_path: str,
        formation=None
    ):

        super().__init__(x, y, width, height, color)
        self._hp = hp
        self._score = score

        self._anim_timer = 0
        self._anim_state = False

        self.base_x = x
        self.base_y = y
        self.formation = formation
        
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (width, height))
        self.image = self.original_image
        
        self.flash_timer = 0
        
        if self.formation:
            x = self.base_x + self.formation._offset_x
            y = self.base_y + self.formation._offset_y


    @property
    def score(self) -> int:
        return self._score

    @property
    def hp(self) -> int:
        return self._hp
    
    @property
    def rect(self):
        if self.formation:
            x = self.base_x + self.formation._offset_x
            y = self.base_y + self.formation._offset_y
        else:
            x = self.base_x
            y = self.base_y
        return pygame.Rect(int(x), int(y), self.width, self.height)

    def hit(self):
        self._hp -= 1
        self.flash_timer = 100
        white_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        white_overlay.fill((255, 255, 255, 180))
        self.flash_image = self.original_image.copy()
        self.flash_image.blit(white_overlay, (0, 0))
        self.image = self.flash_image
        
        if self._hp <= 0:
            self.kill()

    def shoot(self):
        bullet_x = self.rect.x + self.width // 2 - 2
        bullet_y = self.rect.y + self.height
        return Bullet(bullet_x, bullet_y, ENEMY_BULLET_SPEED, RED, "enemy")

    def update(self, dt: float):
        self._anim_timer += dt * 1000
        
        if self.flash_timer > 0:
            self.flash_timer -= dt * 1000
            if self.flash_timer <= 0:
                self.image = self.original_image

        if self._anim_timer >= ENEMY_ANIM_INTERVAL:
            self._anim_timer = 0
            self._anim_state = not self._anim_state

    def draw(self, surface: pygame.Surface):
        if not self.alive:
            return
        surface.blit(self.image, self.rect)


class BasicEnemy(Enemy):
    def __init__(self, x: float, y: float):
        super().__init__(
            x, y,
            ENEMY_WIDTH, ENEMY_HEIGHT,
            ENEMY_COLORS["basic"],
            hp=1,
            score=10,
            image_path="../assets/BasicEnemy.png"
        )


class FastEnemy(Enemy):
    def __init__(self, x: float, y: float):
        super().__init__(
            x, y,
            ENEMY_WIDTH, ENEMY_HEIGHT,
            ENEMY_COLORS["fast"],
            hp=1,
            score=20,
            image_path="../assets/FastEnemy.png"
        )

    def shoot(self):
        bullet = super().shoot()
        bullet._vy *= 1.5
        return bullet


class ToughEnemy(Enemy):
    def __init__(self, x: float, y: float):
        super().__init__(
            x, y,
            ENEMY_WIDTH, ENEMY_HEIGHT,
            ENEMY_COLORS["tough"],
            hp=3,
            score=30,
            image_path="../assets/ToughEnemy.png"
        )
    
