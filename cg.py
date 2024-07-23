import random

class CardGame:
    def __init__(self, start_count, player_list=['computer', 'human'], suite_size=13, card_type_count=4, point_default=1, point_matrix={ }):
        self.hand_size = start_count
        self.game_over = False
        self.turn_index = 0
        self.suites = tuple(range(1, suite_size + 1))
        self.types = tuple(range(1, card_type_count + 1))
        grd = [[{ 'suite': n, 'card': m } for m in self.suites] for n in self.types]
        self.players = []
        for n in player_list:
            self.add_player(n)
        self.deck = []
        for n in grd:
            self.deck.extend(n)
        self.deck = list(map(lambda x: { 'card': x['card'], 'suite': x['suite'], 'points': point_default if x['card'] not in point_matrix else point_matrix[x['card']] }, self.deck))
        self.deck_template = [n for n in self.deck]
        self.shuffle_deck()
        self.deal()

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def draw_card(self, player):
        if len(self.deck) > 0:
            removed_card = self.deck.pop(0)
            player['hand'].append(removed_card)
        else:
            self.on_no_cards_in_deck()

    def on_no_cards_in_deck(self):
        print('no cards left')

    def add_player(self, type):
        self.players.append({ 'name': 'p' + str(len(self.players)), 'type': type, 'hand': [] })

    
    def deal(self):
        for p in self.players:
            [self.draw_card(p) for n in range(0, self.hand_size)]

    def turn_action(self):
        print('turn taken')

    def take_turn(self, action):
        if self.get_current_player()['type'] == 'computer':
            self.turn_action()
            print('I am not human')
            self.finish_turn()
        else:
            action()
        
    
    def finish_turn(self):
        self.turn_index += 1
        if self.turn_index >= len(self.players):
            self.turn_index = 0
    
    def get_current_player(self):
        return self.players[self.turn_index]
    
    def find_card(self, card, lst):
        matches = []
        for i, n in enumerate(lst):
            if n['card'] == card['card'] and n['suite'] == card['suite']:
                matches.append({ 'index': i, 'card': card })
        if len(matches) > 0:
            return matches[0]
        else:
            return None
    
    def unique_card_list(self, lst):
        u_list = []
        for n in lst:
            has_card = len(list(filter(lambda x: x['card'] == n['card'] and x['suite'] == n['suite'], u_list))) > 0
            if not has_card:
                u_list.append(n)
        return u_list
            

    