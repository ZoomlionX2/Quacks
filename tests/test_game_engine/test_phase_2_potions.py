import unittest
import random
from unittest.mock import patch

from game_engine.phase_2_potions import calculate_explosion_probability, has_exploded, should_draw, should_flask, \
    calc_nonwhite_chip_percentage, calculate_red_chip_boost, update_current_space, use_flask, \
    execute_yellow_special_action, select_chip, execute_blue_special_action, run_potions_phase
from models.player import Player
from models.strategy import GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat
from models.strategy import ExplosionRoundStrat, ExplodedStrat
from config.chip_config import ChipColor
from models.chip import Chip
from dataclasses import replace


class TestPhase2Potions(unittest.TestCase):

    def setUp(self):
        """Set up clean objects."""
        # Create a dummy strategy profile
        self.mock_profile = GameStrategyProfile(
            colors=(ChipColor.GREEN, ChipColor.BLUE),
            value=ValueStrat.HIGHEST_VALUE_PAIR,
            ruby=RubyStrat.SAVE,
            flask=FlaskStrat.AT_RISK,
            explosion_prob=ExplosionProbabilityToleranceStrat.MEDIUM,
            explosion_round=ExplosionRoundStrat.MID,
            exploded=ExplodedStrat.POINTS
        )

        # Instantiate player with that strategy profile
        self.player = Player(strategy_profile=self.mock_profile)


    def test_execute_yellow_special_action(self):
        """Verify that the yellow chip's special actions are successfully carried out when appropriate."""
        self.player.played_chips.clear()
        self.player.unplayed_chips.clear()
        self.player.setup_starting_bag()

        # No previously played chip: take no action
        self.player.played_chips.append(Chip(ChipColor.YELLOW, 4))
        self.assertEqual(len(self.player.unplayed_chips), 9)
        self.assertEqual(len(self.player.played_chips), 1)

        # Previously played chip was white: return it to bag
        self.player.played_chips.clear()
        self.player.played_chips.append(Chip(ChipColor.WHITE, 3))
        self.player.played_chips.append(Chip(ChipColor.YELLOW, 4))
        execute_yellow_special_action(self.player)
        self.assertEqual(len(self.player.unplayed_chips), 10)
        self.assertEqual(len(self.player.played_chips), 1)

        # Previously played chip was green: do not return it to bag
        self.player.played_chips.clear()
        self.player.unplayed_chips.clear()
        self.player.setup_starting_bag()
        self.player.played_chips.append(Chip(ChipColor.WHITE, 3))
        self.player.played_chips.append(Chip(ChipColor.GREEN, 1))
        self.player.played_chips.append(Chip(ChipColor.YELLOW, 4))
        execute_yellow_special_action(self.player)
        self.assertEqual(len(self.player.unplayed_chips), 9)
        self.assertEqual(len(self.player.played_chips), 3)


    def test_execute_blue_special_action(self):
        """Verifies that the blue chip's special actions are carried out."""
        self.player.played_chips.clear()
        self.player.unplayed_chips.clear()

        # A blue 4 should draw 4 chips
        chip = Chip(ChipColor.BLUE, 4)
        original_randrange = random.randrange
        random.randrange = lambda x: 0

        try:
            for _ in range(3):
                self.player.unplayed_chips.append(Chip(ChipColor.WHITE, 1))
            self.player.unplayed_chips.append(Chip(ChipColor.GREEN, 4))
            self.player.unplayed_chips.append(Chip(ChipColor.BLUE, 4))
            execute_blue_special_action(self.player, chip)
            last_chip_played = self.player.played_chips[-1]
            self.assertEqual(last_chip_played, Chip(ChipColor.GREEN, 4))

        finally:
            random.randrange = original_randrange

        # Drawing a blue chip should trigger another blue special action
        self.player.played_chips.clear()
        self.player.unplayed_chips.clear()
        for _ in range(5):
            self.player.unplayed_chips.append(Chip(ChipColor.BLUE, 2))
        played_blue = Chip(ChipColor.BLUE, 3)
        self.player.played_chips.append(played_blue)
        execute_blue_special_action(self.player, played_blue)
        self.assertEqual(len(self.player.played_chips), 6)
        self.assertEqual(len(self.player.unplayed_chips), 0)


    def test_select_chip(self):
        """Verifies the correct chip is selected."""
        # One white: select none
        drawn_chips = [Chip(ChipColor.WHITE, 3)]
        self.assertEqual(select_chip(self.player, drawn_chips), None)

        # One white, one yellow 1: select none
        drawn_chips.append(Chip(ChipColor.YELLOW, 1))
        self.assertEqual(select_chip(self.player, drawn_chips), None)

        # Three played pumpkins: select red 1
        self.player.played_chips.clear()
        for _ in range(3):
            self.player.played_chips.append(Chip(ChipColor.ORANGE, 1))
        drawn_chips.append(Chip(ChipColor.RED, 1))
        self.assertEqual(select_chip(self.player, drawn_chips), Chip(ChipColor.RED, 1))

        # Select the blue 4
        drawn_chips.append(Chip(ChipColor.BLUE, 4))
        self.assertEqual(select_chip(self.player, drawn_chips), Chip(ChipColor.BLUE, 4))


    # calculate_explosion_probability()
    def test_new_bag(self):
        """Verify that the probability is zero when no chips have been played from the starting bag."""
        self.player.setup_starting_bag()
        explosion_probability = calculate_explosion_probability(self.player)
        self.assertEqual(explosion_probability, 0)


    def test_empty_bag(self):
        """Verify that the probability is zero for an empty bag."""
        self.player.unplayed_chips.clear()
        self.player.played_chips = []
        played_chips = [
            (ChipColor.WHITE, 2, 2),
            (ChipColor.WHITE, 3, 1),
            (ChipColor.GREEN, 1, 1),
            (ChipColor.ORANGE, 1, 1)
        ]

        for color, value, quantity in played_chips:
            for _ in range(quantity):
                self.player.played_chips.append(Chip(color=color, value=value))

        explosion_probability = calculate_explosion_probability(self.player)
        self.assertEqual(explosion_probability, 0)


    def test_explodable_bag(self):
        """Verify that the probability is non-zero when enough white chips are already in play."""
        unplayed_chips = [
            (ChipColor.WHITE, 2, 1),
            (ChipColor.WHITE, 3, 1),
            (ChipColor.GREEN, 1, 1),
            (ChipColor.ORANGE, 1, 1)
        ]

        played_chips = [
            (ChipColor.WHITE, 1, 4),
            (ChipColor.WHITE, 2, 1)
        ]

        for color, value, quantity in unplayed_chips:
            for _ in range(quantity):
                self.player.unplayed_chips.append(Chip(color=color, value=value))

        for color, value, quantity in played_chips:
            for _ in range(quantity):
                self.player.played_chips.append(Chip(color=color, value=value))

        explosion_probability = calculate_explosion_probability(self.player)
        self.assertEqual(explosion_probability, 0.5)


    def test_should_draw_never_strategy(self):
        """Verify that a player with 'NEVER' risk profile stops if there is any chance of exploding."""
        # Create new strategy profile with updated arguments
        new_strategy_profile = replace(
            self.mock_profile,
            explosion_prob=ExplosionProbabilityToleranceStrat.NEVER,
            explosion_round=ExplosionRoundStrat.EARLY
        )
        self.player.strategy_profile = new_strategy_profile

        # Test 0% risk (should draw)
        self.player.setup_starting_bag()
        self.assertTrue(should_draw(self.player, current_round=1))

        # Test 10% risk (should NOT draw)
        self.player.unplayed_chips.clear()
        for _ in range(9):
            self.player.unplayed_chips.append(Chip(ChipColor.ORANGE, 1))
        self.player.unplayed_chips.append(Chip(ChipColor.WHITE, 1))
        self.player.played_chips.append(Chip(ChipColor.WHITE, 3))
        self.player.played_chips.append(Chip(ChipColor.WHITE, 2))
        self.player.played_chips.append(Chip(ChipColor.WHITE, 2))
        self.assertFalse(should_draw(self.player, current_round=1))


    def test_should_draw_round_context(self):
        """Verify that round strategies block drawing."""
        # Create new strategy profile with updated arguments
        new_strategy_profile = replace(
            self.mock_profile,
            explosion_prob=ExplosionProbabilityToleranceStrat.HIGH,
            explosion_round=ExplosionRoundStrat.EARLY
        )
        self.player.strategy_profile = new_strategy_profile

        # Create safe bag
        self.player.setup_starting_bag()

        # Test for round 2 (should draw)
        self.assertTrue(should_draw(self.player, 2))

        # Test for round 5 (should draw)
        self.assertTrue(should_draw(self.player, 5))

        # Create risk
        self.player.played_chips.append(Chip(ChipColor.WHITE, 3))
        self.player.played_chips.append(Chip(ChipColor.WHITE, 2))
        self.player.played_chips.append(Chip(ChipColor.WHITE, 2))

        # Test for round 2 (should draw)
        self.assertTrue(should_draw(self.player, 2))

        # Test for round 5 (should NOT draw)
        self.assertFalse(should_draw(self.player, 5))

        # Create new strategy profile with updated arguments
        new_strategy_profile = replace(
            self.mock_profile,
            explosion_prob=ExplosionProbabilityToleranceStrat.HIGH,
            explosion_round=ExplosionRoundStrat.MID
        )
        self.player.strategy_profile = new_strategy_profile

        # Test for round 2 (should not draw)
        self.assertFalse(should_draw(self.player, 2))

        # Test for round 5 (should draw)
        self.assertTrue(should_draw(self.player, 5))

        # Test for round 7 (should not draw)
        self.assertFalse(should_draw(self.player, 7))


    def test_should_draw_random(self):
        """Verify that random round-based strategy does not affect drawing and that random explosion probability
        strategy returns a random choice."""
        new_strategy_profile = replace(
            self.mock_profile,
            explosion_prob=ExplosionProbabilityToleranceStrat.RANDOM,
            explosion_round=ExplosionRoundStrat.RANDOM
        )
        self.player.strategy_profile = new_strategy_profile
        self.player.setup_starting_bag()

        with patch('random.choice') as mock_choice:
            mock_choice.return_value = True
            result = should_draw(self.player, 7)
            self.assertTrue(result)


    def test_should_draw_final_scoring_space(self):
        """Verify that drawing stops once the final scoring space (53) is reached."""
        self.player.current_space = 0

        self.player.played_chips.clear()
        for _ in range(16):
            self.player.unplayed_chips.append(Chip(ChipColor.GREEN, 4))

        while should_draw(self.player, 3):
            drawn_chip = self.player.unplayed_chips.pop()
            update_current_space(self.player, drawn_chip, False)

        self.assertEqual(len(self.player.unplayed_chips), 2)


    def test_has_exploded_boundaries(self):
        """Verify the engine accurately identifies when a pot has exploded (> 7 white points)."""
        self.player.played_chips.clear()

        # Scenario A: Exactly 7 white points (safe)
        self.player.played_chips.append(Chip(ChipColor.WHITE, 3))
        self.player.played_chips.append(Chip(ChipColor.WHITE, 2))
        self.player.played_chips.append(Chip(ChipColor.WHITE, 2))
        self.player.played_chips.append(Chip(ChipColor.GREEN, 4))
        self.assertFalse(has_exploded(self.player))

        # Scenario B: 8 white points (exploded)
        self.player.played_chips.append(Chip(ChipColor.WHITE, 1))
        self.assertTrue(has_exploded(self.player))


    def test_calc_nonwhite_chip_percentage(self):
        """Verifies the calculation of non-white chips remain in the bag vs the total owned (played and unplayed)."""
        self.player.played_chips.clear()
        self.player.unplayed_chips.clear()
        self.player.setup_starting_bag()

        # 100% unplayed (starting bag has two non-white chips)
        self.assertEqual(calc_nonwhite_chip_percentage(self.player), 1.0)

        # 50% unplayed (two non-white chips from starting bag and two in pot)
        self.player.played_chips.append(Chip(ChipColor.GREEN, 1))
        self.player.played_chips.append(Chip(ChipColor.GREEN, 1))
        self.assertEqual(calc_nonwhite_chip_percentage(self.player), 0.5)

        # 0% unplayed
        for chip in self.player.unplayed_chips[:]:
            if chip.color != ChipColor.WHITE:
                self.player.unplayed_chips.remove(chip)
        self.assertEqual(calc_nonwhite_chip_percentage(self.player), 0.0)


    def test_calculate_red_chip_boost(self):
        """Verifies that red chips get the proper boost from played orange chips."""
        self.player.played_chips.clear()

        # No orange chips
        self.assertEqual(calculate_red_chip_boost(self.player), 0)

        # 2 orange chips
        self.player.played_chips.append(Chip(ChipColor.ORANGE, 1))
        self.player.played_chips.append(Chip(ChipColor.ORANGE, 1))
        self.assertEqual(calculate_red_chip_boost(self.player), 1)

        # 5 orange chips
        for _ in range(3):
            self.player.played_chips.append(Chip(ChipColor.ORANGE, 1))
        self.assertEqual(calculate_red_chip_boost(self.player), 2)


    def test_update_current_space(self):
        """Verifies the player's space is correctly updated based on a drawn chip."""
        self.player.played_chips.clear()

        # Red chip includes boost
        self.player.current_space = 21
        self.player.played_chips.append(Chip(ChipColor.ORANGE, 1))
        self.player.played_chips.append(Chip(ChipColor.ORANGE, 1))
        update_current_space(self.player, Chip(ChipColor.RED, 1), False)
        self.assertEqual(self.player.current_space, 23)

        # First draw calculation includes rat token and droplet
        self.player.current_space = 0
        self.player.droplet = 3
        self.player.rat_token = 5
        update_current_space(player=self.player, chip=Chip(ChipColor.GREEN, 1), is_first_draw=True)
        self.assertEqual(self.player.current_space, 9)

        # Non-first draw calculation only includes value of chip (for non-red)
        self.player.current_space = 15
        self.player.droplet = 3
        self.player.rat_token = 5
        update_current_space(player=self.player, chip=Chip(ChipColor.GREEN, 1), is_first_draw=False)
        self.assertEqual(self.player.current_space, 16)

        # Player can not go beyond highest scoring space
        self.player.current_space = 52
        update_current_space(player=self.player, chip=Chip(ChipColor.GREEN, 4), is_first_draw=False)
        self.assertEqual(self.player.current_space, 53)



    def test_should_flask(self):
        """Verifies that the engine correctly decides to use the flask based on the flask strategy."""
        # Create new strategy profile with updated arguments
        new_strategy_profile = replace(
            self.mock_profile,
            flask=FlaskStrat.ALWAYS_THREE
        )
        self.player.strategy_profile = new_strategy_profile

        # Always flask round 9
        self.assertTrue(should_flask(self.player, Chip(ChipColor.WHITE, 2), 9))

        # ALWAYS_THREE: Always flask on three
        self.assertTrue(should_flask(self.player, Chip(ChipColor.WHITE, 3), 5))
        self.assertFalse(should_flask(self.player, Chip(ChipColor.WHITE, 2), 5))

        # AT_RISK: Always flask if there is an explosion risk
        new_strategy_profile = replace(
            self.mock_profile,
            flask=FlaskStrat.AT_RISK
        )
        self.player.strategy_profile = new_strategy_profile

        self.player.unplayed_chips.clear()
        self.player.played_chips.clear()
        self.player.setup_starting_bag()

        self.assertFalse(should_flask(self.player, Chip(ChipColor.WHITE, 2), 5))

        self.player.played_chips.append(Chip(ChipColor.WHITE, 2))
        self.player.played_chips.append(Chip(ChipColor.WHITE, 2))
        self.player.played_chips.append(Chip(ChipColor.WHITE, 3))
        self.assertTrue(should_flask(self.player, Chip(ChipColor.WHITE, 3), 5))

        # SEVENTY: Flask if at least 70% of non-white chips are still in bag
        new_strategy_profile = replace(
            self.mock_profile,
            flask=FlaskStrat.SEVENTY
        )
        self.player.strategy_profile = new_strategy_profile

        self.player.unplayed_chips.clear()
        self.player.played_chips.clear()
        self.player.setup_starting_bag()

        for _ in range(3): self.player.played_chips.append(Chip(ChipColor.WHITE, 2))

        self.assertTrue(should_flask(self.player, Chip(ChipColor.WHITE, 2), 5))

        played_orange = self.player.unplayed_chips.pop(self.player.unplayed_chips.index(Chip(ChipColor.ORANGE, 1)))
        self.player.played_chips.append(played_orange)
        self.assertFalse(should_flask(self.player, Chip(ChipColor.WHITE, 2), 5))

        # RANDOM: Randomly choose between flasking or not
        new_strategy_profile = replace(
            self.mock_profile,
            flask=FlaskStrat.RANDOM
        )
        self.player.strategy_profile = new_strategy_profile

        with patch('random.choice') as mock_choice:
            mock_choice.return_value = False
            result = should_flask(self.player, Chip(ChipColor.WHITE, 2), 5)
            self.assertFalse(result)


    def test_use_flask(self):
        """Ensures that white chip is removed from board and returned to bag and flask state is changed."""
        self.player.played_chips.clear()
        self.player.unplayed_chips.clear()
        self.player.setup_starting_bag()

        # Search for a white 2-chip and play it
        idx_white = self.player.unplayed_chips.index(Chip(ChipColor.WHITE, 2))
        drawn_chip = self.player.unplayed_chips.pop(idx_white)
        self.player.played_chips.append(drawn_chip)

        # Flask chip: it should be removed from played, returned to unplayed, and flask_full should set to False
        use_flask(self.player, drawn_chip)
        self.assertEqual(len(self.player.played_chips), 0)
        self.assertEqual(len(self.player.unplayed_chips), 9)
        self.player.flask_full = False


    def test_run_potions_phase(self):
        """Integration test of run_potions_phase."""
        original_randrange = random.randrange
        random.randrange = lambda x: x - 1

        try:
            # Scenario A: Player plays chips and quits when there is a risk of exploding
            # Set up new strategy profile
            self.cautious_profile = GameStrategyProfile(
                colors=(ChipColor.GREEN, ChipColor.BLUE),
                value=ValueStrat.HIGHEST_VALUE_PAIR,
                ruby=RubyStrat.SAVE,
                flask=FlaskStrat.AT_RISK,
                explosion_prob=ExplosionProbabilityToleranceStrat.NEVER,
                explosion_round=ExplosionRoundStrat.EARLY,
                exploded=ExplodedStrat.POINTS
            )

            # Instantiate player with that strategy profile
            self.player = Player(strategy_profile=self.cautious_profile)

            # Adjust starting attributes
            self.player.droplet = 3
            self.player.rat_token = 5
            self.player.current_space = 0

            # Set up bag
            self.player.unplayed_chips.clear()
            self.player.played_chips.clear()

            self.player.unplayed_chips.append(Chip(ChipColor.WHITE, 1))     # Place chip on space 9, continue
            self.player.unplayed_chips.append(Chip(ChipColor.WHITE, 2))     # Place chip on space 11, continue
            self.player.unplayed_chips.append(Chip(ChipColor.GREEN, 4))     # Place chip on space 15, continue
            self.player.unplayed_chips.append(Chip(ChipColor.BLUE, 2))      # Place chip on space 17, draw 2
                                                                            # (white 1, orange 1), select orange 1,
                                                                            # place on space 18, continue
            self.player.unplayed_chips.append(Chip(ChipColor.WHITE, 1))     # Place on space 19, continue
            self.player.unplayed_chips.append(Chip(ChipColor.ORANGE, 1))    # Already placed when blue 2 was played
            self.player.unplayed_chips.append(Chip(ChipColor.YELLOW, 1))    # Place on space 20, remove previous white,
                                                                            # continue, draw removed white 1, place
                                                                            # on space 21, continue
            self.player.unplayed_chips.append(Chip(ChipColor.WHITE, 1))     # Place on space 22, continue
            self.player.unplayed_chips.append(Chip(ChipColor.RED, 1))       # Place on space 24 (boosted by 1), continue
            self.player.unplayed_chips.append(Chip(ChipColor.WHITE, 1))     # Place on space 25, stop (explosion risk)
            self.player.unplayed_chips.append(Chip(ChipColor.WHITE, 2))     # Not pulled
            self.player.unplayed_chips.append(Chip(ChipColor.ORANGE, 1))    # Not pulled
            self.player.unplayed_chips.append(Chip(ChipColor.ORANGE, 1))    # Not pulled

            # Reverse the order to account for speed-up trick (swapping random chip with last chip in list)
            self.player.unplayed_chips.reverse()
            run_potions_phase(self.player, 3)

            # Verify state
            self.assertEqual(len(self.player.unplayed_chips), 3)
            self.assertEqual(len(self.player.played_chips), 10)
            self.assertFalse(self.player.flask_full)
            self.assertEqual(self.player.current_space, 25)


            # Scenario B: Player plays chips until pot explodes
            # Set up new strategy profile
            self.aggressive_profile = GameStrategyProfile(
                colors=(ChipColor.GREEN, ChipColor.BLUE),
                value=ValueStrat.HIGHEST_VALUE_PAIR,
                ruby=RubyStrat.SAVE,
                flask=FlaskStrat.ALWAYS_THREE,
                explosion_prob=ExplosionProbabilityToleranceStrat.HIGH,
                explosion_round=ExplosionRoundStrat.LATE,
                exploded=ExplodedStrat.POINTS
            )

            # Instantiate player with that strategy profile
            self.player = Player(strategy_profile=self.aggressive_profile)

            # Adjust starting attributes
            self.player.droplet = 0
            self.player.rat_token = 0
            self.player.current_space = 0

            # Set up bag
            self.player.unplayed_chips.clear()
            self.player.played_chips.clear()

            self.player.unplayed_chips.append(Chip(ChipColor.BLUE, 4))      # Place chip on space 4, draw 4 chips
                                                                            # (white 2, green 4, blue 2, white 1)
                                                                            # Select green 4, place on space 8, continue
            self.player.unplayed_chips.append(Chip(ChipColor.WHITE, 2))     # Place chip on space 10, continue
            self.player.unplayed_chips.append(Chip(ChipColor.GREEN, 4))     # Already placed
            self.player.unplayed_chips.append(Chip(ChipColor.BLUE, 2))      # Place chip on space 12, draw 2
                                                                            # (white 1, blue 2), select blue 2 place on
                                                                            # space 14, draw 2 (white 1, green 1),
                                                                            # select neither
            self.player.unplayed_chips.append(Chip(ChipColor.WHITE, 1))     # Place on space 15, continue
            self.player.unplayed_chips.append(Chip(ChipColor.BLUE, 2))      # Already placed when blue 2 was played
            self.player.unplayed_chips.append(Chip(ChipColor.GREEN, 1))     # Place on space 16, continue
            self.player.unplayed_chips.append(Chip(ChipColor.WHITE, 1))     # Place on space 17, continue
            self.player.unplayed_chips.append(Chip(ChipColor.RED, 1))       # Place on space 18 (not boosted), continue
            self.player.unplayed_chips.append(Chip(ChipColor.WHITE, 1))     # Place on space 19, (explosion risk)
            self.player.unplayed_chips.append(Chip(ChipColor.ORANGE, 1))    # Place on space 20, continue
            self.player.unplayed_chips.append(Chip(ChipColor.WHITE, 3))     # Place on space 23, exploded! (can't flask)
            self.player.unplayed_chips.append(Chip(ChipColor.ORANGE, 1))    # Not pulled

            # Reverse the order to account for speed-up trick (swapping random chip with last chip in list)
            self.player.unplayed_chips.reverse()
            run_potions_phase(self.player, 7)

            # Verify state
            self.assertEqual(self.player.played_chips[1], Chip(ChipColor.GREEN, 4))
            self.assertEqual(len(self.player.unplayed_chips), 1)
            self.assertEqual(len(self.player.played_chips), 12)
            self.assertTrue(has_exploded(self.player))
            self.assertTrue(self.player.flask_full)
            self.assertEqual(self.player.current_space, 23)


        finally:
            random.randrange = original_randrange


if __name__ == '__main__':
    unittest.main()