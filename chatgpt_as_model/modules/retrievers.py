from logs import get_logger

logger = get_logger("debug_logger","logs/debug/debug_logger.log")
logger_error = get_logger("error_logger","logs/error/error_logger.log")


def naive_retriever(vectorstore):
    """ Create Naive Retriever with k=5 using Vectorstore Qdrant """
    try:
        logger.info(":) RETRIEVER CREATION STARTED :) line 10 in modules/retrievers.py")
        naive_retriever = vectorstore.as_retriever(search_kwargs={ "k" : 10})
        logger.info(":) RETRIEVER CREATED SUCCESSFULLY :) line 12 in modules/retrievers.py")
        return naive_retriever
    except Exception as e:
        logger_error.error(f'An eror occured in embdeddings.py : {e} line 15 in modules/retrievers.py')


