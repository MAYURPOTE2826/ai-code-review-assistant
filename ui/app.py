import streamlit as st
import os
import sys
import json
from datetime import datetime

# Add project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

# Custom CSS for Premium UI
st.markdown("""
<style>
    /* Clean Global Typography */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Gradient Hero Text */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #7928CA, #FF0080);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: #8b949e;
        margin-bottom: 2rem;
    }
    
    /* Gradient Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(106, 17, 203, 0.4);
        color: white !important;
    }
    
    /* Modern Input Focus Shadows */
    .stTextInput > div > div > input:focus, .stTextArea > div > textarea:focus {
        border-color: #7928CA;
        box-shadow: 0 0 0 1px #7928CA;
    }
    
    /* Premium Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6a11cb, #2575fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="hero-title">🧠 CodeInsight AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">An AI-powered repository analysis and code review assistant using Gemini 3.5 Flash.</p>', unsafe_allow_html=True)

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
                        
                    st.success("Analysis Complete!")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Python Files Parsed", len(python_files))
                    with col2:
                        st.metric("Vector Embeddings", len(embedded_chunks))
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
        
        col_agent, col_code = st.columns([1, 2])
        
        with col_agent:
            st.markdown("### 1. Select Agent")
            agent_type = st.selectbox("Available Experts", [
                "Bug Detection", "Security Review", "Performance Optimization",
                "Documentation Generation", "Test Generation"
            ], label_visibility="collapsed")
            
            st.markdown("### 2. Execute")
            analyze_btn = st.button("🚀 Analyze Code", use_container_width=True)
            
        with col_code:
            st.markdown("### Code Snippet")
            code_input = st.text_area("Paste Python code to review:", height=250, label_visibility="collapsed")
        
        if analyze_btn:
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
                    
                try:
                    response_text = agent.analyze(code_input)
                    review_data = json.loads(response_text)
                    
                    # Display metrics and summary
                    c1, c2 = st.columns(2)
                    c1.metric("Severity Level", str(review_data.get("severity_level", "unknown")).upper())
                    c2.metric("Estimated Risk", str(review_data.get("estimated_risk", "unknown")).upper())
                    
                    st.info(review_data.get("summary", "Analysis completed."))
                    
                    # Organize results into tabs
                    t_issues, t_improve, t_pos = st.tabs(["🐛 Issues", "✨ Improvements", "✅ Positive Aspects"])
                    
                    with t_issues:
                        issues = review_data.get("issues", [])
                        if not issues:
                            st.success("No critical issues found!")
                        for issue in issues:
                            with st.expander(f"{str(issue.get('type', 'issue')).upper()} at {issue.get('line', 'Unknown')}", expanded=True):
                                st.write(f"**Issue:** {issue.get('issue')}")
                                st.write(f"**Impact:** {issue.get('impact')}")
                                if "suggestion" in issue:
                                    st.markdown("**Suggestion:**")
                                    st.code(issue["suggestion"])
                                    
                    with t_improve:
                        improvements = review_data.get("improvements", [])
                        if not improvements:
                            st.info("No improvements suggested.")
                        for imp in improvements:
                            with st.expander(f"Improve {imp.get('area', 'code')} (Priority: {str(imp.get('priority', 'low')).upper()})"):
                                st.write(f"**Current:** {imp.get('current')}")
                                st.markdown("**Suggestion:**")
                                st.code(imp.get("suggestion", ""))
                                
                    with t_pos:
                        positives = review_data.get("positive_aspects", [])
                        for pos in positives:
                            st.markdown(f"- ✅ {pos}")
                            
                except json.JSONDecodeError:
                    st.error("AI returned invalid JSON format.")
                    st.code(response_text)
                except Exception as e:
                    st.error(f"Error parsing analysis: {e}")

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
