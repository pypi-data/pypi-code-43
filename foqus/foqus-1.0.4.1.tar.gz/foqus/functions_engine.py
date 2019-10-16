#! /usr/bin/python
# -*- coding:utf-8 -*-
from foqus.customers import *
from foqus.request_api import *
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
import string, random, hashlib, uuid, tldextract
from datetime import datetime, date
api = APIFoqus()


def get_all_plans_payement(customerEmail, type_user_admin):
    type_user_sender = db.verif_permission(customerEmail=customerEmail, type_user=type_user_admin)
    msg = "You are not allowed to get_all_plans_payement."
    if (str(type_user_sender) != "Email not found") and (str(type_user_sender) != "Error"):
        if str(type_user_sender) == "admin":
            result = []
            list_plan = db.get_all_plans_payement(table_name="plan")
            for plan in list_plan:
                plan_name = {'plan_name': plan[1]}
                payment_period = {'payment_period': plan[2]}
                # total = {'total': round(float(plan[3]), 2)}
                total = {'total': float(plan[3])}
                max_image_training = {'max_image_training': plan[4]}
                data = [plan_name, payment_period, total,max_image_training ]
                result.append(data)
            return (result)
        elif str(type_user_sender) in ["customer", "SN1", "SN2", "SN3"]:
            return (msg)
        else:
            return (msg)
    else:
        return "Please check your customer_email."


def start_training(customer_name=None, customer_type=None, customer_universe=None):
    response = api.apipost('', customer_name, customer_type, None, None,
                           customer_universe)


def list_all_clients_with_projects():
    result = []
    response = db.select_list_all_clients_with_projects("status_projects")
    try:
        df = DataFrame(response.groupby(['customer_name', 'customer_type']))
        for i in range(0, len(df)):
            customer_nametype = str(df[0][i])
            values = df[1][i]
            list_index = list(values.index)
            name = {'customer_name': customer_nametype.split("', '")[0].replace("('", "")}
            type = {'customer_type': customer_nametype.split("', '")[1].replace("')", "")}
            response = []
            for j in list_index:
                response.append({'project': values['project'][j], 'api': values['api'][j], 'status': values['status'][j],
                                 'name': values['name'][j]})

            projects = {'projects': response}
            data = [name, type, projects]
            result.append(data)
    except Exception as e:
        logger.error("Error in getting user with projects %s" %e)
    return result


def number_post_per_clients():
    response = db.select_number_post_per_clients("client_history_table")
    result = []
    for res in response:
        name = {'customer_name': res[1]}
        type = {'customer_type': res[2]}
        nb_post = {'number_post': res[0]}
        data = [name, type, nb_post]
        result.append(data)
    return result


def predict_image(image_path, customer_name, customer_type, project_name, similars=None):
    response = api.apiget('get_category', customer_name, customer_type, project_name, image_path)
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    category = json.loads(response)
    image_domaine = (tldextract.extract(image_path)).domain
    if similars is None:

        db.insert_or_update_into_table_history('client_history_table', today, customer_name, customer_type,
                                               project_name, image_path, 'classification', json.dumps({}),
                                               json.dumps(response), ip_adress="",domain_url=image_domaine , type_reference="")

    return category


def get_historic(customer_name, customer_type):
    response_historic = []
    list_response = db.select_similars_classification_result("client_history_table",  customer_name, customer_type)
    for response in list_response:
        each_search = []
        each_search.append({"date": response[1].strftime("%d-%m-%Y")})
        each_search.append({"project": response[4]})
        each_search.append({"url": response[5]})
        each_search.append({"api": response[6]})
        each_search.append(json.loads(response[7]))
        each_search.append(json.loads(response[8]))
        each_search.append({"country": response[11]})
        each_search.append({"searched_time": response[9]})
        response_historic.append(each_search)

    return {"response": response_historic}


def get_client_payment_status(customer_name , customer_type):
    response = db.get_client_payment(customer_name, customer_type)
    return response


