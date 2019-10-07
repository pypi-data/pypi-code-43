#!/usr/bin/env python

import sys
import re
import logging
import json
import cv2
import os
from functools import wraps
import click
from click_aliases import ClickAliasedGroup
from tabulate import tabulate
from datetime import datetime, timedelta, date
from salesforce_expense.core import TimecardEntry
from salesforce_expense import __version__, __description__

logger = logging.getLogger("salesforce_expense")
handler = logging.StreamHandler(sys.stdout)
FORMAT = "[%(asctime)s][%(levelname)s] %(message)s"
handler.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

te = TimecardEntry()


CATEGORY = ["Accommodation", "Client entertainment", "Car hire", "Flights", "Fuel", "Internet", "IT consumables" , "IT services (subscription &amp; licences)", "Mileage",
    "Office supplies and comsumables", "Other", "Parking & Tolls", "Per Diem" , "Private Accommodation", "Professional training & Exam",
    "Staff entertainment", "Staff welfare", "Subsistence", "Taxi", "Trains", "Transport - other", "Weekly Groceries", "Telephony"]

def catch_exceptions(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        """
        Invokes ``func``, catches expected errors, prints the error message and
        exits sceptre with a non-zero exit code.
        """
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            click.echo(" bye bye")
        except:
            if len(str(sys.exc_info()[1])) > 0:
                logger.error(sys.exc_info()[1])
                sys.exit(1)

    return decorated


@click.group(cls=ClickAliasedGroup)
@click.version_option(prog_name=__description__, version=__version__)
@click.option("-v", "--verbose", is_flag=True, help="verbose")
@click.pass_context
def cli(ctx, verbose):  # pragma: no cover

    if verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("enabling DEBUG mode")
    ctx.obj = {
        "options": {}
    }


# def show_webcam(mirror=False):
#     cam = cv2.VideoCapture(0)
#     while True:
#         ret_val, img = cam.read()
#         if mirror: 
#             img = cv2.flip(img, 1)
#         cv2.imshow('Press ESC to get the image', img)
#         if cv2.waitKey(1) == 27: 
#             cv2.imwrite('camera.png', img)
#             break  # esc to quit
#     cv2.destroyAllWindows()

def show_webcam(image_name):
    capture = cv2.VideoCapture(0)
    if capture.isOpened() is False:
        raise("IO Error")
    name = "Press 'q' to get the image"
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    # cv2.setMouseCallback(name, on_mouse, 0)

    while True:
        ret, image = capture.read()
        if ret == False:
            continue

        cv2.imshow(name, image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.imwrite(image_name, image)
            break

    capture.release()
    cv2.destroyAllWindows()


# def on_mouse(event, x, y, flags, params):
#     # global img
#     t = time()
    
#     if event == cv2.EVENT_LBUTTONDOWN:
#         print ('Start Mouse Position: '+str(x)+', '+str(y))
#         sbox = [x, y]
#         boxes.append(sbox)
#              # print count
#              # print sbox
             
#     elif event == cv2.EVENT_LBUTTONUP:
#         print 'End Mouse Position: '+str(x)+', '+str(y)
#         ebox = [x, y]
#         boxes.append(ebox)
#         print boxes
#         crop = img[boxes[-2][1]:boxes[-1][1],boxes[-2][0]:boxes[-1][0]]

#         cv2.imshow('crop',crop)
#         k =  cv2.waitKey(0)
#         if ord('r')== k:
#             cv2.imwrite('Crop'+str(t)+'.jpg',crop)
#             print "Written to file"

@cli.command(name="add", aliases=["a", "ad"])
@click.option(
    "-p", "--project", default="", help="Project Name")
@click.option(
    "-d", "--description", default="", help="Description to add")
@click.option(
    "-a", "--amount", default=0,type=float ,  help="amount to add")
@click.option(
 "--date", default=date.today().strftime("%Y-%m-%d"), help="Date") 
@click.option(
    "--currency",
    type=click.Choice(["EUR", "USD" , "GBP", "NOK"]),
    default="EUR",
    help="currency")
@click.option(
    "--category",
    type=click.Choice(CATEGORY),
    default="Subsistence",
    help="category")
@click.option("--noreceipt", default=False, is_flag=True, help="Lost receipt") 
@click.option("--billable/--non-billable", default=True, help="billable flag")
@click.option(
    "--inpolicy",
    type=click.Choice(["Yes", "No"]),
    default="Yes",
    help="In Policy")
@click.option(
    "-f", "--filename", default="", help="Receipt")
@click.pass_context
@catch_exceptions
def add(ctx, project, description, amount, date, currency, category, noreceipt, billable, inpolicy, filename):
    assignment_id = None
    active_assignment = te.get_assignments_active()
    for _, assign in active_assignment.items():
        if project.lower() in assign["assignment_name"].lower() and len(project) > 2:
            logger.info("found :{}".format(assign["assignment_name"]))
            assignment_id = assign["assignment_id"]
            break

    if not assignment_id:
        nice_assign = []
        i = 0
        click.echo("Please choose which project:")
        for _, assign in active_assignment.items():
            click.echo("[{}] {}".format(i, assign["assignment_name"]))
            nice_assign.append(assign["assignment_id"])
            i += 1

        select_assign = input("Project Selection: ")
        assignment_id = nice_assign[int(select_assign)]
        
    project_id = active_assignment[assignment_id]["project_id"]

    # this code checks if the assignment is a billable one, and if so it
    # overrides the billable flag. this doesn't really make sense
    # _billable = active_assignment[assignment_id].get("billable", None)
    #
    # if not _billable:
    #     _billable = billable
    _billable = billable

    if category == "":
        nice_data = []
        i = 0
        click.echo("Please choose which category:")
        for c in category:
            click.echo("[{}] {}".format(i, c))
            nice_data.append(c)
            i += 1
        selection = input("Selection: ")
        category = nice_data[int(selection)]


    if amount == 0:
        amount_in = float(input("amount to add: "))
    else:
        amount_in = float(amount)

    if description == "":
        description_in = input("add your description: ")
    else:
        description_in = description      


    new_exp = {
            'CurrencyIsoCode': currency,
            'pse__Billing_Currency__c': currency,
            'pse__Amount__c': amount_in,
            'pse__Resource__c': te.contact_id,
            'pse__Project__c': project_id,
            'pse__Description__c': description_in,
            'pse__Type__c': category,
            'pse__Expense_Date__c': date,
            'pse__Assignment__c': assignment_id,
            'pse__Billable__c': _billable,
            'In_Policy__c': inpolicy,
    }


    expense_id = te._upload_expense(new_exp)  # dry_run=True
    if noreceipt == False:
        if filename == "":
            image_name = str(datetime.now().strftime("%Y_%m_%d_%H_%M")) + '.jpg'
            show_webcam(image_name)
        else:
            image_name = filename
        te._upload_image(image_name ,expense_id)
        if filename == "":
            os.remove(image_name)


    logger.info("Expense added")
