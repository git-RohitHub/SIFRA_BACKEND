import warnings
warnings.filterwarnings("ignore")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from modules.crawlink_links import  get_all_website_links,combined_links
from urllib.parse import urlparse
from modules.scraper import create_document
import modules.vectorstore as vectorstore
import modules.qdrant as qdrant
import modules.splitter as splitter
import os
import uvicorn
from openai_dir.load_llm import generate_response
from openai_dir.prompt import formatter_prompt
from modules.search_collection import collection_exists
from modules.update_response_db import update_db
from modules.retrievers import naive_retriever
from modules.fetch_context import relevant_chunks,reranker                                                                                                                                                                                                                                                  
from openai_dir.response import creating_response,creating_response_with_memory
from modules.load_pdf import load_pdfs
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
from starlette.middleware.cors import CORSMiddleware
from openai_dir.load_memory import load_memory
from openai_dir.reframe_query import has_topic_changed
from openai_dir.conversation_title import generate_conversation_title
from logs import get_logger
from dotenv import load_dotenv
import re
load_dotenv()



## SETTING UP ENVIRONMENT VARIABLES 

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    
GPT_MODEL_NAME = os.getenv("GPT_MODEL_NAME")
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
UPDATE_DB_URL = os.getenv("UPDATE_DB_URL")






## CREATING FASTAPI APP

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

logger = get_logger("debug_logger","logs/debug/debug_logger.log")
logger_error = get_logger("error_logger","logs/error/error_logger.log")


logger.info("Entering into FastApi Environment ")
logger.info("Environment Variables Fetched Successfully ")


## LOADING MEMORY 

logger.info("MEMORY LOADING line 66 in main.py ")
memory = load_memory()
llm = ChatOpenAI(model_name = GPT_MODEL_NAME)
## PYDANTIC MODEL FOR REQUEST BODY 

class CrawlRequest(BaseModel):
    document_url: str
    collection_id : str

class AnswerQuery(BaseModel):
    query:str
    collection_id : str
    chat_id:str
    interaction_id:str


class AnswerQueryMultipleCollection(BaseModel):
    query : str
    collection_id : list

class checkCollection(BaseModel):
    collection_ids : list


class conversation_title(BaseModel):
    question:list
    answer:list
    interaction_id:str

# FastAPI ENDPOINTS 

@app.get("/")
def ai_bot():
    return f":) Hello dude welcome :)"

