import streamlit as st
import os
import json
from datetime import datetime

st.set_page_config(page_title="CodeInsight AI", layout="wide", page_icon="🧠")

# Import our modular core components
from db.sqlite_db import DatabaseManager
from core.parser.repo_manager import RepositoryManager
from core.parser.ast_extractor import parse_python_file
from core.embeddings.chunker import CodeChunker
from core.embeddings.embedder import CodeEmbedder
from core.vector_store.chroma_db import VectorStore
from core.agents.specialized_agents import (
    BugDetectionAgent, SecurityReviewAgent, PerformanceOptimizationAgent,
    DocumentationAgent, TestGenerationAgent, RepositorySummarizationAgent
)

# Initialize singletons for the session
@st.cache_resource
def get_services():
    db = DatabaseManager()
    repo_manager = RepositoryManager()
    chunker = CodeChunker()
    embedder = CodeEmbedder()
    vector_store = VectorStore()
    return db, repo_manager, chunker, embedder, vector_store

db, repo_manager, chunker, embedder, vector_store = get_services()

st.title("🧠 CodeInsight AI")
st.markdown("*An AI-powered repository analysis and code review assistant using Gemini 2.5 Pro.*")

# Sidebar for Repository Management
with st.sidebar:
    st.header("Repository Setup")
    repo_url = st.text_input("GitHub URL to Analyze:", placeholder="https://github.com/user/repo.git")
    repo_name = st.text_input("Project Name (unique):", placeholder="my-awesome-project")
    
    if st.button("Clone & Analyze Repository"):
        if repo_url and repo_name:
            with st.spinner("Cloning repository..."):
                try:
                    local_path = repo_manager.clone_repository(repo_url, repo_name)
                    st.success(f"Cloned to {local_path}")
                    
                    # Store in SQLite
                    repo_id = db.insert_repository(repo_name, local_path, repo_url)
                    st.session_state['current_repo_id'] = str(repo_id)
                    st.session_state['current_repo_path'] = local_path
                    st.session_state['current_repo_name'] = repo_name
                    
                    with st.spinner("Extracting AST & Generating Embeddings..."):
                        python_files = repo_manager.get_python_files(local_path)
                        all_chunks = []
                        
                        for file in python_files:
                            ast_results = parse_python_file(file)
                            file_chunks = chunker.chunk_ast_nodes(file, ast_results)
                            if not file_chunks:
                                # Fallback for non-AST files or huge files
                                with open(file, 'r', encoding='utf-8') as f:
                                    text = f.read()
                                file_chunks = chunker.chunk_text(text, metadata={"file": file})
                            all_chunks.extend(file_chunks)
                            
                        # Embed and store
                        embedded_chunks = embedder.embed_chunks(all_chunks)
                        vector_store.insert_chunks(str(repo_id), embedded_chunks)
                        
                    st.success(f"Analyzed {len(python_files)} files. Stored {len(embedded_chunks)} vector chunks.")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please provide both URL and Name.")

# Main Dashboard Interface
if 'current_repo_id' in st.session_state:
    st.divider()
    st.header(f"Active Project: {st.session_state['current_repo_name']}")
    
    tab1, tab2, tab3 = st.tabs(["💬 Ask AI (RAG)", "🕵️ Specialized Agents", "📊 Export Reports"])
    
    # RAG Chat Interface
    with tab1:
        st.subheader("Semantic Search & QA")
        query = st.text_input("Ask a question about the codebase:", placeholder="Where is the database logic?")
        
        if query:
            with st.spinner("Searching vector database..."):
                query_vec = embedder.generate_embeddings(query)[0]
                results = vector_store.semantic_search(st.session_state['current_repo_id'], query_vec, n_results=3)
                
                if results:
                    context = "\n\n".join([f"File: {r['metadata'].get('file', 'Unknown')}\nCode:\n{r['content']}" for r in results])
                    
                    # Use a generic agent to answer using the RAG context
                    agent = BugDetectionAgent() # Reusing LLM client
                    agent.system_instruction = "You are a senior developer. Answer the user's question based strictly on the provided code context."
                    prompt = f"Context:\n{context}\n\nQuestion:\n{query}"
                    
                    answer = agent.llm.generate_response(agent.system_instruction, prompt)
                    
                    st.markdown("### AI Answer")
                    st.write(answer)
                    
                    with st.expander("View Retrieved Source Code Context"):
                        for r in results:
                            st.code(r['content'], language='python')
                else:
                    st.info("No relevant code found.")

    # Specialized Agents UI
    with tab2:
        st.subheader("Run Code Review")
        agent_type = st.selectbox("Select AI Agent", [
            "Bug Detection", "Security Review", "Performance Optimization",
            "Documentation Generation", "Test Generation"
        ])
        
        code_input = st.text_area("Paste Python code to review:", height=200)
        
        if st.button("Analyze Code"):
            with st.spinner(f"Running {agent_type}..."):
                if agent_type == "Bug Detection":
                    agent = BugDetectionAgent()
                elif agent_type == "Security Review":
                    agent = SecurityReviewAgent()
                elif agent_type == "Performance Optimization":
                    agent = PerformanceOptimizationAgent()
                elif agent_type == "Documentation Generation":
                    agent = DocumentationAgent()
                else:
                    agent = TestGenerationAgent()
                    
                response = agent.analyze(code_input)
                st.markdown(response)

    # Export Features
    with tab3:
        st.subheader("Export Project Summary")
        if st.button("Generate Markdown Report"):
            summary_agent = RepositorySummarizationAgent()
            report = summary_agent.summarize_repo(f"Repo path: {st.session_state['current_repo_path']}")
            
            st.download_button(
                label="Download Report.md",
                data=report,
                file_name="CodeInsight_Report.md",
                mime="text/markdown"
            )
else:
    st.info("👈 Please clone and analyze a repository from the sidebar to begin.")
