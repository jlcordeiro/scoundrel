import pygame

from widgets import WIDTH, HEIGHT

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (70, 70, 70)

class TitleScreen:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont(None, 120)
        self.button_font = pygame.font.SysFont(None, 60)
                
        button_width, button_height = 300, 80
        self.button_rect = pygame.Rect(0, 0, button_width, button_height)
        self.button_rect.center = (WIDTH // 2, HEIGHT // 3 * 2)

    def draw(self, hover=False):
        self.screen.fill(DARK_GRAY)

        # ---- Title ----
        title_surface = self.title_font.render("Scoundrel", True, WHITE)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.screen.blit(title_surface, title_rect)

        # ---- Button ----
        color = LIGHT_GRAY if hover else BLACK

        pygame.draw.rect(self.screen, color, self.button_rect, border_radius=20)

        btn_text = self.button_font.render("New Game", True, WHITE)
        btn_rect = btn_text.get_rect(center=self.button_rect.center)
        self.screen.blit(btn_text, btn_rect)
