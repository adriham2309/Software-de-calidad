"""
This module contains all the required functions to generate a translation
"""
from distutils.log import error
import json
import logging
from datetime import datetime, timedelta
import sys
import requests
from flatten_json import flatten, unflatten_list
from django.conf import settings
import asyncio
import os
import pytz
import shutil

from invias.models import (
    Method_Publication,
    Pending,
    Store,
)
from asgiref.sync import sync_to_async
from threading import Thread
import time
from django.utils import timezone

# List of function value
# ------------------------------------------------------
def system_date():
    """
    Returns the date of the system.

        Returns:
            The date of the system with
            the format "%Y-%m-%dT%H:%M:%S+05:00"
    """

    return datetime.now(pytz.timezone(settings.TIMEZONE)).strftime(
        "%Y-%m-%dT%H:%M:%S%z"
    )


# ------------------------------------------------------


# Functions for the general translator to work.
# ------------------------------------------------------
def map_datex_routes(
    tln_result_dict: dict, tln_information: dict, tln_value, index=None
):
    """
    Add the translation of the given routes, functions for the value specified.
    This translation is saved into a dictionary that contains the translation result

        Parameters:
            tln_result_dict (dict) : The dictionary that containts
            the results of a translation

            tln_information (dict) : The information that containts
            the routes and the functions to apply to the translation

            tln_value (Any) : The value to assign to the translation

            index (tuple) : a tuple argument that specifies the index of the translation
    """
    for route in tln_information["datex_routes"]:
        function_type = eval(tln_information["type"])

        if tln_information["function"]["type"] == "function-value":
            function_to_apply = eval(tln_information["function"]["name"])
            tln_value = function_to_apply()

        if index is None:
            tln_result_dict[route] = function_type(tln_value)
        else:
            tln_result_dict[route.format(index)] = function_type(tln_value)


def header_items(mdp, translator):
    """
    Assign the items that go along the header in the dictionary that
    cointains the result of the translation

        Parameters:
            mdp (dict) : The dictionary that containts
            the results of a translation

            translator (dict) : The dictionary that contains
            the routes and values that should be translated to the
            header of the publication

    """
    header = translator["head"]
    for tln_value, tln_information in header.items():
        if tln_information["forced"]:
            map_datex_routes(mdp, tln_information, tln_value)


def translate(mdp, item, index, translator):
    """
    Assign the items that should be translated into the dictionary that
    containst he result of the translation.

        Parameters:
            mdp (dict) : The dictionary that containts
            the results of a translation

            item (dict) : The element to translate

            index (int) : The index level into an array

            translator (dict) : The dictionary that contains
            the routes and values that should be translated to the
            header of the publication
    """
    for tln_value, tln_information in translator["body-forced"].items():
        map_datex_routes(mdp, tln_information, tln_value, index)

    for tln_key, tln_information in translator["body-endpoint"].items():
        tln_value = item.get(tln_key, None)
        if not tln_value is None:
            map_datex_routes(mdp, tln_information, tln_value, index)


# ------------------------------------------------------


def monitoring_size(mdp, max_size):
    """
    Returns a boolean value that indicates is the size of the result
    have exceeded the specified size.

        Parameters:
            mdp : The dictionary that containts
            the results of a translation
        Returns :
            (Boolean) : Result of the evaluation of the
            size of the element in memory in bytes
    """
    if sys.getsizeof(mdp) > max_size:
        return True
    return False


def write_publication(session, mdp):
    """
    Writes an archive in json format that contains
    the result of the translation.

        Parameters:
            mdp (dict) : The dictionary that containts
            the results of a translation
    """
    if mdp == {}:
        logging.info(
            "MAIN_TASK_LOOP - 104: The execution of the Bogotá translator ends without results"
        )
    else:
        session_process(session, [mdp])


def assign_site_id(mapping, idvct):
    """
    Returns a list of sites that represents the one to many mapping from
    one site of the idvct to multiple shorter sites.
        Parameters:
            mapping (dict): Dictionary used to map an idvct big vector
            to a list of shorter vectors.
            idvct (string): Name of the idvct big vector.
        Returns:
            (list): List of shorter sites into a new representation
            that matchs the larger original site.
    """
    return mapping.get(str(idvct), None)


