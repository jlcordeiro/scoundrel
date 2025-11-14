

SUITS = ['H', 'D', 'C', 'S']

class Deck:
    def __init__(self, shuffled=True):
        def shuffle_deck(deck):
            import random
            random.shuffle(deck)
            return deck

        def valid_card(card):
            """ In this game, we do not allow red aces or red face cards. """
            rank = Deck.card_rank(card)
            suit = Deck.card_suit(card)
            if suit in ('H', 'D'):
                if rank in (11, 12, 13, 14):
                    return False
            return True

        deck = [i for i in range(0, 52) if valid_card(i)]
        if shuffled:
            deck = shuffle_deck(deck)

        assert not valid_card(0)    # Ace of Hearts (invalid)
        assert not valid_card(10)  # Jack of Hearts (invalid)
        assert len(deck) == 44  # 52 total cards - 8 invalid cards
        assert len([i for i in deck if Deck.card_rank(i) == 14]) == 2  # Only black aces remain
        assert len([i for i in deck if Deck.card_rank(i) == 11]) == 2  # Only black aces remain
        assert len([i for i in deck if Deck.card_rank(i) == 12]) == 2  # Only black aces remain
        assert len([i for i in deck if Deck.card_rank(i) == 13]) == 2  # Only black aces remain
        assert len([i for i in deck if Deck.card_suit(i) == 'H']) == 9
        assert len([i for i in deck if Deck.card_suit(i) == 'C']) == 13
        
        self.deck = deck

    def card_suit(card):
        assert card >= 0 and card < 52
        return SUITS[card // 13]

    def card_rank(card):
        assert card >= 0 and card < 52
        rank = 1 + card % 13
        return 14 if rank == 1 else rank
    
    def card_is_monster(card):
        return Deck.card_suit(card) in ('C', 'S')
    
    def size(self):
        return len(self.deck)
    
    def move_to_end(self, n):
        self.deck = self.deck[n:] + self.deck[0:n]
        
    def top(self, n):
        return self.deck[0:min(n, len(self.deck))]
    
    def remove(self, cards):
        for card in cards:
            self.deck.remove(card)