def get_apikey_expiration_time(customer_name):
    # TODO add customer_type to the function
    apikey = db.get_apikey_from_customer(customer_name)
    api_key = apikey[0]
    response = datetime.fromtimestamp(get_apikey_expiration(api_key)).strftime(" Le %d-%m-%Y  à %I:%M:%S")
    return response


def get_details_trainings_for_client(customer_name,customer_type,project_name, api ):
    response = db.get_training_detalis('status_projects',customer_name, customer_type, project_name, api)
    status_training = response[2]
    if response[1] == 0:
        date_end_training = ""
        url_training_file = ""
    else:
        info_last_training = json.loads(response[0])['training'+ str(response[1])]
        date_end_training = info_last_training['date_end_training']
        url_training_file = info_last_training['url_training_file']

    result={'url_training_file': url_training_file,
            'date_end_training': date_end_training,
            'status_training': status_training}
    return result


def get_details_trainings_for_admin(customer_name,customer_type,project_name, api ):
    response = db.get_training_detalis('status_projects', customer_name, customer_type, project_name, api)
    if response is not None:
        result={'trainings_details':json.loads(response[0]),
                'number_trainings_by_project': response[1],
                'status_last_training': response[2]}
    else:
        result = {'trainings_details': '',
                  'number_trainings_by_project': 0,
                  'status_last_training': 0}
    return result


def historic_users_management():
    response = db.get__historic_users_management()
    result = []
    for res in response:
        email = {'email': res[0]}
        customer_name = {'customer_name' : res[6]}
        customer_type = {'customer_type' : res[7]}
        expiration_apikey = {'expiration_apikey' : datetime.fromtimestamp(res[8]).strftime("%d-%m-%Y %I:%M:%S")}
        cnx_counter = {'cnx_counter' : int(res[1])}
        cnx_date = {'cnx_date' : list(res[2].split("+++"))}
        ip_addr = {'ip_address': list(res[3].split("+++"))}
        devices = {'device': list(res[4].split("+++"))}
        city = {'city': list(res[5].split("+++"))}
        data = [email,customer_name,customer_type,expiration_apikey, cnx_counter, cnx_date,ip_addr,devices,city]
        result.append(data)
    return result


def text_training_retrieve_json(excel_path, customer_name, customer_type, customer_universe, project_name):
    send_email_when_training_started(customer_name, project_name, 'classification', 'Apprentissage lancé!')
    if project_name:
        operation = 'training_classification'
    else:
        operation = 'training_text_detection'
    response = api.apipost(operation, customer_name, customer_type, project_name, excel_path,
                               customer_universe)
    result = json.loads(response.text)
    if int(result['status']) < 1:
        return True
    else:
        return False


def predict_customer(excel_path, customer_name, customer_type, customer_universe):
    response = api.apiget('predict_customer', customer_name, customer_type, customer_universe, excel_path)
    if response == 'True':
        return True
    else:
        return False


def new_similars(customer_name, customer_type, project_name, image, adress_ip):
    try:
        similars = api.apiget('get_similars', customer_name, customer_type, project_name, image)
        response = json.loads(similars)
        if response['response']['similars'] != []:
            today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            image_domain = (tldextract.extract(image)).domain
            db.insert_or_update_into_table_history('client_history_table', today, customer_name, customer_type, project_name, image,
                                                    'search_similars', response['response'], response['category'], ip_adress = adress_ip,domain_url=image_domain , type_reference="")
        return json.dumps(response)
    except Exception as e:
        print('Exception %s' %e)


