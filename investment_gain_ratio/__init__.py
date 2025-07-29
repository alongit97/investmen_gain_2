from otree.api import *
import json
import pandas as pd
import random
import csv
import os
import ast
from docx import Document

c = cu
doc = ''

def custom_export(players):
    # header row
    yield ['participant_code', 'game_settings', 'estimate_A', 'estimate_B', 'chosen_market', 'shuffle_seed_A', 'shuffle_seed_B',  'bonus']
    for p in players:
        yield [
            p.participant.code,
            p.game_settings,
            p.estimate_A,
            p.estimate_B,
            p.chosen_market,
            p.shuffle_seed_A,
            p.shuffle_seed_B,
            p.bonus
        ]      

class C(BaseConstants):
    NAME_IN_URL = 'investment_gain_ratio'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    NUM_PAIRS = 36
    STARTING_MONEY = 120

class Subsession(BaseSubsession):
    pass

def creating_session(subsession: 'Subsession'):
    session = subsession.session
    file_path = session.config['file_name']
    doc = Document(file_path)

    tables = doc.tables
    if not tables:
        raise ValueError("The DOCX file contains no tables.")

    # Use the first (and only) wide table
    table = tables[0]

    pairs_A = []
    pairs_B = []

    for row in table.rows[1:]:  # skip header row
        cells = row.cells
        if len(cells) < 5:
            continue  # not enough data in this row

        def safe_int(text):
            text = text.strip()
            return int(text) if text.isdigit() else None

        a1 = safe_int(cells[0].text)
        a2 = safe_int(cells[1].text)
        b1 = safe_int(cells[3].text)
        b2 = safe_int(cells[4].text)

        if None not in (a1, a2, b1, b2):
            pairs_A.append((a1, a2))
            pairs_B.append((b1, b2))

    if not pairs_A or not pairs_B:
        raise ValueError("Failed to extract valid numeric pairs from the table.")

    # Store full sets in the session object
    session.full_pairs_A = pairs_A
    session.full_pairs_B = pairs_B

    for player in subsession.get_players():
        player.set_random_pairs(session.full_pairs_A, session.full_pairs_B)

class Group(BaseGroup):
    pass

class Player(BasePlayer):

    game_settings = models.StringField()
    shuffle_seed_A = models.IntegerField(default=0)
    shuffle_seed_B = models.IntegerField(default=0)
    pairs_A_all = models.LongStringField()
    pairs_B_all = models.LongStringField()

    estimate_A = models.IntegerField(
    choices=[
        [1, "large gain"],
        [2, "medium gain"],
        [3, "small gain"],
        [4, "hardly a difference"],
        [5, "small lose"],
        [6, "medium lose"],
        [7, "large lose"]
    ]
    )
    estimate_B = models.IntegerField(
    choices=[
        [1, "large gain"],
        [2, "medium gain"],
        [3, "small gain"],
        [4, "hardly a difference"],
        [5, "small lose"],
        [6, "medium lose"],
        [7, "large lose"]
    ]
    )
   
    chosen_market = models.IntegerField(choices=[[1, 'Market 1'], [2, 'Market 2']], default = 0)
    bonus = models.CurrencyField(default=0)
    random_gain = models.CurrencyField(default=0)
    random_investment = models.CurrencyField(default=0)

    awareness_answer = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    status = models.StringField(default = 'empty')
    attention1_q1 = models.StringField(default="" ,label="What is the sum of one and three? (write down your answer in letters)")
    attention1_q2 = models.StringField(default="" ,label="What word would you get if you combine the first and last letters of the sentence 'Anyone can do that'.")

    num_pairs = models.IntegerField(initial=12, verbose_name="Number of card pairs to show per set(between 1 and 12)", max = 12, min = 1)
    card_time = models.IntegerField(initial=4000, verbose_name="Time for each card to be on screen(in milliseconds)", min = 1)

    def set_random_pairs(self, full_pairs_A, full_pairs_B):
        self.shuffle_seed_A = random.randint(1, 1_000_000)
        self.shuffle_seed_B = random.randint(1, 1_000_000)

        rnd_A = random.Random(self.shuffle_seed_A)
        rnd_B = random.Random(self.shuffle_seed_B)

        pairs_A = full_pairs_A[:]
        rnd_A.shuffle(pairs_A)

        pairs_B = full_pairs_B[:]
        rnd_B.shuffle(pairs_B)

        self.pairs_A_all = json.dumps(pairs_A)
        self.pairs_B_all = json.dumps(pairs_B)

    # def restore_pairs(self, full_pairs, seed):
    #     rnd = random.Random(seed)
    #     pairs_A = full_pairs[:]
    #     rnd.shuffle(pairs_A)
    
    #     pairs_B = [(b, a) for (a, b) in pairs_A]
    #     rnd.shuffle(pairs_B)

    #     print(pairs_A) 
    #     print(pairs_B)

