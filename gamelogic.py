from Deck import Deck, CardHand, Card

ROOM_SIZE = 4
MAX_HP = 20


def heal(current_hp, card):
    suit = Deck.card_suit(card)
    rank = Deck.card_rank(card)
    if suit != 'H':
        return current_hp
    return min(MAX_HP, current_hp + rank)

assert heal(2, 4) == 7 # 5 of Hearts
assert heal(1, 11) == 13  # Queen of Hearts    
assert heal(MAX_HP - 1, 11) == MAX_HP  # Does not go above max hp
assert heal(2, 18) == 2 # Diamons
assert heal(2, 31) == 2 # Clubs
assert heal(2, 44) == 2 # Spades

def can_use_weapon(weapon_card, weapon_killed_card, monster_card):
    if weapon_card is None or Deck.card_is_monster(monster_card) == False:
        return False
    
    if weapon_killed_card is None:
        return True

    weapon_rank = Deck.card_rank(weapon_killed_card)
    monster_rank = Deck.card_rank(monster_card)
    return weapon_rank > monster_rank

def battle(monster_card, current_hp, weapon_current, weapon_killed, force_fists):
    suit = Deck.card_suit(monster_card)
    if suit not in ('C', 'S'):
        return current_hp, weapon_current, weapon_killed

    monster_rank = Deck.card_rank(monster_card)
    if force_fists or False == can_use_weapon(weapon_current, weapon_killed, monster_card):
        dmg_reduction = 0
    else:
        dmg_reduction = Deck.card_rank(weapon_current)
        weapon_killed = monster_card
    
    new_hp = current_hp - max(0, monster_rank - dmg_reduction)
    
    return (new_hp, weapon_current, weapon_killed)

# Non monster cards should keep world state unchanged
assert battle(4, 104, 544, 927, False) == (104, 544, 927)  # Hearts
assert battle(18, 104, 544, 927, True) == (104, 544, 927)  # Diamonds
# battle with weapon
assert battle(31, 19, 5, 13, False) == (19, 5,31), battle(31, 19, 5, 13, False)  # Clubs rank 6
assert battle(31, 20, 5, 13, True) == (14, 5, 13)  # Clubs rank 6 but with force_fists
assert battle(31, 20, None, 13, False) == (14, None, 13)  # Clubs rank 6 but without weapon
assert battle(31, 20, None, 13, True) == (14, None, 13)  # Clubs rank 6 but without weapon and force_fists
print("All tests passed.")
assert battle(31, 19, 5, None, False) == (19, 5, 31), battle(31, 19, 5, None, False)  # Clubs rank 6 with weapon but weapon is new
assert battle(31, 20, 5, 4, False) == (14, 5, 4)  # Clubs rank 6 with weapon but monster is stronger than what is supposed
assert battle(44, 20, 5, 4, False) == (14, 5, 4)  # Same as above but spades




class DungeonState:
    def __init__(self):
        self.deck = Deck()
        self.hp = MAX_HP
        self.weapon_current = None
        self.weapon_last_killed = None
        self.room = CardHand(self.deck, ROOM_SIZE)
        self.chosen_card = None 
        self.healead_this_round = False


class GameController:
    def __init__(self):
        self.dungeon = DungeonState()
        
        
    def is_finished(self):
        return self.dungeon.hp <= 0 or self.dungeon.deck.size() < ROOM_SIZE
    
    
    def play_card(self, use_fists):
        card = self.dungeon.chosen_card
        if card is None:
            return
        card.used = True
        card = card.card

        suit = Deck.card_suit(card)
        if Deck.card_is_monster(card):
            self.dungeon.hp, self.dungeon.weapon_current, self.dungeon.weapon_last_killed = battle(
                card, self.dungeon.hp, self.dungeon.weapon_current,
                self.dungeon.weapon_last_killed,
                use_fists
            )
        elif suit == 'H':
            if self.dungeon.healead_this_round is False:
                self.dungeon.hp = heal(self.dungeon.hp, card)
                self.dungeon.healead_this_round = True
        elif suit == 'D':
            self.dungeon.weapon_current = card
            self.dungeon.weapon_last_killed = None
            
        
    def end_round(self):
        used_cards = self.dungeon.room.get_used()
        n_used = len(used_cards)
        if n_used not in (0, ROOM_SIZE - 1):
            return False
        
        if n_used == 0:
            self.dungeon.deck.move_to_end(ROOM_SIZE)

        self.dungeon.deck.remove(used_cards)
        self.dungeon.room = CardHand(self.dungeon.deck, ROOM_SIZE)
        self.dungeon.chosen_card = None
        
        self.dungeon.healead_this_round = False
        return True
    
    def select_card(self, card):
        self.dungeon.chosen_card = card
        return can_use_weapon(
            self.dungeon.weapon_current,
            self.dungeon.weapon_last_killed,
            card.card
        )