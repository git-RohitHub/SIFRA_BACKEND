from logs import get_logger
logger = get_logger("debug_logger","logs/debug/debug_logger.log")
logger_error = get_logger("error_logger","logs/error/error_logger.log")

from langchain.memory import ConversationBufferWindowMemory
def load_memory():
    try:
        memory = ConversationBufferWindowMemory(k=5, input_key="question", memory_key="history")
        logger.info("Memory Loaded successfully line 9 in openai_dir/load_memory.py")
        return memory
    except Exception as e:
        logger.error(f"Error Occoured in load_memory : {e}")
        # raise(e)