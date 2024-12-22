import json 
from logs import get_logger

logger = get_logger("debug_logger","logs/debug/debug_logger.log")
logger_error = get_logger("error_logger","logs/error/error_logger.log")

def detect_topic_shift_with_llm(llm, question,history):
    try:
      prompt = f"""
      You are an intelligent assistant tasked with determining the semantic relationship between a new query and the conversation history. You must also check if the new query contains implicit references to prior context and clarify them.

      **Instructions:**
      - Evaluate the semantic relationship between the new query and the conversation history.
      - Respond strictly in the following JSON format:
        ```json
        {{"SemanticallyRelated": "<Yes/No>", "NewQuery": "<ReframedQuery or OriginalQuery>"}}
        ```
        - If "SemanticallyRelated" is "No," the "NewQuery" field must contain the original query without any changes.
        - If "SemanticallyRelated" is "Yes," clarify implicit references in the query using the conversation history for context and update the "NewQuery" accordingly.
      - Provide no explanations, comments, or additional data outside the JSON format.

      **Examples for Reference:**

      ### Example 1:
      **History:**
      Human: what is Biconomy?
      AI: Biconomy is a decentralized platform for blockchain-based identity verification.
      **New Query:** what are its applications?

      **ANSWER:**
      ```json
      {{"SemanticallyRelated": "Yes", "NewQuery": "what are the applications of Biconomy?"}}
      ```

      ### Example 2:
      **History:**
      Human: what is Biconomy?
      AI: Biconomy is a decentralized platform for blockchain-based identity verification.
      **New Query:** where is the Eiffel Tower located?

      **ANSWER:**
      ```json
      {{"SemanticallyRelated": "No", "NewQuery": "where is the Eiffel Tower located?"}}
      ```

      ### Example 3:
      **History:**
      Human: what is Biconomy?
      AI: Biconomy is a platform for blockchain-based identity verification.
      Human: How does it work?
      **New Query:** Can you explain it in detail?

      **ANSWER:**
      ```json
      {{"SemanticallyRelated": "Yes", "NewQuery": "Can you explain how Biconomy works in detail?"}}
      ```

      ### Example 4:
      **History:**
      Human: who is the current Prime Minister of India?
      AI: Narendra Modi is the current Prime Minister of India.
      **New Query:** where was he born?

      **ANSWER:**
      ```json
      {{"SemanticallyRelated": "Yes", "NewQuery": "where was Narendra Modi born?"}}
      ```

      ### Task:
      Analyze the inputs below:
      **History:**
      {history}

      **New Query:**
      {question}

      - Identify whether the new query is semantically related to the history.
      - Check for implicit references in the new query and modify it to include full context.
      - Respond in the JSON format only, as shown in the examples.
      """
      response = llm(prompt)
      # print(response)
      return response
    except Exception as e:
       logger_error.error("Error Occured : {e} line 84 openai_dir/reframe_query.py")
       raise(e)


def extract_json(response):
  try:
      # Remove the ```json and ``` markers
      clean_content = response.content.strip("```json").strip("```").strip()

      # Parse the JSON
      parsed_json = json.loads(clean_content)
      return parsed_json  # Output the parsed JSON
  except json.JSONDecodeError as e:
      logger_error.error("Error Occured : {e} line 97 openai_dir/reframe_query.py")
      raise(e)


def has_topic_changed(llm,question,memory):
    """
    Determines if the topic has shifted based on similarity.
    """
    try:
      logger.info(":) QUERY REFRAMING STARTED :) line 99 openai_dir/reframe_query.py")
      history = memory.load_memory_variables({}).get("history", "")
      if not history.strip():
          logger.info(":) NO CHAT HISTORY PRESENT :) line 104 openai_dir/reframe_query.py")
          response =  {'SemanticallyRelated':True,'NewQuery':question} 
          return response['NewQuery'] # No history means a new topic
      else:
        logger.info(":) CHAT HISTORY LOADED :) line 102 openai_dir/reframe_query.py")
        model_response = detect_topic_shift_with_llm(llm, question, history)
        logger.info(":) TOPIC SHIFT DETECTION DONE :) line 109 in openai_dir/reframe_query.py")
        json_response = extract_json(model_response)
        return json_response['NewQuery']
    except Exception as e:
       logger_error.info("ERROR OCCOURED : {e} line 114 in openai_dir/reframe_query.py")