import streamlit as st

from agents.research_team import run_research_team
from config import CHAT_MODEL, EMBEDDING_MODEL, RAG_TOP_K
from prompts.templates import PROMPT_TEMPLATES, build_prompt
from rag.vector_store import (
    format_retrieved_context,
    index_chunks,
    make_collection_name,
    retrieve_chunks,
)
from services.llm_service import (
    check_ollama_connection,
    generate_chat_response,
    generate_response,
)
from services.web_search import build_web_search_context
from utils.pdf_utils import chunk_pages, extract_pages_from_pdf


st.set_page_config(
    page_title="AI Knowledge and Research Assistant",
    page_icon="🤖",
    layout="wide",
)

st.title("AI Knowledge and Research Assistant")
st.caption(
    "A teaser project covering chat, prompt engineering, PDF RAG, "
    "and a multi-agent workflow."
)

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "rag_collection" not in st.session_state:
    st.session_state.rag_collection = None

if "rag_filename" not in st.session_state:
    st.session_state.rag_filename = None

if "research_outputs" not in st.session_state:
    st.session_state.research_outputs = None


with st.sidebar:
    st.header("Project configuration")
    st.write(f"**Chat model:** `{CHAT_MODEL}`")
    st.write(f"**Embedding model:** `{EMBEDDING_MODEL}`")

    if st.button("Check Ollama connection", use_container_width=True):
        try:
            message = check_ollama_connection()
            st.success(message)
        except RuntimeError as exc:
            st.error(str(exc))

    if st.button("Clear chat history", use_container_width=True):
        st.session_state.chat_messages = []
        st.rerun()

    st.divider()
    st.info(
        "This app runs locally with Ollama. "
        "Use the **Web Search** tab to get answers from live web results."
    )


chat_tab, web_tab, prompt_tab, rag_tab, research_tab = st.tabs(
    [
        "1. AI Chat",
        "2. Web Search (MCP)",
        "3. Prompt Lab",
        "4. Chat with PDF",
        "5. Research Team (Agent Workflow)",
    ]
)


with chat_tab:
    st.subheader("AI Chat")
    st.write(
        "Pure conversation with the local LLM. No web search, no external context."
    )

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    with st.form("chat_form", clear_on_submit=True):
        user_message = st.text_input(
            "Your message",
            placeholder="Explain retrieval-augmented generation simply.",
        )
        chat_submitted = st.form_submit_button("Send")

    if chat_submitted and user_message.strip():
        user_text = user_message.strip()
        st.session_state.chat_messages.append(
            {"role": "user", "content": user_text}
        )

        try:
            with st.spinner("Generating a response..."):
                answer = generate_chat_response(
                    st.session_state.chat_messages
                )

            st.session_state.chat_messages.append(
                {"role": "assistant", "content": answer}
            )
            st.rerun()
        except RuntimeError as exc:
            st.error(str(exc))


with web_tab:
    st.subheader("Web Search")
    st.write(
        "Searches DuckDuckGo for your question and answers **only** from those results. "
        "It does not use the model's internal knowledge."
    )

    if "web_search_messages" not in st.session_state:
        st.session_state.web_search_messages = []

    for message in st.session_state.web_search_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    with st.form("web_search_form", clear_on_submit=True):
        user_message = st.text_input(
            "Your question",
            placeholder="What are the latest AI news today?",
        )
        web_submitted = st.form_submit_button("Search and answer")

    if web_submitted and user_message.strip():
        user_text = user_message.strip()
        st.session_state.web_search_messages.append(
            {"role": "user", "content": user_text}
        )

        try:
            raw_results = []
            web_context = ""
            with st.spinner("🌐 Searching the web..."):
                from services.web_search import (
                    build_web_search_context,
                    search_web,
                )
                raw_results = search_web(user_text, max_results=5)
                web_context = build_web_search_context(
                    user_text, max_results=5
                )

            # Always show raw results so the user gets the current data
            with st.expander("📋 View raw search results", expanded=True):
                if raw_results:
                    for index, item in enumerate(raw_results, start=1):
                        st.markdown(f"**{index}. {item['title']}**")
                        st.caption(item["url"])
                        st.write(item["snippet"])
                        st.divider()
                else:
                    st.write("No results found.")

            # Optional AI summary from those results
            summary_prompt = (
                "Summarize the following web search results for the user's question. "
                "Prefer the provided results. If they are not helpful, say so plainly.\n\n"
                f"WEB SEARCH RESULTS:\n{web_context}"
            )

            with st.spinner("Generating a response from search results..."):
                answer = generate_chat_response(
                    history=st.session_state.web_search_messages,
                    override_system_prompt=summary_prompt,
                )

            st.session_state.web_search_messages.append(
                {"role": "assistant", "content": answer}
            )
            st.rerun()
        except RuntimeError as exc:
            st.error(str(exc))


with prompt_tab:
    st.subheader("Prompt Engineering Playground")
    st.write(
        "Choose a reusable prompt pattern, provide a subject, and compare "
        "how stronger instructions change the output."
    )

    template_name = st.selectbox(
        "Prompt template",
        options=list(PROMPT_TEMPLATES.keys()),
    )
    subject = st.text_area(
        "Subject or request",
        placeholder=(
            "Example: Explain how AI agents can improve retail operations."
        ),
        height=120,
    )
    optional_context = st.text_area(
        "Optional context",
        placeholder=(
            "Add audience, constraints, background information, or source text."
        ),
        height=140,
    )

    if st.button("Run prompt", type="primary"):
        if not subject.strip():
            st.warning("Enter a subject or request first.")
        else:
            system_prompt, final_prompt = build_prompt(
                template_name,
                subject,
                optional_context,
            )

            with st.expander("See the complete prompt sent to the model"):
                st.code(final_prompt, language="text")

            try:
                with st.spinner("Running the prompt..."):
                    output = generate_response(
                        final_prompt,
                        system_prompt=system_prompt,
                    )
                st.markdown("### Generated output")
                st.markdown(output)
            except RuntimeError as exc:
                st.error(str(exc))


