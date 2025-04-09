from otree.api import *
import json
import pandas as pd
import random

c = cu
doc = ''

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
    file_path = "Items_to_Present_Inv-Vee_3_Pres-Inc-then-Inv_Ask-FIRST-Inc-per-Unit-Inv.xlsx"
    df = pd.read_excel(file_path, usecols="I,K", skiprows=1, nrows=36, header=None)
    df.columns = ['Investment', 'Gain']
    session.full_pairs = list(zip(df['Investment'], df['Gain']))

    for player in subsession.get_players():
        player.set_random_pairs(session.full_pairs)

class Group(BaseGroup):
    pass

class Player(BasePlayer):
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
   
    chosen_market = models.IntegerField(choices=[[1, 'Market 1'], [2, 'Market 2']])
    bonus = models.CurrencyField()
    random_gain = models.CurrencyField()
    random_investment = models.CurrencyField()

    awareness_answer = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    attention1_q1 = models.StringField(default="" ,label="What is the sum of one and three? (write down your answer in letters)")
    attention1_q2 = models.StringField(default="" ,label="What word would you get if you combine the first and last letters of the sentence 'Anyone can do that'.")

    num_pairs = models.IntegerField(initial=12, verbose_name="Number of card pairs to show per set(between 1 and 12)", max = 12, min = 1)
    response_time = models.IntegerField(initial=5000, verbose_name="Time until next card apear by itself (in milliseconds)", max = 15000, min = 1000)


    def set_random_pairs(self, full_pairs):
        pairs_A = full_pairs[:]
        random.shuffle(pairs_A)
        pairs_B = [(b, a) for (a, b) in pairs_A]
        random.shuffle(pairs_B)
        self.pairs_A_all = json.dumps(pairs_A)
        self.pairs_B_all = json.dumps(pairs_B)

class ClientSettingsPage(Page):
    form_model = 'player'
    form_fields = ['num_pairs', 'response_time']

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'current_num_pairs': player.num_pairs,
            'current_response_time': player.response_time
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        print("ClientSettingsPage - num_pairs:", player.num_pairs)
        print("ClientSettingsPage - response_time:", player.response_time)



class Instructions(Page):
    pass

class AttentionCheck1(Page):
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

class BeforePartA(Page):
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)

class BeforePartB(Page):
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)    

class ShowInvestment(Page):
    template_name = 'investment_experiment_demo/ShowInvestment.html'
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

class AttentionCheck2(Page):
    form_model = 'player'
    form_fields = ['awareness_answer']
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)

    @staticmethod
    def vars_for_template(player: Player):
        pairs_A = player.participant.vars.get('current_pairs_A', [])
        final_investment = pairs_A[-1][0] if pairs_A else None
        return {'final_investment': final_investment}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pairs_A = player.participant.vars.get('current_pairs_A', [])
        correct_answer = pairs_A[-1][0] if pairs_A else None
        if player.awareness_answer != correct_answer:
            player.error_count += 1
        if player.error_count > 1:
            player.participant.vars['is_disqualified'] = True

class EstimationQuestionA(Page):
    form_model = 'player'
    form_fields = ['estimate_A']
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)

class ReverseShowProfit(Page):
    template_name = 'investment_experiment_demo/ReverseShowProfit.html'
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
        final_gain = pairs_B[-1][0] if pairs_B else None
        return {'final_gain': final_gain}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pairs_B = player.participant.vars.get('current_pairs_B', [])
        correct_answer = pairs_B[-1][0] if pairs_B else None
        if player.awareness_answer != correct_answer:
            player.error_count += 1
        if player.error_count > 1:
            player.participant.vars['is_disqualified'] = True

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
        all_pairs = json.loads(player.pairs_A_all)
        selected_pair = random.choice(all_pairs)
        player.random_investment = selected_pair[0]
        player.random_gain = selected_pair[1]
        player.bonus = player.random_gain - player.random_investment
        player.payoff = C.STARTING_MONEY + player.bonus

class FinalPage(Page):
    def is_displayed(player: Player):
        return not player.participant.vars.get('is_disqualified', False)

class Disqualified(Page):
    def is_displayed(player: Player):
        return player.participant.vars.get('is_disqualified', False)

    @staticmethod
    def vars_for_template(player: Player):
        return {'message': 'You have been disqualified from the experiment due to too many incorrect answers.'}

page_sequence = [
    ClientSettingsPage,
    Instructions,
    AttentionCheck1,
    BeforePartA,
    ShowInvestment,
    AttentionCheck2,
    ShowInvestment,
    AttentionCheck2,
    ShowInvestment,
    #AttentionCheck2,
    EstimationQuestionA,
    BeforePartB,
    ReverseShowProfit,
    AttentionCheck3,
    ReverseShowProfit,
    AttentionCheck3,
    ReverseShowProfit,
    #AttentionCheck3,
    EstimationQuestionB,
    ChooseSet,
    BonusCalculation,
    FinalPage,
    Disqualified
]
