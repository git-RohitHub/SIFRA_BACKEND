from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage

def prompt(chatbot_name,created_by):
    prompt_template = PromptTemplate(
        input_variables=["context", "input"],
        template=(
            "You are a friendly assistant for question-answering tasks. "
            f"Your name is {chatbot_name} and you are created by {created_by}"
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use clear sentences and keep the "
            "answer concise and to the point.\n\n"
            "{context}\n\n"
            "Question: {input}"
        )
    )
    return prompt_template

def formatter_prompt(query,context,chatbot_name,created_by):
    prompt_template = prompt(chatbot_name,created_by)
    formatted_prompt = prompt_template.format(input=query, context=context)
    messages = [
        SystemMessage(content="You are an assistant for question-answering tasks."),
        HumanMessage(content=formatted_prompt)
    ]
    return messages