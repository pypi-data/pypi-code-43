#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright (C) 2019 Brandon M. Pace
#
# This file is part of contentmatcher
#
# contentmatcher is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# contentmatcher is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with contentmatcher.
# If not, see <https://www.gnu.org/licenses/>.


import copy

from typing import Any, Collection, Dict, Iterable, List, Sequence, Set, Tuple


class Pattern(object):
    __slots__ = '_data', '_frozenset', '_list', '_list_len'

    def __init__(self, data: Collection):
        """
        Initializes a Pattern object
        :param data: An object that is both Iterable and Sized (e.g. list, set, str)
        """
        self._data = copy.copy(data)
        self._list = (data.copy() if isinstance(data, list) else list(data))
        self._list_len = len(self._list)
        if not self._list_len:
            raise ValueError('data must not be empty')
        self._frozenset = frozenset(data)

    def fast_match_ratio(self, other: Iterable) -> float:
        """
        The ratio of unique matched objects in the pattern to total unique objects in the pattern.
        Recommended as a first-pass match.
        :param other: Iterable object to match against
        :return: float with value from 0.0 to 1.0
        """
        return len(self._frozenset.intersection(other)) / len(self._frozenset)

    def intersection(self, other: Iterable) -> frozenset:
        """
        Return a frozenset with values that appear in self and other
        :param other: Iterable object to match against
        :return: frozenset
        """
        return self._frozenset.intersection(other)

    def longest_ordered_chunk_match_ratio(self, other: Sequence) -> float:
        """
        The ratio of the longest matching chunk of the pattern to total length of the pattern.
        This is useful when your patterns are shorter than the data you are checking.
        It indicates the percentage of the pattern that appears in the other data. (in the same order as the pattern)
        :param other: Iterable object to match against
        :return: float with value from 0.0 to 1.0
        """
        completed_chunks: List[Dict[str, Any]] = []
        last_pattern_index = self._list_len - 1
        longest_chunk = 0
        matches: List[Dict[str, Any]] = []

        for item in other:
            for match in matches:
                if item == match['expected']:
                    current_index = match['last'] + 1
                    match['last'] = current_index
                    if current_index < last_pattern_index:
                        match['expected'] = self._list[current_index + 1]
                    else:
                        # reached last pattern index
                        chunk_size = match['last'] - match['first'] + 1
                        if chunk_size > longest_chunk:
                            longest_chunk = chunk_size
                        completed_chunks.append(match)
                else:
                    # chunk no longer matches
                    chunk_size = match['last'] - match['first'] + 1
                    if chunk_size > longest_chunk:
                        longest_chunk = chunk_size
                    completed_chunks.append(match)

            if completed_chunks:
                for chunk in completed_chunks:
                    matches.remove(chunk)
                completed_chunks.clear()

            if item in self._frozenset:
                for index, check_item in enumerate(self._list):
                    if item == check_item:
                        if index == last_pattern_index:
                            if longest_chunk == 0:
                                longest_chunk = 1
                        else:
                            matches.append({'first': index, 'last': index, 'expected': self._list[index + 1]})

        for match in matches:
            # address any in-progress matches
            chunk_size = match['last'] - match['first'] + 1
            if chunk_size > longest_chunk:
                longest_chunk = chunk_size

        matches.clear()

        return longest_chunk / self._list_len

    def ordered_chunk_matches(self, other: Sequence) -> Set[Tuple]:
        """
        Get the matching ordered chunks of the pattern found in other
        :param other: Iterable object to match against
        :return: set of tuple objects containing the unique chunks of the pattern that were found in other
        """
        chunks_found: Set[Tuple] = set()
        completed_chunks: List[Dict[str, Any]] = []
        last_pattern_index = self._list_len - 1
        matches: List[Dict[str, Any]] = []

        for item in other:
            for match in matches:
                if item == match['expected']:
                    current_index = match['last'] + 1
                    match['last'] = current_index
                    match['data'].append(item)
                    if current_index < last_pattern_index:
                        match['expected'] = self._list[current_index + 1]
                    else:
                        # reached last pattern index
                        completed_chunks.append(match)
                else:
                    # chunk no longer matches
                    completed_chunks.append(match)

            if completed_chunks:
                for chunk in completed_chunks:
                    chunks_found.add(tuple(chunk['data']))
                    matches.remove(chunk)
                completed_chunks.clear()

            if item in self._frozenset:
                for index, check_item in enumerate(self._list):
                    if item == check_item:
                        chunks_found.add((item,))
                        if index != last_pattern_index:
                            matches.append(
                                {'data': [item], 'first': index, 'last': index, 'expected': self._list[index + 1]}
                            )

        for match in matches:
            # address any in-progress matches
            chunks_found.add(tuple(match['data']))

        matches.clear()

        return chunks_found
