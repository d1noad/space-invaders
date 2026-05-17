# абстрактные базовые классы 
""" Используется:
Абстракция
Инкапсуляция
"""


from abc import ABC, abstractmethod
import pygame
from settings import BLACK


class GameObject(ABC):

    def __init__(
        self, 
        x: float, y: float, 
        width: int, height: float
    ):
        self._x = float(x)
        self._y = float(y)
        self._width = int(width)
        self._height = int(height)
        self._alive = True

    @property
    def x(self) -> float:
        return self._x
    
    @x.setter
    def x(self, value: float):
        self._x = float(value)

    @property
    def y(self) -> float:
        return self._y
    
    @y.setter
    def y(self, value: float):
        self._y = float(value)  
    
    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height
    
    @property
    def alive(self) -> bool:
        return self._alive
    
    def kill(self):
        self._alive = False
    
    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self._x), int(self._y), self._width, self._height)

    def collides_with(self, other: "GameObject") -> bool:
        return self.alive and other.alive and self.rect.colliderect(other.rect)
    
    @abstractmethod
    def update(self, dt: int) -> None:
        ...

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        ...

    def __repr__(self):
        return (f"<{self.__class__.__name__} "
                f"x={self._x:.0f} y={self._y:.0f} alive={self._alive}>")


class Sprite(GameObject):

    def __init__(
        self, x: float, y: float, 
        width: int, height: float, 
        color: tuple = BLACK
    ):
        super().__init__(x, y, width, height)
        self._color = color
        self._vx = 0.0
        self._vy = 0.0
        self._image = None

    @property
    def color(self) -> tuple:
        return self._color
    
    @color.setter
    def color(self, value: tuple):
        self._color = value

    def draw(self, surface: pygame.Surface) -> None:
        if self.alive:
            if self._image:
                surface.blit(self._image, self.rect)
            else:
                pygame.draw.rect(surface, self._color, self.rect)

    @abstractmethod
    def update(self, dt: int) -> None:
        ...