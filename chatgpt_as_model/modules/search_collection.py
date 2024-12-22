from logs import get_logger

logger = get_logger("scraper_debug_logger","logs/debug/scraper.log")
logger_error = get_logger("scraper_error_logger","logs/error/scraper.log")

def collection_exists(qdrant_client, collection_name):
    """ Check if the collection exist or not in Qdrant """
    try:
        logger.info(":) CHECKING COLLECTION EXISTS OR NOT")
        collections = qdrant_client.get_collections()  
        for collection in collections.collections:  
            if collection.name == collection_name:
                logger.info(" :) CHECKED COLLECTION EXIST :)")
                return True
        logger.info(":( CHECKED COLLECTION DID NOT EXIST :(")
        return False
    except Exception as e:
        logger_error.error(f'An eror occured in search_collection.py : {e}')