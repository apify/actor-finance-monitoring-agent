from langchain_openai import ChatOpenAI


class ChatOpenAISingleton:
    """Singleton class for ChatOpenAI instance."""

    _instance: ChatOpenAI | None = None

    @classmethod
    def create_get_instance(cls, model: str) -> ChatOpenAI:
        """Creates and returns ChatOpenAI instance, used for creating the singleton instance.

        Returns:
            ChatOpenAI: ChatOpenAI instance
        """
        if cls._instance is None:
            cls._instance = ChatOpenAI(model=model)
        return cls._instance

    @classmethod
    def get_instance(cls) -> ChatOpenAI:
        """Gets ChatOpenAI instance.

        Returns:
            ChatOpenAI: ChatOpenAI instance.

        Raises:
            ValueError: If instance is not created yet.
        """
        if cls._instance is None:
            msg = 'ChatOpenAI instance not created yet!'
            raise ValueError(msg)
        return cls._instance