def historic_users_management_customer():
    response = db.get__historic_users_management_customer()
    result = []

    for res in response:
        email = {'email' : res[0]}
        customer_name = {'customer_name' : res[6]}
        customer_type = {'customer_type' : res[7]}
        expiration_apikey = {'expiration_apikey' : datetime.fromtimestamp(res[8]).strftime("%d-%m-%Y %I:%M:%S")}
        cnx_counter = {'cnx_counter' : int(res[1])}
        cnx_date = {'cnx_date' : list(res[2].split("+++"))}
        ip_addr = {'ip_address': list(res[3].split("+++"))}
        devices = {'device': list(res[4].split("+++"))}
        city = {'city': list(res[5].split("+++"))}
        data = [email ,customer_name,customer_type,expiration_apikey, cnx_counter, cnx_date,ip_addr,devices,city]
        result.append(data)
    return result


def customer_authentication_api(customerEmail, customerPassword, type_user):
    login = db.login(customerEmail=customerEmail, customerPassword=customerPassword, type_user=type_user)

    is_authenticated = login.split("#$#")[0]
    type_user = login.split("#$#")[1]

    permission = ""
    if str(is_authenticated) == "True":
        resssss = db.get_permission(type_user=type_user)[0]
        for key, value in resssss[1].items():
            if value == 1:
                permission = permission + key+ "|"

    return str(is_authenticated) + "#$#" + permission


def can_create_users_api(customerEmail, permission, type_user_admin, type_new_user,email, password,entreprise, nom, prenom,num_tel, domaine):
    type_user_sender = db.verif_permission(customerEmail=customerEmail, type_user=type_user_admin)
    msg = "You are not allowed to create a " + type_new_user + " account"
    if (str(type_user_sender) != "Email not found") and (str(type_user_sender) != "Error"):
        if str(type_user_sender) == "admin":
            resssss = db.get_permission(type_user=type_user_sender)[0]
            for key, value in resssss[1].items():
                if key == permission and value == 1:
                    if type_new_user == "customer":

                        hash_password = hashlib.sha512(password.encode('utf-8')).hexdigest()
                        uid = str(uuid.uuid4())
                        token = str(uuid.uuid4())
                        db.create_users_management_table()
                        test = db.add_customer(customer=entreprise, customerPassword=hash_password,
                                               customerEmail=str(email), customerJob="", customerPhone=num_tel, token=token,
                                               aboutUs="",
                                               subjectHelp="",
                                               domaine=domaine, firstName=nom, lastName=prenom, stafNumber="", apikey=uid,
                                               expiration_duration_in_hours=720, type=type_new_user)
                        if test is True:
                            db.commit_db_changes()

                            customer = db.get_profile(table_name=DATABASE_USERS_MANAGEMENT_TABLE_NAME,
                                                      customerEmail=email)
                            full_url = DOMAIN + 'activate/' + urlsafe_base64_encode(
                                *force_bytes(customer[0])).decode('utf-8') \
                                       + '/' + customer[12]

                            send_inscription_email(customer_email=email, full_url= full_url, password_client=password)
                            msg = email + "##" + type_new_user + "##" + entreprise  + "##" + domaine
                        else:
                            msg = "Email already in use"
                    elif type_new_user in ["SN1", "SN2", "SN3", "admin"]:
                        hash_password = hashlib.sha512(password.encode('utf-8')).hexdigest()
                        uid = str(uuid.uuid4())
                        token = str(uuid.uuid4())
                        db.create_users_management_table()
                        test = db.add_customer(customer=entreprise, customerPassword=hash_password,
                                               customerEmail=str(email), customerJob="", customerPhone=num_tel,
                                               token=token,
                                               aboutUs="",
                                               subjectHelp="",
                                               domaine=domaine, firstName=nom, lastName=prenom, stafNumber="",
                                               apikey=uid,
                                               expiration_duration_in_hours=720, type=type_new_user)
                        if test is True:
                            db.commit_db_changes()
                            send_inscription_email(customer_email=email, full_url="",
                                                             password_client=password)

                            msg = email + "##" + type_new_user + "##" + entreprise  + "##" + domaine
                        else:
                            msg = "Email already in use"

            return (msg)

        elif str(type_user_sender) == "SN2" or str(type_user_sender) == "SN3":
            resssss = db.get_permission(type_user=type_user_sender)[0]
            for key, value in resssss[1].items():
                if key == permission and value == 1:
                    if type_new_user == "customer":
                        hash_password = hashlib.sha512(password.encode('utf-8')).hexdigest()
                        uid = str(uuid.uuid4())
                        token = str(uuid.uuid4())
                        db.create_users_management_table()
                        test = db.add_customer(customer=entreprise, customerPassword=hash_password,
                                               customerEmail=str(email), customerJob="", customerPhone=num_tel,
                                               token=token,
                                               aboutUs="",
                                               subjectHelp="",
                                               domaine=domaine, firstName=nom, lastName=prenom, stafNumber="",
                                               apikey=uid,
                                               expiration_duration_in_hours=720, type=type_new_user)
                        if test is True:
                            db.commit_db_changes()
                            send_inscription_email(customer_email=email, full_url="",
                                                             password_client=password)

                            msg = email + "##" + type_new_user + "##" + entreprise + "##" + domaine
                        else:
                            msg = "Email already in use"

                    else:
                        msg = "You are not allowed to create a " + type_new_user + " account"
            return (msg)
        elif str(type_user_sender) == "SN1":
            return (msg)

        elif  str(type_user_sender) == "customer":
            return (msg)
        else:
            return (msg)

    else:
        return "Please check your customer_email."


