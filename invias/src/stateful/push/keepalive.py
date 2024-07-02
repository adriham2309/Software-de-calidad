# from pytest import Session
from django.conf import settings
from typing import Optional
from requests.auth import HTTPBasicAuth
import threading
import json
import requests
import logging
import datetime


logging.basicConfig(level=logging.INFO)

exit_event = threading.Event()


class KeepAliveTask(threading.Thread):
    """
    This class is a task managing service, which allows executing tasks in background using the ``threading`` Python
    module. It is an extension of the :class:`threading.Thread` class.
    """
    def __init__(self):
        """
        This class is a task managing service, which allows executing tasks in background using the ``threading``
        Python module. It is an extension of the :class:`threading.Thread` class.

        This class has three needed attributes which have to be set: ``session``, ``data``, ``auth``. The ``session``
        attribute is a cookie value for the current session which needs to be passed to the instance class. The ``data``
        attribute carries the information of the data of the session opened. And the ``auth`` attribute has the API key
        value to validate the authentication in the server side.

        """

        # starting a Thread class instance from which the current class will inherit attributes and methods
        threading.Thread.__init__(self)
        # url attribute related to the request url to keep the session alive
        self.url = settings.ENV_SERVER_URL + settings.KEEP_ALIVE_PATH
        # time in minutes to do a request to the server
        self.every_minutes = settings.ENV_KEEP_ALIVE_MINUTES
        # session key stored in the session cookies
        self.session: Optional[str] = None
        # data related to the session opened
        self.data: Optional[dict] = None
        # authentication information
        self.auth: Optional[HTTPBasicAuth] = None
        # type publication stored in the session opened
        self.typepublication: Optional[str] = None

    def run(self):
        """
        Method that overrides the Thread method with the same name. This method allows doing request to the
        URL stored in the ``url`` parameter. It is necessary to define the cookie parameter ``session`` and the
        authentication parameter ``auth`` that store the API key value in the :class:`requests.auth.HTTPBasicAuth`
        format class.

        """
        # loop to keep task running, it stops when exit_event.set() is called
        base_time_checking = datetime.datetime.now()
        try:
            while not exit_event.is_set():
                # request to the server side
                urltype =  f'{settings.ENV_SERVER_URL}/{self.typepublication}{settings.KEEP_ALIVE_PATH}'
                if (datetime.datetime.now() - base_time_checking).seconds >= 60 * self.every_minutes:
                    response = requests.post(                            
                        url=urltype,
                        cookies=dict(session=self.session),
                        data=json.dumps(self.data),
                        auth=self.auth
                    )
                    
                    logging.info('Keeping alive session...')
                    # logging.info('120: Keeping alive response <' + str(response.status_code) + '> ' + str(response.content, settings.ENCODING))
                    # logging.info('Keeping alive response is {}'.format(response.content))
                    respuesta_status=response.json()
                    # print(respuesta_status["exchangeInformation"]["DynamicInformation"]["exchangeStatus"])
                    if respuesta_status["exchangeInformation"]["DynamicInformation"]["exchangeStatus"] == "online":
                        logging.info('115: Ack keepAlive -- Client Status ON')
                    else:
                        self.stop()
                        logging.info('209: Fail on KeepAlive -- Client Status OFF')
                    base_time_checking = datetime.datetime.now()
            # logging.info('task ended...')
        except:
            self.stop()
            # res = self.request_close_session()
            logging.info('209: Fail on KeepAlive -- Client Status OFF')

    def stop(self):
        """
        Method to stops the execution of a running task.

        """

        exit_event.set()
    def is_alive(self) -> bool:
        return super().is_alive()