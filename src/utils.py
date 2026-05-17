import pygame



def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def center_text(surface, text, font, color, y):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(rendered, rect)

