import Deck
from Deck import Deck, SUITS
import pygame
import sys

ROOM_SIZE = 4
FISTS = 0
max_hp = 20

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

CARD_WIDTH = 240

def print_card(card):
    rank = Deck.card_rank(card)
    suit = Deck.card_suit(card)
    rank_str = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}.get(rank, str(rank))
    return rank_str + suit


def heal(current_hp, card):
    suit = Deck.card_suit(card)
    rank = Deck.card_rank(card)
    if suit != 'H':
        return current_hp
    return min(max_hp, current_hp + rank)

assert heal(2, 4) == 7 # 5 of Hearts
assert heal(1, 11) == 13  # Queen of Hearts    
assert heal(max_hp - 1, 11) == max_hp  # Does not go above max hp
assert heal(2, 18) == 2 # Diamons
assert heal(2, 31) == 2 # Clubs
assert heal(2, 44) == 2 # Spades

def battle(monster_card, current_hp, weapon_current, weapon_last_slain, force_fists):
    suit = Deck.card_suit(monster_card)
    if suit not in ('C', 'S'):
        return current_hp, weapon_current, weapon_last_slain

    monster_rank = Deck.card_rank(monster_card)
    if weapon_current is None or force_fists or (weapon_last_slain and weapon_last_slain <= monster_rank):
        dmg_reduction = 0
        weapon_last_slain = weapon_last_slain
    else:
        dmg_reduction = weapon_current
        weapon_last_slain = monster_rank
    
    new_hp = current_hp - max(0, monster_rank - dmg_reduction)
    
    return (new_hp, weapon_current, weapon_last_slain)

# Non monster cards should keep world state unchanged
assert battle(4, 104, 544, 927, False) == (104, 544, 927)  # Hearts
assert battle(18, 104, 544, 927, True) == (104, 544, 927)  # Diamonds
# battle with weapon
assert battle(31, 20, 5, 13, False) == (19, 5, 6)  # Clubs rank 6
assert battle(31, 20, 5, 13, True) == (14, 5, 13)  # Clubs rank 6 but with force_fists
assert battle(31, 20, None, 13, False) == (14, None, 13)  # Clubs rank 6 but without weapon
assert battle(31, 20, None, 13, True) == (14, None, 13)  # Clubs rank 6 but without weapon and force_fists
assert battle(31, 20, 5, None, False) == (19, 5, 6)  # Clubs rank 6 with weapon but weapon is new
assert battle(31, 20, 5, 4, False) == (14, 5, 4)  # Clubs rank 6 with weapon but monster is stronger than what is supposed
assert battle(44, 20, 5, 4, False) == (14, 5, 4)  # Same as above but spades

test_deck = Deck(shuffled=False)

pygame.init()
WIDTH, HEIGHT = 1800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scoundrel")
font = pygame.font.SysFont(None, 36)
pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


all_images = {}
for i in range(0, 52):    
    rank = Deck.card_rank(i)
    suit = Deck.card_suit(i)
    filename = f"png/{suit}{rank}.png"
    all_images[i] = pygame.image.load(filename)

offset_x, offset_y = 0, 0

# ---- Simple Button ----
class Button:
    def __init__(self, width, height, text):
        self.rect = pygame.Rect(-50, -50, width, height)
        self.text = font.render("Use Fists", True, BLACK)
        self.visible = False
        self.toggled = False
        self.color_on = (0, 255, 0)
        self.color_off = GRAY
    
    def draw_at(self, x, y):
        self.rect.x = x + 10
        self.rect.y = y
        self.visible = True
        
        draw_color = self.color_on if self.toggled else self.color_off
        pygame.draw.rect(screen, draw_color, self.rect, border_radius=12)
        text_rect = self.text.get_rect(center=self.rect.center)
        screen.blit(self.text, text_rect)
        
    def toggle_if_clicked(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos) and self.visible:
            self.toggled = not self.toggled
            return True
        return False
    
    def disable(self):
        self.visible = False
        self.toggled = False

button_force_fists = Button(CARD_WIDTH - 20, 50, "Use Fists")

skip_rect = pygame.Rect(1020, 10, 160, 160)
play_rect = pygame.Rect(1020, 180, 160, 160)

skip_text = font.render("SKIP", True, BLACK)
play_text = font.render("PLAY", True, BLACK)

# ---- Main Loop ----
clock = pygame.time.Clock()


def draw_bar(surface, val, max, x, y, w=200, h=25, barcolor=(0, 200, 0)):
    pygame.draw.rect(surface, (0, 0, 0), (x, y, w, h), 2)
    fill = int((val / max) * (w - 4))
    pygame.draw.rect(surface, (200, 0, 0), (x + 2, y + 2, fill, h - 4))
    text = font.render(f"{val}/{max}", True, (70, 70, 70))
    screen.blit(text, (x + w + 70, y))  # adjust position

def draw_hp_bar(surface, current_hp, max_hp, x, y, w=200, h=25):
    draw_bar(surface, current_hp, max_hp, x, y, w=200, h=25, barcolor=(200, 0, 0))

def draw_progress_bar(surface, current_size, max_size, x, y, w=200, h=25):
    draw_bar(surface, current_size, max_size, x, y, w=200, h=25, barcolor=(0, 200, 0))

deck = Deck()
hp = max_hp
weapon_current = None
weapon_last_slain = None
weapon_card = None
weapon_last_killed = None

