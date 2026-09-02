import random
import unittest
from unittest.mock import patch

from config.pot_config import POT_BOARD_SPACES
from game_engine import play_single_round
from game_engine.phase_1_prep import calculate_rat_tails
from game_engine.phase_2_potions import run_potions_phase, use_flask, update_current_space, draw_chip, \
    execute_yellow_special_action, select_chip, has_exploded
from game_engine.phase_3_evaluation import FINAL_ROUND
from game_engine.phase_3_evaluation.step_a_bonus_die import execute_bonus_die_reward
from game_engine.phase_3_evaluation.step_b_chip_actions import execute_black_special_action, \
    execute_green_special_action, execute_purple_special_action
from game_engine.phase_3_evaluation.step_c_rubies import award_ruby
from game_engine.phase_3_evaluation.step_d_points import award_victory_points, should_choose_points_on_explosion
from game_engine.phase_3_evaluation.step_e_buy_chips import execute_buying_phase, finalize_chip_purchase, \
    MONEY_TO_VC_PRICE
from game_engine.phase_3_evaluation.step_f_end_of_turn import spend_rubies
from models.player import Player
from models.strategy import (GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat,
                                 ExplosionProbabilityToleranceStrat, ExplosionRoundStrat, ExplodedStrat, ChipColor)
import game_engine.match_runner


CURRENT_TEST_ROUND_LIMIT = 9


