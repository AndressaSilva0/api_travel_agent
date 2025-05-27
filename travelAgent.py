import os
import json
import bs4
from datetime import datetime
from functools import lru_cache
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain import hub
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import JSONResponse  

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")

app = FastAPI()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=google_api_key)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@lru_cache(maxsize=1)
def get_retriever():
    print("🔄 Carregando conteúdo da web...")

    loader = WebBaseLoader(
        web_paths=[
            "https://pt.wikipedia.org/wiki/Turismo_no_Brasil",
            "https://www.viajenaviagem.com/"
        ]
    )

    try:
        docs = loader.load()
        print(f"✅ Documentos carregados: {len(docs)}")
    except Exception as e:
        print(f"❌ Erro ao carregar os documentos: {e}")
        docs = []

    if not docs:
        print("⚠️ Nenhum documento encontrado. Usando fallback.")
        docs = [Document(page_content="Texto de exemplo sobre turismo no Brasil.")]

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    if not splits:
        raise ValueError("❌ Nenhum conteúdo encontrado para gerar embeddings!")

    print(f"✅ Chunks gerados: {len(splits)}")

    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001", api_key=google_api_key)

    try:
        emb_test = embedding.embed_query("Teste de embedding")
        print("✅ Embedding testado com sucesso.")
    except Exception as e:
        raise RuntimeError(f"❌ Erro ao gerar embedding: {e}")

    vectorstore = Chroma.from_documents(documents=splits, embedding=embedding)
    retriever = vectorstore.as_retriever()
    return retriever

def getRelevantDocs(query):
    retriever = get_retriever()
    return retriever.invoke(query)

def researchAgent(query, llm):
    tools = load_tools(["wikipedia"], llm=llm)
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, prompt=prompt, handle_parsing_errors=True)
    webContext = agent_executor.invoke({"input": query})
    return webContext['output']

def supervisorAgent(query, llm, webContext, relevant_documents):
    prompt_template = """
    Você é um gerente de viagens inteligente e atencioso. Seu papel é ajudar o usuário a planejar a melhor viagem possível.
    Responda com um roteiro completo, incluindo eventos, sugestões e preços reais, se disponíveis.

    Considere o seguinte:

    - O input do usuário com suas preferências.
    - Contexto extraído da web.
    - Documentos relevantes sobre turismo, passagens e experiências.

    🎯 Seja objetivo, amigável e prático.

    Contexto online: {webContext}
    Documentos relevantes: {relevant_documents}
    Pergunta do usuário: {query}

    Resposta detalhada:
    """
    prompt = PromptTemplate(
        input_variables=['webContext', 'relevant_documents', 'query'],
        template=prompt_template
    )
    sequence = RunnableSequence(prompt | llm)
    response = sequence.invoke({
        "webContext": webContext,
        "relevant_documents": relevant_documents,
        "query": query
    })
    return response

def getResponse(query, llm):
    webContext = researchAgent(query, llm)
    relevant_documents = getRelevantDocs(query)
    response = supervisorAgent(query, llm, webContext, relevant_documents)
    return response
def salvar_historico(query, resposta):
    caminho = "historico.json"
    
    # Se o arquivo não existir, crie com uma lista vazia
    if not os.path.exists(caminho):
        with open(caminho, "w", encoding="utf-8") as file:
            json.dump([], file)

    # Verificar se o arquivo está vazio
    with open(caminho, "r+", encoding="utf-8") as file:
        try:
            conteudo = file.read().strip()
            dados = json.loads(conteudo) if conteudo else []
        except json.JSONDecodeError:
            dados = []

        dados.append({
            "timestamp": datetime.now().isoformat(),
            "pergunta": query,
            "resposta": resposta
        })

        file.seek(0)
        json.dump(dados, file, indent=4, ensure_ascii=False)
        file.truncate()


class QueryRequest(BaseModel):
    query: str

@app.post("/perguntar")
async def perguntar(dados: QueryRequest):
    try:
        resposta = getResponse(dados.query, llm)
        resposta_content = resposta.content if hasattr(resposta, 'content') else str(resposta)
        salvar_historico(dados.query, resposta_content)
        return {
            "content": resposta_content,
            "role": "assistant"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "content": f"Erro: {str(e)}",
                "role": "assistant"
            }
        )