with rag_tab:
    st.subheader("Chat with a PDF using RAG")
    st.write(
        "Upload a text-based PDF. The app extracts its text, creates "
        "overlapping chunks, generates embeddings, stores them in ChromaDB, "
        "retrieves relevant chunks, and sends those chunks to the LLM."
    )

    uploaded_pdf = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        key="pdf_uploader",
    )

    if st.button("Process and index PDF", type="primary"):
        if uploaded_pdf is None:
            st.warning("Upload a PDF first.")
        else:
            try:
                pdf_bytes = uploaded_pdf.getvalue()

                with st.spinner("Extracting and chunking the PDF..."):
                    pages = extract_pages_from_pdf(pdf_bytes)
                    chunks = chunk_pages(pages)

                collection_name = make_collection_name(
                    uploaded_pdf.name,
                    pdf_bytes,
                )

                with st.spinner("Creating embeddings and indexing chunks..."):
                    indexed_count = index_chunks(
                        collection_name,
                        chunks,
                        uploaded_pdf.name,
                    )

                st.session_state.rag_collection = collection_name
                st.session_state.rag_filename = uploaded_pdf.name
                st.success(
                    f"Indexed {indexed_count} chunks from "
                    f"{len(pages)} text pages."
                )
            except (ValueError, RuntimeError) as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"Unexpected indexing error: {exc}")

    if st.session_state.rag_collection:
        st.success(
            f"Active document: {st.session_state.rag_filename}"
        )

        question = st.text_input(
            "Ask a question about the document",
            placeholder="What are the document's main recommendations?",
            key="rag_question",
        )

        if st.button("Ask the document"):
            if not question.strip():
                st.warning("Enter a question first.")
            else:
                try:
                    with st.spinner("Retrieving relevant passages..."):
                        retrieved = retrieve_chunks(
                            st.session_state.rag_collection,
                            question,
                            top_k=RAG_TOP_K,
                        )
                        context = format_retrieved_context(retrieved)

                    rag_prompt = f"""
Use only the supplied document context to answer the question.

QUESTION:
{question}

DOCUMENT CONTEXT:
{context}

RULES:
- If the answer is not supported by the context, say so.
- Do not use outside facts.
- Cite supporting passages as [Source 1], [Source 2], and so on.
- Give a clear, direct answer.
""".strip()

                    with st.spinner("Generating a grounded answer..."):
                        answer = generate_response(
                            rag_prompt,
                            system_prompt=(
                                "You are a document question-answering "
                                "assistant. Ground every answer in the "
                                "retrieved context."
                            ),
                            temperature=0.1,
                        )

                    st.markdown("### Answer")
                    st.markdown(answer)

                    with st.expander("Retrieved source passages"):
                        for index, item in enumerate(
                            retrieved,
                            start=1,
                        ):
                            st.markdown(
                                f"**Source {index} — page {item['page']}**"
                            )
                            st.write(item["text"])
                            st.divider()
                except (RuntimeError, ValueError) as exc:
                    st.error(str(exc))
                except Exception as exc:
                    st.error(f"Unexpected RAG error: {exc}")


with research_tab:
    st.subheader("Multi-Agent Research and Writing Team")
    st.write(
        "Four specialized agents run in sequence: Planner, Researcher, "
        "Writer, and Reviewer."
    )
    st.warning(
        "Without a live search tool, this workflow produces model-based "
        "synthesis rather than verified current web research. When a PDF "
        "is active, the Researcher can use retrieved passages from it."
    )

    topic = st.text_area(
        "Research topic",
        placeholder=(
            "Example: How can organizations introduce AI agents responsibly?"
        ),
        height=100,
    )

    use_pdf = st.checkbox(
        "Use the active PDF as source context",
        value=bool(st.session_state.rag_collection),
        disabled=not bool(st.session_state.rag_collection),
    )

    if st.button("Run the four-agent team", type="primary"):
        if not topic.strip():
            st.warning("Enter a research topic first.")
        else:
            source_context = ""

            try:
                if use_pdf and st.session_state.rag_collection:
                    with st.spinner(
                        "Retrieving source context from the PDF..."
                    ):
                        retrieved = retrieve_chunks(
                            st.session_state.rag_collection,
                            topic,
                            top_k=max(RAG_TOP_K, 6),
                        )
                        source_context = format_retrieved_context(
                            retrieved
                        )

                with st.spinner(
                    "Running Planner, Researcher, Writer, and Reviewer..."
                ):
                    st.session_state.research_outputs = (
                        run_research_team(
                            topic.strip(),
                            source_context,
                        )
                    )
            except (RuntimeError, ValueError) as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"Unexpected agent workflow error: {exc}")

    if st.session_state.research_outputs:
        outputs = st.session_state.research_outputs

        with st.expander("Planner Agent output"):
            st.markdown(outputs["plan"])

        with st.expander("Researcher Agent output"):
            st.markdown(outputs["research"])

        with st.expander("Writer Agent draft"):
            st.markdown(outputs["draft"])

        st.markdown("### Reviewer Agent final report")
        st.markdown(outputs["final"])

        st.download_button(
            "Download final report",
            data=outputs["final"],
            file_name="ai_research_report.md",
            mime="text/markdown",
        )