def can_delete_users_api(customerEmail, permission, type_user_admin, email):
    type_user_sender = db.verif_permission(customerEmail=customerEmail, type_user=type_user_admin)
    type_del_user = db.get_type_user(customerEmail=email)

    msg = "You are not allowed to delete a " + type_del_user + " account"

    if (str(type_user_sender) != "Email not found") and (str(type_user_sender) != "Error"):
        if type_del_user != "Email not found":
            if str(type_user_sender) == "admin":
                resssss = db.get_permission(type_user=type_user_sender)[0]
                for key, value in resssss[1].items():
                    if key == permission and value == 1:
                        if type_del_user in ["customer","SN1", "SN2", "SN3", "admin"]:
                            test = db.delete_user(table_name=DATABASE_USERS_MANAGEMENT_TABLE_NAME,
                                                  email=email)
                            if test is True:
                                msg = "Deleting user: " + email + " succuessfully..."
                            else:
                                msg = "Deleting user: " + email + " failed..."

                return (msg)

            elif str(type_user_sender) == "SN2" or str(type_user_sender) == "SN3":
                resssss = db.get_permission(type_user=type_user_sender)[0]
                for key, value in resssss[1].items():
                    if key == permission and value == 1:
                        if type_del_user == "customer":
                            test = db.delete_user(table_name=DATABASE_USERS_MANAGEMENT_TABLE_NAME,
                                                  email=email)
                            if test is True:
                                msg = "Deleting user: " + email + " succuessfully..."
                            else:
                                msg = "Deleting user: " + email + " failed..."
                        else:
                            msg = "You are not allowed to delete a " + type_del_user + " account"
                return (msg)
            elif str(type_user_sender) == "SN1":
                return (msg)
            elif str(type_user_sender) == "customer":
                return (msg)
            else:
                return (msg)
        else:
            return "The user that you want deleted does not exist."

    else:
        return "Please check your customer_email."


