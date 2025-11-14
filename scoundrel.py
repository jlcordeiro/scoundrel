import sys

import pygame
pygame.init()

import Deck
from Deck import Deck, CardHand, Card
from widgets import *
from gamelogic import *
from titlescreen import TitleScreen


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scoundrel")
font = pygame.font.SysFont(None, 36)
pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


# ---- Main Loop ----
clock = pygame.time.Clock()

title_screen = TitleScreen(screen)

game_controller = GameController()
game_layout = LayoutMainGame(screen)

def show_title_screen():
    """ Show the title screen and wait for the user to click "New Game"
    """
    title_screen = TitleScreen(screen)
    redraw = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if title_screen.button_rect.collidepoint(pos):
                    return

        if redraw:
            title_screen.draw()
            pygame.display.flip()
            redraw = False
            clock.tick(60)


while True:
    show_title_screen()

    redraw = True
    while not game_controller.is_finished():

        for event in pygame.event.get():
            if game_controller.is_finished():
                break

            # ---------------------------------------------------------
            # 1. ESC KEY HANDLER
            # ---------------------------------------------------------
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    break
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
            for idx, card in enumerate(game_controller.dungeon.room.cards):
                if card.used:
                    continue
                if CARD_RECTS[idx].collidepoint(pos):
                    can_choose_weapon = game_controller.select_card(card)

                    if can_choose_weapon:
                        game_layout.button_force_fists.disable()
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
                game_controller.end_round()

                game_layout.button_skip.disable()
                game_layout.button_force_fists.disable()
                redraw = True
                continue  # Nothing else to process

            # ---------------------------------------------------------
            # 2d. CLICKED PLAY?
            # ---------------------------------------------------------
            if game_layout.button_play.collideswith(pos):
                use_fists = game_layout.button_force_fists.toggled
                game_controller.play_card(use_fists)

                game_layout.button_skip.visible = False
                game_layout.button_force_fists.disable()

                if game_controller.end_round():
                    game_layout.button_skip.visible = True

                redraw = True


        # ---- Drawing ----
        if redraw:
            redraw = False
            game_layout.draw(game_controller.dungeon)    
        clock.tick(60)
            

    if False:      
        monsters_left = sum([Deck.card_rank(c) for c in deck.deck if Deck.card_suit(c) in ('C', 'S')])
        healing_left = sum([Deck.card_rank(c) for c in deck.deck if Deck.card_suit(c) in ('H')])
        if hp <= 0:
            total_score = - monsters_left
            print("You have been defeated! Total score:", total_score)
        else:
            total_score = hp + healing_left - monsters_left
            print("You have cleared all rooms with total score:", total_score)


pygame.quit()
