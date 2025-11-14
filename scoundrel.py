import sys

import pygame
pygame.init()

import Deck
from Deck import Deck, SUITS
from widgets import Button, ProgressBar

ROOM_SIZE = 4
FISTS = 0
max_hp = 20

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
button_force_fists = Button(CARD_WIDTH - 20, 50, "Use Fists")
button_play = Button(160, 160, "PLAY")
button_skip = Button(160, 160, "SKIP")

button_play.visible = True
button_skip.visible = True

hp_bar = ProgressBar(10, 400, 600, 50, barcolor=(200, 0, 0))
cards_bar = ProgressBar(10, 460, 600, 50, barcolor=(0, 200, 0))

# ---- Main Loop ----
clock = pygame.time.Clock()

deck = Deck()
hp = max_hp
weapon_current = None
weapon_last_slain = None
weapon_card = None
weapon_last_killed = None

CARD_RECTS = []
FIST_RECTS = []
card_height = all_images[0].get_height()
for i in range(ROOM_SIZE):
    x = 10 + i * (CARD_WIDTH + 10)
    
    rect = pygame.Rect(x, 10, CARD_WIDTH, card_height)
    CARD_RECTS.append(rect)
    
    fist_rect = pygame.Rect(10 + x, rect.bottom + 5, CARD_WIDTH - 40, 10)
    FIST_RECTS.append(fist_rect)

class Card:
    def __init__(self, card):
        self.card = card
        self.used = False
        self.selected = False

class Room:
    def __init__(self, deck):
        self.cards = []
        for card in deck.top(ROOM_SIZE):
            self.cards.append(Card(card))
        
    def get_used(self):
        return [c.card for c in self.cards if c.used]


def draw_main_game():
    screen.fill((255, 255, 255))

    # Draw buttons
    button_play.draw_at(screen, 1020, 180)
    button_skip.draw_at(screen, 1020, 10)

    hp_bar.draw(screen, hp, max_hp)
    cards_bar.draw(screen, deck.size(), test_deck.size())


    for (idx, card) in enumerate(room.cards):
        rect = CARD_RECTS[idx]
        first_rect = FIST_RECTS[idx]

        if card.used: continue
        if chosen_card and chosen_card.card == card.card:
            pygame.draw.rect(screen, (255, 0, 0), rect.inflate(10, 10), 51, border_radius=12)                    
            button_force_fists.draw_at(screen, first_rect.left, first_rect.top)
                    
        screen.blit(all_images[card.card], rect.topleft)
        
    if weapon_current is not None and weapon_card is not None:            
        if weapon_last_killed is not None:
            killed_img = all_images[weapon_last_killed]
            screen.blit(killed_img, (1220, 10))

        weapon_img = all_images[weapon_card]
        screen.blit(weapon_img, (1270, 10))
    

    pygame.display.flip()


room = Room(deck)

chosen_card = None
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
            for (idx, card) in enumerate(room.cards):
                if not card.used and CARD_RECTS[idx].collidepoint(event.pos):
                    chosen_card = card
                    redraw = True
                
                    if weapon_current \
                        and Deck.card_is_monster(chosen_card.card) \
                        and (weapon_last_slain is None or rank < (weapon_last_slain or 0)):
                            button_force_fists.visible = True
                            
                    break

            redraw = redraw or button_force_fists.toggle_if_clicked(event.pos)

            if button_skip.collideswith(event.pos):
                deck.move_to_end(ROOM_SIZE)
                chosen_card = None
                room = Room(deck)
                button_skip.disable()
                button_force_fists.disable()
                redraw = True

            if button_play.collideswith(event.pos):              
                if chosen_card is None:
                    continue

                button_skip.visible = False

                card = chosen_card.card
                suit = Deck.card_suit(card)

                if Deck.card_is_monster(card):
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
                
                chosen_card.used = True  # Mark as used
                
                # if only one rect not used
                used_cards = room.get_used()
                if len(used_cards) == ROOM_SIZE - 1:
                    deck.remove(used_cards)
                    room = Room(deck)
                    button_skip.visible = True

                chosen_card = None
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
        draw_room()    
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
