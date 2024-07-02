
from datetime import datetime, timedelta
from django.conf import settings
from invias.src.stateful.push.core import SessionManager
import invias.src.translator.bogota_translator as bogota_translator
import logging
import asyncio

async def main_task_loop(session):
    process = 1
    while True:
        process += 1
        try:
            logging.info('105: We proceed to start the execution to the Bogotá translator')
            bogota_translator.session_process(session)
            logging.info('106: The execution of the Bogotá translator ends')
        except ConnectionError:
            logging.error("205: An unexpected error occurred in the execution of the translator.")
        await asyncio.sleep(30 * 1)
        # await asyncio.sleep(60 * settings.ENV_REQUEST_TIME)