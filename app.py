import streamlit as st

# from dotenv import load_dotenv
# load_dotenv()

from youtube_transcript_api import (
    TranscriptsDisabled,
    NoTranscriptFound
)

from rag import (
    process_video,
    ask_question
)

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="YouTube AI Assistant",
    page_icon="🎥",
    layout="wide"
)



# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #0e1117;
}

.title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
    margin-top: 20px;
}

.subtitle {
    text-align: center;
    color: #9aa4b2;
    font-size: 18px;
    margin-bottom: 30px;
}

.block {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 15px;
    padding: 20px;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "video_id" not in st.session_state:
    st.session_state.video_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">🎥 YouTube AI Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Ask questions about any YouTube video'
    '</div>',
    unsafe_allow_html=True
)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Controls")

    # Clear chat button
    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # How the application works
    st.markdown("### How it works")

    st.markdown("""
    **1.** Enter YouTube URL

    **2.** Process the video

    **3.** Transcript is extracted

    **4.** Text is split into chunks

    **5.** FAISS creates the knowledge base

    **6.** Ask questions

    **7.** Gemini generates answers
    """)

# ============================================================
# YOUTUBE URL
# ============================================================

st.markdown("### 🎬 YouTube Video")

video_url = st.text_input(
    "YouTube URL",
    placeholder="Paste YouTube video link here...",
    label_visibility="collapsed"
)

process_button = st.button(
    "🚀 Process Video",
    type="primary",
    use_container_width=True
)

# ============================================================
# PROCESS VIDEO
# ============================================================

if process_button:

    if not video_url:

        st.warning(
            "Please enter a YouTube URL."
        )

    else:

        try:

            with st.spinner(
                "📥 Processing video..."
            ):

                # Call RAG pipeline from rag.py
                video_id, vector_store = process_video(
                    video_url
                )

            # Save results in Streamlit session
            st.session_state.vector_store = vector_store
            st.session_state.video_id = video_id
            st.session_state.messages = []

            st.success(
                "✅ Video processed successfully!"
            )

            st.rerun()

        except TranscriptsDisabled:

            st.error(
                "❌ Captions are disabled for this video."
            )

        except NoTranscriptFound:

            st.error(
                "❌ No transcript was found for this video."
            )

        except Exception as e:

            st.error(
                f"❌ Error: {str(e)}"
            )

# ============================================================
# VIDEO PREVIEW
# ============================================================

if st.session_state.vector_store:

    st.divider()

    # Display YouTube video
    st.video(
        f"https://www.youtube.com/watch?v="
        f"{st.session_state.video_id}"
    )

    # Status cards
    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Status",
            "🟢 Ready"
        )

    with col2:

        st.metric(
            "Vector Database",
            "FAISS"
        )

    with col3:

        st.metric(
            "AI Model",
            "Gemini"
        )

# ============================================================
# CHAT
# ============================================================

if st.session_state.vector_store:

    st.divider()

    st.markdown(
        "### 💬 Ask About The Video"
    )

    # ----------------------------------------
    # Display previous chat messages
    # ----------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    # ----------------------------------------
    # User question
    # ----------------------------------------

    question = st.chat_input(
        "Ask something about this video..."
    )

    if question:

        # ------------------------------------
        # Display user question
        # ------------------------------------

        with st.chat_message("user"):

            st.markdown(question)

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        # ------------------------------------
        # Generate AI response
        # ------------------------------------

        with st.chat_message("assistant"):

            with st.spinner(
                "🤔 Thinking..."
            ):

                try:

                    # Call RAG function from rag.py
                    answer = ask_question(
                        st.session_state.vector_store,
                        question
                    )

                    st.markdown(answer)

                except Exception as e:

                    answer = (
                        "Sorry, an error occurred: "
                        + str(e)
                    )

                    st.error(answer)

        # ------------------------------------
        # Save AI response
        # ------------------------------------

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

# ============================================================
# INITIAL MESSAGE
# ============================================================

else:

    st.info(
        "👆 Enter a YouTube URL and click "
        "**Process Video** to get started."
    )
