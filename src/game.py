# game.py - полностью

import pygame
import sys
import json
from entities import Player
from formation import Formation
from settings import *


class Game:
    def __init__(self):
        self._screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self._clock = pygame.time.Clock()
        self._running = True
        self._state = "menu"
        self._menu_state = "level"
        self._level = 1
        self._selected_level = 1
        self._selected_formation_index = 0
        self._score = 0
        self._player = None
        self._formation = None
        self._bullets = []
        self._win = False
        self._font_small = pygame.font.SysFont(None, FONT_SIZE_SMALL)
        self._font_medium = pygame.font.SysFont(None, FONT_SIZE_MEDIUM)
        self._font_large = pygame.font.SysFont(None, FONT_SIZE_LARGE)
        
        self._load_formation_screenshots()
        
        self._mouse_x = SCREEN_WIDTH // 2
        
        self._level_buttons = []
        self._left_arrow_rect = None
        self._right_arrow_rect = None
        self._editor_button_rect = None

        self._paused = False
        self._resume_button_rect = None
        self._quit_to_menu_button_rect = None

    def _load_formation_screenshots(self):
    
        # Загружаем пользовательские карты
        try:
            with open("custom_maps.json", "r", encoding='utf-8') as f:
                CUSTOM_MAPS = json.load(f)
            for custom_map in CUSTOM_MAPS:
                name = custom_map["name"]
                if name not in FORMATIONS:
                    FORMATIONS[name] = custom_map["data"]
                if name not in FORMATION_NAMES:
                    FORMATION_NAMES.append(name)
                if name not in FORMATION_SCREENSHOTS:
                    FORMATION_SCREENSHOTS[name] = None
        except:
            pass
        
        # Загружаем скриншоты
        for name in FORMATION_NAMES:
            try:
                path = f"../assets/formations/{name}.png"
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (200, 150))
                FORMATION_SCREENSHOTS[name] = img
            except:
                FORMATION_SCREENSHOTS[name] = None
    def run(self):
        while self._running:
            dt = self._clock.tick(FPS) / 1000
            self._handle_events()
            
            if self._state == "menu":
                self._draw_menu()
            elif self._state == "playing":
                self._update(dt)
                self._draw_game()
            elif self._state == "game_over":
                self._draw_game_over()
            elif self._state == "win":
                self._draw_win()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
    
    
    def _handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self._state == "playing" and not self._paused:
                    self._mouse_x = mouse_pos[0]
            
            elif event.type == pygame.KEYDOWN:
                if self._state == "menu":
                    if event.key == pygame.K_ESCAPE:
                        if self._menu_state == "formation":
                            self._menu_state = "level"
                        else:
                            self._running = False
                    elif event.key == pygame.K_SPACE:
                        if self._menu_state == "level":
                            self._menu_state = "formation"
                        else:
                            formation_name = FORMATION_NAMES[self._selected_formation_index]
                            self._start_game(self._selected_level, formation_name)
                
                elif self._state == "playing":
                    if event.key == pygame.K_ESCAPE:
                        self._paused = not self._paused
                
                elif self._state == "game_over":
                    if event.key == pygame.K_ESCAPE:
                        self._running = False
                    elif event.key == pygame.K_SPACE:
                        self._menu_state = "level"
                        self._state = "menu"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self._state == "menu":
                        if self._menu_state == "level":
                            for i, rect in enumerate(self._level_buttons):
                                if rect.collidepoint(mouse_pos):
                                    self._selected_level = i + 1
                                    break
                            
                            if self._next_button_rect and self._next_button_rect.collidepoint(mouse_pos):
                                self._menu_state = "formation"
                            elif self._quit_button_rect and self._quit_button_rect.collidepoint(mouse_pos):
                                self._running = False
                        
                        elif self._menu_state == "formation":
                            if self._left_arrow_rect and self._left_arrow_rect.collidepoint(mouse_pos):
                                self._selected_formation_index = (self._selected_formation_index - 1) % len(FORMATION_NAMES)
                            elif self._right_arrow_rect and self._right_arrow_rect.collidepoint(mouse_pos):
                                self._selected_formation_index = (self._selected_formation_index + 1) % len(FORMATION_NAMES)
                            elif self._editor_button_rect and self._editor_button_rect.collidepoint(mouse_pos):
                                from map_editor import MapEditor
                                editor = MapEditor(self._screen)
                                editor.run()
                                self._load_formation_screenshots()
                                self._selected_formation_index = 0
                            elif self._start_button_rect and self._start_button_rect.collidepoint(mouse_pos):
                                formation_name = FORMATION_NAMES[self._selected_formation_index]
                                self._start_game(self._selected_level, formation_name)
                            elif self._back_button_rect and self._back_button_rect.collidepoint(mouse_pos):
                                self._menu_state = "level"
                    
                    elif self._state == "playing" and not self._paused:
                        if self._player.can_shoot():
                            bullet = self._player.shoot()
                            self._bullets.append(bullet)
                    
                    elif self._state == "game_over":
                        if self._menu_button_rect and self._menu_button_rect.collidepoint(mouse_pos):
                            self._menu_state = "level"
                            self._state = "menu"
                        elif self._quit_button_rect and self._quit_button_rect.collidepoint(mouse_pos):
                            self._running = False
                    
                    elif self._state == "playing" and self._paused:
                        if self._resume_button_rect and self._resume_button_rect.collidepoint(mouse_pos):
                            self._paused = False
                        elif self._quit_to_menu_button_rect and self._quit_to_menu_button_rect.collidepoint(mouse_pos):
                            self._state = "menu"
                            self._menu_state = "level"
                            self._paused = False

                    elif self._state == "win":
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if self._menu_button_rect and self._menu_button_rect.collidepoint(mouse_pos):
                                self._menu_state = "level"
                                self._state = "menu"
                                self._win = False
                            elif self._quit_button_rect and self._quit_button_rect.collidepoint(mouse_pos):
                                self._running = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                self._running = False
                            elif event.key == pygame.K_SPACE:
                                self._menu_state = "level"
                                self._state = "menu"
                                self._win = False
        
    def _start_game(self, level, formation_name):
        self._level = level
        self._score = 0
        self._player = Player(SCREEN_WIDTH // 2, PLAYER_START_Y)
        self._formation = Formation(self._level, formation_name)
        self._bullets = []
        self._state = "playing"
    
    def _update(self, dt: float):
        if self._paused:
            return
        target_x = self._mouse_x - self._player.width // 2
        target_x = max(0, min(target_x, SCREEN_WIDTH - self._player.width))
        self._player.x = target_x
        
        self._formation.update(dt)

        for bullet in self._bullets:
            bullet.update(dt)
        
        enemy_bullets = self._formation.try_shoot()
        if enemy_bullets:
            self._bullets.extend(enemy_bullets)

        self._check_collisions()
        self._bullets = [bullet for bullet in self._bullets if bullet.alive]

        if self._formation.all_dead():
            self._level += 1
            if self._level > MAX_LEVEL:
                self._state = "win"  # вместо game_over
                self._win = True
            else:
                self._formation = Formation(self._level, self._formation._formation_type)
        
        if not self._player.alive:
            self._state = "game_over"
            self._win = False
        elif self._formation.reached_bottom():
            self._state = "game_over"
            self._win = False
    
    def _check_collisions(self):
        for bullet in self._bullets[:]:
            if bullet.owner == "player":
                for enemy in self._formation.enemies:
                    if bullet.collides_with(enemy):
                        enemy.hit()
                        bullet.kill()
                        if not enemy.alive:
                            self._score += enemy.score
                        break
            elif bullet.owner == "enemy":
                if bullet.collides_with(self._player):
                    self._player.hit()
                    bullet.kill()
    
    def _draw_menu(self):
        self._screen.fill(BLACK)
        
        title = self._font_large.render("SPACE INVADERS", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self._screen.blit(title, title_rect)
        
        if self._menu_state == "level":
            level_text = self._font_medium.render("ВЫБЕРИ УРОВЕНЬ:", True, WHITE)
            level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
            self._screen.blit(level_text, level_rect)
            
            self._level_buttons = []
            for i in range(1, MAX_LEVEL + 1):
                y = 200 + i * 50
                if i == self._selected_level:
                    color = GREEN
                    bg_color = DARK_GRAY
                else:
                    color = WHITE
                    bg_color = (50, 50, 50)
                
                button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, y - 15, 200, 40)
                self._level_buttons.append(button_rect)
                
                pygame.draw.rect(self._screen, bg_color, button_rect)
                pygame.draw.rect(self._screen, color, button_rect, 2)
                
                level_option = self._font_medium.render(f"УРОВЕНЬ {i}", True, color)
                option_rect = level_option.get_rect(center=(SCREEN_WIDTH // 2, y))
                self._screen.blit(level_option, option_rect)
            
            self._next_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, 420, 160, 40)
            pygame.draw.rect(self._screen, GREEN, self._next_button_rect)
            pygame.draw.rect(self._screen, WHITE, self._next_button_rect, 2)
            next_text = self._font_small.render("ДАЛЕЕ", True, BLACK)
            next_rect = next_text.get_rect(center=(SCREEN_WIDTH // 2, 440))
            self._screen.blit(next_text, next_rect)
            
            self._quit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, 480, 160, 40)
            pygame.draw.rect(self._screen, RED, self._quit_button_rect)
            pygame.draw.rect(self._screen, WHITE, self._quit_button_rect, 2)
            quit_text = self._font_small.render("ВЫХОД", True, WHITE)
            quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
            self._screen.blit(quit_text, quit_rect)
        
        else:
            formation_text = self._font_medium.render("ВЫБЕРИ КАРТУ:", True, WHITE)
            formation_rect = formation_text.get_rect(center=(SCREEN_WIDTH // 2, 90))
            self._screen.blit(formation_text, formation_rect)
            
            # Кнопка редактора карт - сверху над картами
            self._editor_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 105, 200, 35)
            pygame.draw.rect(self._screen, (100, 100, 200), self._editor_button_rect)
            pygame.draw.rect(self._screen, WHITE, self._editor_button_rect, 2)
            editor_text = self._font_small.render("СОЗДАТЬ КАРТУ", True, WHITE)
            editor_rect = editor_text.get_rect(center=self._editor_button_rect.center)
            self._screen.blit(editor_text, editor_rect)
            
            current_name = FORMATION_NAMES[self._selected_formation_index]
            current_screenshot = FORMATION_SCREENSHOTS[current_name]
            
            preview_width = 250
            preview_height = 160
            preview_x = SCREEN_WIDTH // 2 - preview_width // 2
            preview_y = 160  
            
            self._left_arrow_rect = pygame.Rect(preview_x - 70, preview_y + preview_height // 2 - 25, 50, 50)
            self._right_arrow_rect = pygame.Rect(preview_x + preview_width + 20, preview_y + preview_height // 2 - 25, 50, 50)
            
            if current_screenshot:
                scaled_img = pygame.transform.scale(current_screenshot, (preview_width, preview_height))
                self._screen.blit(scaled_img, (preview_x, preview_y))
            else:
                pygame.draw.rect(self._screen, DARK_GRAY, (preview_x, preview_y, preview_width, preview_height))
                pygame.draw.rect(self._screen, WHITE, (preview_x, preview_y, preview_width, preview_height), 2)
                if current_name == "RANDOM":
                    preview_text = self._font_medium.render("СЛУЧАЙНАЯ", True, LIGHT_GRAY)
                else:
                    preview_text = self._font_medium.render(current_name, True, LIGHT_GRAY)
                preview_rect = preview_text.get_rect(center=(preview_x + preview_width // 2, preview_y + preview_height // 2))
                self._screen.blit(preview_text, preview_rect)
            
            pygame.draw.rect(self._screen, DARK_GRAY, self._left_arrow_rect)
            pygame.draw.rect(self._screen, WHITE, self._left_arrow_rect, 2)
            left_arrow = self._font_large.render("<", True, WHITE)
            self._screen.blit(left_arrow, left_arrow.get_rect(center=self._left_arrow_rect.center))
            
            pygame.draw.rect(self._screen, DARK_GRAY, self._right_arrow_rect)
            pygame.draw.rect(self._screen, WHITE, self._right_arrow_rect, 2)
            right_arrow = self._font_large.render(">", True, WHITE)
            self._screen.blit(right_arrow, right_arrow.get_rect(center=self._right_arrow_rect.center))
            
            if current_name == "RANDOM":
                name_text = self._font_medium.render("СЛУЧАЙНАЯ", True, YELLOW)
            else:
                name_text = self._font_medium.render(current_name, True, GREEN)
            name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, preview_y + preview_height + 30))
            self._screen.blit(name_text, name_rect)
            
            self._start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 470, 200, 40)
            pygame.draw.rect(self._screen, GREEN, self._start_button_rect)
            pygame.draw.rect(self._screen, WHITE, self._start_button_rect, 2)
            start_text = self._font_small.render("СТАРТ", True, BLACK)
            start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, 490))
            self._screen.blit(start_text, start_rect)
            
            self._back_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 515, 200, 40)
            pygame.draw.rect(self._screen, RED, self._back_button_rect)
            pygame.draw.rect(self._screen, WHITE, self._back_button_rect, 2)
            back_text = self._font_small.render("НАЗАД", True, WHITE)
            back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, 535))
            self._screen.blit(back_text, back_rect)
        
        controls = self._font_small.render("МЫШЬ - УПРАВЛЕНИЕ", True, WHITE)
        controls_rect = controls.get_rect(center=(SCREEN_WIDTH // 2, 590))
        self._screen.blit(controls, controls_rect)
    
    def _draw_game(self):
        self._screen.fill(BLACK)
        
        self._player.draw(self._screen)
        self._formation.draw(self._screen)
        for bullet in self._bullets:
            bullet.draw(self._screen)
        
        score_text = self._font_small.render(f"СЧЁТ: {self._score}", True, WHITE)
        level_text = self._font_small.render(f"УРОВЕНЬ: {self._level}", True, WHITE)
        lives_text = self._font_small.render(f"ЖИЗНЕЙ: {self._player.lives}", True, WHITE)
        
        if self._formation._formation_type == "RANDOM":
            formation_text = self._font_small.render("КАРТА: СЛУЧАЙНАЯ", True, YELLOW)
        else:
            formation_text = self._font_small.render(f"КАРТА: {self._formation._formation_type}", True, WHITE)
        
        self._screen.blit(score_text, (20, 10))
        self._screen.blit(level_text, (SCREEN_WIDTH // 2 - 80, 10))
        self._screen.blit(formation_text, (SCREEN_WIDTH // 2 + 40, 10))
        self._screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))
        
        # Отрисовка паузы
        if self._paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self._screen.blit(overlay, (0, 0))
            
            pause_text = self._font_large.render("ПАУЗА", True, WHITE)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
            self._screen.blit(pause_text, pause_rect)
            
            self._resume_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 300, 200, 50)
            pygame.draw.rect(self._screen, GREEN, self._resume_button_rect)
            pygame.draw.rect(self._screen, WHITE, self._resume_button_rect, 2)
            resume_text = self._font_medium.render("ПРОДОЛЖИТЬ", True, BLACK)
            resume_rect = resume_text.get_rect(center=self._resume_button_rect.center)
            self._screen.blit(resume_text, resume_rect)
            
            self._quit_to_menu_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 370, 200, 50)
            pygame.draw.rect(self._screen, RED, self._quit_to_menu_button_rect)
            pygame.draw.rect(self._screen, WHITE, self._quit_to_menu_button_rect, 2)
            menu_text = self._font_medium.render("В МЕНЮ", True, WHITE)
            menu_rect = menu_text.get_rect(center=self._quit_to_menu_button_rect.center)
            self._screen.blit(menu_text, menu_rect)
    
    def _draw_game_over(self):
        self._draw_game()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self._screen.blit(overlay, (0, 0))
        
        game_over = self._font_large.render("GAME OVER", True, RED)
        game_over_rect = game_over.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self._screen.blit(game_over, game_over_rect)
        
        score_text = self._font_medium.render(f"СЧЁТ: {self._score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self._screen.blit(score_text, score_rect)
        
        self._menu_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, 350, 240, 45)
        pygame.draw.rect(self._screen, GREEN, self._menu_button_rect)
        pygame.draw.rect(self._screen, WHITE, self._menu_button_rect, 2)
        menu_text = self._font_medium.render("ГЛАВНОЕ МЕНЮ", True, BLACK)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, 372))
        self._screen.blit(menu_text, menu_rect)
        
        self._quit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, 420, 240, 45)
        pygame.draw.rect(self._screen, RED, self._quit_button_rect)
        pygame.draw.rect(self._screen, WHITE, self._quit_button_rect, 2)
        quit_text = self._font_medium.render("ВЫХОД", True, WHITE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, 442))
        self._screen.blit(quit_text, quit_rect)
    
    def _draw_win(self):
        self._screen.fill(BLACK)
        
        # Показываем последнее состояние игры (уровень, счёт)
        self._player.draw(self._screen)
        self._formation.draw(self._screen)
        for bullet in self._bullets:
            bullet.draw(self._screen)
        
        score_text = self._font_small.render(f"СЧЁТ: {self._score}", True, WHITE)
        level_text = self._font_small.render(f"УРОВЕНЬ: {self._level}", True, WHITE)
        self._screen.blit(score_text, (20, 10))
        self._screen.blit(level_text, (SCREEN_WIDTH // 2 - 40, 10))
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self._screen.blit(overlay, (0, 0))
        
        win_text = self._font_large.render("ПОБЕДА!", True, GREEN)
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self._screen.blit(win_text, win_rect)
        
        score_final = self._font_medium.render(f"ФИНАЛЬНЫЙ СЧЁТ: {self._score}", True, WHITE)
        score_final_rect = score_final.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self._screen.blit(score_final, score_final_rect)
        
        self._menu_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, 350, 240, 45)
        pygame.draw.rect(self._screen, GREEN, self._menu_button_rect)
        pygame.draw.rect(self._screen, WHITE, self._menu_button_rect, 2)
        menu_text = self._font_medium.render("ГЛАВНОЕ МЕНЮ", True, BLACK)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, 372))
        self._screen.blit(menu_text, menu_rect)
        
        self._quit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, 420, 240, 45)
        pygame.draw.rect(self._screen, RED, self._quit_button_rect)
        pygame.draw.rect(self._screen, WHITE, self._quit_button_rect, 2)
        quit_text = self._font_medium.render("ВЫХОД", True, WHITE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, 442))
        self._screen.blit(quit_text, quit_rect)