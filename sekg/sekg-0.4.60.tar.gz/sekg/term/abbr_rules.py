#!/usr/bin/env python
# -*- conding: utf-8 -*-
from abc import abstractmethod, ABCMeta
import re
import textdistance


class Rule(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def extract(self, sentence):
        pass


class Rule4Bracket(Rule):
    PATTERN = re.compile(r'(\(.*?\))')
    UPPER = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    def __init__(self):
        pass

    def extract(self, text):
        # print(text)
        term_set = set()
        pairs = set()
        for term in self.PATTERN.findall(text):
            cleaned_term = re.sub("'s|’s", "", term)
            cleaned_term = cleaned_term.strip(" '\",.?*/\\‘’()[]")
            index = text.index(term)
            # print(term)
            if index == 0:
                continue
            # abbreviation in bracket
            if len(cleaned_term.split()) == 1:
                if len(cleaned_term) == 1 or len(cleaned_term) > 5:
                    continue
                abbreviation = cleaned_term
                words = text[:index].strip().split()[-(len(cleaned_term) + 1):]

            # full name in bracket
            else:
                abbreviation = text[:index].strip().split()[-1]
                words = cleaned_term.split()
            # print(abbreviation, words)
            upper_count = 0
            for letter in abbreviation:
                if letter in self.UPPER:
                    upper_count += 1
            if upper_count == 0 or len(abbreviation) / upper_count > 2:
                continue
            full_name = self.search(abbreviation, words)
            if full_name is not None:
                term_set.add(abbreviation)
                term_set.add(full_name)
                pairs.add((full_name, abbreviation))

        return term_set, pairs

    def search(self, letters, words):
        temp_letters = letters.lower()
        temp_words = [w.lower() for w in words[:]]

        for i in range(len(temp_words) - 1, -1, -1):
            if temp_words[i][0] == temp_letters[0]:
                # print(temp_words[i:])
                index = self.BFS(temp_letters, temp_words[i:], i)
                if index != -1:
                    name = " ".join(words[i:])
                    if not name.lower().startswith(letters.lower()):
                        return name
        return None

    def BFS(self, letters, words, index):
        if len(letters) == 0:
            return index
        if letters[0] != words[0][0]:
            return -1
        if len(letters) == 1:
            return index + 1
        if len(words) == 1:
            if textdistance.levenshtein(words[0], letters) == len(words[0]) - len(letters):
                return index + 1
            else:
                return -1
        Queue = []
        Queue.append((letters[1:], words[1:]))
        i, j = 1, 1
        for i in range(1, len(letters), 1):
            if j != len(words[0]) and letters[i] in words[0][j:]:
                Queue.append((letters[i + 1:], words[1:]))
            j += 1
        # print(Queue)
        while len(Queue) != 0:
            (l, w) = Queue.pop(0)
            temp = self.BFS(l, w, index + 1)
            # print(temp)
            if temp == -1 and len(Queue) == 0:
                return temp
            elif temp != -1:
                return temp


class Rule4Colon(Rule):
    PATTERN = re.compile(r' ?([a-zA-Z0-9\-]+\+{0,2}) ?:')
    UPPER = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    def __init__(self):
        pass

    def extract(self, text):
        term_set = set()
        pairs = set()
        for term in self.PATTERN.findall(text):
            cleaned_term = re.sub("'s|’s", "", term)
            cleaned_term = cleaned_term.strip(" '\",.?*/\\‘’()[]")
            index = text.index(term)
            if index == len(text) - 1:
                continue
            # abbreviation in bracket
            if len(cleaned_term.split()) == 1:
                if len(cleaned_term) == 1 or len(cleaned_term) > 5:
                    continue
                abbreviation = cleaned_term
                words = text[index + 1:].strip().split()[:len(cleaned_term) + 1]

            upper_count = 0
            for letter in abbreviation:
                if letter in self.UPPER:
                    upper_count += 1
            if upper_count == 0 or len(abbreviation) / upper_count > 2:
                continue
            full_name = self.search(abbreviation, words)

            if full_name is not None:
                term_set.add(abbreviation)
                term_set.add(full_name)
                pairs.add((full_name, abbreviation))
        return term_set, pairs

    def search(self, letters, words):
        temp_letters = letters.lower()
        temp_words = [w.lower() for w in words[:]]

        for i in range(len(temp_words) - 1, -1, -1):
            if temp_words[i][0] == temp_letters[0]:
                # print(temp_words[i:])
                index = self.BFS(temp_letters, temp_words[i:], i)
                if index != -1:
                    name = " ".join(words[i:])
                    if not name.lower().startswith(letters.lower()):
                        return name
        return None

    def BFS(self, letters, words, index):
        if len(letters) == 0:
            return index
        if letters[0] != words[0][0]:
            return -1
        if len(letters) == 1:
            return index + 1
        if len(words) == 1:
            if textdistance.levenshtein(words[0], letters) == len(words[0]) - len(letters):
                return index + 1
            else:
                return -1
        Queue = []
        Queue.append((letters[1:], words[1:]))
        i, j = 1, 1
        for i in range(1, len(letters), 1):
            if j != len(words[0]) and letters[i] in words[0][j:]:
                Queue.append((letters[i + 1:], words[1:]))
            j += 1
        # print(Queue)
        while len(Queue) != 0:
            (l, w) = Queue.pop(0)
            temp = self.BFS(l, w, index + 1)
            # print(temp)
            if temp == -1 and len(Queue) == 0:
                return temp
            elif temp != -1:
                return temp