@app.post("/crawling_url")
def crawl_website(crawl_request: CrawlRequest):
    logger.info(":) CRAWLING_URL ENDPOINT HIT :)")
    url = crawl_request.document_url
    logger.info(f"=========== url==================:{url}")
    extension = url.split('.')[-1]
    if extension!="pdf":
        collection_name = crawl_request.collection_id
        logger.info(":) CRAWLER STARTED :) ")
        if not urlparse(url).scheme:
            logger.error(f"""{HTTPException(status_code=400, detail="Invalid URL format. URL must start with http:// or https://.")}""")

        try:
            crawl_result = get_all_website_links(url, max_threads=500)
            logger.info(":) CRAWLER STOP :)")
            total_links = combined_links(
                crawl_result["visited_links"],
                crawl_result["pdf_links"],
                crawl_result['other_non_html_links']
            )
            logger.info(f" :) ALL URL's CRAWLED FROM THE DOCUMENT  : {len(total_links)} :) line 112 in main.py")
            embeddings = OpenAIEmbeddings()
            logger.info(":) EMBEDDING MODEL LOADED SUCCESSFULLY :) line 114 in main.py")
            data = create_document(total_links)
            logger.info(":) ALL DATA SCRAPED FROM THE DOCUMENT SUCCESSFULLY :) line 116 in main.py")
            chunks = splitter.splitting_doc(data)
            logger.info(":) CHUNKS CREATION FROM SCRAPED DATA DONE :) line 118 in main.py")
            qdrant_client = qdrant.setting_qdrant_connection(QDRANT_URL,QDRANT_API_KEY)
            logger.info(":) QDRANT CONNECTION SET UP SUCCESSFULLY :) line 120 in main.py")
            qdrant.create_collection(qdrant_client,collection_name)
            logger.info(f":) COLLECTION : {collection_name} CREATED IN QDRANT SUCCESSFULLY :) line 122 in main.py")
            vectorstores_obj = vectorstore.create_or_fetch_vectorstore(qdrant_client,collection_name,embeddings)
            logger.info(":) VECTORSTORE CREATED SUCCESSFULLY  :) line 124 in main.py")
            status,success = vectorstore.vectorstore_add_data(qdrant_client,collection_name,vectorstores_obj,chunks)
            logger.info(":) DATA PUSHED INTO VECTOR DB :)")
            return {
                "status":status,
                "success":success
            }
        except Exception as e:
            logger_error.error(f"An Error occured while crawling: {str(e)} line 132 in main.py")
    else:
        collection_name = crawl_request.collection_id
        data = load_pdfs(url)
        logger.info(":) ALL DATA SCRAPED FROM THE PDF SUCCESSFULLY :) line 136 main.py")
        embeddings = OpenAIEmbeddings()
        logger.info(":) EMBEDDINGS LOADED SUCCESSFULLY :) line 138 in main.py")
        chunks = splitter.splitting_doc(data)
        logger.info(":) CHUNKS CREATION DONE :) line 140 main.py")
        qdrant_client = qdrant.setting_qdrant_connection(QDRANT_URL,QDRANT_API_KEY)
        logger.info(":) QDRANT CONNECTION SET UP :) line 142 main.py")
        qdrant.create_collection(qdrant_client,collection_name)
        logger.info("QDRANT COLLECTION CREATED FOR PDF SUCCESSFULLY :) line 144 main.py")
        vectorstores_obj = vectorstore.create_or_fetch_vectorstore(qdrant_client,collection_name,embeddings)
        logger.info(":) VECTORSTORE CREATED FOR PDF SUCCESSFULLY :) line 146 main.py")
        status,success = vectorstore.vectorstore_add_data(vectorstores_obj,chunks)
        logger.info(":) DATA PUSHED INTO VECTOR DB :) line 148 main.py")
        return {
                "response":status,
                "success":success
                }

   

## ENDPOINT 2 : 

@app.post("/answer_query") 
def answer_query(answer_query_request:AnswerQuery):
    logger.info(":) ANSWER QUERY ENDPOINT HIT :)")
    query = answer_query_request.query
    collection = answer_query_request.collection_id
    chatId = answer_query_request.chat_id
    interaction_Id = answer_query_request.interaction_id
    try:
        embeddings = OpenAIEmbeddings()
        logger.info(":) EMBEDDING MODEL LOADED SUCCESSFULLY :) line 165 main.py")
        qdrant_client = qdrant.setting_qdrant_connection(QDRANT_URL,QDRANT_API_KEY)
        logger.info(":) QDRANT CONNECTION ESTABLISHED SUCCESSFULLY :) line 167 main.py")
        if collection_exists(qdrant_client,collection) :
            vectorstores_obj = vectorstore.create_or_fetch_vectorstore(qdrant_client,collection,embeddings)
            logger.info(":) COLLECTION FETCHED FROM QDRANT :) line 170 main.py")
        else:
            return "No such collection exist please upload document first"
        naive_retriever_obj = naive_retriever(vectorstores_obj)
        logger.info(":) RETRIEVER CREATED SUCCESSFULLY :) line 174 main.py")
        updated_query = has_topic_changed(llm,query,memory)
        logger.info(":) QUERY REFRAMED SUCCESSFULLY :) line 178 main.py")
        logger.info(":) RETRIEVER CREATED SUCCESSFULLY :)")
        logger.info(":) INVOKING LLM :)")
        # response = creating_response(updated_query,naive_retriever_obj,GPT_MODEL_NAME)  ## INCASE YOU DON'T WANT MEMORY
        response2 = creating_response_with_memory(updated_query,naive_retriever_obj,GPT_MODEL_NAME,memory=memory)
        try:
            db_status = update_db(chatId,response2,UPDATE_DB_URL)
            if db_status.status_code==200:
                return {"response":response2,"db_status":'updated','interaction_Id':interaction_Id}
            else:
                return {"response":response2,"db_status":'failed_to_update','interaction_Id':interaction_Id}
        except Exception as e:
            pass
        logger.info(":) LLM ANSWERED THE QUESTION SUCCESSFULLY :) line 183 main.py")
        return {"response":response2,"db_status":'updated'}
    except Exception as e:
        logger_error.error(f"An error Occured in answer query main.py : {e} line 186 main.py")
    



