import requests
from preprocess import get_docs, FunctionDoc
from typing import List, Tuple

from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma



""" 
Build the index using openai embeddings and save to directory
"""
def build_index_db(documents : List[Document], index_name):
    embeddings = OpenAIEmbeddings()
    vectordb   = Chroma.from_documents(documents, embeddings, persist_directory=index_name+"_index")
    vectordb.persist()


"""
Get pre-built index db
"""
def get_index_db(persist_directory : str) -> Chroma:
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory=persist_directory+"_index", embedding_function=embeddings)
    return vectordb


"""
Pull code from github and extract function signatures and docstrings
"""
def ingest_doc_page(doc_url, index_name) -> List[Document]:
    code : str = requests.get(doc_url).text
    docs : list[FunctionDoc] = get_docs(code, index_name)
    return [Document(page_content=str(doc)) for doc in docs]