def can_edit_users_api(customerEmail,permission, type_user_admin, email, password,entreprise,nom,prenom, num_tel, domaine):
    type_user_sender = db.verif_permission(customerEmail=customerEmail, type_user=type_user_admin)
    type_edit_user = db.get_type_user(customerEmail=email)
    msg = "You are not allowed to edit a " + type_edit_user + " account"
    if (str(type_user_sender) != "Email not found") and (str(type_user_sender) != "Error"):
        if str(type_user_sender) == "admin":
            resssss = db.get_permission(type_user=type_user_sender)[0]
            for key, value in resssss[1].items():
                if key == permission and value == 1:
                    customer = db.get_profile(table_name=DATABASE_USERS_MANAGEMENT_TABLE_NAME,
                                              customerEmail=email)
                    if type_edit_user == "customer":
                        hash_password = hashlib.sha512(password.encode('utf-8')).hexdigest()
                        test = db.set_all_profile(table_name=DATABASE_USERS_MANAGEMENT_TABLE_NAME,
                                       firstName=nom, lastName=prenom,
                                       customerJob="", customerPhone=num_tel, id=str(customer[0]), password=hash_password, customer=entreprise, domaine=domaine)

                        if test is True:
                            full_url = DOMAIN + 'activate/' + urlsafe_base64_encode(
                                force_bytes(customer[0])).decode('utf-8') \
                                       + '/' + customer[12]

                            send_inscription_email(customer_email=email, full_url= full_url, password_client=password)
                            msg = email + "##" + type_edit_user + "##" + entreprise  + "##" + domaine
                        else:
                            msg = "Email not found"
                    elif type_edit_user in ["SN1", "SN2", "SN3", "admin"]:
                        hash_password = hashlib.sha512(password.encode('utf-8')).hexdigest()

                        test = db.set_all_profile(table_name=DATABASE_USERS_MANAGEMENT_TABLE_NAME,
                                                  firstName=nom, lastName=prenom,
                                                  customerJob="", customerPhone=num_tel, id=str(customer[0]),
                                                  password=hash_password,customer=entreprise, domaine=domaine)

                        if test is True:
                            send_inscription_email(customer_email=email, full_url="",
                                                             password_client=password)

                            msg = email + "##" + type_edit_user + "##" + entreprise  + "##" + domaine
                        else:
                            msg = "Email not found"
                    elif type_edit_user == "Email not found":
                        msg = "Email not found of user that you want edit informations "
            return (msg)

        elif str(type_user_sender) == "SN2" or str(type_user_sender) == "SN3":
            resssss = db.get_permission(type_user=type_user_sender)[0]
            for key, value in resssss[1].items():
                if key == permission and value == 1:
                    customer = db.get_profile(table_name=DATABASE_USERS_MANAGEMENT_TABLE_NAME,
                                              customerEmail=email)
                    if type_edit_user == "customer":

                        hash_password = hashlib.sha512(password.encode('utf-8')).hexdigest()


                        test = db.set_all_profile(table_name=DATABASE_USERS_MANAGEMENT_TABLE_NAME,
                                                  firstName=nom, lastName=prenom,
                                                  customerJob="", customerPhone=num_tel, id=str(customer[0]),
                                                  password=hash_password,customer=entreprise, domaine=domaine)

                        if test is True:
                            send_inscription_email(customer_email=email, full_url="",
                                                             password_client=password)

                            msg = email + "##" + type_edit_user + "##" + entreprise + "##" + domaine
                        else:
                            msg = "Email not found"

                    elif type_edit_user == "Email not found":
                        msg = "Email not found of user that you want edit informations "
                    else:
                        msg = "You are not allowed to create a " + type_edit_user + " account"
            return (msg)
        elif str(type_user_sender) == "SN1" :
            return (msg)

        elif  str(type_user_sender) == "customer" :
            return (msg)
        else:
            return (msg)
    else:
        return "Please check your customer_email."


