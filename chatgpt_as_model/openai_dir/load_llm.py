import warnings
warnings.filterwarnings("ignore")


def generate_response(messages,model_name):
    try:
        llm = ChatOpenAI(model=model_name)
        response = llm(messages)
        return {"answer": response.content}
    except Exception as e:
        return {"error": "An error occurred while generating the answer."}