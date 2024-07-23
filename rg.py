import cg
from functools import reduce

CardGame = cg.CardGame

class RummyGame (CardGame):
    def __init__(self, player_list=['computer', 'human'], suite_size=13, card_type_count=4, match_min_length=3, point_matrix={ 13: 2, 12: 2, 11: 2, 10: 2, 1: 3 }):
        CardGame.__init__(self, 7, player_list, suite_size, card_type_count, point_matrix=point_matrix)
        self.match_min_length = match_min_length
        self.run_min_length = match_min_length
        self.discard_pile = []
        self.sets = []
        self.seen_cards = []
        self.cards_taken_by_other_players = []
        self.cards_never_seen = []
        self.no_cards_left_count = 0
        for n in self.players:
            self.set_discard_rating_value(n['name'])
        
        removed_card = self.deck.pop(0)
        self.discard_pile.append(removed_card)
    
    def set_discard_rating_value(self, player_name, card_point_factor=1, same_card_factor=1, same_suite_one_away_factor=1, same_suite_two_away_factor=1, same_card_num_other_players_factor=1, same_suite_one_card_away_other_players_factor=1, same_suite_two_cards_away_other_players_factor=1, same_card_num_never_seen_factor=1, same_suite_one_card_away_never_seen_factor=1, same_suite_two_cards_away_never_seen_factor=1):
        indexed_players = [ { 'index': i, 'name': n['name'] } for i, n in enumerate(self.players)]
        matching_players = list(filter(lambda x: x['name'] == player_name, indexed_players))
        if len(matching_players) > 0:
            self.players[matching_players[0]['index']]['card_point_factor'] = card_point_factor
            self.players[matching_players[0]['index']]['same_card_factor'] = same_card_factor
            self.players[matching_players[0]['index']]['same_suite_one_away_factor'] = same_suite_one_away_factor
            self.players[matching_players[0]['index']]['same_suite_two_away_factor'] = same_suite_two_away_factor
            self.players[matching_players[0]['index']]['same_card_num_other_players_factor'] = same_card_num_other_players_factor
            self.players[matching_players[0]['index']]['same_suite_one_card_away_other_players_factor'] = same_suite_one_card_away_other_players_factor
            self.players[matching_players[0]['index']]['same_suite_two_cards_away_other_players_factor'] = same_suite_two_cards_away_other_players_factor
            self.players[matching_players[0]['index']]['same_card_num_never_seen_factor'] = same_card_num_never_seen_factor
            self.players[matching_players[0]['index']]['same_suite_one_card_away_never_seen_factor'] = same_suite_one_card_away_never_seen_factor
            self.players[matching_players[0]['index']]['same_suite_two_cards_away_never_seen_factor'] = same_suite_two_cards_away_never_seen_factor

    def turn_action(self):
        super().turn_action()

        # pile_options = self.get_set_options(include_hand=False, include_pile=True)
        # if len(pile_options['options']) > 0:
        #     # process hand sets
        #     print('pile options')
        #     print(pile_options['options'][0]) # iterate through options
        #     # if has options add cards to hand

        # print('opportunities')
        # print(self.get_existing_set_opportunitie(include_pile=True))

        cards_gone_missing = self.get_not_seen_cards()
        self.cards_taken_by_other_players = cards_gone_missing['taken']
        self.cards_never_seen = cards_gone_missing['never_seen']
        print('cards taken by other players')
        print(self.cards_taken_by_other_players)
        print('cards never seen')
        print(self.cards_never_seen)

        combo_options = self.get_set_options(include_hand=True, include_pile=True)
        combo_opps = self.get_existing_set_opportunitie(include_pile=True)
        hand_before_combo = len(self.get_current_player()['hand'])
        first_card_picked_up = None
        # print(str(hand_before_combo) + ' cards')
        if len(combo_options['options']) > 0 or len(combo_opps['opps']) > 0:
            cards_to_draw = []
            cards_to_draw.extend(combo_options['unique_options'])
            cards_to_draw.extend(combo_opps['opps'])
            first_card_picked_up = self.draw_from_discard_pile(cards_to_draw)
            # print('first card picked up')
            # print(first_card_picked_up)

        hand_after_combo = len(self.get_current_player()['hand'])
        if (hand_before_combo == hand_after_combo):
            self.draw_card(self.get_current_player()) # only if there are no pile related options

        hand_options = self.get_set_options()
        hand_opps = self.get_existing_set_opportunitie()
        fcpu_options = []
        fcpu_opps = []
        if len(hand_options['options']) > 0 or len(hand_opps['opps']):
            if first_card_picked_up:
                options_with_fcpu = list(map(lambda x: len(list(filter(lambda y: y['card'] == first_card_picked_up['card'] and y['suite'] == first_card_picked_up['suite'] ,x['cards']))) > 0 ,hand_options['options']))
                if len(list(filter(lambda x: x ,options_with_fcpu))) > 0:
                    for i, n in enumerate(options_with_fcpu):
                        if n:
                            fcpu_options.append(hand_options['options'][i])
                    fcpu_options = list(reversed(list(sorted(fcpu_options, key=lambda x: x['point_totals']))))
                    # flag first set
                else:
                    opps_with_fcpu = list(map(lambda x: x['card']['card'] == first_card_picked_up['card'] and x['card']['suite'] == first_card_picked_up['suite'] ,hand_opps['opps']))
                    if len(list(filter(lambda x: x ,opps_with_fcpu))) > 0:
                        for i, n in enumerate(opps_with_fcpu):
                            if n:
                                fcpu_options.append(hand_opps['opps'][i])
                        fcpu_opps = list(reversed(list(sorted(fcpu_opps, key=lambda x: x['point_totals']))))
                        # flag first opp
            # process hand sets
            if len(fcpu_options) > 0 and 'cards' in fcpu_options[0].keys():
                self.add_set(self.get_current_player(), fcpu_options[0]['cards'])
            
            if len(fcpu_opps) > 0 and 'cards' in fcpu_opps[0].keys() and 'set' in fcpu_opps[0].keys():
                self.add_card_to_set(fcpu_opps[0]['card'], fcpu_opps[0]['set'])
            
            for i, n in enumerate(hand_options['options']):
                self.add_set(self.get_current_player(), hand_options['options'][i]['cards'])
            
            for i, n in enumerate(hand_opps['opps']):
                self.add_card_to_set(n['card'], n['set'])
            print('sets')
            print(self.sets)

        self.discard() # create logit to choose card to discard
    
    def on_no_cards_in_deck(self):
        self.no_cards_left_count += 1
        if len(self.discard_pile) > 0:
            reversed_discard_indexes = list(reversed([n for n in range(0, len(self.discard_pile))]))
            for n in reversed_discard_indexes:
                self.deck.append(self.discard_pile.pop(n))
            self.shuffle_deck()
        else:
            self.game_over = True
            self.get_winner()
        if self.no_cards_left_count > 5:
            self.game_over = True
            self.get_winner()

    def can_add_to_set(self):
        set_counts = [0 for n in self.sets]
        for i, n in enumerate(self.sets):
            set_counts[i] = len(list(filter(lambda x: x['player'] == self.get_current_player()['name'], n)))
        number_of_sets = len(list(filter(lambda x: x >= self.match_min_length, set_counts)))
        print('number of sets')
        print(number_of_sets)
        return number_of_sets > 0

    def get_winner(self):
        player_points = { n['name']: 0 for n in self.players }
        for n in self.players:
            list_of_points_in_hand = list(map(lambda x: x['points'], n['hand']))
            points_in_hand = 0
            if len(list_of_points_in_hand) > 0:
                points_in_hand = reduce(lambda x, y: x + y, list_of_points_in_hand)
            point_values_in_sets = []
            points_in_sets = 0
            for m in self.sets:
                filter_by_player = list(filter(lambda x: x['player'] == n['name'], m))
                filtered_points = list(map(lambda x: x['card']['points'], filter_by_player))
                point_values_in_sets.extend(filtered_points)
            if len(point_values_in_sets) > 0:
                points_in_sets = reduce(lambda x, y: x + y, point_values_in_sets)
            player_points[n['name']] = points_in_sets - points_in_hand
        print('player points')
        print(player_points)

    def discard(self, card_index=-1):
        if (len(self.get_current_player()['hand'])):
            if card_index < 0:
                card_ratings = []
                combo_cards = []
                combo_cards.extend(self.get_current_player()['hand'])
                combo_cards.extend(self.discard_pile)
                for i, n in enumerate(self.get_current_player()['hand']):
                    same_card_num = len(list(filter(lambda x: x['card'] == n['card'], combo_cards)))
                    same_suite_one_card_away = len(list(filter(lambda x: x['suite'] == n['suite'] and (n['card'] == x['card'] + 1 or n['card'] == x['card'] - 1), combo_cards)))
                    same_suite_two_cards_away = len(list(filter(lambda x: x['suite'] == n['suite'] and (n['card'] == x['card'] + 2 or n['card'] == x['card'] - 2), combo_cards)))
                    same_card_num_other_players = len(list(filter(lambda x: x['card'] == n['card'], self.cards_taken_by_other_players)))
                    same_suite_one_card_away_other_players = len(list(filter(lambda x: x['suite'] == n['suite'] and (n['card'] == x['card'] + 1 or n['card'] == x['card'] - 1), self.cards_taken_by_other_players)))
                    same_suite_two_cards_away_other_players = len(list(filter(lambda x: x['suite'] == n['suite'] and (n['card'] == x['card'] + 2 or n['card'] == x['card'] - 2), self.cards_taken_by_other_players)))
                    same_card_num_never_seen = len(list(filter(lambda x: x['card'] == n['card'], self.cards_never_seen)))
                    same_suite_one_card_away_never_seen = len(list(filter(lambda x: x['suite'] == n['suite'] and (n['card'] == x['card'] + 1 or n['card'] == x['card'] - 1), self.cards_never_seen)))
                    same_suite_two_cards_away_never_seen = len(list(filter(lambda x: x['suite'] == n['suite'] and (n['card'] == x['card'] + 2 or n['card'] == x['card'] - 2), self.cards_never_seen)))
                    rating_values = [
                        n['points'] * self.get_current_player()['card_point_factor'],
                        same_card_num * self.get_current_player()['same_card_factor'],
                        same_suite_one_card_away * self.get_current_player()['same_suite_one_away_factor'],
                        same_suite_two_cards_away * self.get_current_player()['same_suite_two_away_factor'],
                        same_card_num_other_players * self.get_current_player()['same_card_num_other_players_factor'],
                        same_suite_one_card_away_other_players * self.get_current_player()['same_suite_one_card_away_other_players_factor'],
                        same_suite_two_cards_away_other_players * self.get_current_player()['same_suite_two_cards_away_other_players_factor'],
                        same_card_num_never_seen * self.get_current_player()['same_card_num_never_seen_factor'],
                        same_suite_one_card_away_never_seen * self.get_current_player()['same_suite_one_card_away_never_seen_factor'],
                        same_suite_two_cards_away_never_seen * self.get_current_player()['same_suite_two_cards_away_never_seen_factor'],
                    ]
                    card_rating = reduce(lambda x, y: x + y, rating_values) 
                    card_ratings.append({ 'rating': card_rating, 'index': i })
                card_ratings = list(sorted(card_ratings, key=lambda x: x['rating']))
                card_to_discard = self.get_current_player()['hand'].pop(card_ratings[0]['index'])
                self.discard_pile.append(card_to_discard)
            else:
                card_to_discard = self.get_current_player()['hand'].pop(card_index)
                self.discard_pile.append(card_to_discard)
        else:
            self.game_over = True
            self.get_winner()
            print('game over')

    def get_matchables(self, lst):
        return list(filter(lambda z: z['count'] >= self.match_min_length, map(lambda y: { 'card': y, 'count': len(list(filter(lambda x: x['card'] == y, lst ))) }, self.suites)))
    
    def card_matches(self, lst):
        matchables = self.get_matchables(lst)
        return [list(filter(lambda x: n['card'] == x['card'], lst)) for n in matchables]
    
    def card_runs(self, lst):
        suite_groups = [list(filter(lambda x: n == x['suite'], lst)) for n in self.suites]
        eligible_suite_groups = list(filter(lambda x: len(x) >= self.run_min_length, suite_groups))
        sorted_esgs = [list(sorted(n, key=lambda x: x['card'])) for n in eligible_suite_groups]
        runs = []
        for group in sorted_esgs:
            run = []
            for n in group:
                if len(run) == 0 or run[len(run) - 1]['card'] == n['card'] - 1:
                    run.append(n)
                elif len(run) < 3:
                    run = []
            if len(run) >= 3:
                runs.append(run)
        return runs
    
    def get_options(self, include_hand=True, include_pile=False):
        option_list = []
        if include_pile:
            pile_matches = self.card_matches(self.discard_pile)
            pile_runs = self.card_runs(self.discard_pile)
            option_list.append(pile_matches)
            option_list.append(pile_runs)
        if include_hand:
            hand_matches = self.card_matches(self.get_current_player()['hand'])
            hand_runs = self.card_runs(self.get_current_player()['hand'])
            option_list.append(hand_matches)
            option_list.append(hand_runs)
        if include_pile and include_hand:
            hand_pile_combo = [n for n in self.discard_pile]
            hand_pile_combo.extend(self.get_current_player()['hand'])
            combo_matches = self.card_matches(hand_pile_combo)
            combo_runs = self.card_runs(hand_pile_combo)
            option_list.append(combo_matches)
            option_list.append(combo_runs)
        return option_list
    
    def get_set_options(self, include_hand=True, include_pile=False):
        option_list = self.get_options(include_hand=include_hand, include_pile=include_pile)
        valid_match_matrix = list(filter(lambda x: len(x) > 0, option_list))
        match_manifest = []
        full_list = []
        if len(valid_match_matrix) > 0:
            for entry in valid_match_matrix:
                for n in entry:
                    point_sum = sum(list(map(lambda x: x['points'], n)))
                    match_manifest.append({ 'cards': n, 'point_totals': point_sum })
                    full_list.extend(n)
        return { 'options': list(reversed(list(sorted(match_manifest, key=lambda x: x['point_totals'])))), 'unique_options': self.unique_card_list(full_list) }
    
    def get_used_cards(self):
        used_cards = []
        for n in self.sets:
            cards_in_set = map(lambda x: { 'card': x['card']['card'], 'suite': x['card']['suite'] }, n)
            used_cards.extend(cards_in_set)
        return used_cards

    def get_existing_set_opportunitie(self, include_pile=False):
        match_sets = list(filter(lambda x: x[0]['card']['card'] == x[1]['card']['card'], self.sets))
        match_opportunities = []
        combo_list = [n for n in self.get_current_player()['hand']]
        if include_pile:
            combo_list.extend(self.discard_pile)
        for n in match_sets:
            match_opp = list(filter(lambda x: x['card'] == n[0]['card']['card'], combo_list))
            if len(match_opp) > 0:
                match_opportunities.extend(map(lambda x: { 'card': x, 'set': n[0]['index'] } , match_opp))
        # print('match opportunities')
        # print(match_opportunities)
        
        run_sets = list(filter(lambda x: x[0]['card']['suite'] == x[1]['card']['suite'], self.sets))
        # print('run sets')
        # print(run_sets)
        run_opportunities = []
        for n in run_sets:
            first_in_run = n[0]
            last_in_run = n[-1]
            values_before_first = list(reversed(list(filter(lambda x: x < first_in_run['card']['card'], self.suites))))
            values_after_first = list(filter(lambda x: x > last_in_run['card']['card'], self.suites))
            run_opp = []
            for vb in values_before_first:
                filtered_run = list(filter(lambda x: x['card'] == vb and n[0]['card']['suite'] == x['suite'], combo_list))
                if len(filtered_run) > 0:
                    run_opp.extend(filtered_run)
                else:
                    break
            
            for va in values_after_first:
                filtered_run = list(filter(lambda x: x['card'] == va and n[0]['card']['suite'] == x['suite'], combo_list))
                if len(filtered_run) > 0:
                    run_opp.extend(filtered_run)
                else:
                    break
            if len(run_opp) > 0:
                run_opportunities.extend(map(lambda x: { 'card': x, 'set': n[0]['index'] } , run_opp))
        # iterate forward and backward to check for run additions
        opportunities = []
        opportunities.extend(match_opportunities)
        opportunities.extend(run_opportunities)
        cards_in_opp = list(map(lambda x: x['card'], opportunities))
        return { 'opps': opportunities, 'uniqe_opps': self.unique_card_list(cards_in_opp) }

    def add_set(self, player, cards):
        cards_for_set = []
        for n in cards:
            card_in_hand = self.find_card(n, self.get_current_player()['hand'])
            if card_in_hand:
                removed_hand_card = self.get_current_player()['hand'].pop(card_in_hand['index'])
                cards_for_set.append(removed_hand_card)
            # else:
            #     card_in_pile = self.find_card(n, self.discard_pile)
            #     if card_in_pile:
            #         removed_pile_card = self.discard_pile.pop(card_in_hand['index'])
            #         cards_for_set.append(removed_pile_card)
        if len(cards_for_set) >= self.match_min_length:
            set_index = len(self.sets)
            self.sets.append(list(map(lambda x: { 'card': x, 'player': player['name'], 'index': set_index } ,cards_for_set)))
    
    def add_card_to_set(self, card, set_index):
        if self.can_add_to_set():
            card_to_add = card
            card_in_hand = self.find_card(card_to_add, self.get_current_player()['hand'])
            if card_in_hand:
                removed_hand_card = self.get_current_player()['hand'].pop(card_in_hand['index'])
                self.sets[set_index].append({'card': removed_hand_card, 'player': self.get_current_player()['name'], 'index': set_index})

    def get_not_seen_cards(self):
        visible_cards = [n for n in self.discard_pile]
        cards_in_sets = []
        for n in self.sets:
            card_in_set = [m['card'] for m in n]
            cards_in_sets.extend(card_in_set)
        # print('cards in sets')
        # print(cards_in_sets)
        visible_cards.extend(cards_in_sets)
        visible_cards.extend(self.get_current_player()['hand'])
        self.seen_cards.extend(visible_cards)
        self.seen_cards = self.unique_card_list(self.seen_cards)
        visible_cards = self.unique_card_list(visible_cards)
        seen_cards_from_template = list(map(lambda x: { 'card': x, 'seen': len(list(filter(lambda y: y['card'] == x['card'] and y['suite'] == x['suite'], self.seen_cards))) > 0, 'seen_now': len(list(filter(lambda y: y['card'] == x['card'] and y['suite'] == x['suite'], visible_cards))) > 0 }, self.deck_template))
        # print('seen cards from template')
        # print(seen_cards_from_template)
        cards_currently_missing = list(filter(lambda x: x['seen'] and not x['seen_now'], seen_cards_from_template))
        cards_not_yet_seen = list(filter(lambda x: not x['seen'] and not x['seen_now'], seen_cards_from_template))
        # print('cards currntly missing')
        # print(cards_currently_missing)
        cards_that_disapeared = list(map(lambda x: x['card'], cards_currently_missing))
        cards_never_seen_by_player = list(map(lambda x: x['card'], cards_not_yet_seen))
        return { 'taken': cards_that_disapeared, 'never_seen': cards_never_seen_by_player }
    
    def draw_from_discard_pile(self, target_cards):
        discard_pile_with_indexes = []
        for i, n in enumerate(self.discard_pile):
            discard_pile_with_indexes.append({ 'card': n['card'], 'suite': n['suite'], 'index': i })
        filtered_indexed_discard_matches = list(filter(None, [self.find_card(n, target_cards) for n in discard_pile_with_indexes]))
        sorted_discard_matches = list(sorted(list(map(lambda x: x['index'], filtered_indexed_discard_matches))))

        first_card_pulled = None
        if len(sorted_discard_matches) > 0:
            cards_to_pickup = list(reversed(list(range(sorted_discard_matches[0], len(self.discard_pile)))))
            for i, n in enumerate(cards_to_pickup):
                pulled_card = self.discard_pile.pop(n)
                if i == 0:
                    first_card_pulled = pulled_card
                self.get_current_player()['hand'].append(pulled_card)
        return first_card_pulled