def can_view_users_api(customerEmail, permission, type_user_admin):
    type_user_sender = db.verif_permission(customerEmail=customerEmail, type_user=type_user_admin)

    msg = "You are not allowed to view users "

    if (str(type_user_sender) != "Email not found") and (str(type_user_sender) != "Error"):
            if str(type_user_sender) == "admin":
                resssss = db.get_permission(type_user=type_user_sender)[0]
                list_users = []
                for key, value in resssss[1].items():
                    if key == permission and value == 1:
                            list_users = db.get_users_for_admin(table_name=DATABASE_USERS_MANAGEMENT_TABLE_NAME)
                result = []
                for user in list_users:
                    email = {'email': user[3]}
                    type_user = {'type_user': user[21]}
                    num_tel = {'num_tel': user[5]}
                    apikey = {'apikey': user[13]}
                    dat_expiration_apikey = {
                        'date_expiration_apikey': datetime.fromtimestamp(user[14]).strftime("%d-%m-%Y %I:%M:%S")}
                    firstname = {'firstname':user[9]}
                    lastname = {'lastname': user[10]}

                    data = [email, type_user, num_tel, apikey, dat_expiration_apikey, firstname, lastname]
                    result.append(data)
                return (result)
            elif str(type_user_sender) in ["customer","SN1", "SN2", "SN3"]:
                return (msg)
            else:
                return (msg)
    else:
        return "Please check your customer_email."


def can_view_customers_api(customerEmail, permission, type_user_admin):
    type_user_sender = db.verif_permission(customerEmail=customerEmail, type_user=type_user_admin)

    msg = "You are not allowed to view users "

    if (str(type_user_sender) != "Email not found") and (str(type_user_sender) != "Error"):
            if str(type_user_sender)in ["admin","customer","SN1", "SN2", "SN3"]:
                resssss = db.get_permission(type_user=type_user_sender)[0]
                list_users = []
                for key, value in resssss[1].items():
                    if key == permission and value == 1:
                            list_users = db.get_customers(table_name=DATABASE_USERS_MANAGEMENT_TABLE_NAME)
                result = []
                for user in list_users:
                    email = {'email': user[3]}
                    type_user = {'type_user': user[21]}
                    num_tel = {'num_tel': user[5]}
                    apikey = {'apikey': user[13]}
                    dat_expiration_apikey = {
                        'date_expiration_apikey': datetime.fromtimestamp(user[14]).strftime("%d-%m-%Y %I:%M:%S")}
                    firstname = {'firstname':user[9]}
                    lastname = {'lastname': user[10]}
                    customer_name = {'customer_name': user[1]}
                    customer_type = {'customer_type': user[8]}
                    is_active = {'is_active': user[15]}
                    data = [email, customer_name, customer_type, type_user, is_active, num_tel, apikey, dat_expiration_apikey, firstname, lastname]
                    result.append(data)
                return (result)

            else:
                return (msg)
    else:
        return "Please check your customer_email."


def can_update_apikey_api(customerEmail,permission, type_user_admin, email):
    type_user_sender = db.verif_permission(customerEmail=customerEmail, type_user=type_user_admin)
    info_user = db.get_info_user(customerEmail=email)
    type_user_update_apikey = info_user[0]
    customer_name = info_user[1]
    customer_type = info_user[2]

    msg = "You are not allowed to update apikey for " + type_user_update_apikey + " account"

    if (str(type_user_sender) != "Email not found") and (str(type_user_sender) != "Error"):
        if type_user_update_apikey != "Email not found":
            if str(type_user_sender) == "admin":
                resssss = db.get_permission(type_user=type_user_sender)[0]
                for key, value in resssss[1].items():
                    if key == permission and value == 1:
                        if type_user_update_apikey in ["customer","SN1", "SN2", "SN3", "admin"]:
                            create_or_update_user_apikey(user=customer_name, period_in_hours=720)
                            user_apikey = get_user_apikey(customer_name)
                            return customer_name + "##" + customer_type + "##" + user_apikey
            elif str(type_user_sender) == "SN2" or str(type_user_sender) == "SN3":
                resssss = db.get_permission(type_user=type_user_sender)[0]
                for key, value in resssss[1].items():
                    if key == permission and value == 1:
                        if type_user_update_apikey == "customer":
                            create_or_update_user_apikey(user=customer_name, period_in_hours=720)
                            user_apikey = get_user_apikey(customer_name)
                            return customer_name + "##" + customer_type + "##" + user_apikey
            elif str(type_user_sender) == "SN1":
                return (msg)
            elif str(type_user_sender) == "customer":
                return (msg)
            else:
                return (msg)
        else:
            return "The user that you want update apikey does not exist. Please ckeck the email of this user."

    else:
        return "Please check your customer_email."


