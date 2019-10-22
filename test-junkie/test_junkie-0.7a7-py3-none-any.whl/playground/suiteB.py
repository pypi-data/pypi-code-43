# # -*- encoding: utf-8 -*-
# import datetime
# import time
# from random import randint
#
# from playground.Browser import Browser
# from test_junkie.decorators import Suite, test
# from tests.junkie_suites.TestListener import TestListener
#
#
# @Suite(retry=2,
#        listener=TestListener,
#        meta={"name": "Suite B", "known_bugs": []},
#        parameters=[1, 2], priority=1, feature="Store",
#        owner="George")
# class ShoppingCartSuite:
#
#     @test(priority=1,
#           component="Shopping Cart",
#           tags=["ui", "cart", "positive_flow"])
#     def add_to_cart(self):
#         # print(datetime.datetime.now())
#         # print("асдфсадфа")
#         # time.sleep(randint(0, 7))
#         # print("Finished SUITE B / TEST A")
#         print("1add_to_cart: ", Browser.get_driver())
#         print("2add_to_cart: ", Browser.get_driver())
#         print("3add_to_cart: ", Browser.get_driver())
#
#     @test(priority=1,
#           component="Shopping Cart",
#           tags=["ui", "cart", "positive_flow"])
#     def remove_from_cart(self):
#         # time.sleep(randint(0, 4))
#         print("1remove_from_cart: ", Browser.get_driver())
#         print("2remove_from_cart: ", Browser.get_driver())
#         print("3remove_from_cart: ", Browser.get_driver())
#
#     @test(priority=1,
#           component="Shopping Cart",
#           tags=["ui", "cart", "positive_flow"])
#     def increase_quantity(self):
#         # time.sleep(randint(0, 4))
#         print("1increase_quantity: ", Browser.get_driver())
#         print("2increase_quantity: ", Browser.get_driver())
#         print("3increase_quantity: ", Browser.get_driver())
#
#     @test(priority=1,
#           component="Shopping Cart",
#           tags=["ui", "cart", "positive_flow"])
#     def decrease_quantity(self):
#         # time.sleep(randint(0, 4))
#         print("1decrease_quantity: ", Browser.get_driver())
#         print("2decrease_quantity: ", Browser.get_driver())
#         print("3decrease_quantity: ", Browser.get_driver())
#
#     @test(priority=1,
#           component="Shopping Cart",
#           tags=["ui", "cart", "positive_flow"])
#     def save_for_later(self):
#         # time.sleep(randint(0, 4))
#         print("1save_for_later: ", Browser.get_driver())
#         print("2save_for_later: ", Browser.get_driver())
#         print("3save_for_later: ", Browser.get_driver())
