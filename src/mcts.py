"""
MCTS
====
References
[1] http://www.csse.uwa.edu.au/cig08/Proceedings/papers/8057.pdf
"""
from random import randint
from sys import float_info
import math


class MCTSData:
    def __init__(self, *, state, action=None, visit=0, score=0, depth=0, is_terminal=False, parent=None):
        """
        Holds the mcts data, will be used during MCTS algorithm
        :param state: State object that can be forwarded in game
        :param action: action taken to get to this state from the parent state, None if parent
        :param visit: total amount of visits done on this node
        :param score: average score
        :param depth: depth of the node in the mcts tree
        :param is_terminal: is this is a terminal state
        :param parent: parent mcts data
        """
        self.state = state.clone()
        self.state.save()
        if action:
            self.actions = [action]
        else:
            self.actions = None
        self.visit = visit
        self.score = score
        self.depth = depth
        self.is_terminal = is_terminal
        if parent:
            self.parents = [parent]
        else:
            self.parents = None
        self.is_updated = False

    def add_parent(self, parent, action):
        if self.parents and self.actions and parent not in self.parents:
            self.parents.append(parent)
            self.actions.append(action)
            return True
        return False

    def update_score_visit(self, *, un_avg_score, visit):
        """
        update score according to UCT3 in transposition
        :param un_avg_score: score of newly added child
        :param visit: total visit of their child
        :return: None
        """
        new_visit = self.visit + visit
        if new_visit:
            self.score = self.score * (self.visit / new_visit) + un_avg_score / new_visit
            self.visit = new_visit

    def update_score(self, *, score):
        """
        updates the average score stored in the score
        also updates the total visits
        :param score: new obtained score
        :return: None
        """
        new_visit = self.visit + 1
        self.score = self.score * (self.visit / new_visit) + score / new_visit
        self.visit = new_visit

    def calculate_ucb1(self, *, total_visit, exploration_constant):
        """
        calculates the ucb1 score of the node
        :param total_visit: total amount of visits in tree
        :param exploration_constant:  ucb1 exploration constant, C_p
        :return: ucb1 score
        """
        exploitation_score = self.score
        exploration_score = 2 * exploration_constant * math.sqrt(2 * total_visit / self.visit)
        ucb_score = exploitation_score + exploration_score
        return ucb_score