def assign_multiple_sites_to_item(sites, item, translator, mdp, index):
    """
    Assigns all the vector specified in the sites list, creating a new element
    for every new vector
        Parameters:
            sites (list): The list of all the sites to be assigned as new elements
            in the translation
            item (dict): The item information we want to propagate trough all the new
            sites generated
            translator (dict): The dictionary that contains
            the routes and values that should be translated to the
            header of the publication
            mdp (dict): The dictionary that containts
            the results of a translation
            index (int):  The index position of the element in the translation
        Returns:
            index (int): The index that represents the position in the array which belongs
            to the last element translated
    """
    for site in sites:
        item = flatten(item)
        item["site_id"] = site
        item["version_id"] = "1"
        item["timef_ltp"] = datetime.strptime(item["timef_lt"], "%Y-%m-%d %H:%M:%S")
        item["timef_ltp"] = (
            item["timef_ltp"]
            .astimezone(pytz.timezone(settings.ENV_TIMEZONE))
            .strftime("%Y-%m-%dT%H:%M:%S%z")
        )
        translate(mdp, item, index, translator)
        index += 1
    return index


def request_data(username_api, password_api, endpoint, endpoint_cookie):
    """
    Returns the result of an API get request
        Returns:
            res (list): All the elements containing the respond from the request.
    """
    try:
        payload = {"username": username_api, "password": password_api}
        resp = requests.post(endpoint_cookie, data=payload, verify=False)
        r = requests.get(endpoint, cookies=resp.cookies, verify=False)
        elementos = json.loads(r.text)
        if len(elementos) > 0:
            return r.json()
        else:
            return None
    except Exception as e:
        logging.error(
            "206: It was not possible to connect to the bogotá endpoint to request the data. %s",
            e,
        )
        raise ConnectionError from e

def pub_initial(session, data):
    res = session.request_put_data(data)
    if not res == b"{}":
        logging.info(
            "119: response <"
            + str(res.status_code)
            + "> "
            + str(res.content, settings.ENCODING)
        )
        if res.status_code == 200:
            pass
        else:
            stored_data(session.typepublication, data)
            res = session.request_close_session()
            session.session_id = None
    else:
        stored_data(session.typepublication, data)
        res = session.request_close_session()
        session.session_id = None

def session_process(session) -> None:
    """stasteful session control"""
    print(f"send information of {session.typepublication}")

    try:
        method_publication_val = Method_Publication.objects.get(name=session.typepublication)
        method_publication_val.verification_date = timezone.now()
        method_publication_val.save()
    except Method_Publication.DoesNotExist:
        pass

    if session.task.session is None:
        # try to open session
        logging.info(f"METHOD: {session.typepublication}")
        logging.info("109: Open Session- Client Status OFF")
        try:
            res = session.request_open_session(
                settings.ENV_COUNTRY_CODE,
                settings.ENV_NATIONAL_IDENTIFIER,
                settings.FAKE_API_KEY,
            )
            logging.info(
                "118: response <"
                + str(res.status_code)
                + "> "
                + str(res.content, settings.ENCODING)
            )
        except Exception as e:
            print('Open Session Error ', e)
            res = None
        # if the session is not opened then execute the following code
        if session.session_id is None:
            logging.info("110: Timeout or fail on openSession")
            logging.info("111: Storing publications in files...")
            # data to be stored in a file due to the server is not responding
            # the data has the unsent status
            # stored_data(session.typepublication, data)
        # if the session is opened is executed the following code
        else:
            logging.info("116: Payload put data")
            # follow normal process
            # pub_initial(session, data)
            start_process(session)
    else:
        start_process(session)

def start_process(session):
    try:

        store_values = Store.objects.filter(
            pending__method_publication__name=session.typepublication,
            status=0
        ).exists()

        if store_values:
            Thread(target=send_data_files_loop, args=(session,)).start()
        else:
            logging.info(
                f"STORE - {session.typepublication} - Not Data..."
            )
            pendind_process(session)

    except Exception as e:
        print('ERROR ::::::::: start_process ', e)

def pendind_process(session):
    logging.info(
        f"PENDING - {session.typepublication} - Init Process..."
    )

    pending_values = Pending.objects.filter(
        method_publication__name=session.typepublication,
        status=0
    )

    if pending_values:
        pending_ids = [pending_value.id for pending_value in pending_values]
        print('pending_ids::::::::::')
        print(pending_ids)
        Pending.objects.filter(id__in=pending_ids).update(status=1)
        Thread(target=send_pending_data, args=(session, pending_values)).start()
    else:
        logging.info(
            f"PENDING - {session.typepublication} - Not Data..."
        )

    logging.info(
        f"PENDING - {session.typepublication} - End Process..."
    )


