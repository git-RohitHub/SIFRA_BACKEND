from langchain.text_splitter import RecursiveCharacterTextSplitter
from logs import get_logger

logger = get_logger("debug_logger","logs/debug/debug_logger.log")
logger_error = get_logger("error_logger","logs/error/error_logger.log")

def splitting_doc(docs):
  ''' Used to split the scraped text into chunks of size 1000 with overlap of 300 '''
  try:
    logger.info(":) CHUNKS CREATION STARTED :) line 10 in modules/splitter.py")
    text_splitter = RecursiveCharacterTextSplitter(
          separators=['\n\n', '\n', '(?<=\. )', ' ', ''],
          chunk_size=1000,
          chunk_overlap=300
      )
    splits = text_splitter.split_documents(docs)
    logger.info(":) CHUNKS CREATION DONE :) line 17 in modules/splitter.py")
    return splits
  except Exception as e:
    logger_error.error(f'An eror occured in search_collection.py : {e} line 20 in modules/splitter.py')
