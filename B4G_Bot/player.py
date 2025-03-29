from skeleton.actions import CallAction, CheckAction, FoldAction, RaiseAction
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
from skeleton.states import (
    BIG_BLIND,
    NUM_ROUNDS,
    SMALL_BLIND,
    STARTING_STACK,
    GameState,
    RoundState,
    TerminalState,
)

from utils import preflop_eval, postflop_eval, get_mdf

class Player(Bot):
    """
    A pokerbot.
    """

    def __init__(self):
        pass

    def handle_new_round(self, game_state, round_state, active):
        pass

    def handle_round_over(self, game_state, terminal_state, active):
        pass

    def get_action(self, game_state, round_state, active):
        legal_actions = round_state.legal_actions()
        street = round_state.street
        my_cards = round_state.hands[active]
        board_cards = round_state.deck[:street]
        my_pip = round_state.pips[active]
        opp_pip = round_state.pips[1 - active]
        my_stack = round_state.stacks[active]
        opp_stack = round_state.stacks[1 - active]
        continue_cost = opp_pip - my_pip
        my_contribution = STARTING_STACK - my_stack
        opp_contribution = STARTING_STACK - opp_stack
        pot_size = my_contribution + opp_contribution

        can_raise = RaiseAction in legal_actions
        can_call = CallAction in legal_actions
        can_check = CheckAction in legal_actions
        can_fold = FoldAction in legal_actions

        if can_raise:
            min_raise, max_raise = round_state.raise_bounds()
            min_cost = min_raise - my_pip
            max_cost = max_raise - my_pip

        #####################################
        # Pre Flop
        ######################################
        if street == 0:
            preflop_strength = preflop_eval(my_cards)
            # Big Blind
            if bool(active):  
                OPEN_THRESHOLD = 32
                CALL_THRESHOLD = 24
                RERAISE_THRESHOLD = 50
            # Small Blind
            else:  
                OPEN_THRESHOLD = 26
                CALL_THRESHOLD = 20
                RERAISE_THRESHOLD = 45
            
            # Opponent Raises
            if continue_cost == 0:
                if preflop_strength >= RERAISE_THRESHOLD and can_raise:
                    return RaiseAction(min_raise)
                elif preflop_strength >= CALL_THRESHOLD and can_call:
                    return CallAction()
                else:
                    return FoldAction()
            else:
                if preflop_strength >= OPEN_THRESHOLD and can_raise:
                    return RaiseAction(min_raise)
                elif preflop_strength >= CALL_THRESHOLD and can_call:
                    return CallAction()
                else:   
                    return FoldAction()


        #####################################
        # Post Flop / Turn
        ######################################
        elif street in [2, 4]:
            postflop_strength = postflop_eval(my_cards, board_cards)

            # raises/calls
            if continue_cost > 0:
                mdf = get_mdf(pot_size, continue_cost)
                fold_cutoff = (1.0 - mdf) * 100

                if postflop_strength < fold_cutoff:
                    return FoldAction() if can_fold else (CallAction() if can_call else CheckAction())
                else:
                    if can_raise and postflop_strength > 85:
                        return RaiseAction(max(min_raise, pot_size // 2))
                    else:
                        return CallAction() if can_call else CheckAction()
            else:
                threshold = 55 if street == 2 else 48
                if postflop_strength > threshold and can_raise:
                    return RaiseAction(max(min_raise, pot_size // 3))
                else:
                    return CheckAction() if can_check else (CallAction() if can_call else FoldAction())

        return CheckAction() if can_check else FoldAction()


if __name__ == '__main__':
    run_bot(Player(), parse_args())
