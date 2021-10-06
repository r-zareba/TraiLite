#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 11:23:52 2019

@author: rafal
"""
import abc
import hyperopt
import numpy as np
import pandas as pd

# from . import technicals
# from . import file_readers

import technicals
import file_readers


class BaseTechnicalOptimizer:
    """
    Base class implementation - bayesian optimizer for searching
    best combintion of technical indicator strategy params
    """
    __slots__ = ('_file_path', '_file_source', '_param_space', '_fee',
                 '_priority', '_Backtester', '_market_data', '_trained',
                 '_best_params', '_hyperopt_space', '_trials')

    def __init__(self, file_path: str, file_source: str,
                 param_space: dict, fee: float,
                 priority: str = 'return'):

        self._file_path = file_path
        self._file_source = file_source
        self._param_space = param_space
        self._fee = fee
        self._priority = priority

        self._Backtester: technicals.BaseTechnicalsBacktester = None
        self._market_data = pd.DataFrame()
        self._trained = False
        self._best_params = dict()

        # Hyperopt
        self._hyperopt_space = dict()
        self._trials = hyperopt.Trials()

    @property
    def best_params(self) -> dict:
        if not self._trained:
            raise ValueError('Cannot get best params dict - '
                             'optimizer is not trained, use fit method first')
        return self._best_params

    def _prepare_data(self) -> None:
        """
        Sets '_market_data' attribute to keep that in memory
        This way while hyper optimization searching, data is not read
        from file every iteration
        """
        file_reader = file_readers.FileReaderFactory(
            self._file_path, self._file_source).get_file_reader()
        self._market_data = file_reader.read_data()

    @abc.abstractmethod
    def _init_hyperopt_space(self) -> None:
        """ Wraps object dict type param space to hyperopt dict type space """
        self._hyperopt_space = {
            'enter_interval': hyperopt.hp.choice(
                'enter_interval', self._param_space['enter_interval']),
            'exit_interval': hyperopt.hp.choice(
                'exit_interval', self._param_space['exit_interval']),
            'start_hour': hyperopt.hp.choice(
                'start_hour', self._param_space['start_hour']),
            'end_hour': hyperopt.hp.choice(
                'end_hour', self._param_space['end_hour'])
        }

    def _objective_function(self, params: dict) -> float:
        """ Function to minimize using bayesian hyperopt model """
        params['fee'] = self._fee
        backtester_model = self._Backtester(**params)
        backtester_model.fit_from_data(market_data=self._market_data)

        if self._priority == 'return':
            return 1 - backtester_model.strategy_return
        elif self._priority == 'drawdown':
            return backtester_model.maximum_drawdown

    def _save_best_params(self, best_dict: dict) -> None:
        """
        Translates indices to values from param_space
        By default hyperopt best_dict dictionary keeps only indices
        of params_space
        :param best_dict: Dict with best params found in optimiztion proccess
        """
        for k in best_dict:
            if isinstance(best_dict[k], float):
                self._best_params[k] = round(best_dict[k], 2)
            else:
                self._best_params[k] = self._param_space[k][best_dict[k]]

    def fit(self, n_iterations: int) -> None:
        """
        Starts Bayesian optimization
        Depends on data size, number of parameters to search, might take
        very long time - run it only in dedicated thread or process when
        MongoDB Trials are not set!
        """
        self._prepare_data()
        self._init_hyperopt_space()
        best_dict = hyperopt.fmin(fn=self._objective_function,
                                  space=self._hyperopt_space,
                                  algo=hyperopt.tpe.suggest,
                                  trials=self._trials,
                                  max_evals=n_iterations)

        self._save_best_params(best_dict=best_dict)
        self._trained = True


class StochasticOptimizer(BaseTechnicalOptimizer):
    """ Bayesian optimizer for Stochastic Indicator strategy """
    __slots__ = ()

    def __init__(self, file_path: str, file_source: str, param_space: dict,
                 fee: float, priority: str) -> None:
        super().__init__(file_path, file_source, param_space, fee, priority)
        self._Backtester = technicals.StochasticOscilatorBacktester

    def _init_hyperopt_space(self) -> None:
        super()._init_hyperopt_space()
        self._hyperopt_space['enter_k_period'] = hyperopt.hp.choice(
            'enter_k_period', self._param_space['enter_k_period'])
        self._hyperopt_space['enter_smooth'] = hyperopt.hp.choice(
            'enter_smooth', self._param_space['enter_smooth'])
        self._hyperopt_space['enter_d_period'] = hyperopt.hp.choice(
            'enter_d_period', self._param_space['enter_d_period'])
        self._hyperopt_space['exit_k_period'] = hyperopt.hp.choice(
            'exit_k_period', self._param_space['exit_k_period'])
        self._hyperopt_space['exit_smooth'] = hyperopt.hp.choice(
            'exit_smooth', self._param_space['exit_smooth'])
        self._hyperopt_space['exit_d_period'] = hyperopt.hp.choice(
            'exit_d_period', self._param_space['exit_d_period'])
        self._hyperopt_space['stoch_long_threshold'] = hyperopt.hp.uniform(
            'stoch_long_threshold',
            self._param_space['stoch_long_threshold'][0],
            self._param_space['stoch_long_threshold'][1])
        self._hyperopt_space['stoch_short_threshold'] = hyperopt.hp.uniform(
            'stoch_short_threshold',
            self._param_space['stoch_short_threshold'][0],
            self._param_space['stoch_short_threshold'][1])


#

# import objsize
path = '/Users/kq794tb/Desktop/TRAI_Lite/DAX_bid.csv'
file_source = 'dukascopy'

my_params = {
        'enter_interval': ['1T', '5T', '15T'],
        'exit_interval': ['1T', '5T', '15T'],
        'start_hour': np.arange(7, 10, dtype=int),
        'end_hour': np.arange(15, 19, dtype=int),
        'enter_k_period': np.arange(7, 14, dtype=int),
        'enter_smooth': np.arange(1, 3, dtype=int),
        'enter_d_period': np.arange(1, 3, dtype=int),
        'exit_k_period': np.arange(7, 14, dtype=int),
        'exit_smooth': np.arange(1, 3, dtype=int),
        'exit_d_period': np.arange(1, 3, dtype=int),
        'stoch_long_threshold': [5, 30],
        'stoch_short_threshold': [70, 90]
        }


optimizer = StochasticOptimizer(
    file_path=path, file_source=file_source, param_space=my_params,
    fee=0.0, priority='return')

optimizer.fit(n_iterations=100)
print(optimizer.best_params)
#
# print(objsize.get_deep_size(optimizer))
# optimizer.fit()










