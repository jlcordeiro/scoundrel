import pygame
from Deck import Deck
from gamelogic import *

WIDTH, HEIGHT = 1800, 600

CARD_WIDTH = 240

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (70, 70, 70)

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
        
        
# ---- Main Loop Assets ----

CARD_IMGS = {}
for i in range(0, 52):    
    rank = Deck.card_rank(i)
    suit = Deck.card_suit(i)
    filename = f"png/{suit}{rank}.png"
    CARD_IMGS[i] = pygame.image.load(filename)


CARD_RECTS = []
FIST_RECTS = []
card_height = CARD_IMGS[0].get_height()
for i in range(ROOM_SIZE):
    x = 10 + i * (CARD_WIDTH + 10)
    
    rect = pygame.Rect(x, 10, CARD_WIDTH, card_height)
    CARD_RECTS.append(rect)
    
    fist_rect = pygame.Rect(10 + x, rect.bottom + 5, CARD_WIDTH - 40, 10)
    FIST_RECTS.append(fist_rect)



class LayoutMainGame:
    def __init__(self, screen):
        self.screen = screen

        self.button_force_fists = Button(CARD_WIDTH - 20, 50, "Use Fists")
        self.button_play = Button(160, 160, "PLAY")
        self.button_skip = Button(160, 160, "SKIP")

        self.button_play.visible = True
        self.button_skip.visible = True

        self.hp_bar = ProgressBar(10, 400, 600, 50, barcolor=(200, 0, 0))
        self.cards_bar = ProgressBar(10, 460, 600, 50, barcolor=(0, 200, 0))


    def draw(self, dungeon_state):
        self.screen.fill((255, 255, 255))

        # Draw buttons
        self.button_play.draw_at(self.screen, 1020, 180)
        self.button_skip.draw_at(self.screen, 1020, 10)

        self.hp_bar.draw(self.screen, dungeon_state.hp, MAX_HP)
        self.cards_bar.draw(self.screen, dungeon_state.deck.size(), dungeon_state.deck.initial_size())

        for (idx, card) in enumerate(dungeon_state.room.cards):
            rect = CARD_RECTS[idx]
            first_rect = FIST_RECTS[idx]
            chosen_card = dungeon_state.chosen_card

            if card.used: continue
            if chosen_card and chosen_card.card == card.card:
                pygame.draw.rect(self.screen, (255, 0, 0), rect.inflate(10, 10), 51, border_radius=12)                    
                self.button_force_fists.draw_at(self.screen, first_rect.left, first_rect.top)
                        
            self.screen.blit(CARD_IMGS[card.card], rect.topleft)
            
        if dungeon_state.weapon_current is not None:            
            if dungeon_state.weapon_last_killed is not None:
                killed_img = CARD_IMGS[dungeon_state.weapon_last_killed]
                self.screen.blit(killed_img, (1220, 10))

            weapon_img = CARD_IMGS[dungeon_state.weapon_current]
            self.screen.blit(weapon_img, (1270, 10))
        

        pygame.display.flip()