def can_delete_project_api(customerEmail, permission, type_user_admin,customer_name, customer_type,project_name):
    type_user_sender = db.verif_permission(customerEmail=customerEmail, type_user=type_user_admin)

    msg = "You are not allowed to delete project "

    if (str(type_user_sender) != "Email not found") and (str(type_user_sender) != "Error"):
            if str(type_user_sender) == "admin":
                resssss = db.get_permission(type_user=type_user_sender)[0]
                for key, value in resssss[1].items():
                    if key == permission and value == 1:
                        test = db.delete_project(table_name="status_projects",
                                              customer_name=customer_name,customer_type=customer_type,project_name=project_name)


                        if test is True:
                            msg = "Deleting project: " + project_name + " succuessfully..."
                        else:
                            msg = "Deleting project: " + project_name + " failed..."

                return (msg)
            elif str(type_user_sender) in ["customer","SN1", "SN2", "SN3"]:
                return (msg)
            else:
                return (msg)
    else:
        return "Please check your customer_email."


def creation_entreprise_package(customerEmail,type_user_admin, plan_name, total,max_images_training):
    type_user_sender = db.verif_permission(customerEmail=customerEmail, type_user=type_user_admin)
    msg = "You are not allowed to create entreprise package."
    if (str(type_user_sender) != "Email not found") and (str(type_user_sender) != "Error"):
            if str(type_user_sender) == "admin":

                test = db.add_entreprise_package(table_name= "plan", plan_name=plan_name, total=total, max_images_training= max_images_training )
                if test is True:
                    msg = "Creation entreprise package succuessfully..."
                elif test is False:
                    msg = "Plan_name already existed."
                else:
                    msg = "Creation entreprise package failed..."

                return (msg)
            elif str(type_user_sender) in ["customer","SN1", "SN2", "SN3"]:
                return (msg)
            else:
                return (msg)
    else:
        return "Please check your customer_email."


def customer_inscription(customer_email, customer_name, customer_type, type_user):
    api_key = str(uuid.uuid4())
    token = str(uuid.uuid4())
    password = ''.join(random.choice(string.ascii_uppercase) for _ in range(8))
    logger.info('Password for client %s is %s' % (customer_email, password))
    hash_password = hashlib.sha512(password.encode('utf-8')).hexdigest()

    add_customer = db.add_customer(customer=customer_name, customerPassword=hash_password, customerEmail=customer_email,
                                   customerJob="", customerPhone="", token=token, aboutUs="", subjectHelp="",
                                   domaine=customer_type, firstName="", lastName="", stafNumber="", apikey=api_key,
                                   expiration_duration_in_hours=100, type=type_user)

    if add_customer:
        db.commit_db_changes()
        # sending email
        customer = db.get_profile(table_name=DATABASE_USERS_MANAGEMENT_TABLE_NAME,
                                  customerEmail=customer_email)
        full_url = DOMAIN + 'activate/' + urlsafe_base64_encode(force_bytes(customer[0])).decode('utf-8')\
                + '/' + customer[12]
        send_inscription_email(customer_email, full_url, password)
        return api_key
    else:
        return 'The email address is already in use. Please try another email address.'


