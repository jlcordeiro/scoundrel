from Deck import Deck

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


def battle(monster_card, current_hp, weapon_current, weapon_killed, force_fists):
    suit = Deck.card_suit(monster_card)
    if suit not in ('C', 'S'):
        return current_hp, weapon_current, weapon_killed

    monster_rank = Deck.card_rank(monster_card)
    if weapon_current is None or \
        force_fists or \
        (weapon_killed and Deck.card_rank(weapon_killed) <= monster_rank):
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