

import random
import pygame

from enemies import BasicEnemy, FastEnemy, ToughEnemy, ShotgunEnemy
from settings import *


class Formation:
    def __init__(self, level: int = 1, formation_type: str = "RANDOM"):
        self._enemies = []
        self._formation_type = formation_type

        self._direction = 1
        self._speed = ENEMY_MOVE_SPEED * LEVELS[level]["speed_mult"]
        self._offset_x = 0
        self._offset_y = 0

        self._drop_speed = ENEMY_DROP_STEP
        self._shoot_mult = LEVELS[level]["shoot_mult"]
        self._move_down_flag = False
        self._create_formation(level, formation_type)

    @property
    def enemies(self):
        return self._enemies
    
    def _create_formation(self, level: int, formation_type: str):
        if formation_type == "RANDOM":
            self._create_random_formation(level)
        else:
            self._create_custom_formation(level, formation_type)
    
    def _create_random_formation(self, level: int):
        rows = LEVELS[level]["rows"]
        cols = LEVELS[level]["cols"]
        
        enemy_types = ["basic", "fast", "tough", "shotgun"]
        weights = [0.5, 0.2, 0.2, 0.1]
        
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
                    elif enemy_type == "shotgun":
                        enemy = ShotgunEnemy(x, y)
                    else:
                        enemy = ToughEnemy(x, y)
                    
                    enemy.formation = self
                    self._enemies.append(enemy)
    
    def _create_custom_formation(self, level: int, formation_type: str):
        formation_map = FORMATIONS.get(formation_type)
        
        if formation_map is None:
            formation_map = FORMATIONS["КЛИН"]
        
        # Убираем полностью пустые строки в начале и конце
        while formation_map and all(c == ' ' for c in formation_map[0]):
            formation_map = formation_map[1:]
        while formation_map and all(c == ' ' for c in formation_map[-1]):
            formation_map = formation_map[:-1]
        
        if not formation_map:
            return
        
        # Находим реальную ширину карты (обрезаем пустые колонки слева и справа)
        min_col = len(formation_map[0])
        max_col = 0
        
        for row in formation_map:
            for col, ch in enumerate(row):
                if ch != ' ':
                    min_col = min(min_col, col)
                    max_col = max(max_col, col)
        
        # Обрезаем каждую строку
        trimmed_map = []
        for row in formation_map:
            trimmed_row = row[min_col:max_col+1]
            trimmed_map.append(trimmed_row)
        
        formation_map = trimmed_map
        
        enemy_types = ["basic", "fast", "tough", "shotgun"]
        weights = [0.4, 0.3, 0.2, 0.1]
        
        formation_width = len(formation_map[0])
        start_x = (SCREEN_WIDTH - (formation_width * ENEMY_H_SPACING)) // 2
        
        # Начальная позиция по Y - фиксированная
        start_y = ENEMY_START_Y
        
        for row_idx, line in enumerate(formation_map):
            for col, char in enumerate(line):
                if char != ' ':
                    x = start_x + col * ENEMY_H_SPACING
                    y = start_y + row_idx * ENEMY_V_SPACING
                    
                    # Если враг спавнится слишком низко - поднимаем всю формацию
                    if y + ENEMY_HEIGHT >= PLAYER_START_Y - 150:
                        y = ENEMY_START_Y + row_idx * ENEMY_V_SPACING - 50
                    
                    if char == 'E':
                        enemy_type = random.choices(enemy_types, weights=weights)[0]
                        if enemy_type == "basic":
                            enemy = BasicEnemy(x, y)
                        elif enemy_type == "fast":
                            enemy = FastEnemy(x, y)
                        elif enemy_type == "shotgun":
                            enemy = ShotgunEnemy(x, y)
                        else:
                            enemy = ToughEnemy(x, y)
                    elif char == 'F':
                        enemy = FastEnemy(x, y)
                    elif char == 'T':
                        enemy = ToughEnemy(x, y)
                    elif char == 'S':
                        enemy = ShotgunEnemy(x, y)
                    else:
                        continue
                    
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
        
        bullets = []
        for enemy in alive_enemies:
            if isinstance(enemy, ShotgunEnemy):
                chance = SHOTGUN_SHOOT_CHANCE
            else:
                chance = ENEMY_SHOOT_CHANCE * self._shoot_mult
            
            if random.random() < chance:
                result = enemy.shoot()
                if isinstance(result, list):
                    bullets.extend(result)
                else:
                    bullets.append(result)
        
        return bullets if bullets else None
    
    def all_dead(self) -> bool:
        return all(not enemy.alive for enemy in self._enemies)
    
    def reached_bottom(self) -> bool:
        for enemy in self._enemies:
            if enemy.alive:
                if enemy.rect.y + enemy.height >= PLAYER_START_Y - 20:
                    return True
        return False