import sys

import pygame
pygame.init()

import Deck
from Deck import Deck, CardHand, Card
from widgets import *
from gamelogic import *


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scoundrel")
font = pygame.font.SysFont(None, 36)
pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


# ---- Simple Button ----
class LayoutMainGame:
    def __init__(self):
        self.button_force_fists = Button(CARD_WIDTH - 20, 50, "Use Fists")
        self.button_play = Button(160, 160, "PLAY")
        self.button_skip = Button(160, 160, "SKIP")

        self.button_play.visible = True
        self.button_skip.visible = True

        self.hp_bar = ProgressBar(10, 400, 600, 50, barcolor=(200, 0, 0))
        self.cards_bar = ProgressBar(10, 460, 600, 50, barcolor=(0, 200, 0))


    def draw(self):
        screen.fill((255, 255, 255))

        # Draw buttons
        self.button_play.draw_at(screen, 1020, 180)
        self.button_skip.draw_at(screen, 1020, 10)

        self.hp_bar.draw(screen, hp, MAX_HP)
        self.cards_bar.draw(screen, deck.size(), deck.initial_size())


        for (idx, card) in enumerate(room.cards):
            rect = CARD_RECTS[idx]
            first_rect = FIST_RECTS[idx]

            if card.used: continue
            if chosen_card and chosen_card.card == card.card:
                pygame.draw.rect(screen, (255, 0, 0), rect.inflate(10, 10), 51, border_radius=12)                    
                self.button_force_fists.draw_at(screen, first_rect.left, first_rect.top)
                        
            screen.blit(CARD_IMGS[card.card], rect.topleft)
            
        if weapon_current is not None:            
            if weapon_last_killed is not None:
                killed_img = CARD_IMGS[weapon_last_killed]
                screen.blit(killed_img, (1220, 10))

            weapon_img = CARD_IMGS[weapon_current]
            screen.blit(weapon_img, (1270, 10))
        

        pygame.display.flip()


game_layout = LayoutMainGame()

# ---- Main Loop ----
clock = pygame.time.Clock()

deck = Deck()
hp = MAX_HP
weapon_current = None
weapon_last_killed = None
room = CardHand(deck, ROOM_SIZE)


chosen_card = None
redraw = True
while hp > 0 and deck.size() >= ROOM_SIZE:

    for event in pygame.event.get():
        # Safety break
        if hp <= 0 or deck.size() < ROOM_SIZE:
            break

        # ---------------------------------------------------------
        # 1. ESC KEY HANDLER
        # ---------------------------------------------------------
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("Escape pressed!")
                pygame.quit()
                sys.exit()
            continue  # Skip rest of processing for key events

        # ---------------------------------------------------------
        # 2. MOUSE DOWN HANDLER
        # ---------------------------------------------------------
        if event.type != pygame.MOUSEBUTTONDOWN:
            continue

        pos = event.pos
        redraw = False

        # ---------------------------------------------------------
        # 2a. CLICKED ON A CARD?
        # ---------------------------------------------------------
        for idx, card in enumerate(room.cards):
            if card.used:
                continue
            if CARD_RECTS[idx].collidepoint(pos):
                chosen_card = card
                card_rank = Deck.card_rank(card.card)
                last_killed_rank = (
                    Deck.card_rank(weapon_last_killed)
                    if weapon_last_killed else None
                )

                # Show fists button if monster is weaker
                if (
                    weapon_current
                    and Deck.card_is_monster(card.card)
                    and (weapon_last_killed is None or card_rank < last_killed_rank)
                ):
                    game_layout.button_force_fists.visible = True

                redraw = True
                break  # Stop scanning rectangles

        # ---------------------------------------------------------
        # 2b. CLICKED FORCE FISTS TOGGLE?
        # ---------------------------------------------------------
        redraw = redraw or game_layout.button_force_fists.toggle_if_clicked(pos)

        # ---------------------------------------------------------
        # 2c. CLICKED SKIP?
        # ---------------------------------------------------------
        if game_layout.button_skip.collideswith(pos):
            deck.move_to_end(ROOM_SIZE)
            room = CardHand(deck, ROOM_SIZE)
            chosen_card = None

            game_layout.button_skip.disable()
            game_layout.button_force_fists.disable()

            redraw = True
            continue  # Nothing else to process

        # ---------------------------------------------------------
        # 2d. CLICKED PLAY?
        # ---------------------------------------------------------
        if game_layout.button_play.collideswith(pos):

            if chosen_card is None:
                continue

            game_layout.button_skip.visible = False

            card = chosen_card.card
            suit = Deck.card_suit(card)

            # Battle / heal / pick up weapon
            if Deck.card_is_monster(card):
                hp, weapon_current, weapon_last_killed = battle(
                    card, hp, weapon_current,
                    weapon_last_killed,
                    game_layout.button_force_fists.toggled
                )
            elif suit == 'H':
                hp = heal(hp, card)
            elif suit == 'D':
                weapon_current = card
                weapon_last_killed = None

            # Mark card as used
            chosen_card.used = True

            # If only 1 card left → refresh room
            used_cards = room.get_used()
            if len(used_cards) == ROOM_SIZE - 1:
                deck.remove(used_cards)
                room = CardHand(deck, ROOM_SIZE)
                game_layout.button_skip.visible = True

            game_layout.button_force_fists.disable()

            chosen_card = None
            redraw = True


    # ---- Drawing ----
    if redraw:
        redraw = False
        game_layout.draw()    
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
