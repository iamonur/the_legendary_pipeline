class MCTSParameters:
    def __init__(self, *,
                 simulation_time_ms=300,
                 rollout_length=8,
                 gamma=0.95,
                 exploration_constant=3,
                 tree_depth=1,
                 goal_value=100,
                 fulfilment_threshold=0.01,
                 game_length=100,
                 reward_multiplier=1,
                 over_rep_reward=-0.5,
                 unknown_feature_reward=-1,
                 prev_graph=False,
                 verbose=True):
        """
        Structure of MCTS parameters
        :param simulation_time_ms: simulation time in ms
        :param rollout_length: rollout length of one simulation, currently random rollout is used
        :param gamma: decay value of future rewards
        :param exploration_constant: UCT exploration constant
        :param tree_depth: depth to be explored by MCTS, used during expansion
        :param goal_value: reward to be obtained for playing according to criteria
        :param fulfilment_threshold: threshold for criteria fulfilment
        :param verbose: verbose flag
        """
        self.simulation_time_ms = simulation_time_ms
        self.rollout_length = rollout_length
        self.gamma = gamma
        self.exploration_constant = exploration_constant
        self.tree_depth = tree_depth
        self.goal_value = goal_value
        self.fulfilment_threshold = fulfilment_threshold
        self.game_length = game_length
        self.reward_multiplier = reward_multiplier
        self.over_rep_reward = over_rep_reward
        self.unknown_feature_reward = unknown_feature_reward
        self.prev_graph = prev_graph
        self.verbose = verbose

    def __str__(self):
        import pprint
        return pprint.pformat(self.__dict__, indent=4)

    def __repr__(self):
        import pprint
        return pprint.pformat(self.__dict__, indent=4)
