from langchain_groq import ChatGroq
from langchain_core.retrievers import BaseRetriever 
from langchain_core.prompts import BasePromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import MessagesPlaceholder

from flipkart.config import config


class RAGChainBuilder:
    def __init__(self, vector_store: BaseRetriever):
        self.vector_store = vector_store
        self.llm = ChatGroq(model=config.LLM_MODEL, api_key=config.GROQ_API_KEY, temperature=0.5)
        self.chat_history = {}
    
    def _get_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.chat_history:
            self.chat_history[session_id] = ChatMessageHistory()
        return self.chat_history[session_id]

    def _create_history_aware_retriever(self, 
        llm: ChatGroq, 
        retriever: BaseRetriever, 
        prompt_template: BasePromptTemplate,
    ) -> BaseRetriever:
        """
        Create a history-aware retriever that incorporates conversation history into the retrieval process.

        Args:
            llm (ChatGroq): The language model to use for generating responses.
            retriever (BaseRetriever): The base retriever to wrap with history awareness.
            prompt_template (BasePromptTemplate): The prompt template to use for generating queries.
        Returns:
            BaseRetriever: A new retriever that incorporates conversation history.
        """

        # Rewriter Chain
        question_rewriter = (
            prompt_template
            | llm
            | StrOutputParser()
        )

        # History-Aware Retriever Chain
        history_aware_chain = (
            RunnablePassthrough.assign(
                standalone_question=question_rewriter
            )
            | (lambda x: retriever.invoke(x["standalone_question"]))
        )

        return history_aware_chain
    
    def _create_stuff_documents_chain(self, 
        llm: ChatGroq, 
        prompt_template: BasePromptTemplate,
        ) -> RunnablePassthrough:
        """
        Create a chain that stuffs retrieved documents into the prompt for the language model.

        Args:
            llm (ChatGroq): The language model to use for generating responses.
            prompt_template (BasePromptTemplate): The prompt template to use for generating queries.
        Returns:
            A chain that stuffs retrieved documents into the prompt for the language model.
        """

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        chain = (
            RunnablePassthrough.assign(
                context=lambda x: format_docs(x["context"]),
            )
            | prompt_template
            | llm
            | StrOutputParser()
        )

        return chain
    
    def _create_retrieval_chain(
        self,
        retriever: BaseRetriever,
        document_chain,
    ):
        """
        Full RAG pipeline:
        1. Retrieve docs
        2. Generate answer
        3. Return answer + context
        """

        retrieval_chain = (
            RunnablePassthrough.assign(
                context=retriever
            )
            .assign(
                answer=document_chain
            )
        )

        return retrieval_chain

    
    def build_chain(self):
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

        # Define prompt templates
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
        
        history_aware_retriever = self._create_history_aware_retriever(
            llm=self.llm,
            retriever=retriever,
            prompt_template=context_prompt
        )
        
        document_chain = self._create_stuff_documents_chain(
            llm=self.llm,
            prompt_template=qa_prompt
        )
        
        retrieval_chain = self._create_retrieval_chain(
            retriever=history_aware_retriever,
            document_chain=document_chain
        )
        
        conversational_chain = RunnableWithMessageHistory(
            retrieval_chain,
            self._get_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer"
        )
        
        return conversational_chain