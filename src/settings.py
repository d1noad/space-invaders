

# Экран
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Space Invaders"

# Все цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 220, 0)
CYAN = (0, 220, 220)
DARK_GRAY = (30, 30, 30)
LIGHT_GRAY = (180, 180, 180)
SHIELD_COLOR = (80, 200, 120)

# Цвета врагов по типу
ENEMY_COLORS = {
    "basic": (180, 80, 220), #фиолетовый
    "fast": (80, 180, 220), #голубой
    "tough": (220, 100, 60), #оранжевый
}

# Игрок
PLAYER_SPEED = 400
PLAYER_BULLET_SPEED = 600
PLAYER_LIVES = 3
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 50
PLAYER_COLOR = GREEN
PLAYER_SHOOT_DELAY = 400 # миллисекунд между выстрелами
PLAYER_START_Y = SCREEN_HEIGHT - 60
RESPAWN_DELAY = 1500 # мс после смерти до возрождения

# Враги
ENEMY_ROWS = 4
ENEMY_COLS = 10
ENEMY_WIDTH = 36
ENEMY_HEIGHT = 28
ENEMY_H_SPACING = 56 # шаг по горизонтали
ENEMY_V_SPACING = 50 # шаг по вертикали
ENEMY_START_X = 60
ENEMY_START_Y = 70
ENEMY_MOVE_SPEED = 1.0 # базовая скорость (множитель)
ENEMY_DROP_STEP = 20 # px вниз при смене направления
ENEMY_ANIM_INTERVAL = 600 # мс между кадрами анимации
ENEMY_BULLET_SPEED = 250
ENEMY_SHOOT_CHANCE = 0.0008 # вероятность выстрела за кадр

# Щиты
SHIELD_WIDTH = 64
SHEILD_HEIGHT = 40
SHIELD_COUNT = 4
SHIELD_Y = SCREEN_HEIGHT - 130
SHIELD_BLOCK_SIZE = 8 #размер одного блока щита

# Уровни сложности
LEVELS = {
    1: {"speed_mult": 1.0, "shoot_mult": 1.0, "rows": 3, "cols": 9},
    2: {"speed_mult": 1.4, "shoot_mult": 1.6, "rows": 4, "cols": 10},
    3: {"speed_mult": 1.9, "shoot_mult": 2.4, "rows": 4, "cols": 11},
}
MAX_LEVEL = 3

# Очки от типа врага
ENEMY_SCORES = {
    "basic": 10,
    "fast":  20,
    "tough": 30,
}

# UI
FONT_SIZE_LARGE = 48
FONT_SIZE_MEDIUM = 28
FONT_SIZE_SMALL = 18
HUD_HEIGHT = 40
