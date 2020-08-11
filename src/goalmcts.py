"""
GoalMCTS
========
Goal oriented MCTS, internally uses criteria based MCTS
Provides learn, test functionality
"""


class GoalMCTS:
    def __init__(self, *, state, criteria):
        """
        Goal based MCTS, this is actually a driver class that uses MCTS, but implemented due to
        fit to learner interface
        :param state: game
        :param criteria: goal criteria
        """
        self.state = state.clone()
        self.state.set_feature_tracking(True)
        self.state.save()

        self.criteria = criteria
        self.game_length = 100
        self.fulfilment_threshold = 0.1
        self.verbose = False

        self.actions = []
        self.max_vals = []
        self.criteria_completion = []

    def learn(self, *, parameters=None):
        """
        learn to play the game using MCTS, MCTS will play according to the parameters
        :param parameters: MCTS parameters
        :return: None
        """
        import time
        import logging
        from benchmark import is_file_logging

        is_file = is_file_logging()

        if not parameters:
            from mcts import MCTSParameters
            parameters = MCTSParameters()

        self.game_length = parameters.game_length
        self.fulfilment_threshold = parameters.fulfilment_threshold
        self.verbose = parameters.verbose

        logging.info("Running MCTS")
        from mcts import MCTS

        state_clone = self.state.clone()
        state_clone.save()

        max_str_len = 0
        total_time = 0
        prev_graph = {}
        print_percent = 0
        percent_inc = self.game_length / 100
        sim_counters = []
        for i in range(self.game_length):
            mcts = MCTS(state=state_clone,
                        prev_graph=prev_graph,
                        criteria=self.criteria,
                        remaining_moves=self.game_length - i)
            start = time.time()
            action, action_idx, score, sim_counter = mcts.run(parameters=parameters)
            sim_counters.append(sim_counter)
            total_time += time.time() - start

            if not parameters.prev_graph:
                prev_graph = {}
            else:
                prev_graph = mcts.get_prev_graph()

            # clear the unnecessary memory
            mcts.clear()
            state_clone.process(action=action)

            f_t = self.fulfilment_threshold
            status, completion = state_clone.feature_tracker.check_criteria(self.criteria, f_t)

            self.actions.append(action_idx)
            self.max_vals.append(score)
            self.criteria_completion.append(completion)

            will_break = False
            if state_clone.is_game_over():
                will_break = True
            if completion == 1:
                will_break = True

            if self.verbose:
                fl, log_fulfilment = state_clone.feature_tracker.calculate()
                log_fulfilment = list(map(lambda x: x if x < 10 else '-', log_fulfilment))

                p_str = "MCTS: {0:.2f}% Goal Completion: {1:.2f}% Ful: {2} Status: {3} Avg Time: {4:.3f}s" \
                    .format((i + 1) * 100 / self.game_length,
                            (completion * 100),
                            ["{:.2f}".format(_l_f) if type(_l_f) is float else _l_f for _l_f in log_fulfilment],
                            state_clone.get_avatar_status(),
                            total_time / (i + 1))
                max_str_len = max(max_str_len, len(p_str))

                if is_file and ((i + 1) >= print_percent or will_break):
                    print_percent += percent_inc
                    logging.info(p_str)
                elif not is_file:
                    print('\r', p_str.ljust(max_str_len + 1), end='')

            if will_break:
                break

        if self.verbose and not is_file:
            print()

        from statistics import mean, stdev
        if len(sim_counters) >= 2:
            logging.info("MCTS Simulation Mean: {} Std: {}".format(mean(sim_counters), stdev(sim_counters)))

    def test(self, *, game_length=100, completion_check=True, check_qs=False):
        """
        play on the actual state with respect to certain criteria
        :param game_length: maximum steps to be taken, actually this is similar to MCTS game length
        probably will be same
        :param completion_check: terminate the steps if 100% completion is achieved
        :param check_qs: while playing the actions terminate after the last positive q_value
        :return: actions taken by their numeral order
        """
        avatar = self.state.game_state.avatar
        last_idx = min(game_length, len(self.actions))

        if completion_check:
            max_comp = max(self.criteria_completion)
            if max_comp != 0:
                # + 1 is due to it being an index rather a length
                comp_idx = self.criteria_completion.index(max_comp) + 1
                last_idx = min(comp_idx, last_idx)
            else:
                # prune by checking q values
                last_pos = 0
                for idx, val in enumerate(self.max_vals):
                    if val > 0.0:
                        last_pos = idx + 1

                last_idx = min(last_pos, last_idx)

        actions = self.actions[0:last_idx]
        self.state.load()
        for a in actions:
            self.state.process(avatar.get_action(a))

        return actions

    def reset(self):
        """
        clears the class
        :return: None
        """
        self.actions = []
        self.max_vals = []
        self.criteria_completion = []

    @staticmethod
    def name():
        """
        :return: name of the algorithm
        """
        return "MCTS"