def stored_data(publication_type, data) -> None:

    path = f"{settings.BASE_DIR}/{settings.UNSENT_PUB_DIR}"
    if not os.path.exists(path):
        os.makedirs(path)

    try:
        method_publication_val = Method_Publication.objects.get(name=publication_type)
    except Method_Publication.DoesNotExist:
        method_publication_val = Method_Publication()
        method_publication_val.name = publication_type
        method_publication_val.amount = 1
        method_publication_val.save()

    date_name = str(datetime.now().strftime("%d%m%Y %H%M%S-%f"))
    # filename where are stored the publication
    unsent_publication_file = (
        f"{settings.UNSENT_PUB_DIR}/{publication_type}-{date_name}.json"
    )

    with open(settings.BASE_DIR / unsent_publication_file, "w", encoding=settings.ENCODING) as file_sent:
        json.dump(data, file_sent)

    logging.info("112: The unsent publication is stored in the file")

def pending_data(publication_type, data) -> None:
    # variable to store a list of dictionary with information about publication and status (unsent, sent)
    file_data = []

    path = f"{settings.BASE_DIR}/{settings.PENDING_PUB_DIR}"
    if not os.path.exists(path):
        os.makedirs(path)

    date_name = str(datetime.now().strftime("%d%m%Y %H%M%S-%f"))
    # filename where are stored the publication
    pending_publication_file = (
        f"{settings.PENDING_PUB_DIR}/{publication_type}-{date_name}.json"
    )

    print('pending_publication_file::::::::::::::::::')
    print(pending_publication_file)

    # the current publication, stored in pub_data, is added to file_data list
    file_data = file_data + data
    # the files where are stored the unsent publication is opened as a writing file
    # the information is updated using the current file_data list
    # with open(unsent_publication_file, "wb+", encoding=settings.ENCODING) as file_sent:
    with open(settings.BASE_DIR / pending_publication_file, "w", encoding=settings.ENCODING) as file_sent:
        json.dump(file_data, file_sent)

        try:
            method_publication_val = Method_Publication.objects.get(name=publication_type)
            method_publication_val.amount = method_publication_val.amount + 1
        except Method_Publication.DoesNotExist:
            method_publication_val = Method_Publication()
            method_publication_val.name = publication_type
            method_publication_val.amount = 1
        method_publication_val.last_process = timezone.now()
        method_publication_val.save()

        pending_val = Pending()
        pending_val.method_publication = method_publication_val
        pending_val.path = pending_publication_file
        pending_val.save()

    logging.info("112: The unsent publication is stored in the file")


def send_data_files_loop(session):
    logging.info("CHECK_DATA_FILES_LOOP - checking files with data to be uploaded...")
    # Maximum time to send data before starting the main process again
    max_time = 60*(settings.ENV_REQUEST_TIME - 1)
    timeout = time.time() + (max_time if max_time > 0 else 30)

    while True:
        # Set limit publish data
        store_values = Store.objects.filter(
            pending__method_publication__name=session.typepublication,
            status=0
        )[:settings.ENV_PROCESS_AMOUNT]

        if not store_values:
            print('break while send_data_files_loop ::::::::::::::::')
            logging.info(
                f"CHECK_DATA_FILES_LOOP - store values with data to be published not found..."
            )
            break
        
        if time.time() > timeout:
            print('break while send_data_files_loop ::::::::::::::::')
            logging.info(
                f"CHECK_DATA_FILES_LOOP - time limit met..."
            )
            break
        print('continue')

        store_ids = [store_value.id for store_value in store_values]
        Store.objects.filter(id__in=store_ids).update(status=1)
        print('store_ids::::::::::')
        print(store_ids)

        files_data = []
        for store_value in store_values:
            try:
                logging.info(
                    "CHECK_DATA_FILES_LOOP - opening file with unsent publications..."
                )
                # open file and store data in file_data list
                with open(
                    settings.BASE_DIR / str(store_value.path), encoding=settings.ENCODING
                ) as file_sent:
                    file_data = json.load(file_sent)
                # iterate on each publication found in the file
                print('file_data::::::::::::::::::::::::::::::::::::::::::::::')
                print(file_data)

                files_data = files_data + file_data
            except FileNotFoundError:
                store_value.error_description = 'FileNotFoundError'
                store_value.status = 3
                store_value.save()
                logging.error(
                    f"CHECK_DATA_FILES_LOOP - file {str(store_value.path)} not found..."
                )
                pass

        
        print('SEND DATA STORE')
        try:
            logging.info("113: Snapshot Synchronisation")
            res = session.request_put_snapshot_data(files_data)
            logging.info("changing status...")
            if not res == b"{}":
                # logging.info(res.json())
                logging.info(
                    "117: response <"
                    + str(res.status_code)
                    + "> "
                    + str(res.content, settings.ENCODING)
                )
                # the status of each sent publication is changed to sent if response is 200
                if res.status_code == 200:
                    logging.info(
                        f"CHECK_DATA_FILES_LOOP - success..."
                    )
                    Store.objects.filter(id__in=store_ids).update(status=2)
                    # removing file with sent data
                    # os.remove(settings.BASE_DIR / settings.UNSENT_PUB_DIR / file_name)
                else:
                    Store.objects.filter(id__in=store_ids).update(status=0)
                    res = session.request_close_session()
                    break
            else:
                Store.objects.filter(id__in=store_ids).update(status=0)
                res = session.request_close_session()
                break

        except requests.exceptions.ConnectionError:
            logging.error("CHECK_DATA_FILES_LOOP - error opening session...")
            pass

        time.sleep(settings.ENV_PROCESS_TIME_SECONDS)

