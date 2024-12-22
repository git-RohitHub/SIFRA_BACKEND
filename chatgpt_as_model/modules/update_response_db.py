import requests
from logs import get_logger
logger = get_logger("debug_logger","logs/debug/debug_logger.log")
logger_error = get_logger("error_logger","logs/error/error_logger.log")

def update_db(chatId,chatResponse,UPDATE_DB_URL):
    try:
        logger.info(":) UPDATING INTERACTION IN DATABASE line 8 update_response_db.py :)")
        headers = {
            'Content-Type': 'application/json',
        }

        json_data = {
            'chatResponse': chatResponse,
            'chatId': chatId,
        }

        response = requests.put(UPDATE_DB_URL, headers=headers, json=json_data)
        if response.status_code==200:
            logger.info(":) UPDATION SUCCESSFULL line 20 update_response_db.py :)")
        else:
            logger.info(":) UPDATION FAILED line 22 update_response_db.py :)")
        return response
    except Exception as e:  
        logger_error.error("An Error Occoured in line 25 update_response_db.py ")


        