"""
.. module:: dh_mail
   :platform: Unix, Windows
   :synopsis: A module which contains the boiler plate methods to be used
   for sending mail alerts.

.. moduleauthor:: Dharmateja Yarlagadda <dharmateja.yarlagadda@eneco.com>

"""

import os
import math
import smtplib
import logging
from time import sleep
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
logging.basicConfig(format='%(asctime)s %(levelname)-4s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')


def trigger_mail(error_message, host, port, sender, password, job_name, recipient):
    """
    Sends email with error message.

    :param error_message: Contains the error description
    :type error_message: String
    :param host: The SMTP host
    :type host: String
    :param port: The SMTP port
    :type port: Integer
    :param sender: The email address of the sender
    :type sender: String
    :param password: The password of the sender
    :type password: String
    :param job_name: The name of the job
    :type job_name: String
    :param recipient: The email address list of the recipients
    :type recipient: List
    :return: No return
    """
    smtp_server = smtplib.SMTP(host, port)
    try:
        smtp_server.starttls()
        smtp_server.login(sender, password)
        message = "Hi Team," + "\n" + "\n" + job_name + " job got failed with below error at time" + " " + \
                  datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') + "\n" + "\n" + error_message + "\n" + "\n" + \
                  "Thanks" + "\n" + "Data-hub"
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = job_name + " Job Failed at " + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        msg.attach(MIMEText(message, 'plain'))
        smtp_server.send_message(msg)
    except Exception as e:
        logging.info('Send status email failed')
        logging.info(ValueError('Error/exception thrown by sendEmail function: {}'.format(str(e))))
    finally:
        smtp_server.quit()


def trigger_validations_mail(mail_type, validated_df, job_name, host, port, sender, password, recipient):
    """
    Sends email with error/warning message and file attachments.

    :param mail_type: The mail type whether it is warning or error.
    :type mail_type: String
    :param validated_df: The validated dataframe
    :type validated_df: DataFrame
    :param host: The SMTP host
    :type host: String
    :param port: The SMTP port
    :type port: Integer
    :param sender: The email address of the sender
    :type sender: String
    :param password: The password of the sender
    :type password: String
    :param job_name: The name of the job.
    :type job_name: String
    :param recipient: The email address list of the recipients
    :type recipient: List
    :return: No return
    """
    smtp_server = smtplib.SMTP(host, port)
    try:
        smtp_server.starttls()
        smtp_server.login(sender, password)
        validated_df.to_csv('{}.csv'.format(job_name), sep=',', index=False, date_format='%Y-%m-%d %H:%M:%S')
        message = "Hi Team," + "\n" + "\n" + job_name + " job had issues with the data for the run at " + " " + \
                  datetime.utcnow().strftime(
                      '%Y-%m-%d %H:%M:%S') + "\n" + "Please check the attached csv for the check which have failed" + \
                  "\n" + "Thanks" + "\n" + "Data - hub"
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = mail_type + ": " + job_name + " Job had issues with data " + datetime.utcnow().strftime(
            '%Y-%m-%d %H:%M:%S')
        msg.attach(MIMEText(message, 'plain'))
        with open("{}.csv".format(job_name), "rb") as fil:
            part = MIMEApplication(fil.read())
            part['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(job_name)
            msg.attach(part)
        smtp_server.send_message(msg)
        sleep(10)
        os.remove("{}.csv".format(job_name))
    except Exception as e:
        logging.info('Send status email failed')
        logging.info(ValueError('Error/exception thrown by sendEmail function: {}'.format(str(e))))
    finally:
        smtp_server.quit()


def send_mail(count, err, host, port, sender, password, job_name, recipient, sleep_time=10):
    """
    Check the error_count and send mail if required.

    :param count: number of times error came
    :type count: Integer
    :param err: error message
    :type err: String
    :param host: The SMTP host
    :type host: String
    :param port: The SMTP port
    :type port: Integer
    :param sender: The email address of the sender
    :type sender: String
    :param password: The password of the sender
    :type password: String
    :param job_name: The name of the job
    :type job_name: String
    :param recipient: The email address list of the recipients
    :type recipient: List
    :param sleep_time: The sleep time between each error. Default value is 10 (optional)
    :type sleep_time: Integer
    :return: return the count of error
    """
    if count == 0:
        trigger_mail(str(err), host, port, sender, password, job_name, recipient)
        return count
    else:
        if count >= 24:
            trigger_mail(str(err), host, port, sender, password, job_name, recipient)
            count = 0
            return count
        sleep(sleep_time)
    return count


def send_mail_validations(host, port, sender, password, job_name, recipient, checks, columns_df, validated_df):
    """
    Check the validation flags of the dataframe and take decision to send mail or not.

    :param host: The SMTP host
    :type host: String
    :param port: The SMTP port
    :type port: Integer
    :param sender: The email address of the sender
    :type sender: String
    :param password: The password of the sender
    :type password: String
    :param job_name: The name of the job
    :type job_name: String
    :param recipient: The email address list of the recipients
    :type recipient: List
    :param checks: The list of validations checks.
    :type checks: List
    :param columns_df: The dataframe containing the list of columns.
    :type columns_df: DataFrame
    :param validated_df: The dataframe with all the validation flags updated.
    :type validated_df: DataFrame
    :return: return the count of error
    """
    # check_validations
    # use the validations list if more than 2 types of mails have to be sent.
    validations = []
    for row in columns_df.itertuples():
        column = row.column_name
        for check in checks:
            if check != 'snapshot':
                if row.min_value is None and check == 'range':
                    continue
                flag_total = validated_df[column + '_' + check + '_flag'].sum()
                if flag_total > 2:
                    trigger_validations_mail('ERROR', validated_df, job_name, host, port, sender, password,
                                             recipient)
                    return
                elif flag_total > 0:
                    validations.append(flag_total)
            # Add equals comparison for snapshot if in case in the future there are more such checks
            # with different implementations
            elif check == 'snapshot':
                # To handle nulls in the column
                if row.snapshot is None:
                    continue
                # To handle nan's in the column.
                # Separated on the off chance we might have different implementations in future
                if math.isnan(row.snapshot):
                    continue
                flag_total = sum(validated_df[column + '_' + check + '_flag'].unique())
                if flag_total > 2:
                    trigger_validations_mail('ERROR', validated_df, job_name, host, port, sender, password,
                                             recipient)
                    return
                elif flag_total > 0:
                    validations.append(flag_total)
    if sum(validations) >= 1:
        trigger_validations_mail('WARNING', validated_df, job_name, host, port, sender, password,
                                 recipient)
    return
