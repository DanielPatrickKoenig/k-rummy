from rg import RummyGame
from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class GameManager():
    INSTANCE = None
    def __init__(self):
        self.game = RummyGame(player_list=["computer", "human"])
        GameManager.INSTANCE = self
    
    def execute_turn(self, data=None):
        self.game.take_turn(lambda: print('Turn Taken'))
    
class CardLayout(BoxLayout):
    def __init__(self, card, card_color=(2.5,2.5,2.5,1), **kwargs):
        super().__init__(*kwargs)
        self.card = card
        self.card_click_handler = None
        button = Button(text=str(card['card'])+" - "+str(card['suite']), background_color=card_color, color=(0,0,0,1))
        self.add_widget(button)

        button.on_release = self.on_card_clicked
        # self.num_label = Label(text=str(card['card']))
        # self.suite_label = Label(text=str(card['suite']))
        # self.add_widget(self.num_label)
        # self.add_widget(self.suite_label)

    def on_card_clicked(self, data=None):
        if self.card_click_handler:
            self.card_click_handler(self.card)

class CardGroupLayout(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(*kwargs)
        self.card_widgets = []
        self.update_size()
        self.size_hint_y = None
        self.size_hint_x = None
        self.card_click_handler = None
    
    def set_cards(self, cards):
        for widget in self.card_widgets:
            self.remove_widget(widget)
        
        self.card_widgets = []
        
        for i, card in enumerate(cards):
            # card_widget = Button(text=str(card["card"])+"-"+str(card["suite"]), pos_hint={}, size_hint_y=None, size_hint_x=None, width=80, height=120, x=i*30, y=300)
            card_widget = CardLayout(card, self.get_card_color(card))
            card_widget.pos_hint = {}
            card_widget.size_hint_y = None
            card_widget.size_hint_x = None
            card_widget.width = 80
            card_widget.height = 120
            card_widget.x = i*80
            card_widget.card_click_handler = self.card_click_handler
            self.add_widget(card_widget)
            self.card_widgets.append(card_widget)

        self.update_size()
    
    def update_size(self):
        self.width = (len(self.card_widgets) * 30) + 100
        self.height = 125
    
    def get_card_color(self, card):
        return (2.5,2.5,2.5,1)

class SetLayout(CardGroupLayout):
    def __init__(self, player, **kwargs):
        super().__init__(*kwargs)
        self.player = player
    
    def get_card_color(self, card):
        return (2.5,2.5,2.5,1) if card['player'] == self.player else (1.5,1.5,1.5,1)

class SetGroupLayout(BoxLayout):
    def __init__(self, player, **kwargs):
        super().__init__(*kwargs)
        self.orientation = 'vertical'
        self.player = player
        self.set_layouts = []
        self.size_hint_x = None
        self.size_hint_y = None
        self.width = 500
        self.height = 500
    
    def set_sets(self, sets):
        for widget in self.set_layouts:
            self.remove_widget(widget)
        
        self.set_layouts = []
        
        for set in sets:
            cards_to_add = list(map(lambda x: { 'card': x['card']['card'], 'suite': x['card']['suite'], 'player': x['player'] }, set))
            cards_for_owner = list(filter(lambda x: x['player'] == self.player, cards_to_add))
            print(cards_for_owner)
            if len(cards_for_owner) > 0:
                set_layout = SetLayout(self.player)
                self.add_widget(set_layout)
                set_layout.set_cards(cards_to_add)
                self.set_layouts.append(set_layout)
    
    def update_size(self):
        super.update_size()
        self.height = 50


class GameLayout(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(*kwargs)
        TestButton = Button(text="hello", pos_hint={}, size_hint_y=None, size_hint_x=None, width=50, height=50, x=100, y=100, on_release=self.turn_action)
        self.add_widget(TestButton)
        self.discard_group = CardGroupLayout()
        self.add_widget(self.discard_group)
        self.discard_group.pos_hint = { 'top': .95 }

        self.hand_group = CardGroupLayout()
        self.add_widget(self.hand_group)
        self.hand_group.pos_hint = { 'top': .85 }

        self.set_group_1 = SetGroupLayout('p0')
        self.add_widget(self.set_group_1)
        self.set_group_1.pos_hint = { 'right': .5 }

        self.set_group_2 = SetGroupLayout('p1')
        self.add_widget(self.set_group_2)
        self.set_group_2.pos_hint = { 'right': .8 }

    
    def turn_action(self, data=None):
        player_type = GameManager.INSTANCE.game.get_current_player()['type']
        
        GameManager.INSTANCE.game.take_turn(lambda: print('turn taken 2'))
        
        self.discard_group.set_cards(GameManager.INSTANCE.game.discard_pile)

        self.hand_group.set_cards(GameManager.INSTANCE.game.players[1]['hand'])
        
        self.set_group_1.set_sets(GameManager.INSTANCE.game.sets)
        self.set_group_2.set_sets(GameManager.INSTANCE.game.sets)

        if player_type == 'human':
            modal = TurnStartModal(self)
            modal.open_modal()

class BaseModal(BoxLayout):
    OPEN_MODALS = []
    def __init__(self, parent, **kwargs):
        super().__init__(*kwargs)
        self.parent_widget = parent
        self.orientation = 'vertical'
        self.create_ui()
    
    def create_ui(self):
        test_label = Label(text='Test Message')
        self.add_widget(test_label)

    def open_modal(self):
        self.parent_widget.add_widget(self)
        for modal in BaseModal.OPEN_MODALS:
            modal.close_modal()
        BaseModal.OPEN_MODALS = []
        BaseModal.OPEN_MODALS.append(self)
        print(BaseModal.OPEN_MODALS)
    
    def close_modal(self):
        self.parent_widget.remove_widget(self)
    
class TurnStartModal(BaseModal):
    def create_ui(self):
        top_box = BoxLayout()

        message_label = Label(text='Do you want to select from the discard pile?')
        top_box.add_widget(message_label)

        bottom_box = BoxLayout()
        yes_button = Button(text='yes')
        no_button = Button(text='no')
        no_button.on_release = self.on_no
        bottom_box.add_widget(yes_button)
        bottom_box.add_widget(no_button)

        self.add_widget(top_box)
        self.add_widget(bottom_box)
    
    def on_no(self, data=None):
        modal = DiscardModal(self.parent)
        modal.open_modal()


    
class DiscardModal(BaseModal):
    def create_ui(self):
        top_box = BoxLayout()

        message_label = Label(text='What card do you want to discard')
        top_box.add_widget(message_label)

        self.add_widget(top_box)

        bottom_box = BoxLayout()

        player_hand = CardGroupLayout()
        player_hand.card_click_handler = self.on_card_selected
        player_hand.set_cards(GameManager.INSTANCE.game.get_current_player()['hand'])
        bottom_box.add_widget(player_hand)

        self.add_widget(bottom_box)

    def on_card_selected(self, card):
        print('card to discard')
        print(card)
        # discard selected card
        # end turn

class RummyApp(App):
    def build(self):
        GameManager()
        return GameLayout()

if __name__ == "__main__":
    RummyApp().run()