from langchain_huggingface import HuggingFaceEmbeddings
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableLambda
)
from langchain_core.output_parsers import StrOutputParser

from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import os


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("API key loaded:", api_key is not None)


# ============================================================
# YOUTUBE VIDEO ID
# ============================================================

def extract_video_id(url):

    parsed_url = urlparse(url)

    # Normal YouTube URL
    if parsed_url.hostname in [
        "www.youtube.com",
        "youtube.com"
    ]:

        return parse_qs(
            parsed_url.query
        ).get("v", [None])[0]

    # Short YouTube URL
    if parsed_url.hostname in [
        "youtu.be",
        "www.youtu.be"
    ]:

        return parsed_url.path.strip(
            "/"
        ).split("?")[0]

    return None


# ============================================================
# FETCH YOUTUBE TRANSCRIPT
# ============================================================

def get_transcript(video_id):

    api = YouTubeTranscriptApi()

    transcript_data = api.fetch(
        video_id
    )

    transcript_list = (
        transcript_data.to_raw_data()
    )

    transcript = " ".join(
        chunk["text"]
        for chunk in transcript_list
    )

    return transcript


# ============================================================
# CREATE VECTOR STORE
# ============================================================

def create_vector_store(transcript):

    # Split transcript
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.create_documents(
        [transcript]
    )

    # Create embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name=
        "sentence-transformers/"
        "all-MiniLM-L6-v2"
    )

    # Create FAISS vector database
    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    return vector_store


# ============================================================
# CREATE RAG CHAIN
# ============================================================

def create_rag_chain(vector_store):

    # Retriever
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 4
        }
    )

    # Check API key
    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:

        raise ValueError(
            "GEMINI_API_KEY is not configured."
        )

    # Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        temperature=0.2,
        google_api_key=api_key
    )

    # Prompt
    prompt = PromptTemplate(
        template="""
You are a helpful assistant.

Answer ONLY from the provided YouTube
transcript context.

Rules:
- Do not use outside knowledge.
- If the answer is not present in the transcript,
  say "I don't know based on this video."
- Give a clear and useful answer.

Transcript Context:
{context}

Question:
{question}

Answer:
""",
        input_variables=[
            "context",
            "question"
        ]
    )

    # Format documents
    def format_docs(docs):

        return "\n\n".join(
            doc.page_content
            for doc in docs
        )

    # RAG pipeline
    parallel_chain = RunnableParallel({

        "context":
            retriever
            | RunnableLambda(format_docs),

        "question":
            RunnablePassthrough()

    })

    parser = StrOutputParser()

    main_chain = (
        parallel_chain
        | prompt
        | llm
        | parser
    )

    return main_chain


# ============================================================
# COMPLETE RAG PIPELINE
# ============================================================

def process_video(video_url):

    # Extract video ID
    video_id = extract_video_id(
        video_url
    )

    if not video_id:

        raise ValueError(
            "Invalid YouTube URL."
        )

    # Fetch transcript
    transcript = get_transcript(
        video_id
    )

    if not transcript.strip():

        raise ValueError(
            "Transcript is empty."
        )

    # Create vector database
    vector_store = create_vector_store(
        transcript
    )

    return video_id, vector_store


# ============================================================
# ASK QUESTION
# ============================================================

def ask_question(
    vector_store,
    question
):

    rag_chain = create_rag_chain(
        vector_store
    )

    answer = rag_chain.invoke(
        question
    )

    return answer