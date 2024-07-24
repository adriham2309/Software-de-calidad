from datetime import datetime
from requests.auth import HTTPBasicAuth
from requests import Session, Response
from django.conf import settings
from invias.src.stateful.push.keepalive import KeepAliveTask
from typing import Optional
import logging

import json


class SessionManager(Session):
    """
    This is a class representation of a Session used to manage sessions request in a cloud service. It is an extension
    of the :class:`requests.Session` class.

    """
    def __init__(self):
        """
        This is a class representation of a Session used to manage sessions request in a cloud service. It is an
        extension of the :class:`requests.Session` class.

        """

        # starting a Session class instance from which the current class will inherit attributes and methods
        Session.__init__(self)
        # defining task
        self.task = KeepAliveTask()
        # defining authentication attribute in the current class
        self.auth: Optional[HTTPBasicAuth] = None
        # session ID attribute
        self.session_id: Optional[str] = None
        # data attribute to store the current response message of the server
        self.data: Optional[dict] = None
        # type publication stored in the session opened
        self.typepublication: Optional[str] = None

    def request_open_session(self, country_code: str, national_identifier: str, api_key: str) -> Response:
        """

        Method to open a session using country code, national identifier, and API key parameters. The response is an
        instance of the :class:`requests.Response` class containing the session ID and other information returned by
        the server.

        To open a session first we have to create an instance of the :class:`stateful.push.core.SessionManager` class

        >>> from stateful.push.core import SessionManager
        >>> session = SessionManager()

        Then, using the ``session`` instance it is
        opened the session as follows

        >>> session.request_open_session('COUNTRY_CODE', 'NATIONAL_IDENTIFIER', 'API_KEY_VALUE')

        where ``'CONUNTRY_CODE'`` is the country code, ``'NATIONAL_IDENTIFIER'`` is the national identifier, and
        ``'API_KEY_VALUE'`` is the API key value to access the session. Opening the session is created a task job to
        keep alive the session. This job is executed every quantity of time (minutes) as is defined in the
        ``stateful.config.settings`` module using the ``KEEP_ALIVE_MINUTES`` parameter. This task is stoped
        automatically after closing the session.

        :param country_code: country code
        :type country_code: str

        :param national_identifier: national identifier
        :type national_identifier: str

        :param api_key: API key
        :type api_key: str

        :return: :class:`requests.Response`

        """

        # defining authentication attribute in the current class
        self.auth = HTTPBasicAuth('apikey', api_key)
        # obtaining the current time stamp
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        # international identifier of the service defined using the input parameters of the method
        international_identifier = {
            'country': country_code,
            'nationalIdentifier': national_identifier
        }
        # defining data with necessary information and a openingSession status
        data = {
            'exchangeInformation': {
                '_modelBaseVersion': '3',
                'ExchangeContext': {
                    'codedExchangeProtocol': 'statefulPush',
                    'exchangeSpecificationVersion': 'Exchange2020',
                    'supplierOrCisRequester': {
                        'internationalIdentifier': international_identifier
                    }
                },
                'DynamicInformation': {
                    'exchangeStatus': 'openingSession',
                    'messageGenerationTimestamp': timestamp
                }
            }
        }
        # serialization of data to JSON formatted str
        body = json.dumps(data)
        print('body 1111 ::::::::::::::::::::::::::::::::::::::::')
        print(body)
        # consuming the service to open a new session, response stored in response variable
        url_pub= f'{settings.ENV_SERVER_URL}/{self.typepublication}{settings.OPEN_SESSION_PATH}'
        print('url_pub::::::::::::::::::::::::::::::::::::::::')
        print(url_pub)
        response = self.post(url_pub, auth=self.auth, data=body)
        # checking if response is correct, if not it is returned an error
        # the response is stored in the data attribute as a dict format
        try:
            self.data = json.loads(response.text)
            # The session ID is stored in the session_id attribute
            self.session_id = self.data['exchangeInformation']['DynamicInformation']['sessionInformation']['sessionID']
            # starting task to keep alive the session, this is done calling the start() method
            # of the KeepAliveTask class, after giving values to the session, data, and auth attributes
            self.task.session = self.cookies.get('session')
            self.task.data = self.data
            self.task.auth = self.auth
            self.task.typepublication=self.typepublication
            self.task.start()
        except ValueError:
            pass

        return response

    def request_put_data(self, payload: list) -> Response:
        logging.info('2000: request_put_data')
        """
        Method to put data to the server. This method returns an instance of the :class:`requests.Response` class which
        indicates whether the data format is correct or not.

        To put the data in the server it is necessary to have a session opened

        >>> from stateful.push.core import SessionManager
        >>> session = SessionManager()
        >>> session.request_open_session('COUNTRY_CODE', 'NATIONAL_IDENTIFIER' 'API_KEY_VALUE')

        where ``'COUNTRY_CODE'`` is the country code, ``'NATIONAL_IDENTIFIER'`` is the national identifier,
        and ``'API_KEY_VALUE'`` is the API key value to access the session. After opening the session
        using the ``session`` instance, the same instance is used to put the data to the server as follows

        >>> session.request_put_data(payload)

        where ``payload`` is a ``list`` format data where the data to be sent is stored.

        :param payload: data to be sent to the server
        :type payload: list

        :return: :class:`requests.Response`

        """

        # obtaining the current time stamp
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        try:
            # updating the data to be sent to the server
            # creating the data information within the payload
            data = {'exchangeInformation': self.data['exchangeInformation'], 'payload': payload}
            # adding the timestamp according to the time when the message is created
            data['exchangeInformation']['DynamicInformation']['messageGenerationTimestamp'] = timestamp
        except ValueError:
            data = None
        except TypeError:
            data = None
        # serialization of data to JSON formatted str
        body = json.dumps(data)
        print('data:::::::::::::::::::::::::::::::::')
        print(data)
        # consuming the service to put data, requesting the server to upload the data stored in data variable
        try:
            url_pub= f'{settings.ENV_SERVER_URL}/{self.typepublication}{settings.PUT_DATA_PATH}'
            response =  self.post(url_pub, data=body)
        except :
            response = b"{}"
            logging.error('209: Fail on put data -- Client Status OFF')
        # checking if response is correct, if not it is returned an error
        if self.session_id is None:
            # stop task job
            self.task.stop()
            # self.task.join()

        return response

    def request_put_snapshot_data(self, payload: list) -> Response:
        """
        Method to put snapshot data to the server. This method returns an instance of the :class:`requests.Response`
        class which indicates whether the data format is correct or not.

        To put the snapshot data in the server it is necessary to have a session opened

        >>> from stateful.push.core import SessionManager
        >>> session = SessionManager()
        >>> session.request_open_session('COUNTRY_CODE', 'NATIONAL_IDENTIFIER', 'API_KEY_VALUE')

        where ``'COUNTRY_CODE'`` is the country code, ``'NATIONAL_IDENTIFIER'`` is the national identifier,
        and ``'API_KEY_VALUE'`` is the API key value to access the session. After opening the session
        using the ``session`` instance, it is used to put the snapshot data to the server as follows

        >>> session.request_put_snapshot_data(payload)

        where ``payload`` is a ``list`` format data where the data to be sent is stored.

        :param payload: data to be sent to the server
        :type payload: list

        :return: :class:`requests.Response`

        """

        # obtaining the current time stamp
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        try:
            # updating the data to be sent to the server
            # creating the data information within the payload
            data = {'exchangeInformation': self.data['exchangeInformation'], 'payload': payload}
            # adding the timestamp according to the time when the message is created
            data['exchangeInformation']['DynamicInformation']['messageGenerationTimestamp'] = timestamp
        except ValueError:
            data = None
        except TypeError:
            data = None
        # serialization of data to JSON formatted str
        body = json.dumps(data)
        # consuming the service to put data, requesting the server to upload the data stored in data variable
        try:
            url_pub= f'{settings.ENV_SERVER_URL}/{self.typepublication}{settings.PUT_SNAPSHOT_DATA_PATH}'
            response = self.post(url_pub, data=body)
        except :
            response = b"{}"
            logging.error('207: Fail on put SnapshotData -- Client Status OFF')
        # checking if response is correct, if not it is returned an error
        if self.session_id is None:
            # stop job
            self.task.stop()
            # self.task.join()

        return response

    def request_close_session(self) -> Response:
        """
        Method to close an opened session. This method returns an instance of the :class:`request.Response` class.

        To close the session it is necessary to have a session opened

        >>> from stateful.push.core import SessionManager
        >>> session = SessionManager()
        >>> session.request_open_session('COUNTRY_CODE', 'NATIONAL:IDENTIFIER', 'API_KEY_VALUE')

        where ``'COUNTRY_CODE'`` is the country code, ``'NATIONAL_IDENTIFIER'`` is the national identifier,
        and ``'API_KEY_VALUE'`` is the API key value to access the session. After opening the session
        using the ``session`` instance, it is used to close the session as follows

        >>> session.request_close_session()

        The previous line of code closes both the session in the server and the session created within this class at
        the moment the ``session`` instance is created. Also is stoped the task job, created when the session was
        opened.

        :return: :class:`requests.Response`

        """

        # obtaining the current time stamp
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        # updating the data to be sent to the server
        # creating the data information and the status is changed to closingSession
        try:
            self.data['exchangeInformation']['DynamicInformation']['exchangeStatus'] = 'closingSession'
            # adding the timestamp according to the time when the message is created
            self.data['exchangeInformation']['DynamicInformation']['messageGenerationTimestamp'] = timestamp
        except TypeError:
            pass
        # serialization of data attribute to JSON formatted str
        body = json.dumps(self.data)
        # consuming the service to close the session
        try:
            url_pub= f'{settings.ENV_SERVER_URL}/{self.typepublication}{settings.CLOSE_SESSION_PATH}'
            response = self.post(url_pub, data=body)
        except :
            response = b"{}"
            logging.error('208: Fail on close session -- Client Status OFF')
        # stop active job
        self.task.stop()
        self.session_id = None
        # self.task.join()
        # close SessionManager session
        logging.info('114: Client Status OFF')
        self.close()

        return response