def get_client_statistics(customer_name,customer_type ):
    response1 = get_counter_of_last_four_months(customer_name, customer_type)
    response2 = db.get_sum_of_counter_from_country_code('client_history_table', customer_name, customer_type)
    response3 = db.get_date_and_counter_from_historic_table('client_history_table', customer_name, customer_type , month=str(date.today())[5:7])
    response4 = scores_repartition_per_users(customer_name, customer_type)
    requests_four_last_months = {}
    for i in range(0, len(response1)):
        requests_four_last_months[response1[i][0]]= (response1[i][1])
    request_by_country = {}
    for c in range(0,len(response2)):
        request_by_country[response2[c][1]] = response2[c][0]
    score_repartition_per_user = {}
    score_repartition_per_user["[10%-30%]"] = response4[0]
    score_repartition_per_user["[30%-50%]"] = response4[1]
    score_repartition_per_user["[50%-75%]"] = response4[2]
    score_repartition_per_user["[75%-90%]"] = response4[3]
    score_repartition_per_user["[90%-100%]"] = response4[4]
    daily_request_current_month= {}
    for j in range(0, len(response3)):
        daily_request_current_month[(response3[j][1]).strftime('%d-%m-%Y')] = (response3[j][0])
    result = {
                'number_of_requests_for_the_four_last_months': requests_four_last_months,
                'request_repartition':request_by_country,
                'daily_request_for_current_month':daily_request_current_month,
                'scores_repartition_per_users':score_repartition_per_user,
            }
    return result


def all_status_project(customer_name, customer_type):
    result = db.select_status_project_similars(table_name="status_projects", customer=customer_name, customer_type=customer_type)
    data=[]
    for i in range(0, len(result)):
        data.append([result[i][0],result[i][1]])
    return data


def customer_info(customer_email):
    try:
        customer_info = db.get_profile(table_name=DATABASE_USERS_MANAGEMENT_TABLE_NAME,customerEmail=customer_email)

        result= {}
        result['customer_name']=customer_info[1]
        result['customer_type']=customer_info[8]
        result['api_key']=customer_info[13]
        result['customer_email']=customer_email
    except Exception as e:
        logger.error('email not found for this customer , Please verify your email  %s' %e)
        return []
    return result



def save_client_reviews(customer_name, customer_type, project_name, review, url_image):
    response = db.save_client_reviews(customer_name, customer_type, project_name, review,url_image)
    return response


def get_client_statistics_admin(customer_name,customer_type ):

    response1 = get_counter_of_last_four_months(customer_name, customer_type)
    response2 = db.get_sum_of_counter_from_country_code('client_history_table', customer_name, customer_type)
    response3 = db.get_date_and_counter_from_historic_table('client_history_table', customer_name, customer_type , month=str(date.today())[5:7])
    response4 = scores_repartition_per_users(customer_name, customer_type)
    response5 = db.get_reviews(customer_name, customer_type)

    reviews = {}
    total_reviews = 0
    for review in response5:
        total_reviews = total_reviews + review[1]
    for review in response5:
        reviews[str(review[0])] = round((review[1]/total_reviews)*100, 2)

    keys_reviews =["1", "2", "3", "4", "5"]
    for key in keys_reviews:
        if key not in reviews:
            reviews[key] = 0


    requests_four_last_months = {}
    for i in range(0, len(response1)):
        requests_four_last_months[response1[i][0]]= (response1[i][1])
    request_by_country = {}
    for c in range(0,len(response2)):
        request_by_country[response2[c][1]] = response2[c][0]
    score_repartition_per_user = {}
    score_repartition_per_user["[10%-30%]"] = response4[0]
    score_repartition_per_user["[30%-50%]"] = response4[1]
    score_repartition_per_user["[50%-75%]"] = response4[2]
    score_repartition_per_user["[75%-90%]"] = response4[3]
    score_repartition_per_user["[90%-100%]"] = response4[4]
    daily_request_current_month= {}
    for j in range(0, len(response3)):
        daily_request_current_month[(response3[j][1]).strftime('%d-%m-%Y')] = (response3[j][0])
    result = {
                'number_of_requests_for_the_four_last_months': requests_four_last_months,
                'request_repartition':request_by_country,
                'daily_request_for_current_month':daily_request_current_month,
                'scores_repartition_per_users':score_repartition_per_user,
                'reviews' : reviews,
            }
    return result

