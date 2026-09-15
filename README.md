# 🎥 YouTube AI Assistant

A Retrieval-Augmented Generation (RAG) based chatbot that allows users to ask questions about YouTube videos.

The application extracts the video's transcript, converts it into searchable vector embeddings using a Hugging Face embedding model, stores them in FAISS, retrieves relevant transcript sections, and uses Google's Gemini model to generate answers based only on the retrieved context.

## 🚀 Features

* 🎬 Accepts YouTube video URLs
* 📝 Automatically extracts YouTube transcripts
* ✂️ Splits transcripts into manageable chunks
* 🧠 Generates semantic embeddings using `all-MiniLM-L6-v2`
* 🔎 Uses FAISS for similarity-based retrieval
* 🤖 Uses Gemini for answer generation
* 💬 Interactive Streamlit chat interface
* 🛡️ Answers are restricted to the video's transcript context
* 🗑️ Clear chat functionality
* 🎥 Embedded YouTube video preview

## 🏗️ Architecture

```text
YouTube URL
     ↓
Extract Video ID
     ↓
Fetch Transcript
     ↓
Text Chunking
     ↓
Hugging Face Embeddings
     ↓
FAISS Vector Store
     ↓
Similarity Retriever
     ↓
Relevant Transcript Context
     ↓
Gemini LLM
     ↓
Generated Answer
```

## 📁 Project Structure

```text
RAG/
│
├── app.py              # Streamlit user interface
├── rag.py              # RAG pipeline and processing logic
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
└── .gitignore          # Files excluded from Git
```

## 🛠️ Tech Stack

* Python
* Streamlit
* LangChain
* Google Gemini
* Hugging Face Sentence Transformers
* FAISS
* YouTube Transcript API

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd RAG
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

**Never commit your `.env` file or API key to GitHub.**

### 5. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## 💡 How to Use

1. Enter a valid YouTube video URL.
2. Click **Process Video**.
3. The application fetches the transcript.
4. The transcript is chunked and converted into embeddings.
5. FAISS creates a searchable vector database.
6. Ask questions about the video.
7. The RAG pipeline retrieves relevant transcript sections and Gemini generates the answer.

## 🔐 Environment Variables

The application requires:

```text
GEMINI_API_KEY
```

Keep this key private and configure it through environment variables or the deployment platform's secrets manager.

## 📌 Limitations

* The video must have an accessible transcript/captions.
* FAISS is created when the video is processed and is stored in the current application session.
* Answer quality depends on the quality and availability of the YouTube transcript.

## 👨‍💻 Author

Built as a Retrieval-Augmented Generation project using Python, LangChain, FAISS, Hugging Face embeddings, Gemini, and Streamlit.

````

### One thing before you push

**Check your GitHub repository for the API key.** Your earlier notebook had a Gemini key written directly in it. If that was a real key, revoke it and generate a new one. Don't upload that notebook or any file containing the old key.

Then you can push:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
````

After GitHub is ready, the next step is **deploying this exact repository on Streamlit Community Cloud** and adding `GEMINI_API_KEY` under Streamlit Secrets.
