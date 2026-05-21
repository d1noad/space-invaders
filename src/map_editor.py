import pygame
import json
import os
from settings import *


class MapEditor:
    def __init__(self, screen):
        self._screen = screen
        self._clock = pygame.time.Clock()
        self._running = True
        
        self._grid_width = 11
        self._grid_height = 7
        self._cell_size = 40
        self._grid = [[' ' for _ in range(self._grid_width)] for _ in range(self._grid_height)]
        
        self._start_x = (SCREEN_WIDTH - self._grid_width * self._cell_size) // 2
        self._start_y = 120
        
        self._selected_enemy = "E"
        
        self._enemy_images = {}
        self._load_enemy_images()
        
        self._font_small = pygame.font.SysFont(None, FONT_SIZE_SMALL)
        self._font_medium = pygame.font.SysFont(None, FONT_SIZE_MEDIUM)
        self._font_large = pygame.font.SysFont(None, FONT_SIZE_LARGE)
        
        self._save_button_rect = None
        self._clear_button_rect = None
        self._back_button_rect = None
        self._name_rect = None
        
        self._map_name = ""
        self._input_active = False
        self._input_text = ""
        
        self._message = ""
        self._message_timer = 0

    def _load_enemy_images(self):
        enemies = {
            "E": "../assets/BasicEnemy.png",
            "F": "../assets/FastEnemy.png",
            "T": "../assets/ToughEnemy.png",
            "S": "../assets/ShotgunEnemy.png"
        }
        
        for symbol, path in enemies.items():
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (self._cell_size - 4, self._cell_size - 4))
                self._enemy_images[symbol] = img
            except:
                self._enemy_images[symbol] = None

    def run(self):
        while self._running:
            self._handle_events()
            self._draw()
            self._clock.tick(60)
            pygame.display.flip()
        return True
    
    def _handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self._save_button_rect and self._save_button_rect.collidepoint(mouse_pos):
                        self._save_map()
                    elif self._clear_button_rect and self._clear_button_rect.collidepoint(mouse_pos):
                        self._clear_grid()
                    elif self._back_button_rect and self._back_button_rect.collidepoint(mouse_pos):
                        self._running = False
                    elif self._name_rect and self._name_rect.collidepoint(mouse_pos):
                        self._input_active = True
                        self._input_text = self._map_name
                    
                    for i in range(4):
                        x = 20
                        y = 200 + i * 70
                        rect = pygame.Rect(x, y, 60, 60)
                        if rect.collidepoint(mouse_pos):
                            if i == 0:
                                self._selected_enemy = "E"
                            elif i == 1:
                                self._selected_enemy = "F"
                            elif i == 2:
                                self._selected_enemy = "T"
                            elif i == 3:
                                self._selected_enemy = "S"
                    
                    grid_x = (mouse_pos[0] - self._start_x) // self._cell_size
                    grid_y = (mouse_pos[1] - self._start_y) // self._cell_size
                    if 0 <= grid_x < self._grid_width and 0 <= grid_y < self._grid_height:
                        self._grid[grid_y][grid_x] = self._selected_enemy
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                grid_x = (mouse_pos[0] - self._start_x) // self._cell_size
                grid_y = (mouse_pos[1] - self._start_y) // self._cell_size
                if 0 <= grid_x < self._grid_width and 0 <= grid_y < self._grid_height:
                    self._grid[grid_y][grid_x] = ' '
            
            elif event.type == pygame.KEYDOWN:
                if self._input_active:
                    if event.key == pygame.K_RETURN:
                        if self._input_text.strip():
                            self._map_name = self._input_text.strip().upper().replace(' ', '_')
                            self._input_active = False
                            self._input_text = ""
                            self._show_message(f"NAME: {self._map_name}")
                    elif event.key == pygame.K_ESCAPE:
                        self._input_active = False
                        self._input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self._input_text = self._input_text[:-1]
                    else:
                        allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
                        if event.unicode.upper() in allowed and len(self._input_text) < 20:
                            self._input_text += event.unicode.upper()
    
    def _clear_grid(self):
        self._grid = [[' ' for _ in range(self._grid_width)] for _ in range(self._grid_height)]
        self._show_message("CLEARED")
    
    def _save_map(self):
        if not self._map_name:
            self._show_message("ENTER NAME FIRST!")
            return
        
        map_data = []
        for row in self._grid:
            map_data.append(''.join(row))
        
        existing_maps = []
        file_path = "custom_maps.json"
        

        print(f"Сохранение в: {os.path.abspath(file_path)}")
        
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                existing_maps = json.load(f)
                print(f"Загружено {len(existing_maps)} карт")
        except FileNotFoundError:
            print("Файл не найден, создаём новый")
            existing_maps = []
        except Exception as e:
            print(f"Ошибка: {e}")
            existing_maps = []
        
        new_map = {
            "name": self._map_name,
            "data": map_data
        }
        
        found = False
        for i, existing in enumerate(existing_maps):
            if existing["name"] == self._map_name:
                existing_maps[i] = new_map
                found = True
                break
        
        if not found:
            existing_maps.append(new_map)
        
        try:
            with open(file_path, "w", encoding='utf-8') as f:
                json.dump(existing_maps, f, ensure_ascii=False, indent=2)
            print(f"СОХРАНЕНО! Теперь в файле {len(existing_maps)} карт")
            self._show_message(f"SAVED: {self._map_name}")
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            self._show_message("SAVE ERROR!")
            return
        
        # Обновляем глобальные списки
        if self._map_name not in FORMATIONS:
            FORMATIONS[self._map_name] = map_data
        if self._map_name not in FORMATION_NAMES:
            FORMATION_NAMES.append(self._map_name)
        if self._map_name not in FORMATION_SCREENSHOTS:
            FORMATION_SCREENSHOTS[self._map_name] = None
    
    def _show_message(self, text):
        self._message = text
        self._message_timer = 60
    
    def _draw(self):
        self._screen.fill(BLACK)
        
        title = self._font_large.render("MAP EDITOR", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self._screen.blit(title, title_rect)
        
        enemy_types = [
            {"symbol": "E", "color": (180, 80, 220), "name": "BASIC"},
            {"symbol": "F", "color": (80, 180, 220), "name": "FAST"},
            {"symbol": "T", "color": (220, 100, 60), "name": "TOUGH"},
            {"symbol": "S", "color": (255, 100, 0), "name": "SHOTGUN"},
        ]
        
        for i, enemy in enumerate(enemy_types):
            x = 20
            y = 180 + i * 80
            rect = pygame.Rect(x, y, 60, 60)
            
            if enemy["symbol"] == self._selected_enemy:
                pygame.draw.rect(self._screen, enemy["color"], rect)
                pygame.draw.rect(self._screen, WHITE, rect, 3)
            else:
                pygame.draw.rect(self._screen, enemy["color"], rect)
                pygame.draw.rect(self._screen, (100, 100, 100), rect, 2)
            
            if self._enemy_images.get(enemy["symbol"]):
                img_rect = self._enemy_images[enemy["symbol"]].get_rect(center=rect.center)
                self._screen.blit(self._enemy_images[enemy["symbol"]], img_rect)
            
            name_text = self._font_small.render(enemy["name"], True, WHITE)
            name_rect = name_text.get_rect(center=(x + 30, y + 75))
            self._screen.blit(name_text, name_rect)
        
        for row in range(self._grid_height):
            for col in range(self._grid_width):
                x = self._start_x + col * self._cell_size
                y = self._start_y + row * self._cell_size
                rect = pygame.Rect(x, y, self._cell_size - 1, self._cell_size - 1)
                
                symbol = self._grid[row][col]
                
                if symbol == ' ':
                    pygame.draw.rect(self._screen, (40, 40, 40), rect)
                    pygame.draw.rect(self._screen, (60, 60, 60), rect, 1)
                else:
                    if symbol == 'E':
                        color = (180, 80, 220)
                    elif symbol == 'F':
                        color = (80, 180, 220)
                    elif symbol == 'T':
                        color = (220, 100, 60)
                    else:
                        color = (255, 100, 0)
                    
                    pygame.draw.rect(self._screen, color, rect)
                    
                    if self._enemy_images.get(symbol):
                        img = self._enemy_images[symbol]
                        img_rect = img.get_rect(center=rect.center)
                        self._screen.blit(img, img_rect)
        
        button_x = SCREEN_WIDTH - 180
        self._save_button_rect = pygame.Rect(button_x, 200, 150, 50)
        pygame.draw.rect(self._screen, GREEN, self._save_button_rect)
        pygame.draw.rect(self._screen, WHITE, self._save_button_rect, 2)
        save_text = self._font_medium.render("SAVE", True, BLACK)
        save_rect = save_text.get_rect(center=self._save_button_rect.center)
        self._screen.blit(save_text, save_rect)
        
        self._clear_button_rect = pygame.Rect(button_x, 270, 150, 50)
        pygame.draw.rect(self._screen, RED, self._clear_button_rect)
        pygame.draw.rect(self._screen, WHITE, self._clear_button_rect, 2)
        clear_text = self._font_medium.render("CLEAR", True, WHITE)
        clear_rect = clear_text.get_rect(center=self._clear_button_rect.center)
        self._screen.blit(clear_text, clear_rect)
        
        self._back_button_rect = pygame.Rect(button_x, 540, 150, 45)
        pygame.draw.rect(self._screen, DARK_GRAY, self._back_button_rect)
        pygame.draw.rect(self._screen, WHITE, self._back_button_rect, 2)
        back_text = self._font_small.render("BACK", True, WHITE)
        back_rect = back_text.get_rect(center=self._back_button_rect.center)
        self._screen.blit(back_text, back_rect)
        
        self._name_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 540, 300, 45)
        pygame.draw.rect(self._screen, DARK_GRAY, self._name_rect)
        pygame.draw.rect(self._screen, WHITE, self._name_rect, 2)
        
        if self._input_active:
            display_name = self._input_text + "_"
            pygame.draw.rect(self._screen, YELLOW, self._name_rect, 3)
        else:
            display_name = self._map_name if self._map_name else "ENTER NAME"
        
        name_text = self._font_small.render(f"NAME: {display_name}", True, WHITE)
        name_rect_text = name_text.get_rect(center=self._name_rect.center)
        self._screen.blit(name_text, name_rect_text)
        
        info_text = self._font_small.render("LMB - PLACE, RMB - ERASE", True, LIGHT_GRAY)
        info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, 90))
        self._screen.blit(info_text, info_rect)
        
        name_hint = self._font_small.render("CLICK NAME TO EDIT (A-Z, 0-9, _)", True, LIGHT_GRAY)
        name_hint_rect = name_hint.get_rect(center=(SCREEN_WIDTH // 2, 520))
        self._screen.blit(name_hint, name_hint_rect)
        
        if self._message_timer > 0:
            msg_text = self._font_medium.render(self._message, True, GREEN)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, 490))
            self._screen.blit(msg_text, msg_rect)
            self._message_timer -= 1