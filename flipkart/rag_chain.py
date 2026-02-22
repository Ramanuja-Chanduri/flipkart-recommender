from langchain_groq import ChatGroq
from langchain_core.retrievers import BaseRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from langchain_community.chat_message_histories import ChatMessageHistory

from typing import List
from flipkart.config import config


class RAGChainBuilder:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.llm = ChatGroq(model=config.LLM_MODEL, api_key=config.GROQ_API_KEY, temperature=0.5)
        self.chat_history = {}

    def _get_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.chat_history:
            self.chat_history[session_id] = ChatMessageHistory()
        return self.chat_history[session_id]

    def build_chain(self):
        retriever: BaseRetriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

        context_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given the chat history and user question, rewrite it as a standalone question."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", """You're an e-commerce bot answering product-related queries using reviews and titles.
                          Stick to context. Be concise and helpful.\n\nCONTEXT:\n{context}\n\nQUESTION: {input}"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        def format_docs(docs: List[Document]) -> str:
            return "\n\n".join(doc.page_content for doc in docs)

        # 1. Rewrite the question as a standalone query using chat history
        history_aware_retriever = (
            RunnablePassthrough.assign(
                standalone_question=context_prompt | self.llm | StrOutputParser()
            )
            | (lambda x: retriever.invoke(x["standalone_question"]))
        )

        # 2. Format docs, build prompt, generate answer
        document_chain = (
            RunnablePassthrough.assign(context=lambda x: format_docs(x["context"]))
            | qa_prompt
            | self.llm
            | StrOutputParser()
        )

        # 3. Full RAG pipeline: retrieve → answer
        retrieval_chain = (
            RunnablePassthrough.assign(context=history_aware_retriever)
            .assign(answer=document_chain)
        )

        return RunnableWithMessageHistory(
            retrieval_chain,
            self._get_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer"
        )