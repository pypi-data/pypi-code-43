# -*- coding: utf-8 -*-
import os

from . import cleanoutputdir
from . import generateorders
from . import getdata
from . import getserviceperson
from jmopenorders.core.logger import logger


def report(
        personfile="names.csv",
        datafile="data.csv",
        inputpath="home",
        outputpath="out",
) -> str:

    logger.debug("executing report command")

    # combine the inputpath with the personfile name
    persondata_file = os.path.join(os.path.abspath(inputpath), personfile)

    logger.debug("Personfile= %s", persondata_file)

    # Get the names of the persons to an arrary
    names = getserviceperson.GetServicePerson(persondata_file)
    berater = names.get()

    # Get the data
    data_file = os.path.join(os.path.abspath(inputpath), datafile)
    data = getdata.GetData(data_file)
    orders = data.get()

    cleanoutputdir.CleanOutputDir(os.path.abspath(outputpath))

    if type(berater) is list:
        for actual_berater in berater:
            logger.debug("actual_berater: " + actual_berater)
            berater_name = actual_berater
            logger.debug("Berater Name: " + berater_name)
            create_table = generateorders.GenerateOrders(outputpath)
            create_table.create(
                actual_name=berater_name,
                actual_content=orders,
            )
    else:
        logger.critical("Berater file is empty or not exist")

    return "Hello, {:s}!".format(personfile)
