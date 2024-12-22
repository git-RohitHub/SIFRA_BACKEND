from logs import get_logger
from sentence_transformers import CrossEncoder



logger = get_logger("fetch_context_debug_logger","logs/debug/fetch_context.log")
logger_error = get_logger("fetch_context_error_logger","logs/error/fetch_context.log")

def context(document):
    for doc in document:
        text = ''.join(doc.page_content)
        return text
    
def relevant_chunks(retriever,query):
   """ Invoke the retriever with the query to get the relevant chunks to answer query """
   try:
      logger.info(":) START FETCHING CONTEXT :)")
      documents = retriever.invoke(query)
      logger.info(":) CONTEXT FETCHED SUCCESSFULLY :)")
      response = context(documents)
      return response
   except Exception as e:
      logger_error.error(f"An Error Occured in fetch_contex.py : {e}")


def retriever_content(retriever_list,query):
    '''Fetch Context from the multiple collection based on query and combined'''
    try:
        all_docs = []
        logger.info(":) FETCHING CONTEXT FROM ALL RETRIEVERS IN A LIST :)")
        for retriever in retriever_list:
            docs = retriever.invoke(query)
        logger.info(":) FETCHED CONTEXT FROM ALL RETRIEVERS IN A LIST SUCCESSFULLY :)")
        all_docs.extend(docs)
        return all_docs
    except Exception as e:
        logger_error.error(f"An error Occured in retriever_content : {e}")

def reranker(retriever_list,query,CROSSENCODER):
    try:
        reranker_obj = CrossEncoder(CROSSENCODER)
        documents = retriever_content(retriever_list,query)
        doc_texts = [doc.page_content for doc in documents]
        query_doc_pairs = [[query, doc_text] for doc_text in doc_texts]
        scores = reranker_obj.predict(query_doc_pairs)  
        docs_with_scores = list(zip(documents, scores))
        sorted_docs = sorted(docs_with_scores, key=lambda x: x[1], reverse=True)
        top_4_docs = [doc[0] for doc in sorted_docs[:10]]
        logger.info(":) RERANKING OF CONTEXT DONE :)")
        text = context(top_4_docs)
        logger.info(":) Context Extracted Successfully :)")
        return text
    except Exception as e:
        logger_error.error(f"An error Occured in reranker : {e}")

