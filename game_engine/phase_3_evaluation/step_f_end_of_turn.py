import random
from game_engine.phase_3_evaluation import FINAL_ROUND
from models.player import Player
from models.strategy import RubyStrat

RUBY_TO_VICTORY_POINTS_PRICE = 2
RUBY_TO_DROPLET_PRICE = 2
RUBY_TO_FLASK_PRICE = 2


def spend_rubies(player: Player, current_round: int) -> None:
    """Buys a droplet advance, flask refill, or victory points depending on the player's ruby strategy and round."""
    # Buy victory points for final round instead of a droplet advance or flask refill
    if current_round == FINAL_ROUND:
        rubies_to_trade = player.ruby - (player.ruby % RUBY_TO_VICTORY_POINTS_PRICE)
        player.victory_points += (player.ruby // RUBY_TO_VICTORY_POINTS_PRICE)
        player.ruby -= rubies_to_trade

        return

    if player.strategy_profile.ruby == RubyStrat.RANDOM:
        ruby_strat = random.choice([RubyStrat.SAVE, RubyStrat.DROPLET, RubyStrat.FLASK, RubyStrat.BALANCED])
    else:
        ruby_strat = player.strategy_profile.ruby

    match ruby_strat:

        case RubyStrat.SAVE:
            # Buy neither droplet advance nor flask refill
            return

        case RubyStrat.DROPLET:
            # Buy as many droplet advances as you can afford
            droplet_moves = player.ruby // RUBY_TO_DROPLET_PRICE
            player.droplet += droplet_moves
            player.ruby -= (droplet_moves * RUBY_TO_DROPLET_PRICE)
            return

        case RubyStrat.FLASK:
            # Buy a flask refill
            if not player.flask_full and player.ruby >= RUBY_TO_FLASK_PRICE:
                player.flask_full = True
                player.ruby -= RUBY_TO_FLASK_PRICE
            return

        case RubyStrat.BALANCED:
            # Buy both flask refills and droplet advances, prioritizing the flask on even rounds
            if current_round % 2 == 0:
                if not player.flask_full and player.ruby >= RUBY_TO_FLASK_PRICE:
                    player.flask_full = True
                    player.ruby -= RUBY_TO_FLASK_PRICE

            # Buy one droplet advance
            if player.ruby >= RUBY_TO_DROPLET_PRICE:
                player.droplet += 1
                player.ruby -= RUBY_TO_DROPLET_PRICE

            return

        case _:
            return


def execute_end_of_turn_actions(player: Player, current_round: int) -> None:
    spend_rubies(player, current_round)
    if player.current_space > player.farthest_space_reached:
        player.farthest_space_reached = player.current_space
    if current_round != FINAL_ROUND:
        player.current_space = 0