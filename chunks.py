import os
import re
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from document_preprocess.documents_loader import DocumentLoader
from langchain.text_splitter import CharacterTextSplitter
from document_preprocess.text_splitter import TextSplitter
# Загрузите переменные окружения из .env
# load_dotenv()

class Chunk():
    def __init__(self, ch_size:int=1024):
        # Получите API ключ из переменной окружения
        openai_api_key = 'sk-iX_KNpcImAxA66tJXsTeIPynthstL66eQEjelliJBrT3BlbkFJqwXf-0f5X9sx5m1YGdodn-ofIbYj5x8g59lJrXWHkA'
        self.ch_size = ch_size
        # Создайте экземпляр ChatOpenAI
        self.llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4o", temperature=0.1)
        # Инициализируйте базу данных без документов
        document_loader = DocumentLoader(path="./RAG-Documents")
        documents = document_loader.load_documents()


        splitter = TextSplitter()
        chunks = splitter.split_docs(documents)
        # Создайте документы из кусков текста
        documents = [Document(page_content=str(chunk)) for chunk in chunks]
        self.documents=documents
        # Добавьте новые документы в общий список документов
    
        # Если база данных еще не создана, создайте новую. Если уже существует, добавьте новые документы
        embeddings = OpenAIEmbeddings(api_key=openai_api_key, model='text-embedding-3-large')

        self.db = FAISS.from_documents(documents, embeddings)


  

    def load_pdf(self, path: str):
        """Функция для загрузки и обработки PDF-файлов"""
        document_loader = DocumentLoader(path="./new_files")
        documents = document_loader.load_documents()


        splitter = TextSplitter()
        chunks = splitter.split_docs(documents)
        new_documents  = [Document(page_content=str(chunk)) for chunk in chunks]

        self.documents.extend(new_documents)

        if self.db is None:
            self.db = FAISS.from_documents(new_documents, self.embeddings)
            
                # Проверка формата векторов
                # print(f"Adding {len(new_documents)} new documents to the database.")
                
        self.db.add_documents(new_documents)

    
    async def async_get_answer(self, query:str = None):
        """Асинхронная функция получения ответа от chatgpt

        Args:
            query (str, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """        
        # Задайте системный промпт
        system_prompt = """
        Ты помощник для дорожных служб и должен отвечать пользователям на основе документов с информацией. 
        Не придумывай ничего от себя, отвечай максимально по документу. Не упоминай Документ с информацией 
        для ответа пользователю.
        Если ответа на вопрос нет в документе, отвечай, что не можешь помочь с этим вопросом
        """

        # Найдите релевантные отрезки из базы
        docs = self.db.similarity_search(query, k=4)
        message_content = re.sub(r'\n{2}', ' ', '\n '.join([f'\nОтрывок документа №{i+1}\n=====================' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
        
        # Создайте промпт и получите ответ
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{input}")
        ])
        output_parser = StrOutputParser()
        chain = prompt | self.llm | output_parser 

        # print(message_content)
        answer = chain.invoke({"input": f"Ответь на вопрос пользователя. Не упоминай документ с информацией для ответа пользователю в ответе. Документ с информацией для ответа пользователю: {message_content}\n\nВопрос пользователя: \n{query}"})
        
        return answer

