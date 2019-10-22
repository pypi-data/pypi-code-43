import time
from random import randint

from test_junkie.decorators import Suite, test, beforeClass, beforeTest, afterTest, afterClass
from test_junkie.meta import meta, Meta
from tests.junkie_suites.TestListener import TestListener
from tests.junkie_suites.TestRules import TestRules


@Suite(retry=2,
       listener=TestListener,
       priority=2, feature="Store", owner="Mike", parameters=[1, 2])
class NewProductsSuite:

    ATT = 1

    @beforeClass()
    def before_class1(self):
        print("NewProductsSuite before class")
        # if NewProductsSuite.ATT == 2:
        #     raise Exception("Derp")
        # NewProductsSuite.ATT += 1

    # @beforeTest()
    # def before_test2(self):
    #     # write your code here
    #     pass
    #
    # @afterTest()
    # def after_test3(self):
    #     # write your code here
    #     pass
    #
    # @afterClass()
    # def after_class4(self):
    #     # write your code here
    #     pass

    # @test(component="Admin", tags=["store_management"])
    # def add_new_product(self, suite_parameter):
    #     # time.sleep(randint(0, 4))
    #     print("add_new_product")
    #
    # @test(component="Admin", tags=["store_management"])
    # def remove_product(self):
    #     # time.sleep(randint(0, 4))
    #     print("remove_product")
    #
    # @test(component="Admin", tags=["store_management"])
    # def publish_product(self):
    #     # time.sleep(randint(0, 4))
    #     print("publish_product")

    @test(component="Admin", tags=["store_management"], parameters=[10, 20], parallelized_parameters=True)
    def edit_product(self, parameter, suite_parameter):
        # time.sleep(randint(0, 4))
        print("edit_product")
        if suite_parameter == 2:
            raise Exception("Product not found")

    @test(component="Admin", tags=["store_management"])
    def archive_product(self):
        # time.sleep(randint(0, 4))
        print("archive_product")
        # raise Exception("Product not found")
