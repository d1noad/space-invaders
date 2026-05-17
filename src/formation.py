
import random
import pygame

from enemies import BasicEnemy, FastEnemy, ToughEnemy
from settings import *


class Formation:
    def __init__(self, level: int = 1):
        self._enemies = []

        self._direction = 1
        self._speed = ENEMY_MOVE_SPEED * LEVELS[level]["speed_mult"]
        self._offset_x = 0
        self._offset_y = 0

        self._drop_speed = ENEMY_DROP_STEP
        self._shoot_mult = LEVELS[level]["shoot_mult"]
        self._move_down_flag = False
        self._create_formation(level)

    @property
    def enemies(self):
        return self._enemies
    
    def _create_formation(self, level: int):
        rows = LEVELS[level]["rows"]
        cols = LEVELS[level]["cols"]
        
        enemy_types = ["basic", "fast", "tough"]
        weights = [0.6, 0.3, 0.1]
        
        for row in range(rows):
            for col in range(cols):
                if random.random() < 0.85:
                    x = ENEMY_START_X + col * ENEMY_H_SPACING
                    y = ENEMY_START_Y + row * ENEMY_V_SPACING
                    
                    enemy_type = random.choices(enemy_types, weights=weights)[0]
                    
                    if enemy_type == "basic":
                        enemy = BasicEnemy(x, y)
                    elif enemy_type == "fast":
                        enemy = FastEnemy(x, y)
                    else:
                        enemy = ToughEnemy(x, y)
                    
                    enemy.formation = self
                    self._enemies.append(enemy)

    def update(self, dt: float):
        alive_enemies = [enemy for enemy in self._enemies if enemy.alive]

        if not alive_enemies:
            return
        
        self._offset_x += self._direction * self._speed * dt

        move_down = False
        for enemy in self._enemies:
            if not enemy.alive:
                continue
            x = enemy.base_x + self._offset_x
            if x <= 0 or x + enemy.width >= SCREEN_WIDTH:
                move_down = True
                break
        
        if move_down and not self._move_down_flag:
            self._move_down_flag = True
            self._direction *= -1
            for enemy in alive_enemies:
                enemy.base_y += ENEMY_DROP_STEP
        elif not move_down:
            self._move_down_flag = False
        
        for enemy in alive_enemies:
            enemy.update(dt)
        
    def draw(self, surface):
        for enemy in self._enemies:
            enemy.draw(surface)

    def try_shoot(self):
        alive_enemies = [enemy for enemy in self._enemies if enemy.alive]

        if not alive_enemies:
            return None
        
        for enemy in alive_enemies:
            chance = ENEMY_SHOOT_CHANCE * self._shoot_mult
            if random.random() < chance:
                return enemy.shoot()
        
        return None
    
    def all_dead(self) -> bool:
        return all(not enemy.alive for enemy in self._enemies)
    
    def reached_bottom(self) -> bool:
        for enemy in self._enemies:
            if enemy.alive and enemy.rect.y + enemy.height >= PLAYER_START_Y:
                return True
        return False