@app.post("/answer_query_from_multiple_collection") 
def answer_query_from_multiple_collection(answer_query_multiple_collection_request:AnswerQueryMultipleCollection):
    logger.info(":) ANSWER QUERY ENDPOINT HIT :)")
    query = answer_query_multiple_collection_request.query
    collection_id = answer_query_multiple_collection_request.collection_id
    try:
        embeddings = load_embdeddings_model()
        logger.info(":) EMBEDDING MODEL LOADED SUCCESSFULLY :)")
        qdrant_client = qdrant.setting_qdrant_connection(QDRANT_URL,QDRANT_API_KEY)
        logger.info(":) QDRANT CONNECTION ESTABLISHED SUCCESSFULLY :)")
        vectorstores_list = []
        for collection in collection_id:
            if collection_exists(qdrant_client,collection) :
                vectorstores_obj = vectorstore.create_or_fetch_vectorstore(qdrant_client,collection,embeddings)
                vectorstores_list.append(vectorstores_obj)
                logger.info(":) COLLECTION FETCHED FROM QDRANT :)")
            else:
                return "No such collection exist please upload document first"
        naive_retriever_list = [naive_retriever(vectorstores_item) for vectorstores_item in vectorstores_list]
        logger.info(":) RETRIEVER CREATED SUCCESSFULLY :)")
        context = reranker(naive_retriever_list,query,CROSSENCODER)
        logger.info(":) CONTEXT SENDS AS RESPONSE :)")

        return context
    except Exception as e:
        logger_error.error(f"An error Occured in answer query main.py : {e}")



@app.post("/checkingCollection")
def checkCollection(checkCollection_request:checkCollection):
    logger.info("checkingCollection endpoint hits")
    collections_ids = checkCollection_request.collection_ids
    response_collection =[]
    try:
        logger.info(f"Collection_ids : {collections_ids}")
        qdrant_client = qdrant.setting_qdrant_connection(QDRANT_URL,QDRANT_API_KEY)
        if len(collections_ids)!=0:
            for id in collections_ids:
                if collection_exists(qdrant_client,id):
                    response_collection.append({'collection_id':id,"status":"success"})
                else:
                    with open("logs/debug/failed_collections.log",'r') as f:
                        data = f.read()
                    if re.match(data,id):
                        response_collection.append({'collection_id':id,'status':'error'})
                    else: 
                        response_collection.append({'collection_id':id,"status":"pending"})
                logger.info("Response send successfully ")
            return response_collection
        
        else:
            return f"please provide collection id"
    except Exception as e :
        logger_error.error("An Error Occoured : {e} line 243 main.py")


@app.post("/conversation_title")
def conversation_title(conversation_title_request:conversation_title):
    question = conversation_title_request.question
    answer = conversation_title_request.answer
    interaction_id = conversation_title_request.interaction_id
    try:
        conversation_chain = {'question':question,'answer':answer}
        logger.info(":) GENERATING TITLE FOR CONVERSATION :) ")
        title = generate_conversation_title(llm,conversation_chain)
        logger.info(":)  TITLE GENERATED SUCCESSFULLY :) ")
        return {"conversation_title":title,"interaction_id":interaction_id}
    except Exception as e:
        logger_error.error("An error occoured in main.py line 278 ",e)
                
if __name__ == "__main__":
    uvicorn.run(
        "main:app",  
        host="127.0.0.1",
        port=3000,
        log_level="info",
        reload=True
    )