class TestGoldenMasterAuditTracer(unittest.TestCase):

    @unittest.skip
    @patch('random.randint')
    @patch('random.randrange')
    def test_seeded_single_match(self, mock_randrange, mock_randint):
        """Runs a seeded game and prints chronological log for verification."""
        TEST_SEED = 42
        seeded_rng = random.Random(TEST_SEED)

        # Define strategy profiles
        strat_prof_a = GameStrategyProfile(
            colors=(ChipColor.ORANGE, ChipColor.RED),
            value=ValueStrat.HIGHEST_VALUE_PAIR,
            ruby=RubyStrat.DROPLET,
            flask=FlaskStrat.ALWAYS_THREE,
            explosion_prob=ExplosionProbabilityToleranceStrat.NEVER,
            explosion_round=ExplosionRoundStrat.ALWAYS,
            exploded=ExplodedStrat.MONEY
        )

        strat_prof_b = GameStrategyProfile(
            colors=(ChipColor.GREEN, ChipColor.BLUE, ChipColor.YELLOW, ChipColor.BLACK),
            value=ValueStrat.LEAST_DISPARITY,
            ruby=RubyStrat.SAVE,
            flask=FlaskStrat.AT_RISK,
            explosion_prob=ExplosionProbabilityToleranceStrat.LOW,
            explosion_round=ExplosionRoundStrat.MID_LATE,
            exploded=ExplodedStrat.MONEY
        )

        player_a_instance = None
        player_b_instance = None

        # Spy wrapper for player instantiation
        orig_player_init = Player.__init__
        def spy_player_init(instance, *args, **kwargs):
            nonlocal player_a_instance, player_b_instance
            orig_player_init(instance, *args, **kwargs)
            if player_a_instance is None:
                player_a_instance = instance
            elif player_b_instance is None:
                player_b_instance = instance

        def get_current_player(player_ref):
            if player_ref == player_a_instance:
                return "A"
            if player_ref == player_b_instance:
                return "B"
            else:
                return "X"

        # Spy wrappers for critical actions
        orig_calculate_rat_tails = calculate_rat_tails
        def spy_calculate_rat_tails(player_a, player_b):
            orig_calculate_rat_tails(player_a, player_b)
            if player_a.rat_token > 0:
                print(f"Player A rat token set to {player_a.rat_token}.")
            elif player_b.rat_token > 0:
                print(f"Player B rat token set to {player_b.rat_token}.")
            else:
                print("No rat tokens set.")


        orig_play_single_round = play_single_round
        def spy_play_single_round(player_a, player_b, supply_bank, current_round):
            print(f"\n***ROUND {current_round}***")

            orig_play_single_round(player_a, player_b, supply_bank, current_round)

            print(f"\nEND OF ROUND SUMMARY:")
            for player in [player_a, player_b]:
                print(f"Player {get_current_player(player)}:")
                print(f"  Current droplet position: {player.droplet}")
                print(f"  Number of rubies: {player.ruby}")
                if player.flask_full:
                    print("  Flask status: Full")
                else:
                    print("  Flask status: Empty")
                print(f"  Victory points: {player.victory_points}")


        orig_run_potions_phase = run_potions_phase
        def spy_run_potions_phase(player, current_round):
            print(f"Potions phase for player {get_current_player(player)}:")
            orig_run_potions_phase(player, current_round)
            if has_exploded(player):
                print(f"Player {get_current_player(player)} exploded!")
            elif len(player.unplayed_chips) > 0:
                print(f"Player {get_current_player(player)} has chosen to stop pulling chips.")
            else:
                print(f"Player {get_current_player(player)} has played all chips.")


        orig_use_flask = use_flask
        def spy_use_flask(player, drawn_chip):
            print(f" Flask used: ({drawn_chip.color.upper()}-{drawn_chip.value}) returned to bag.")
            orig_use_flask(player, drawn_chip)


        orig_update_current_space = update_current_space
        def spy_update_current_space(player, chip, is_first_draw):
            orig_update_current_space(player, chip, is_first_draw)
            print(f" Space updated to {player.current_space}.")


        orig_draw_chip = draw_chip
        def spy_draw_chip(player):
            drawn_chip = orig_draw_chip(player)
            print(f"  Drew chip ({drawn_chip.color.upper()}-{drawn_chip.value}):", end="")

            return drawn_chip


        orig_execute_yellow_special_action = execute_yellow_special_action
        def spy_execute_yellow_special_action(player):
            if len(player.played_chips) >= 2:
                if player.played_chips[-2].color == ChipColor.WHITE:
                    chip_to_return = player.played_chips[-2]
                    print(f"  Yellow special action: ({chip_to_return.color.upper()}-{chip_to_return.value}) returned "
                          f"to bag.")
            orig_execute_yellow_special_action(player)


        orig_select_chip = select_chip
        def spy_select_chip(player, drawn_chips):
            print("  Blue special action: drawing the following chip(s):")
            for chip in drawn_chips:
                print(f"    ({chip.color.upper()}-{chip.value})")

            selected_chip = orig_select_chip(player, drawn_chips)

            if selected_chip is not None:
                print(f"  Blue special action: chip ({selected_chip.color.upper()}-{selected_chip.value}) selected and "
                      f"played:", end="")
            else:
                print("  Blue special action: no suitable chip found to play.")

            return selected_chip


        orig_execute_bonus_die_reward = execute_bonus_die_reward
        def spy_execute_bonus_die_reward(player, roll, supply_bank):
            reward = None
            match roll:
                case 1:
                    reward = "one victory point."
                case 2:
                    reward = "a droplet upgrade."
                case 3:
                    reward = "an (ORANGE-1) chip."
                case 4:
                    reward = "a ruby."
                case 5:
                    reward = "two victory points."
                case 6:
                    reward = "one victory point."

            print(f"Player {get_current_player(player)} rolled the bonus die and received " + reward)
            orig_execute_bonus_die_reward(player, roll, supply_bank)


        orig_execute_black_special_action = execute_black_special_action
        def spy_execute_black_special_action(player_a, player_b):
            old_droplet_a = player_a.droplet
            old_droplet_b = player_b.droplet
            old_ruby_a = player_a.ruby
            old_ruby_b = player_b.ruby

            orig_execute_black_special_action(player_a, player_b)

            if player_a.droplet > old_droplet_a:
                print("Black special action: player A received a droplet upgrade.")
            if player_b.droplet > old_droplet_b:
                print("Black special action: player B received a droplet upgrade.")

            if player_a.ruby > old_ruby_a:
                print("Black special action: player A received a ruby.")
            if player_b.ruby > old_ruby_b:
                print("Black special action: player B received a ruby.")


        orig_execute_green_special_action = execute_green_special_action
        def spy_execute_green_special_action(player):
            old_num_rubies = player.ruby
            orig_execute_green_special_action(player)
            if player.ruby - old_num_rubies == 0:
                return
            if player.ruby - old_num_rubies == 1:
                print(f"Green special action: player {get_current_player(player)} received a ruby.")
                return
            if player.ruby - old_num_rubies == 2:
                print(f"Green special action: player {get_current_player(player)} received two rubies.")


        orig_execute_purple_special_action = execute_purple_special_action
        def spy_execute_purple_special_action(player):
            num_purple_chips = sum(1 for chip in player.played_chips if chip.color == ChipColor.PURPLE)
            if num_purple_chips == 1:
                print(f"Purple special action: player {get_current_player(player)} received one victory point.")

            if num_purple_chips == 2:
                print(f"Purple special action: player {get_current_player(player)} received one victory point and one "
                      "ruby.")

            if num_purple_chips >= 3:
                print(f"Purple special action: player {get_current_player(player)} received two victory points and one"
                      " droplet upgrade.")

            orig_execute_purple_special_action(player)


        orig_award_ruby = award_ruby
        def spy_award_ruby(player):
            old_num_rubies = player.ruby
            orig_award_ruby(player)
            if player.ruby > old_num_rubies:
                print(f"Player {get_current_player(player)} received a ruby from their scoring space.")


        orig_award_victory_points = award_victory_points
        def spy_award_victory_points(player, current_round):
            old_vp = player.victory_points
            orig_award_victory_points(player, current_round)
            points_awarded = player.victory_points - old_vp
            if points_awarded > 1:
                print(f"Player {get_current_player(player)} received {points_awarded} victory points from their scoring"
                      f" space.")
            if points_awarded == 1:
                print(f"Player {get_current_player(player)} received {points_awarded} victory point from their scoring "
                      f"space.")


        orig_execute_buying_phase = execute_buying_phase
        def spy_execute_buying_phase(player, supply_bank, current_round):
            if has_exploded(player):
                chose_points = should_choose_points_on_explosion(player, current_round)
                if chose_points:
                    print(f"Player {get_current_player(player)} did not purchase chips because they exploded and "
                          f"chose victory points.")
                    orig_execute_buying_phase(player, supply_bank, current_round)
                    return

            money = POT_BOARD_SPACES[player.current_space].money

            if current_round == FINAL_ROUND:
                print(f"Player {get_current_player(player)} earned {money} coins and spent them on "
                      f"{money // MONEY_TO_VC_PRICE} victory point(s).")
                orig_execute_buying_phase(player, supply_bank, current_round)
                return

            print(f"Player {get_current_player(player)} earned {money} coins and purchased the following chips:")
            orig_execute_buying_phase(player, supply_bank, current_round)


        orig_finalize_chip_purchase = finalize_chip_purchase
        def spy_finalize_chip_purchase(player, supply_bank, item, money: int):
            print(f"  ({item.color.upper()}-{item.value})")
            remaining_money = orig_finalize_chip_purchase(player, supply_bank, item, money)

            return remaining_money


        orig_spend_rubies = spend_rubies
        def spy_spend_rubies(player, current_round):
            old_num_rubies = player.ruby
            old_droplet = player.droplet
            old_flask = player.flask_full
            old_vc = player.victory_points

            orig_spend_rubies(player, current_round)

            ruby_dif = old_num_rubies - player.ruby
            droplet_dif = player.droplet - old_droplet
            vc_dif = player.victory_points - old_vc

            if ruby_dif > 0:
                print(f"Player {get_current_player(player)} spent {ruby_dif} rubies and received:")
                if not old_flask:
                    if player.flask_full:
                        print("  1 flask refill.")
                if droplet_dif > 0:
                    print(f"  {droplet_dif} droplet upgrade(s).")
                if vc_dif > 0:
                    print(f"  {vc_dif} victory point(s).")

            else:
                print(f"Player {get_current_player(player)} spent no rubies.")


        # Setup side effects
        def smart_randrange_side_effect(upper_bound):
            return seeded_rng.randrange(upper_bound)

        def smart_randint_side_effect(a, b):
            return seeded_rng.randint(a, b)

        mock_randrange.side_effect = smart_randrange_side_effect
        mock_randint.side_effect = smart_randint_side_effect

        print(f"\n=============================================================")
        print(f"    GOLDEN MASTER AUDIT: RUNNING ROUNDS 1 TO {CURRENT_TEST_ROUND_LIMIT} (SEED: {TEST_SEED})")
        print(f"=============================================================")

        with (
            patch('game_engine.match_runner.TOTAL_ROUND_COUNT', CURRENT_TEST_ROUND_LIMIT),
            patch.object(Player, '__init__', spy_player_init),
            patch('game_engine.phase_1_prep.calculate_rat_tails', spy_calculate_rat_tails),
            patch('game_engine.match_runner.play_single_round', spy_play_single_round),
            patch('game_engine.phase_2_potions.run_potions_phase', spy_run_potions_phase),
            patch('game_engine.phase_2_potions.use_flask', spy_use_flask),
            patch('game_engine.phase_2_potions.update_current_space', spy_update_current_space),
            patch('game_engine.phase_2_potions.draw_chip', spy_draw_chip),
            patch('game_engine.phase_2_potions.execute_yellow_special_action', spy_execute_yellow_special_action),
            patch('game_engine.phase_2_potions.select_chip', spy_select_chip),
            patch('game_engine.phase_3_evaluation.step_a_bonus_die.execute_bonus_die_reward',
                  spy_execute_bonus_die_reward),
            patch('game_engine.phase_3_evaluation.step_b_chip_actions.execute_black_special_action',
                  spy_execute_black_special_action),
            patch('game_engine.phase_3_evaluation.step_b_chip_actions.execute_green_special_action',
                  spy_execute_green_special_action),
            patch('game_engine.phase_3_evaluation.step_b_chip_actions.execute_purple_special_action',
                  spy_execute_purple_special_action),
            patch('game_engine.phase_3_evaluation.step_c_rubies.award_ruby', spy_award_ruby),
            patch('game_engine.phase_3_evaluation.step_d_points.award_victory_points', spy_award_victory_points),
            patch('game_engine.phase_3_evaluation.step_e_buy_chips.execute_buying_phase', spy_execute_buying_phase),
            patch('game_engine.phase_3_evaluation.step_e_buy_chips.finalize_chip_purchase', spy_finalize_chip_purchase),
            patch('game_engine.phase_3_evaluation.step_f_end_of_turn.spend_rubies', spy_spend_rubies)
        ):

            result = game_engine.match_runner.run_match(strat_prof_a, strat_prof_b)

            print("\nRESULTS DICTIONARY:")
            for key, value in result.items():
                print(f"{key}: {value}")

        print(f"\n=============================================================")
        print(f"              END OF GOLDEN MASTER AUDIT STREAM")
        print(f"=============================================================")


if __name__ == '__main__':
    unittest.main()

