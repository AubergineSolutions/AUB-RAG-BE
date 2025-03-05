from langchain.prompts import PromptTemplate
from ..services.vectorstore import get_vectorstore
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from ..config import Config

prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template='''\n    You are an AI assistant. Answer based on the context provided.\n    \n    {context}\n    ---\n    User Query: {question}\n    ''')

def get_answer(query):
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    llm = ChatOpenAI(model_name="gpt-4", api_key=Config.OPENAI_API_KEY)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
    response = qa_chain({"query": query})
    answer = response["result"]
    sources = [doc.metadata["source"] for doc in response["source_documents"]]
    return {"answer": answer, "sources": sources}