class MCTS:
    def __init__(self, *, state, prev_graph, criteria, remaining_moves):
        """
        construct a MCTS instance
        :param state: state object that can be simulated
        """
        self.state = state.clone()
        self.state.save()

        self.criteria = criteria
        self.remaining_moves = remaining_moves

        from mcts import MCTSParameters
        self.parameters = MCTSParameters()
        self.total_visits = 0
        self.hash_mcts_data = prev_graph  # key is hash, value is mcts data
        self.ucb_children = set()
        self.state_action_hash = {}
        self.avatar = self.state.game_state.avatar

    def run(self, *, parameters=None):
        """
        run the MCTS simulation for the given simulation length
        :return: most rewarding child
        """
        import time
        start = time.time()
        self.__set_parameters(parameters)
        self.__init()

        counter = 0
        while True:
            self.__tree_walk()
            passed = time.time() - start
            counter += 1
            # convert time to ms, child selection takes 10ms
            # TODO average it and calculate throughout the MCTS
            if passed * 1000 >= self.parameters.simulation_time_ms - 10:
                break

        mcts_score, best_child, score = self.__get_highest_child()
        a_idx = self.state.game_state.avatar.get_action_index(best_child)
        return best_child, a_idx, score, counter

    def __init(self):
        self.__tree_add(self.state)

    def __tree_walk(self):
        """
        Tree Walk algorithm, get the child using the tree policy, roll this child using the default policy
        :return: None
        """
        self.__ready_iteration()
        mcts_data = self.__tree_policy()
        self.__ready_iteration()
        self.__default_policy(mcts_data)
        self.total_visits += 1

    def __get_highest_child(self):
        """
        Get the highest scoring child node in the simulations
        :return: highest scoring state
        """
        available_actions = self.avatar.get_actions()
        scores_actions = []
        for action in available_actions:
            score, state_hash = self.__cache_state_action_score(state=self.state, action=action)
            mcts_data = self.hash_mcts_data.get(state_hash, None)

            if mcts_data:
                mcts_score = score + mcts_data.score
                scores_actions.append((mcts_score, action, score))

        if scores_actions:
            scores_actions.sort(key=lambda x: x[0], reverse=True)
            return scores_actions[0]
        else:
            # edge case MCTS not ran even once
            r_int = randint(0, self.avatar.action_count() - 1)
            return -1, self.avatar.get_action(r_int), -1

    def __tree_policy(self):
        """
        apply ucb1 to select the child to simulate
        :return: mcts_data chosen from ucb1
        """
        mcts_data = self.__select_child_ucb1()
        if self.__should_expand(mcts_data):
            mcts_data = self.__expand(mcts_data)
        return mcts_data

    def __should_expand(self, mcts_data):
        """
        checks whether the given mcts_data should be expanded to give birth to new children
        for simulation
        :param mcts_data: MCTSData
        :return: boolean, True if should be expanded False if not
        """
        depth_limit = self.parameters.tree_depth
        return mcts_data.visit and mcts_data.depth < depth_limit and not mcts_data.is_terminal

    def __default_policy(self, mcts_data):
        """
        apply the default policy: rollout the child, then back-propagate the score
        :param mcts_data: chosen mcts data from tree policy, to be simulated
        :return: None
        """
        score = self.__criteria_rollout(mcts_data)
        self.__back_propagate(mcts_data, score)

    def __select_child_ucb1(self):
        """
        Select the child using the UCB1 formulation which balances exploitation & exploration
        :return: Max scoring child calculated by UCB1
        """
        max_ucb_score = -float_info.max
        max_mcts_data = None

        for key in self.ucb_children:
            value = self.hash_mcts_data[key]
            if value.visit == 0:  # if visit is zero
                max_mcts_data = value
                break
            else:
                avg_action_score = 0
                if value.parents and value.actions:
                    iterations = 0
                    for parent, action in zip(value.parents, value.actions):
                        score, state_hash = self.__cache_state_action_score(state=parent.state, action=action)
                        avg_action_score += score
                        iterations += 1
                    if iterations:
                        avg_action_score /= iterations

                exp_const = self.parameters.exploration_constant
                ucb1_score = value.calculate_ucb1(total_visit=self.total_visits, exploration_constant=exp_const)
                ucb_score = ucb1_score + avg_action_score

                # for debugging
                # if value.actions:
                #     ucb_scores.append((value.actions[0].name, "{:.2f}".format(ucb_score), value.visit))
                # else:
                #     ucb_scores.append(("Root", "{:.2f}".format(ucb_score), value.visit))
                # end debug
                if ucb_score > max_ucb_score:
                    max_ucb_score = ucb_score
                    max_mcts_data = value

        # print("UCB Scores: ", ucb_scores)
        if max_mcts_data is None:
            assert "No node at tree"

        return max_mcts_data

    def __rollout(self, mcts_data):
        """
        roll the state using random actions
        :param mcts_data: state we have chosen to roll out
        :return: total reward calculated by this rollout
        """
        rollout_length = self.__calculate_rollout_length(mcts_data)
        gamma = self.parameters.gamma

        available_actions = self.avatar.get_actions()
        # sample random actions
        # TODO use a distribution for better randomness
        actions = [available_actions[randint(0, len(available_actions) - 1)]
                   for i in range(rollout_length)]
        # insert the child index as it can have immediate reward
        state_clone = mcts_data.state.clone()
        state_clone.save()
        total_reward = 0
        discount = 1
        for action in actions:
            rewards, f_ids = state_clone.process(action)
            total_reward += discount * sum(rewards)
            discount *= gamma
            if state_clone.is_game_over():
                break

        return total_reward

    def __criteria_rollout(self, mcts_data):
        """
        roll the state using random actions,
        but adds additional reward depending on the criteria
        and assigns negative reward if feature index does not belong
        :param mcts_data: state we have chosen to roll out
        :return: total reward calculated by this rollout
        """
        rollout_length = self.__calculate_rollout_length(mcts_data)
        gamma = self.parameters.gamma

        available_actions = self.state.game_state.avatar.get_actions()
        actions = [available_actions[randint(0, len(available_actions) - 1)]
                   for i in range(rollout_length)]
        # insert the child index as it can have immediate reward
        state = mcts_data.state.clone()
        total_reward = 0
        discount = 1
        for action in actions:
            score = self.__calculate_state_action_score(action, state)
            total_reward += discount * score
            discount *= gamma
            if state.is_game_over():
                break
        state.load()
        return total_reward

    def __calculate_rollout_length(self, mcts_data):
        rollout_length = min(self.parameters.rollout_length, self.remaining_moves - mcts_data.depth)
        return rollout_length

    def __calculate_criteria(self, state):
        f_t = self.parameters.fulfilment_threshold
        goal_val = self.parameters.goal_value
        status, completion = state.feature_tracker.check_criteria(self.criteria, f_t)

        curr_goal_reward = pow(goal_val, completion)
        return curr_goal_reward

    def __back_propagate(self, mcts_data, score, child_mcts_data=None, action_taken=None):
        """
        back-propagate the score
        :param mcts_data: first node of back propagation
        :param score: calculated score during rollout
        :return: None
        """
        if mcts_data.is_updated:
            return
        else:
            mcts_data.is_updated = True

        total_score = score

        # if it is propagated from a child calculate the immediate reward of taking that action
        if child_mcts_data and action_taken:
            score, state_hash = self.__cache_state_action_score(state=mcts_data.state, action=action_taken)
            total_score += score

        mcts_data.update_score(score=total_score)

        gamma = self.parameters.gamma
        if mcts_data.parents:
            for parent, action in zip(mcts_data.parents, mcts_data.actions):
                self.__back_propagate(parent, score * gamma, mcts_data, action)

    # noinspection PyMethodMayBeStatic
    def __calculate_state_action_score(self, action_taken, state_clone):
        """
        used to calculate criteria based scoring, the features that are not interested are negatively scored
        :param action_taken: action to be taken at a state
        :param state_clone: state
        :return: score calculated from taking an action
        """
        prev_goal_reward = self.__calculate_criteria(state_clone)
        feature_list, fulfilment = self.state.feature_tracker.calculate()
        rewards, f_ids, ints = state_clone.process(action_taken, return_interactions=True)
        # print([(i.hash(),f) for i, f in zip(ints, f_ids)])
        f_idx_list = [f.feature_idx for f in feature_list]
        f_hashes = [f.hash() for f in feature_list]
        curr_goal_reward = self.__calculate_criteria(state_clone)
        crit_reward = self.criteria.reward(f_ids=f_ids,
                                           rewards=rewards,
                                           rew_mult=self.parameters.reward_multiplier,
                                           k_rew=self.parameters.over_rep_reward,
                                           u_rew=self.parameters.unknown_feature_reward,
                                           f_idx_list=f_idx_list,
                                           f_hashes=f_hashes,
                                           fulfilments=fulfilment)

        return crit_reward + (curr_goal_reward - prev_goal_reward)

    def __cache_state_action_score(self, *, state, action):
        """
        cache the state, action so that we can fetch its reward and new state hash
        easily
        :param state: state
        :param action: action
        :return: score, hash of state after taking the action
        """
        s = self.state_action_hash.get(state.hash(), None)
        a_idx = self.avatar.get_action_index(action)
        if s:
            score, state_hash = s.get(a_idx, (None, None))
            if score and state_hash:
                return score, state_hash
            else:
                # insert action to s
                score, state_hash = self.__state_action_score_hash(action, state)
                s[a_idx] = (score, state_hash)
                return score, state_hash
        else:
            init_hash = state.hash()
            score, state_hash = self.__state_action_score_hash(action, state)
            self.state_action_hash[init_hash] = {a_idx: (score, state_hash)}
            return score, state_hash

    def __state_action_score_hash(self, action, state):
        """
        applies the action to the state generates the hash, then loads the state back
        :param action: action
        :param state: state
        :return: score, state_hash
        """
        score = self.__calculate_state_action_score(action_taken=action, state_clone=state)
        state_hash = state.hash()
        state.load()
        return score, state_hash

    def __tree_add(self, state, *, action=None, parent_mcts_data=None):
        """
        adds the given state to the tree, if there is a parent updates the parent hierarchy
        if the state is terminal also marks the state as terminal
        :param state: state
        :param action: action taken to get to this state from parent
        :param parent_mcts_data: parent_mcts_data state
        :return: created mcts_data
        """
        state_hash = state.hash()
        if parent_mcts_data:
            parent_depth = parent_mcts_data.depth
        else:
            parent_depth = -1

        mcts_data = self.hash_mcts_data.get(state_hash, None)
        if mcts_data and parent_mcts_data:
            # order is important
            if mcts_data.add_parent(parent_mcts_data, action):
                self.__update_new_parent(mcts_data, parent_mcts_data, action)

        else:
            self.hash_mcts_data[state_hash] = MCTSData(state=state,
                                                       action=action,
                                                       visit=0, score=0,
                                                       depth=parent_depth + 1,
                                                       is_terminal=state.is_game_over(),
                                                       parent=parent_mcts_data)

        if state_hash not in self.ucb_children:
            self.ucb_children.add(state_hash)

        return self.hash_mcts_data[state_hash]

    def __expand(self, mcts_data):
        """
        expands the given state by adding its children to the tree
        the child added to the tree is from the action order starting from 0 to n
        the child added is returned if all children is added and this node is still
        more well continue with the same state
        :param mcts_data: where children come from, parent
        :return: a child state most probably
        """
        available_actions = self.avatar.get_actions()
        child_mcts_data = None  # start with None and update this when we find an available child

        children = []
        for action in available_actions:
            state = mcts_data.state
            state.process(action)

            if state.hash() not in self.ucb_children:
                cand_mcts_data = self.__tree_add(state, action=action, parent_mcts_data=mcts_data)
                child_mcts_data = cand_mcts_data
            state.load()

        if child_mcts_data:
            return child_mcts_data
        else:
            # take a random child
            if children:
                import random
                r = random.randint(0, len(children) - 1)
                return self.hash_mcts_data[children[r]]
            else:
                # no child just return the parent
                return mcts_data

    def __update_new_parent(self, mcts_data, parent_mcts_data, action):
        """
        a new parent is added to a already known child, therefore we can use its already
        evaluated value, as described in Transpositions and Move Groups http://www.csse.uwa.edu.au/cig08/Proceedings/papers/8057.pdf
        UCT3 is used
        Iteratively updates all parents
        :param mcts_data: already known child data
        :param parent_mcts_data: newly added parent
        :param action: action taken to come from parent to child
        :return: None
        """
        if mcts_data.is_updated:
            return
        else:
            mcts_data.is_updated = True

        total_score = 0
        if mcts_data and action:
            score, state_hash = self.__cache_state_action_score(state=mcts_data.state, action=action)
            total_score += score

        gamma = self.parameters.gamma
        avg_score = gamma * mcts_data.score + total_score

        parent_mcts_data.update_score(score=avg_score)
        if parent_mcts_data.parents:
            for parent, action in zip(parent_mcts_data.parents, parent_mcts_data.actions):
                self.__update_new_parent(parent_mcts_data, parent, action)

    def __set_parameters(self, parameters):
        if parameters:
            self.parameters = parameters

    def __ready_iteration(self):
        for value in self.hash_mcts_data.values():
            value.is_updated = False

    def get_prev_graph(self):
        return self.hash_mcts_data

    def clear(self):
        """
        clears the memory
        :return:
        """
        self.hash_mcts_data = {}
        self.ucb_children = set()
        self.state_action_hash = {}
