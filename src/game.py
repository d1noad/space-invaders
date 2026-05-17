import pygame
import sys

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
        self._level = 1
        self._selected_level = 1
        self._score = 0
        self._player = None
        self._formation = None
        self._bullets = []
        
        self._font_small = pygame.font.SysFont(None, FONT_SIZE_SMALL)
        self._font_medium = pygame.font.SysFont(None, FONT_SIZE_MEDIUM)
        self._font_large = pygame.font.SysFont(None, FONT_SIZE_LARGE)

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
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            
            elif event.type == pygame.KEYDOWN:
                if self._state == "menu":
                    if event.key == pygame.K_DOWN:
                        self._selected_level = min(MAX_LEVEL, self._selected_level + 1)
                    elif event.key == pygame.K_UP:
                        self._selected_level = max(1, self._selected_level - 1)
                    elif event.key == pygame.K_SPACE:
                        self._start_game(self._selected_level)
                    elif event.key == pygame.K_ESCAPE:
                        self._running = False
                
                elif self._state == "playing":
                    if event.key == pygame.K_LEFT:
                        self._player.press_left()
                    elif event.key == pygame.K_RIGHT:
                        self._player.press_right()
                    elif event.key == pygame.K_ESCAPE:
                        self._state = "menu"
                
                elif self._state == "game_over":
                    if event.key == pygame.K_SPACE:
                        self._start_game(self._selected_level)
                    elif event.key == pygame.K_ESCAPE:
                        self._state = "menu"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self._state == "playing":
                    if event.button == 1:
                        if self._player.can_shoot():
                            bullet = self._player.shoot()
                            self._bullets.append(bullet)
            
            elif event.type == pygame.KEYUP:
                if self._state == "playing":
                    if event.key == pygame.K_LEFT:
                        self._player.release_left()
                    elif event.key == pygame.K_RIGHT:
                        self._player.release_right()
    
    def _start_game(self, level):
        self._level = level
        self._score = 0
        self._player = Player(SCREEN_WIDTH // 2, PLAYER_START_Y)
        self._formation = Formation(self._level)
        self._bullets = []
        self._state = "playing"
    
    def _update(self, dt: float):
        self._player.update(dt)
        self._formation.update(dt)

        for bullet in self._bullets:
            bullet.update(dt)
        
        enemy_bullet = self._formation.try_shoot()
        if enemy_bullet:
            self._bullets.append(enemy_bullet)

        self._check_collisions()
        self._bullets = [bullet for bullet in self._bullets if bullet.alive]

        if self._formation.all_dead():
            self._level += 1
            if self._level > MAX_LEVEL:
                self._state = "game_over"
            else:
                self._formation = Formation(self._level)
        
        if not self._player.alive or self._formation.reached_bottom():
            self._state = "game_over"
    
    def _check_collisions(self):
        for bullet in self._bullets:
            if bullet.owner == "player":
                for enemy in self._formation.enemies:
                    if bullet.collides_with(enemy):
                        enemy.hit()
                        bullet.kill()
                        if not enemy.alive:
                            self._score += enemy.score
            elif bullet.owner == "enemy":
                if bullet.collides_with(self._player):
                    self._player.hit()
                    bullet.kill()
    
    def _draw_menu(self):
        self._screen.fill(BLACK)
        
        title = self._font_large.render("SPACE INVADERS", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self._screen.blit(title, title_rect)
        
        level_text = self._font_medium.render("Выберите уровень сложности:", True, WHITE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, 240))
        self._screen.blit(level_text, level_rect)
        
        for i in range(1, MAX_LEVEL + 1):
            if i == self._selected_level:
                color = GREEN
                prefix = "> "
            else:
                color = WHITE
                prefix = "  "
            
            level_option = self._font_medium.render(f"{prefix}LEVEL {i}", True, color)
            option_rect = level_option.get_rect(center=(SCREEN_WIDTH // 2, 250 + i * 40))
            self._screen.blit(level_option, option_rect)
        
        start = self._font_small.render("Space - Начать", True, GREEN)
        start_rect = start.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self._screen.blit(start, start_rect)
        
        
        quit_text = self._font_small.render("Esc - Выйти", True, RED)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, 540))
        self._screen.blit(quit_text, quit_rect)
    
    def _draw_game(self):
        self._screen.fill(BLACK)
        self._player.draw(self._screen)
        self._formation.draw(self._screen)
        for bullet in self._bullets:
            bullet.draw(self._screen)
        
        score_text = self._font_small.render(f"Score: {self._score}", True, WHITE)
        level_text = self._font_small.render(f"Level: {self._level}", True, WHITE)
        lives_text = self._font_small.render(f"Lives: {self._player.lives}", True, WHITE)
        
        self._screen.blit(score_text, (20, 10))
        self._screen.blit(level_text, (SCREEN_WIDTH // 2 - 40, 10))
        self._screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))
        
        esc_text = self._font_small.render("ESC - MENU", True, DARK_GRAY)
        self._screen.blit(esc_text, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 30))
    
    def _draw_game_over(self):
        self._draw_game()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self._screen.blit(overlay, (0, 0))
        
        game_over = self._font_large.render("GAME OVER", True, RED)
        game_over_rect = game_over.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self._screen.blit(game_over, game_over_rect)
        
        restart = self._font_medium.render("SPACE - PLAY AGAIN", True, GREEN)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, 350))
        self._screen.blit(restart, restart_rect)
        
        menu = self._font_medium.render("ESC - MAIN MENU", True, WHITE)
        menu_rect = menu.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self._screen.blit(menu, menu_rect)