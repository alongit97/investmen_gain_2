from otree.api import *
import json
import pandas as pd
import random
import csv
import os
import ast

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
    NAME_IN_URL = 'investment_experiment_demo'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    NUM_PAIRS = 36
    STARTING_MONEY = 50

class Subsession(BaseSubsession):
    pass

def creating_session(subsession: 'Subsession'):
    session = subsession.session
    file_path = session.config['file_name']
    df = pd.read_excel(file_path, usecols="I,K", skiprows=1, nrows=36, header=None)
    df.columns = ['Investment', 'Gain']
    session.full_pairs = list(zip(df['Investment'], df['Gain']))

    for player in subsession.get_players():
        player.set_random_pairs(session.full_pairs)

        #player.restore_pairs(session.full_pairs, player.shuffle_seed)

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
        [1, "Very unlikely"],
        [2, "Unlikely"],
        [3, "Neutral"],
        [4, "Likely"],
        [5, "Very likely"]
    ]
    )
    estimate_B = models.IntegerField(
    choices=[
        [1, "Very unlikely"],
        [2, "Unlikely"],
        [3, "Neutral"],
        [4, "Likely"],
        [5, "Very likely"]
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
    #response_time = models.IntegerField(initial=5000, verbose_name="Time until next card apear by itself (in milliseconds)", max = 15000, min = 0)
    first_card_time = models.IntegerField(initial=2000, verbose_name="Time for first card to apear by itself(in milliseconds)", min = 1)
    second_card_time = models.IntegerField(initial=2500, verbose_name="Time for both cards to apear together(in milliseconds)", min = 1)
    transition_time = models.IntegerField(initial=1, verbose_name="Time for gray card to apear (in milliseconds)", min = 1)

    def set_random_pairs(self, full_pairs):
        # Assign a random seed if it's not already set
        self.shuffle_seed_A = random.randint(1, 1_000_000)
        self.shuffle_seed_B = random.randint(1, 1_000_000)

        rnd_A = random.Random(self.shuffle_seed_A)
        rnd_B = random.Random(self.shuffle_seed_B)

        # Create shuffled pairs_A
        pairs_A = full_pairs[:]
        rnd_A.shuffle(pairs_A)
        
        pairs_B = full_pairs[:]
        rnd_B.shuffle(pairs_B)
        # Create pairs_B and shuffle them as well
        #pairs_B = [(b, a) for (a, b) in pairs_A]

        # Save to fields
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
        #'response_time',
        'first_card_time',
        'second_card_time',
        'transition_time'
    ]

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'current_num_pairs': player.num_pairs,
            #'current_response_time': player.response_time,
            'current_first_card_time': player.first_card_time,
            'current_second_card_time': player.second_card_time,
            'current_transition_time': player.transition_time
        }


class Instructions(Page):
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
    template_name = 'investment_experiment_demo/ShowCardsA.html'
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
        correct_answer = 1 if pairs_A[-1][0] > pairs_A[-1][1] else 2 if pairs_A[-1][0] == pairs_A[-1][1] else 3
        # Store the correct answer in a single variable for the last attention check
        player.participant.vars['correct_answer_last_attention_check'] = correct_answer
        return {'correct_answer': correct_answer}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pairs_A = player.participant.vars.get('current_pairs_A', [])
        correct_answer = final_investment = 1 if pairs_A[-1][0] > pairs_A[-1][1] else 2 if pairs_A[-1][0] == pairs_A[-1][1] else 3
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
    template_name = 'investment_experiment_demo/ShowCardsB.html'
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

class AttentionCheck3(Page):
    form_model = 'player'
    form_fields = ['awareness_answer']
    
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)

    @staticmethod
    def vars_for_template(player: Player):
        pairs_B = player.participant.vars.get('current_pairs_B', [])
        correct_answer = 1 if pairs_B[-1][0] > pairs_B[-1][1] else 2 if pairs_B[-1][0] == pairs_B[-1][1] else 3
        # Store the correct answer in the same variable for the last attention check
        player.participant.vars['correct_answer_last_attention_check'] = correct_answer
        return {'correct_answer': correct_answer}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pairs_B = player.participant.vars.get('current_pairs_B', [])
        correct_answer = 1 if pairs_B[-1][0] > pairs_B[-1][1] else 2 if pairs_B[-1][0] == pairs_B[-1][1] else 3
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
        all_pairs = json.loads(player.pairs_A_all)
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
    Instructions,
    AuthenticationQuestion,
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
    AttentionCheck3,
    WarningPage,
    ShowCardsB,
    AttentionCheck3,
    WarningPage,
    ShowCardsB,
    EstimationQuestionB,
    ChooseSet,
    BonusCalculation,
    FinalPage,
    Disqualified
]

#export_data = custom_export