import gym
from datetime import timedelta, date
from math import log

import numpy as np
from mercury.client.model.option_single import OptionSingle
from mercury.client.model.position import Position
from mercury.envs.api_client import Client
from mercury.envs.utils import *  


class OptionsEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, host=None, trade_id=None, rand=True):
        """
        :param string host: host URL of the platform to connect to
        :param bool rand: Env randomization
        """
        if host is None or len(host) <= 0:
            raise ValueError("Environment URL host has to be defined")

        if trade_id is None or len(trade_id) <= 0:
            raise ValueError("Trade id for the environment has to be defined")

        self._client = Client(host=host)
        self._rand = rand

        # private vars
        self._trade_id = trade_id
        self._state = None
        self._position = None
        self._trade_list = None
        self._start_date = None
        self._end_date = None
        self._expiration = None
        self._pnl_and_margin_date = None
        self._s_expiration = None
        self._s_price = None
        self._seq_len = None
        self._adjustment_num = None
        self._init_adjustment_n = None
        self._end_of_episode = None
        self._opening_date = None
        self._episode_pnl = None
        self._episode_margin = None
        self._total_reward = 0

        # action and observation space
        self.action_space = gym.spaces.Box(low=-np.inf, high=+np.inf, shape=(SEQ_LEN * 4,))
        self.observation_space = gym.spaces.Dict(
            {"price": gym.spaces.Box(low=-np.inf, high=+np.inf, shape=(NUM_PRICE * 4,)),
             "trade": gym.spaces.Box(low=-np.inf, high=+np.inf, shape=(NUM_TRADE * 4,)),
             "timestep": gym.spaces.Box(low=-np.inf, high=+np.inf, shape=(2,))})

        # reset environment
        self.reset()

    def reset(self):
        """
        Resets environment
        :return tuple: Current state, done
        """
        position, trade_list, start_date, end_date, expiration, s_expiration, s_price = \
            self._client.get_fiddle(self._trade_id)

        self._position = Position(trades=list(position.trades))
        self._trade_list = list(trade_list)
        self._start_date = start_date
        self._end_date = end_date
        self._expiration = expiration
        self._pnl_and_margin_date = expiration - timedelta(days=1)
        self._s_expiration = s_expiration
        self._s_price = s_price
        self._seq_len = len(trade_list)
        self._adjustment_num = self._init_adjustment_n = NUM_TRADE - self._seq_len
        self._end_of_episode = expiration - timedelta(days=STOP_BEFORE)

        random_seed = np.random.randint(0, (expiration - timedelta(days=STOP_BEFORE) - end_date).days - 5)
        self._opening_date = end_date + timedelta(days=random_seed * int(self._rand))

        self._state = self._next_state()

        self._episode_pnl = self._client.calculate_instant_decomposed_pnl(
            self._position, self._start_date, self._pnl_and_margin_date)

        self._episode_margin = self._client.get_margin(self._position, self._pnl_and_margin_date)

        self._total_reward = 0.0

        return self._state, False

    def step(self, action):
        """
        Takes given action in the environment

        :param np.array action: Agent's action

        :return tuple: Observation (new state), reward, pnl, done
        """
        single_trades = []
        for i in range(0, 4 * SEQ_LEN, 4):
            if action[i] == 0:
                self._adjustment_num -= 1
                self._seq_len += 1

                adjustment = [
                    DELTA_RANGE[action[i + 2]],
                    self._get_timestep(),
                    (1.0 - 2.0 * action[i + 1]) * (action[i + 3] + 1.0)
                ]

                single, strike, underlying = self._action2single(adjustment)

                single_trades.append(single)
                adjustment[0] = strike
                adjustment[2] = adjustment[2] / NUM_QUANTITY
                adjustment.append(underlying)

                self._trade_list.append(adjustment)

        reward = 0.0
        if len(single_trades) != 0:
            self._position.trades.extend(single_trades)

            pnl = self._client.calculate_instant_decomposed_pnl(
                self._position, self._start_date, self._pnl_and_margin_date)

            margin = self._client.get_margin(self._position, self._pnl_and_margin_date)

            if margin < -MARGIN:
                reward = -10.0
            else:
                reward = self._log(pnl) - self._log(self._episode_pnl) + 0.1 * (
                        self._log(margin) - self._log(self._episode_margin))

            self._episode_pnl = pnl
            self._episode_margin = margin

        self._total_reward += reward

        self._state = self._next_state()

        return self._state, reward, self._episode_pnl, self.check_done()

    def shape(self):
        """
        Returns shape of the state and action

        :return dict: State and action shape
        """
        return {
            'state': (NUM_PRICE * 4 + NUM_TRADE * 4 + 2,),
            'action': (SEQ_LEN * 4,)
        }

    def get_position(self):
        """
        Returns current position

        :return Position: Current position
        """
        return self._position

    def is_adjusted(self):
        """
        Checks if agent made any adjustments

        :return bool:
        """
        return self._init_adjustment_n > self._adjustment_num

    def get_stats(self):
        """
        Returns statistics of episode

        :return tuple: PnL, margin, cumulative reward
        """
        return self._episode_pnl, self._episode_margin, self._total_reward

    def _trade_state_padding(self):
        """
        Pads trade state

        :return list: Padded trade state
        """
        padded_trades = []
        padded_trades.extend(self._trade_list)
        padded_trades.extend([[0.0, 0.0, 0.0, 0.0]] * (NUM_TRADE - len(self._trade_list)))

        return padded_trades

    def state(self):
        """
        State of the environment

        :return np.array: State
        """
        return self._state

    def _next_state(self):
        """
        Next state of the environment

        :return np.array: State
        """
        self._next_trading_day()

        price = np.reshape(self._client.get_equity_quote_before(self._opening_date, NUM_PRICE, self._s_price),
                           [NUM_PRICE * 4])

        trade = np.reshape(self._trade_state_padding(), [-1])  # [num_trade * 4] except for end state

        timestep = np.reshape([self._get_timestep(), self._seq_len], [2])

        return {"price": price, "trade": trade, "timestep": timestep}

    def _get_timestep(self):
        """
        Returns current timestep

        :return float: Timestep
        """
        return ((self._expiration - self._opening_date).days - STOP_BEFORE) / self._s_expiration

    def _next_trading_day(self):
        """
        Finds next trading day
        """
        self._opening_date += timedelta(days=1)

        while not self._client.is_trading_day(self._opening_date):
            self._opening_date += timedelta(days=1)

    def check_done(self):
        """
        Checks if the episode is done

        :return bool: True if done, false otherwise
        """
        if self._adjustment_num <= 0 or self._opening_date > self._end_of_episode \
                or self._episode_margin < -MARGIN:
            return True

        return False

    def _action2single(self, adjustment, symbol='SPX'):
        """
        Creates single trade using action from policy at time step t_i

        :param list adjustment: Agent's action
        :param string symbol: Symbol

        :return tuple: Single, strike, underlying
        """
        contract = self._client.get_closest_strike_to_delta(OptionContractType.PUT,
                                                            self._opening_date,
                                                            self._expiration,
                                                            -1.0 * adjustment[0])

        closing_price = self._client.get_equity_quote(self._opening_date)[1]

        single = OptionSingle(symbol=symbol,
                              quantity=adjustment[2],
                              opening_date=self._opening_date,
                              option_contract=contract)

        return single, log(contract.strike) - closing_price, closing_price - self._s_price

    def _log(self, x):
        """
        Computes log of values in range [-inf, inf]

        :param float x: Value

        :return: Log value
        """
        return -log(-x + 1.0) if x < 0.0 else log(x + 1.0)

    def render(self, mode='human'):
        pass

    def close(self):
        pass
