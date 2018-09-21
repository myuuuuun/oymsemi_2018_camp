from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import numpy as np
import random


doc = """
In this VCG auction, 3 players bid for 2 objects with private values.
"""


class Constants(BaseConstants):
    name_in_url = 'VCG_auction'
    players_per_group = 8
    num_rounds = 10

    num_other_players = players_per_group - 1
    instructions_template = 'VCG_auction/Instructions.html'
    endowment = c(200)
    half_endowment = c(100)

    seed = 20180921


class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
            self.session.vars["random_state"] = np.random.RandomState(Constants.seed)
        
        for p in self.get_players():
            p.a_private_value = self.session.vars["random_state"].randint(0, Constants.half_endowment)
            p.b_private_value = self.session.vars["random_state"].randint(0, Constants.half_endowment)
            ab_sum = p.a_private_value + p.b_private_value
            p.ab_private_value = ab_sum \
                + self.session.vars["random_state"].randint(0, Constants.endowment-ab_sum)


class Group(BaseGroup):
    @staticmethod
    def get_vcg_valuation(a_bids, b_bids, ab_bids, vcg_allocation):
        if vcg_allocation[0] == vcg_allocation[1]:
            return ab_bids[vcg_allocation[0]]
        else:
            return a_bids[vcg_allocation[0]] + b_bids[vcg_allocation[1]]

    def get_vcg_allocation(self, a_bids, b_bids, ab_bids, skip_player=None):
        n_players = len(a_bids)
        opt_allocations = []
        highest_val = 0
        for a in range(n_players):
            for b in range(n_players):
                if a == skip_player or b == skip_player:
                    pass
                else:
                    if a == b:
                        val = ab_bids[a]
                    else:
                        val = a_bids[a] + b_bids[b]

                    if val == highest_val:
                        opt_allocations.append([a, b])
                    elif val > highest_val:
                        opt_allocations = [[a, b]]
                        highest_val = val

        # if tie, winners are chosen at random
        ind = self.session.vars["random_state"].randint(0, len(opt_allocations))
        return opt_allocations[ind]

    def set_payoffs(self):
        players = self.get_players()
        a_bids  = [p.a_bid_amount for p in players]
        b_bids  = [p.b_bid_amount for p in players]
        ab_bids = [p.ab_bid_amount for p in players]
        
        vcg_allocation = self.get_vcg_allocation(a_bids, b_bids, ab_bids)
        
        a_winner = players[vcg_allocation[0]]
        b_winner = players[vcg_allocation[1]]
        a_winner.is_a_winner = True
        b_winner.is_b_winner = True
        
        for i, p in enumerate(players): 
            p.payoff = Constants.endowment
            p.payment = 0
            
            if p.is_a_winner or p.is_b_winner:
                alt_vcg_allocation = self.get_vcg_allocation(
                    a_bids, b_bids, ab_bids, skip_player=i)
                alt_vcg_total_val = self.get_vcg_valuation(
                    a_bids, b_bids, ab_bids, alt_vcg_allocation)

                p.payment += alt_vcg_total_val

                if p.is_a_winner and p.is_b_winner:
                    p.payoff += p.ab_private_value - p.payment

                elif p.is_a_winner:
                    p.payment -= b_bids[vcg_allocation[1]]
                    p.payoff += p.a_private_value - p.payment
                
                elif p.is_b_winner:
                    p.payment -= a_bids[vcg_allocation[0]]
                    p.payoff += p.b_private_value - p.payment
            

class Player(BasePlayer):
    a_private_value = models.CurrencyField()
    b_private_value = models.CurrencyField()
    ab_private_value = models.CurrencyField()
    payment = models.CurrencyField()

    a_bid_amount  = models.CurrencyField(min=0, max=Constants.endowment)
    b_bid_amount  = models.CurrencyField(min=0, max=Constants.endowment)
    ab_bid_amount = models.CurrencyField(min=0, max=Constants.endowment)

    is_a_winner = models.BooleanField(initial=False)
    is_b_winner = models.BooleanField(initial=False)

