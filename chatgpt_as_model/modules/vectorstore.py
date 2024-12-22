from langchain_community.vectorstores import Qdrant
from qdrant_client.http.models import VectorParams
from logs import get_logger

logger = get_logger("debug_logger","logs/debug/debug_logger.log")
logger_failed_collection = get_logger("failed_collections","logs/debug/failed_collections.log")
logger_error = get_logger("error_logger","logs/error/error_logger.log")

def create_or_fetch_vectorstore(qdrant_client,collection_name,embeddings):
  ''' Used to create or fetch existing vectordb from qdrant '''
  try:
     
    logger.info(":) VECTORSTORE CREATION STARTED :) line 12 in modules/vectorstore.py")
    vectorstore = Qdrant(
        client=qdrant_client,
        collection_name=collection_name,
        embeddings=embeddings
    )
    logger.info(":) VECTORSTORE CREATED OR LOADED :) line 18 in modules/vectorstore.py")
    return vectorstore
  except Exception as e:
    qdrant_client.delete_collection(collection_name)
    logger.info(f"Collection : {collection_name} DELETED FROM QDRANT")
    logger_failed_collection.info(collection_name)
    logger_error.error(f'An eror occured in vectorstore.py in create_or_fetch_vectorstore : {e} line 21 in modules/vectorstore.py')


def batch_data(data, batch_size):
  """Splits data into smaller batches."""
  for i in range(0, len(data), batch_size):
      yield data[i:i + batch_size]

import time

def vectorstore_add_data(qdrant_client, collection_name, vectorstore, data, batch_size=100):
    """Adds data to the vectorstore in batches with retry logic."""
    try:
        for batch in batch_data(data, batch_size):
            success = False
            attempts = 3  # Retry up to 3 times
            while not success and attempts > 0:
                try:
                    vectorstore.add_documents(batch)
                    logger.info(f"Batch of size {len(batch)} added successfully.")
                    success = True
                except Exception as e:
                    attempts -= 1
                    logger.warning(f"Retrying batch due to error: {e}. Attempts left: {attempts}")
                    time.sleep(5)  # Wait for 5 seconds before retrying
                    if attempts == 0:
                        raise e
        return ":) Data Added to Vectorstore Successfully :)", True
    except Exception as e:
        qdrant_client.delete_collection(collection_name)
        logger.info(f"Collection: {collection_name} DELETED FROM QDRANT")
        logger_error.error(f"An error occurred in vectorstore_add_data: {e}")
        return f"Error: {e}", False





# def vectorstore_add_data(qdrant_client,collection_name,vectorstore, data, batch_size=100):
#     """Adds data to the vectorstore in batches."""
#     try:
#         for batch in batch_data(data, batch_size):
#             vectorstore.add_documents(batch)
#             logger.info(f"Batch of size {len(batch)} added successfully. line 34 in modules/vectorstore.py")
#         return ":) Data Added to Vectorstore Successfully :)",True
#     except Exception as e:
#         qdrant_client.delete_collection(collection_name)
#         logger.info(f"Collection : {collection_name} DELETED FROM QDRANT")
#         logger_error.error(f"An error occurred in vectorstore_add_data: {e} line 37 in modules/vectorstore.py")
#         return f"Error: {e}",False


# def vectorstore_add_data(vectorstore,data):
#   ''' Used to add Data to the existing or newly created vectordb in qdrant '''
#   try: 
#     logger.info(":) DATA ADDED TO VECTORSTORE :) ")
#     vectorstore.add_documents(data)
#     logger.info(":) DATA ADDED TO VECTORSTORE SUCCESSFULLY :) ")
#     return f":) Data Added to Vectorstore Successfully :)"
#   except Exception as e:
#     logger_error.error(f'An eror occured in vectorstore.py in vectorstore_add_data : {e}')

# def create_collection(qdrant_client,collection_name,vectors):
#     try:
#         qdrant_client.create_collection(
#                 collection_name=collection_name,
#                 vectors_config=VectorParams(  
#                     size=len(vectors[0]),  
#                     distance='Cosine'  
#                 )
#             )
#     except Exception as e:
#         print(f"Collection creation error: {e}")

# def inserting_data_collection(embeddings,splits,qdrant_client,collection_name,):
#     try:
#       vectors = embeddings.embed_documents([doc.page_content for doc in splits])
#       create_collection(qdrant_client,collection_name,vectors)
#       payloads = [{"text": doc.page_content} for doc in splits]  # Prepare payloads
#       ids = list(range(len(vectors))) 
#       qdrant_client.upsert(
#               collection_name=collection_name,
#               points=[
#                   {
#                       "id": id_,
#                       "vector": vector,
#                       "payload": payload
#                   }
#                   for id_, vector, payload in zip(ids, vectors, payloads)
#               ]
#           )
#       return ":) Data Added to Vectorstore Successfully :)"
#     except Exception as e:
#        logger_error.error(f"An error Occured in inserting data to collection {e}")