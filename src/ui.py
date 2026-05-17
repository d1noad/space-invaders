import pygame
from settings import *


class UI:

    def __init__(self):
        self._font_small = pygame.font.SysFont(None, FONT_SIZE_SMALL)
        self._font_large = pygame.font.SysFont(None, FONT_SIZE_LARGE)

    def draw_hud(self, surface, score, level, lives):
        score_text = self._font_small.render(f"Счёт: {score}", True, WHITE)
        level_text = self._font_small.render(f"Уровень: {level}", True, WHITE)
        lives_text = self._font_small.render(f"Жизней: {lives}", True, WHITE)

        surface.blit(score_text, (20, 10))
        surface.blit(level_text, (320, 10))
        surface.blit(lives_text, (650, 10))

    def draw_game_over(self, surface):
        text = self._font_large.render("GAME OVER", True, RED)
        rect = text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )
        surface.blit(text, rect)

    
        