def get_room_images(deck):
    global all_images
    result = []

    i = 0
    for card in deck.top(ROOM_SIZE):
        img = all_images[card]
        rect = img.get_rect(topleft=(10 + i * 250, 10))
        result.append([rect, False])
        i += 1
    
    return result

def get_used_cards(card_rects):
    used = []
    l = len(card_rects)
    for i in range(l):
        if card_rects[i][1]:
            used.append(deck.top(l)[i])
    return used


card_rects = get_room_images(deck)

debug_text = ""
chosen_card = None
previous_input_was_skip = False
redraw = True
while hp > 0 and deck.size() >= ROOM_SIZE:

    for event in pygame.event.get():
        if hp <= 0:
            break
        
        if deck.size() < ROOM_SIZE:
            break

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


        if event.type == pygame.MOUSEBUTTONDOWN:
            for idx, val in enumerate(card_rects):
                rect, used = val
                if used: continue
                if rect.collidepoint(event.pos):
                    chosen_card = idx
                    redraw = True
                    break

            if skip_rect.collidepoint(event.pos):
                if not previous_input_was_skip and len(get_used_cards(card_rects)) == 0:
                    deck.move_to_end(ROOM_SIZE)
                    previous_input_was_skip = True
                    chosen_card = None
                    card_rects = get_room_images(deck)
                    button_force_fists.disable()
                    redraw = True
                    
            redraw = redraw or button_force_fists.toggle_if_clicked(event.pos)

            if play_rect.collidepoint(event.pos):
                
                if chosen_card is not None:
                    card = deck.top(ROOM_SIZE)[chosen_card]
                    suit = Deck.card_suit(card)

                    if suit in ('C', 'S'):
                        prev_weapon_last_slain = weapon_last_slain
                        (hp, weapon_current, weapon_last_slain) = battle(card, hp, weapon_current, weapon_last_slain, button_force_fists.toggled)
                        if weapon_last_slain and weapon_last_slain != prev_weapon_last_slain:
                            weapon_last_killed = card
                    elif suit in ('H'):
                        hp = heal(hp, card)
                    elif suit == 'D':
                        weapon_current = Deck.card_rank(card)
                        weapon_card = card
                        weapon_last_slain = None
                        weapon_last_killed = None
                    
                    rect = card_rects[chosen_card]
                    rect[1] = True  # Mark as used
                    
                    # if only one rect not used
                    used_cards = get_used_cards(card_rects)
                    if len(used_cards) == ROOM_SIZE - 1:
                        deck.remove(used_cards)
                        card_rects = get_room_images(deck)

                    chosen_card = None
                    previous_input_was_skip = False
                    button_force_fists.disable()
                    redraw = True

        # ---- Mouse button up ----
        elif event.type == pygame.MOUSEBUTTONUP:
            pass

        # ---- Mouse motion ----
        elif event.type == pygame.MOUSEMOTION:
            pass
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("Escape pressed!")
                pygame.quit()
                sys.exit()


    # ---- Drawing ----
    if redraw:
        redraw = False
        screen.fill(WHITE)

        # Draw buttons
        if not previous_input_was_skip and len(get_used_cards(card_rects)) == 0:
            pygame.draw.rect(screen, GRAY, skip_rect)
            screen.blit(skip_text, (skip_rect.x + 50, skip_rect.y + 100))

        pygame.draw.rect(screen, GRAY, play_rect)
        screen.blit(play_text, (play_rect.x + 50, play_rect.y + 100))
        
        l = min(ROOM_SIZE, deck.size())
        for i in range(l):
            if card_rects[i][1]: continue
            card = deck.top(ROOM_SIZE)[i]
            if chosen_card == i:
                pygame.draw.rect(screen, (255, 0, 0), card_rects[i][0].inflate(12, 12), 51, border_radius=12)
                if Deck.card_suit(card) in ('C', 'S'):
                    rank = Deck.card_rank(card)
                    if weapon_current and (weapon_last_slain is None or rank < (weapon_last_slain or 0)):
                        button_force_fists.draw_at(card_rects[i][0].left, card_rects[i][0].bottom + 10)
                        
            screen.blit(all_images[card], card_rects[i][0].topleft)
            
        if weapon_current is not None and weapon_card is not None:            
            if weapon_last_killed is not None:
                killed_img = all_images[weapon_last_killed]
                killed_pos = (1220, 10)
                screen.blit(killed_img, killed_pos)

            weapon_img = all_images[weapon_card]
            weapon_pos = (1270, 10)
            screen.blit(weapon_img, weapon_pos)


        # Draw info text
        monsters_left = sum([Deck.card_rank(c) for c in deck.deck if Deck.card_suit(c) in ('C', 'S')])
        info_text = f"Score: -{monsters_left}"
        info_surface = font.render(info_text, True, BLACK)
        screen.blit(info_surface, (50, 500))
        
        draw_hp_bar(screen, hp, max_hp, 10, 400, 600, 50)
        draw_progress_bar(screen, deck.size(), test_deck.size(), 10, 460, 600, 50)

        pygame.display.flip()
    
    clock.tick(60)
        

        
monsters_left = sum([Deck.card_rank(c) for c in deck.deck if Deck.card_suit(c) in ('C', 'S')])
healing_left = sum([Deck.card_rank(c) for c in deck.deck if Deck.card_suit(c) in ('H')])
if hp <= 0:
    total_score = - monsters_left
    print("You have been defeated! Total score:", total_score)
else:
    total_score = hp + healing_left - monsters_left
    print("You have cleared all rooms with total score:", total_score)


pygame.quit()
