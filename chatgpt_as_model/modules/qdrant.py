from qdrant_client import QdrantClient
from logs import get_logger

logger = get_logger("debug_logger","logs/debug/debug_logger.log")
logger_error = get_logger("error_logger","logs/error/error_logger.log")

def setting_qdrant_connection(QDRANT_URL,QDRANT_API_KEY):
  ''' Setting up the connection with qdrant database '''
  try:
    logger.info(":) CREATING CONNECTION WITH QDRANT :) line 10 in modules/qdrant.py")
    qdrant_client = QdrantClient(
          url=QDRANT_URL,
          api_key=QDRANT_API_KEY
      )
    logger.info(":) CONNECTION CREATED WITH QDRANT :) line 15 in modules/qdrant.py")
    return qdrant_client
  except Exception as e:
    logger_error.error(f'An eror occured in embdeddings.py : {e} line 18 in modules/qdrant.py')


def create_collection(qdrant_client,collection_name,vector_size=1536,distance='Cosine'):
  ''' Used to create collection in qdrant '''
  try:
    logger.info(":) CREATING OR FETCHING COLLECTION FROM OR TO QDRANT :) line 24 in modules/qdrant.py")
    qdrant_client.create_collection(
        collection_name=collection_name, 
        vectors_config={
            "size":vector_size, # 384,  # Dimension of embeddings from "sentence-transformers/all-MiniLM-L6-v2"
            "distance": distance #"Cosine"  # Choose Cosine distance for vector similarity
        }
    )
    logger.info(":) FETCHED OR CREATED COLLECTION SUCCESSFULLY :)  line 32 in modules/qdrant.py")
    return f"{collection_name} is created successfully in qdrant"
  except Exception as e:
    logger_error.error(f'An eror occured in qdrant.py : {e} line 35 in modules/qdrant.py')