def send_pending_data(session, pending_values):
    try:
        logging.info("PENDING - checking data")

        logging.info(
            "PENDING - opening files pending publications..."
        )

        files_data = []
        pending_ids = [pending_value.id for pending_value in pending_values]
        if pending_values:
            for pending_value in pending_values:

                pending_publication_file = (
                    f"{settings.BASE_DIR}/{pending_value.path}"
                )

                print('pending_publication_file::::::::::::::::::::')
                print(pending_publication_file)
                
                try:
                    # open file and store data in file_data list
                    with open(
                        pending_publication_file, encoding=settings.ENCODING
                    ) as file_sent:
                        file_data = json.load(file_sent)
                    # iterate on each publication found in the file
                    logging.info("116: Payload put data")
                    files_data = files_data + file_data

                except FileNotFoundError:
                    logging.error(
                        f"PENDING - file {session.typepublication} - {pending_publication_file} not found..."
                    )
                    pass

            # # -----------------------------------------------
            # pending_to_store(pending_values, 3)
            # # -----------------------------------------------

            res = session.request_put_data(files_data)
            if not res == b"{}":
                logging.info(
                    "119: response <"
                    + str(res.status_code)
                    + "> "
                    + str(res.content, settings.ENCODING)
                )
                if res.status_code == 200:
                    logging.info(
                        f"PENDING - removing file {session.typepublication}..."
                    )
                    Pending.objects.filter(id__in=pending_ids).update(status=2)
                else:
                    pending_to_store(pending_values, 3)
            else:
                pending_to_store(pending_values, 3)
    except requests.exceptions.ConnectionError:
        logging.error("PENDING - error opening session...")
        pass

def pending_to_store(pending_values, status):
    pending_ids = [pending_value.id for pending_value in pending_values]
    for pending_value in pending_values:
        stored_file(pending_value)

    Pending.objects.filter(id__in=pending_ids).update(status=status)

def stored_file(pending_value) -> None:

    path = f"{settings.BASE_DIR}/{settings.UNSENT_PUB_DIR}"
    if not os.path.exists(path):
        os.makedirs(path)
    
    pending_publication_file = (
        f"{settings.BASE_DIR}/{pending_value.path}"
    )

    date_name = str(datetime.now().strftime("%d%m%Y %H%M%S-%f"))
    unsent_publication_file = (
        f"{settings.UNSENT_PUB_DIR}/{pending_value.method_publication.name}-{date_name}.json"
    )
    try:
        shutil.move(pending_publication_file, unsent_publication_file)

        store_val = Store()
        store_val.pending = pending_value
        store_val.path = unsent_publication_file
        store_val.save()

        logging.info("112: The unsent publication is stored in the file")
    except FileNotFoundError:
        logging.error(
            f"PENDING TO STORE - file {pending_value.method_publication.name} - {pending_publication_file} not found..."
        )
        pass