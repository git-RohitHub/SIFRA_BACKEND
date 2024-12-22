import warnings
warnings.filterwarnings("ignore")
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, SystemMessage
from logs import get_logger

logger = get_logger("debug_logger","logs/debug/debug_logger.log")
logger_error = get_logger("error_logger","logs/error/error_logger.log")


def format_response(response):
    # Ensure proper spacing and remove unwanted characters
    formatted = response.strip()
    # Additional formatting logic can be added here if needed
    return formatted

def creating_response(query,retriever,model_name):
    llm = ChatOpenAI(model_name=model_name)
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, say that you don't know. "
        "Your answer should be short conscise and to the point and if required provide detailed answer"
        "Provide your response in Markdown format:\n"
        "- Use **bold** for emphasis.\n"
        "- Use bullet points for lists.\n"
        "- Separate sections with headings.\n"
        "\n"
        "{context}"
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    results = rag_chain.invoke({"input": query})
    response = format_response(results['answer'])
    return response





def creating_response_with_memory(query, retriever, model_name='gpt-4', memory=None):
    try:
        # Define the LLM with the specified model name
        llm = ChatOpenAI(model=model_name)
        logger.info(":) LLM LOADED FOR QUESTION ANSWERING SUCCESSFULLY line 55 in openai_dir/response.py :)")
        # Define the system prompt template
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer, say that you don't know. "
            "Your answer should be short, concise, and to the point. "
            "If required, provide a detailed answer. "
            "Provide your response in Markdown format:\n"
            "- Use **bold** for emphasis.\n"
            "- Use bullet points for lists.\n"
            "- Separate sections with headings.\n"
            "\n"
            "{context}"
        )
        logger.info(":) PROMPT LOADED SUCCESSFULLY line 71 in openai_dir/response.py :)")
        # Initialize memory with explicit input and output keys
        if memory is None:
            memory = ConversationBufferMemory(
                memory_key="history", 
                input_key="question", 
                output_key="response", 
                return_messages=True
            )
        
        # Retrieve context using RAG chain
        question_answer_chain = create_stuff_documents_chain(llm, ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{input}")]))
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        retrieved_context = rag_chain.invoke({"input": query})
        
        # Prepare input messages for the LLM
        messages = [
            SystemMessage(content=system_prompt.format(context=retrieved_context.get("context", ""))),
            HumanMessage(content=query)
        ]
        
        # Generate the final response using the LLM
        response = llm(messages)
        logger.info(":) RESPONSE GENERATED SUCCESSFULLY line 93 in openai_dir/response.py :)")
        # Save the query and response to memory
        memory.save_context(
            inputs={"question": query},
            outputs={"response": response.content}
        )
        logger.info(":) CHAT SAVED TO HISTORY SUCCESSFULLY line 99 in openai_dir/response.py :)")
        return response.content
    except Exception as e:
        logger_error.error(f"Error Occoured : {e} line 103 openai_dir/response.py")