class ClientSettingsPage(Page):
    form_model = 'player'
    form_fields = [
        'num_pairs',
        'card_time',
    ]

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'current_num_pairs': player.num_pairs,
            'current_card_time': player.card_time,

        }
class PreTestInstructions(Page):
    form_model = 'player'
    form_fields = ['error_count']

    @staticmethod
    def vars_for_template(player: Player):
        if player.status == 'empty':
            player.status = 'in progress'
        return {}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Set game_settings from session config
        player.game_settings = player.session.config.get('display_name', "")

        # Set disqualification flag
        if player.error_count == 100:
            player.participant.vars['is_disqualified'] = True
            player.status = 'disagreed'

class Instructions(Page):
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)

class AuthenticationQuestion(Page):
    form_model = 'player'
    form_fields = ['attention1_q1', 'attention1_q2']

    @staticmethod
    def error_message(player, values):
        q1_correct = values['attention1_q1'].strip().lower() == 'four'
        q2_correct = values['attention1_q2'].strip().lower() == 'at'

        if q1_correct and q2_correct:
            return  # All good

        # Check if already failed once
        if player.participant.vars.get('attention_check_1_failed_once'):
            # Second failure: disqualify and allow to move forward silently
            player.error_count = 200
            player.participant.vars['is_disqualified'] = True
            return  # No error messages, move on
        else:
            # First failure: flag as failed and show specific errors
            player.participant.vars['attention_check_1_failed_once'] = True
            errors = {}
            if not q1_correct:
                errors['attention1_q1'] = "This is not the correct answer."
            if not q2_correct:
                errors['attention1_q2'] = "This is not the correct answer."
            return errors

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.error_count == 200:
            player.status = 'failed authentication'

class BeforePartA(Page):
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)

class BeforePartB(Page):
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)    

class ShowCardsA(Page):
    template_name = 'investment_gain_ratio/ShowCardsA.html'
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)

    @staticmethod
    def vars_for_template(player: Player):
        count = player.participant.vars.get('show_investment_count', 0)
        all_pairs = json.loads(player.pairs_A_all)
        segment = all_pairs[count*12:(count+1)*12]
        player.participant.vars['current_pairs_A'] = segment
        return {'pairs_A': segment}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['show_investment_count'] = player.participant.vars.get('show_investment_count', 0) + 1

class AttentionCheckA(Page):
    form_model = 'player'
    form_fields = ['awareness_answer']
    
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)

    @staticmethod
    def vars_for_template(player: Player):
        pairs_A = player.participant.vars.get('current_pairs_A', [])
        correct_answer = 1 if pairs_A[-1][0] > 95 else 2 if pairs_A[-1][0] == 95 else 3
        # Store the correct answer in a single variable for the last attention check
        player.participant.vars['correct_answer_last_attention_check'] = correct_answer
        return {'correct_answer': correct_answer}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pairs_A = player.participant.vars.get('current_pairs_A', [])
        correct_answer = 1 if pairs_A[-1][0] > 95 else 2 if pairs_A[-1][0] == 95 else 3
        if player.awareness_answer != correct_answer:
            player.error_count += 1
        if player.error_count > 1:
            player.participant.vars['is_disqualified'] = True
            player.status = "wrong answers"

