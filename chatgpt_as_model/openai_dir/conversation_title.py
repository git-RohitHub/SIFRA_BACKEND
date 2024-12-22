
def generate_conversation_title(llm, conversation_chain):
    try:
        prompt = f"""
        Create an attractive, interesting, and engaging title based on the following conversation chain. 
        The title should clearly reflect the main question or topic discussed while ensuring it is memorable and helpful for the user to recall the conversation's purpose later.

        Conversation Chain:
        {conversation_chain}
        """
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        pass

