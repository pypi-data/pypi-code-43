# -*- coding: utf-8 -*-
import unittest
from pynlple.processing.mention import cut_text_with_highlights_if_present


class MentionUtilityTest(unittest.TestCase):

    def test_should_not_cut_text_w_highlights(self):
        text = 'this text contains highlights\r\nand new lines so that i can test the utility method\r\n' \
               'some additional lines are added for longer text'
        highlights = [{'start': 5, 'end': 9}, {'start': 45, 'end': 47}, {'start': 100, 'end': 105}]

        expected_text = text
        expected_highlights = highlights
        result_text, result_highlights = cut_text_with_highlights_if_present(text, highlights)
        self.assertEqual(expected_text, result_text)
        self.assertEqual(expected_highlights, result_highlights)

    def test_should_not_cut_text_w_no_highlights(self):
        text = 'this text contains highlights\r\nand new lines so that i can test the utility method\r\n' \
               'some additional lines are added for longer text'
        highlights = []

        expected_text = text
        expected_highlights = highlights
        result_text, result_highlights = cut_text_with_highlights_if_present(text, highlights)
        self.assertEqual(expected_text, result_text)
        self.assertEqual(expected_highlights, result_highlights)

    def test_should_cut_text_w_highlights_in_title(self):
        text = 'this text contains highlights\r\nand new lines so that i can test the utility method\r\n' \
               'some additional lines are added for longer text'
        highlights = [{'start': 5, 'end': 9}]

        expected_text = text[:29]
        expected_highlights = highlights
        result_text, result_highlights = cut_text_with_highlights_if_present(text, highlights)
        self.assertEqual(expected_text, result_text)
        self.assertEqual(expected_highlights, result_highlights)

    def test_should_cut_text_w_highlights_in_title_multiple(self):
        text = 'this text contains highlights\r\nand new lines so that i can test the utility method\r\n' \
               'some additional lines are added for longer text'
        highlights = [{'start': 10, 'end': 14}]

        expected_text = text[:29]
        expected_highlights = highlights
        result_text, result_highlights = cut_text_with_highlights_if_present(text, highlights)
        self.assertEqual(expected_text, result_text)
        self.assertEqual(expected_highlights, result_highlights)

    def test_should_cut_text_w_highlights_in_body(self):
        text = 'this text contains highlights\r\nand new lines so that i can test the utility method\r\n' \
               'some additional lines are added for longer text'
        highlights = [{'start': 45, 'end': 47}, {'start': 100, 'end': 105}]

        expected_text = text[31:]
        expected_highlights = highlights
        result_text, result_highlights = cut_text_with_highlights_if_present(text, highlights)
        self.assertEqual(expected_text, result_text)
        self.assertEqual(expected_highlights, result_highlights)

    def test_should_cut_text_w_highlights_in_body_html_mixed_entities(self):
        text = 'this text contains highlights&#10;and new lines so that i can test the utility method\n' \
               'some additional lines are added for longer text'
        highlights = [{'start': 45, 'end': 47}, {'start': 100, 'end': 105}]

        expected_text = text[34:]
        expected_highlights = highlights
        result_text, result_highlights = cut_text_with_highlights_if_present(text, highlights)
        self.assertEqual(expected_text, result_text)
        self.assertEqual(expected_highlights, result_highlights)

    def test_should_cut_text_w_highlights_in_body_html_mixed_entities_swapped(self):
        text = 'this text contains highlights\nand new lines so that i can test the utility method&#10;' \
               'some additional lines are added for longer text'
        highlights = [{'start': 45, 'end': 47}, {'start': 100, 'end': 105}]

        expected_text = text[30:]
        expected_highlights = highlights
        result_text, result_highlights = cut_text_with_highlights_if_present(text, highlights)
        self.assertEqual(expected_text, result_text)
        self.assertEqual(expected_highlights, result_highlights)

    def test_should_cut_text_w_highlights_in_title_highlight_overlaps_cut(self):
        text = 'this text contains highlights\r\nand new lines so that i can test the utility method\r\n' \
               'some additional lines are added for longer text'
        highlights = [{'start': 20, 'end': 31}]

        expected_text = text[:29]
        expected_highlights = [{'start': 20, 'end': 29}]
        result_text, result_highlights = cut_text_with_highlights_if_present(text, highlights)
        self.assertEqual(expected_text, result_text)
        self.assertEqual(expected_highlights, result_highlights)

    def test_should_cut_text_w_highlights_in_title_highlight_borders_cut(self):
        text = 'this text contains highlights\r\nand new lines so that i can test the utility method\r\n' \
               'some additional lines are added for longer text'
        highlights = [{'start': 20, 'end': 28}]

        expected_text = text[:29]
        expected_highlights = [{'start': 20, 'end': 28}]
        result_text, result_highlights = cut_text_with_highlights_if_present(text, highlights)
        self.assertEqual(expected_text, result_text)
        self.assertEqual(expected_highlights, result_highlights)

    def test_should_cut_text_w_multiple_highlights_in_title_highlight_overlaps_cut(self):
        text = 'this text contains highlights\r\nand new lines so that i can test the utility method\r\n' \
               'some additional lines are added for longer text'
        highlights = [{'start': 5, 'end': 9}, {'start': 20, 'end': 31}]

        expected_text = text[:29]
        expected_highlights = [{'start': 5, 'end': 9}, {'start': 20, 'end': 29}]
        result_text, result_highlights = cut_text_with_highlights_if_present(text, highlights)
        self.assertEqual(expected_text, result_text)
        self.assertEqual(expected_highlights, result_highlights)

    def test_should_cut_text_w_highlights_in_body_overlaps_cut(self):
        text = 'this text contains highlights\r\nand new lines so that i can test the utility method\r\n' \
               'some additional lines are added for longer text'
        highlights = [{'start': 30, 'end': 36}]

        expected_text = text[31:]
        expected_highlights = [{'start': 31, 'end': 36}]
        result_text, result_highlights = cut_text_with_highlights_if_present(text, highlights)
        self.assertEqual(expected_text, result_text)
        self.assertEqual(expected_highlights, result_highlights)

    def test_should_cut_text_w_multiple_highlights_in_body_overlaps_cut(self):
        text = 'this text contains highlights\r\nand new lines so that i can test the utility method\r\n' \
               'some additional lines are added for longer text'
        highlights = [{'start': 30, 'end': 36}, {'start': 100, 'end': 105}]

        expected_text = text[31:]
        expected_highlights = [{'start': 31, 'end': 36}, {'start': 100, 'end': 105}]
        result_text, result_highlights = cut_text_with_highlights_if_present(text, highlights)
        self.assertEqual(expected_text, result_text)
        self.assertEqual(expected_highlights, result_highlights)

    def test_should_cut_text_w_multiple_highlights_in_body_borders_cut(self):
        text = 'this text contains highlights\r\nand new lines so that i can test the utility method\r\n' \
               'some additional lines are added for longer text'
        highlights = [{'start': 31, 'end': 36}, {'start': 100, 'end': 105}]

        expected_text = text[31:]
        expected_highlights = [{'start': 31, 'end': 36}, {'start': 100, 'end': 105}]
        result_text, result_highlights = cut_text_with_highlights_if_present(text, highlights)
        self.assertEqual(expected_text, result_text)
        self.assertEqual(expected_highlights, result_highlights)

    def test_should_cut_text_w_highlights_in_body_html_single_entities(self):
        text = 'this text contains highlights&#10;and new lines so that i can test the utility method&#10;' \
               'some additional lines are added for longer text'
        highlights = [{'start': 45, 'end': 47}, {'start': 100, 'end': 105}]

        expected_text = text[34:]
        expected_highlights = highlights
        result_text, result_highlights = cut_text_with_highlights_if_present(text, highlights)
        self.assertEqual(expected_text, result_text)
        self.assertEqual(expected_highlights, result_highlights)

    def test_should_cut_text_w_highlights_in_body_html_double_entities(self):
        text = 'this text contains highlights&#13;&#10;and new lines so that i can test the utility method&#13;&#10;' \
               'some additional lines are added for longer text'
        highlights = [{'start': 45, 'end': 47}, {'start': 100, 'end': 105}]

        expected_text = text[39:]
        expected_highlights = highlights
        result_text, result_highlights = cut_text_with_highlights_if_present(text, highlights)
        self.assertEqual(expected_text, result_text)
        self.assertEqual(expected_highlights, result_highlights)

    def test_should_cut_text_w_highlights_in_body_html_double_entities_swapped(self):
        text = 'this text contains highlights&#10;&#13;and new lines so that i can test the utility method&#10;&#13;' \
               'some additional lines are added for longer text'
        highlights = [{'start': 45, 'end': 47}, {'start': 100, 'end': 105}]

        expected_text = text[39:]
        expected_highlights = highlights
        result_text, result_highlights = cut_text_with_highlights_if_present(text, highlights)
        self.assertEqual(expected_text, result_text)
        self.assertEqual(expected_highlights, result_highlights)

    def test_should_cut_text_w_highlights_body_real_case(self):
        text = "Подетальная обклейка автомобиля пленкой такси.\r\nНаш сайт http://www.rbtax.ru/ Телефон 8(800) " \
               "707 10-75  или 8(499) 499 10-75 Группа VK: https://vk.com/rbtaxru Работа в #Яндекс такси  Отзыв " \
               "нового водителя Оклеивание отдельной детали ремонт пленки для такси. Такси ГОСТ Желтый цвет под " \
               "такси Как оклеить такси самому. Оклейка авто по ГОСТу 4000р при оклейки авто полностью скидка! " \
               "Специфика ухода за пленкой под такси. Пленка оклейка Оклейка такси по гост магниты яндекс бренд " \
               "Работа в такси без лицензии Обклейка автомобиля / Реклама на автомобилях"
        highlights = [{"end": 174, "start": 169}, {"end": 180, "start": 176}]
        expected_text = text[48:]
        expected_highlights = highlights
        result_text, result_highlights = cut_text_with_highlights_if_present(text, highlights)
        self.assertEqual(expected_text, result_text)
        self.assertEqual(expected_highlights, result_highlights)