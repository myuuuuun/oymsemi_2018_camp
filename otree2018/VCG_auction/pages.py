from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants


class Introduction(Page):
    def is_displayed(self):
        return self.round_number == 1


class Bid(Page):
    form_model = "player"
    form_fields = ["a_bid_amount", "b_bid_amount", "ab_bid_amount"]

    def vars_for_template(self):
        return {
            "endowment": Constants.endowment, 
            }


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        self.group.set_payoffs()


class Results(Page):
    pass


class FinalResults(Page):
    def is_displayed(self):
        return self.subsession.round_number == Constants.num_rounds

    def vars_for_template(self):
        total_payoff = sum([p.payoff for p in self.player.in_all_rounds()])
        
        return {
            "player_in_all_rounds": self.player.in_all_rounds(),
            "total_payoff": total_payoff,
        }


page_sequence = [
    Introduction,
    Bid,
    ResultsWaitPage,
    Results, 
    FinalResults]