class EstimationQuestionA(Page):
    form_model = 'player'
    form_fields = ['estimate_A']
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)

class ShowCardsB(Page):
    template_name = 'investment_gain_ratio/ShowCardsB.html'
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)

    @staticmethod
    def vars_for_template(player: Player):
        count = player.participant.vars.get('reverse_show_profit_count', 0)
        all_pairs = json.loads(player.pairs_B_all)
        segment = all_pairs[count*12:(count+1)*12]
        player.participant.vars['current_pairs_B'] = segment
        return {'pairs_B': segment}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['reverse_show_profit_count'] = player.participant.vars.get('reverse_show_profit_count', 0) + 1

class AttentionCheckB(Page):
    form_model = 'player'
    form_fields = ['awareness_answer']
    
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)

    @staticmethod
    def vars_for_template(player: Player):
        pairs_B = player.participant.vars.get('current_pairs_B', [])
        correct_answer = 1 if pairs_B[-1][0] > 95 else 2 if pairs_B[-1][0] == 95 else 3
        # Store the correct answer in the same variable for the last attention check
        player.participant.vars['correct_answer_last_attention_check'] = correct_answer
        return {'correct_answer': correct_answer}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pairs_B = player.participant.vars.get('current_pairs_B', [])
        correct_answer = 1 if pairs_B[-1][0] > 95 else 2 if pairs_B[-1][0] == 95 else 3
        if player.awareness_answer != correct_answer:
            player.error_count += 1
        if player.error_count > 1:
            player.participant.vars['is_disqualified'] = True
            player.status = "wrong answers"

class EstimationQuestionB(Page):
    form_model = 'player'
    form_fields = ['estimate_B']
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)

class ChooseSet(Page):
    form_model = 'player'
    form_fields = ['chosen_market']
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)

class BonusCalculation(Page):
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):

        # Bonus logic
        all_pairs = json.loads(player.pairs_A_all) if player.chosen_market == 1 else json.loads(player.pairs_B_all)
        selected_pair = random.choice(all_pairs)
        player.random_investment = selected_pair[0]
        player.random_gain = selected_pair[1]
        player.bonus = player.random_gain - player.random_investment
        player.payoff = C.STARTING_MONEY + player.bonus


class FinalPage(Page):
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)


class WarningPage(Page):
    #timeout_seconds = 5  # Show this page for 5 seconds only

    def is_displayed(player: Player):
        return player.error_count == 1 and not player.participant.vars.get('has_seen_warning', False)

    @staticmethod
    def vars_for_template(player: Player):
        correct_answer = player.participant.vars.get('correct_answer_last_attention_check', None)
        return {
            'correct_answer': correct_answer,
            'message': 'The correct answer was: '
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['has_seen_warning'] = True     

class Disqualified(Page):
    def is_displayed(player: Player):
        return player.participant.vars.get('is_disqualified', False)

    @staticmethod
    def vars_for_template(player: Player):
        return {'message': 'You have been disqualified from the experiment due to too many incorrect answers.'}

page_sequence = [
    ClientSettingsPage,
    PreTestInstructions,
    AuthenticationQuestion,
    Instructions,
    BeforePartA,
    ShowCardsA,
    AttentionCheckA,
    WarningPage,
    ShowCardsA,
    AttentionCheckA,
    WarningPage,
    ShowCardsA,
    EstimationQuestionA,
    BeforePartB,
    ShowCardsB,
    AttentionCheckB,
    WarningPage,
    ShowCardsB,
    AttentionCheckB,
    WarningPage,
    ShowCardsB,
    EstimationQuestionB,
    ChooseSet,
    BonusCalculation,
    FinalPage,
    Disqualified
]