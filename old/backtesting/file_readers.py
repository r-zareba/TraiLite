#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 18:49:04 2019

@author: rafal
"""

import abc
import pandas as pd


class BaseFileReader:

    __slots__ = ('_file_path', )

    def __init__(self, file_path: str) -> None:
        self._file_path = file_path

    def _fix_path_from_qt(self) -> None:
        if self._file_path.startswith('file://'):
            self._file_path = self._file_path[7:]

    @staticmethod
    @abc.abstractmethod
    def check_data_source(file_path: str, data_source: str) -> bool:
        pass

    @abc.abstractmethod
    def read_data(self) -> pd.DataFrame:
        pass


class UnknownDataReader(BaseFileReader):

    @staticmethod
    def check_data_source(file_path: str, data_source: str) -> bool:
        pass

    def read_data(self) -> pd.DataFrame:
        pass


class DukascopyCSVReader(BaseFileReader):

    __slots__ = ()

    def __init__(self, file_path: str):
        super().__init__(file_path)

    @staticmethod
    def check_data_source(file_path: str, data_source: str) -> bool:
        return file_path.endswith('.csv') and data_source == 'dukascopy'

    def read_data(self) -> pd.DataFrame:
        self._fix_path_from_qt()
        df = pd.read_csv(self._file_path, index_col='Gmt time',
                         dayfirst=True, parse_dates=True)

        df.index.names = ['Date']
        return df


class FileReaderFactory:

    __slots__ = ('_file_path', '_data_source')

    def __init__(self, file_path: str, data_source: str) -> None:
        self._file_path = file_path
        self._data_source = data_source.lower()

    def get_file_reader(self) -> BaseFileReader:
        for Loader in BaseFileReader.__subclasses__():
            try:
                if Loader.check_data_source(
                        self._file_path, self._data_source):
                    return Loader(self._file_path)
            except KeyError:
                continue

        return UnknownDataReader(self._file_path)

