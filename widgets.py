import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

font = pygame.font.SysFont(None, 36)

class Button:
    def __init__(self, width, height, text):
        self.rect = pygame.Rect(-50, -50, width, height)
        self.text = font.render(text, True, BLACK)
        self.visible = False
        self.toggled = False
        self.color_on = (0, 255, 0)
        self.color_off = GRAY

    
    def draw_at(self, screen, x, y):
        if self.visible == False:
            return

        self.rect.x = x + 10
        self.rect.y = y
        
        draw_color = self.color_on if self.toggled else self.color_off
        pygame.draw.rect(screen, draw_color, self.rect, border_radius=12)
        text_rect = self.text.get_rect(center=self.rect.center)
        screen.blit(self.text, text_rect)
        
    def collideswith(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos) and self.visible
        
    def toggle_if_clicked(self, mouse_pos):
        if self.collideswith(mouse_pos):
            self.toggled = not self.toggled
            return True
        return False
    
    def disable(self):
        self.visible = False
        self.toggled = False
        

class ProgressBar:
    def __init__(self, x, y, w=200, h=25, barcolor=(0, 200, 0)):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.barcolor = barcolor
        
    def draw(self, surface, val, max):
        pygame.draw.rect(surface, (0, 0, 0), (self.x, self.y, self.w, self.h), 2)
        fill = int((val / max) * (self.w - 4))
        pygame.draw.rect(surface, self.barcolor, (self.x + 2, self.y + 2, fill, self.h - 4))
        text = font.render(f"{val}/{max}", True, (70, 70, 70))
        surface.blit(text, (self.x + self.w + 70, self.y))  # adjust position