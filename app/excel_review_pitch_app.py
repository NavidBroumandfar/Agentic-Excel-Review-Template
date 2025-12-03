"""
Agentic Excel Review - Visual Pitch App
A startup-style presentation for non-technical stakeholders
"""

import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Agentic Excel Review",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 2rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .big-number {
        font-size: 3rem;
        font-weight: 700;
        color: #2ecc71;
    }
    .component-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
        font-weight: 600;
    }
    .savings-highlight {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 600;
    }
    .phase-completed { background-color: #2ecc71; }
    .phase-pending { background-color: #f39c12; }
    .phase-planned { background-color: #3498db; }
    .phase-future { background-color: #9b59b6; }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio(
    "Go to:",
    [
        "🏠 Introduction",
        "🔄 Workflow Today",
        "⚠️ Pain Points",
        "🤖 AI Automation",
        "📈 Before vs After",
        "🗓️ Roadmap",
        "🎮 Demo",
        "✅ Conclusion"
    ]
)

# =============================================================================
# PAGE 1: Introduction
# =============================================================================
if page == "🏠 Introduction":
    st.markdown('<h1 class="main-header">🚀 Agentic Excel Review</h1>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📋 What is Excel Review?")
        st.info("""
        **Spreadsheet Data Review**
        
        Complex review workflows to ensure compliance, accuracy, and consistency in data processing.
        """)
    
    with col2:
        st.markdown("### ⚡ Why is it Heavy?")
        st.warning("""
        **High Workload**
        
        Each cycle requires reading hundreds of entries, cross-referencing rules, and producing reports.
        """)
    
    with col3:
        st.markdown("### 🤝 Human-AI Partnership")
        st.success("""
        **AI Assists, Humans Decide**
        
        AI suggests answers and highlights issues — final decisions remain 100% human.
        """)
    
    st.markdown("---")
    st.markdown("### 🎯 Our Mission")
    st.markdown("""
    > **Reduce reviewer workload by 50% while maintaining full human oversight and audit compliance.**
    """)

# =============================================================================
# PAGE 2: Workflow Today
# =============================================================================
elif page == "🔄 Workflow Today":
    st.markdown("## 🔄 Excel Review Workflow Explained")
    st.markdown("---")
    
    # Graphviz diagram
    st.markdown("### Current Process Flow")
    
    workflow_graph = """
    digraph {
        rankdir=LR;
        node [shape=box, style="rounded,filled", fontname="Arial", fontsize=12];
        
        A [label="📥 Data\\nIngestion", fillcolor="#3498db", fontcolor="white"];
        B [label="📊 Excel Macros\\n& Sampling", fillcolor="#9b59b6", fontcolor="white"];
        C [label="👁️ Manual\\nText Review", fillcolor="#e74c3c", fontcolor="white"];
        D [label="📧 Reporting\\n& KPIs", fillcolor="#2ecc71", fontcolor="white"];
        
        A -> B -> C -> D;
    }
    """
    st.graphviz_chart(workflow_graph)
    
    st.markdown("---")
    st.markdown("### Process Steps")
    
    process_steps = pd.DataFrame([
        {"Step": "1️⃣", "Who": "Systems", "What happens": "Excel loaded into system"},
        {"Step": "2️⃣", "Who": "Excel macros", "What happens": "Sampling & formatting"},
        {"Step": "3️⃣", "Who": "Reviewers", "What happens": "Manual reading & decisions"},
        {"Step": "4️⃣", "Who": "Reviewers", "What happens": "Prepare KPIs & emails"},
    ])
    
    st.dataframe(process_steps, use_container_width=True, hide_index=True)

# =============================================================================
# PAGE 3: Pain Points
# =============================================================================
elif page == "⚠️ Pain Points":
    st.markdown("## ⚠️ Current Pain Points")
    st.markdown("---")
    
    # Real numbers
    manual_hours = 30
    admin_hours = 12
    analysis_hours = 8
    total_hours = manual_hours + admin_hours + analysis_hours
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👁️ Manual Reading", f"{manual_hours}h", help="Hours per month")
    with col2:
        st.metric("📋 Admin Tasks", f"{admin_hours}h", help="Hours per month")
    with col3:
        st.metric("🔍 Analysis", f"{analysis_hours}h", help="Hours per month")
    with col4:
        st.metric("📊 TOTAL", f"{total_hours}h", delta=None, help="Hours per month")
    
    st.markdown("---")
    
    # Bar chart
    chart_data = pd.DataFrame({
        'Category': ['Manual Reading', 'Admin Tasks', 'Analysis'],
        'Hours': [manual_hours, admin_hours, analysis_hours]
    })
    st.bar_chart(chart_data.set_index('Category'), height=400)
    
    st.markdown("---")
    st.markdown("### 🔴 Key Issues")
    
    col1, col2 = st.columns(2)
    with col1:
        st.error("**High manual reading load** — reviewers must read every entry carefully")
        st.error("**Repetitive admin tasks** — same report formats, same emails each month")
    with col2:
        st.error("**Error-prone steps** — humans make mistakes when fatigued")
        st.error("**Time wasted** — copy-paste, formatting, low-value actions")

# =============================================================================
# PAGE 4: AI Automation
# =============================================================================
elif page == "🤖 AI Automation":
    st.markdown("## 🤖 How Agentic Automation Works")
    st.markdown("---")
    
    # Pipeline components
    components = [
        ("📥", "Excel Reader", "Safe read-only ingestion", "#3498db"),
        ("📚", "RAG Context", "Loads SOP/rules context", "#9b59b6"),
        ("🧠", "AI Review Assistant", "LLM generates suggestions", "#e74c3c"),
        ("💾", "Safe Writer", "Writes AI_ columns to CSV", "#2ecc71"),
        ("📝", "Log Manager", "Audit logging & tracking", "#f39c12"),
        ("🎯", "Orchestrator", "Full pipeline execution", "#1abc9c"),
    ]
    
    for icon, name, desc, color in components:
        st.markdown(f"""
        <div style="background: {color}; color: white; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
            <strong>{icon} {name}</strong> — {desc}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Pipeline table
    st.markdown("### 📋 Pipeline Components")
    agent_pipeline = pd.DataFrame([
        {"Step": 1, "Component": "Excel Reader", "What it does": "Safe read-only ingestion"},
        {"Step": 2, "Component": "RAG Context", "What it does": "Loads SOP/rules context"},
        {"Step": 3, "Component": "AI Review Assistant", "What it does": "LLM generates suggestions"},
        {"Step": 4, "Component": "Safe Writer", "What it does": "Writes AI_ columns to CSV"},
        {"Step": 5, "Component": "Log Manager", "What it does": "Audit logging"},
        {"Step": 6, "Component": "Orchestrator", "What it does": "Full pipeline execution"},
    ])
    st.dataframe(agent_pipeline, use_container_width=True, hide_index=True)

# =============================================================================
# PAGE 5: Before vs After
# =============================================================================
elif page == "📈 Before vs After":
    st.markdown("## 📈 Before vs After Comparison")
    st.markdown("---")
    
    # Real estimates
    manual_before, manual_after = 30, 12
    admin_before, admin_after = 12, 5
    analysis_before, analysis_after = 8, 8
    hourly_cost_eur = 45
    
    total_before = manual_before + admin_before + analysis_before
    total_after = manual_after + admin_after + analysis_after
    time_saved_per_month = total_before - total_after
    annual_time_saved = time_saved_per_month * 12
    annual_cost_saved = annual_time_saved * hourly_cost_eur
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⏱️ Hours Before", f"{total_before}h/month")
    with col2:
        st.metric("✅ Hours After", f"{total_after}h/month", delta=f"-{time_saved_per_month}h")
    with col3:
        st.metric("📉 Reduction", "50%", delta="Time saved!")
    
    st.markdown("---")
    
    # Comparison chart
    comparison_data = pd.DataFrame({
        'Category': ['Manual Reading', 'Admin Tasks', 'Analysis', 'TOTAL'],
        'Before': [manual_before, admin_before, analysis_before, total_before],
        'After': [manual_after, admin_after, analysis_after, total_after]
    })
    st.bar_chart(comparison_data.set_index('Category'), height=400)
    
    st.markdown("---")
    
    # Annual savings highlight
    st.markdown(f"""
    <div class="savings-highlight">
        💰 Annual Savings: <strong>€{annual_cost_saved:,}</strong> per reviewer<br>
        ⏱️ Time Saved: <strong>{annual_time_saved} hours</strong> per year
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("📝 **NOTE:** These numbers reflect realistic Excel review workload estimates.")

# =============================================================================
# PAGE 6: Roadmap
# =============================================================================
elif page == "🗓️ Roadmap":
    st.markdown("## 🗓️ Implementation Roadmap")
    st.markdown("---")
    
    phases = [
        ("Phase 1", "✅ Completed", "Local prototype", "#2ecc71"),
        ("Phase 2", "🔄 Pending", "Integrate with internal APIs", "#f39c12"),
        ("Phase 3", "📋 Planned", "Pilot with review team", "#3498db"),
        ("Phase 4", "🔮 Future", "Industrialization", "#9b59b6"),
    ]
    
    cols = st.columns(4)
    for i, (phase, status, desc, color) in enumerate(phases):
        with cols[i]:
            st.markdown(f"""
            <div style="background: {color}; color: white; padding: 1.5rem; border-radius: 15px; text-align: center; height: 180px;">
                <h3>{phase}</h3>
                <p><strong>{status}</strong></p>
                <p style="font-size: 0.9rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Roadmap table
    roadmap = pd.DataFrame([
        {"Phase": "Phase 1", "Status": "✅ Completed", "Description": "Local prototype"},
        {"Phase": "Phase 2", "Status": "🔄 Pending", "Description": "Integrate with internal APIs"},
        {"Phase": "Phase 3", "Status": "📋 Planned", "Description": "Pilot with review team"},
        {"Phase": "Phase 4", "Status": "🔮 Future", "Description": "Industrialization"},
    ])
    st.dataframe(roadmap, use_container_width=True, hide_index=True)

# =============================================================================
# PAGE 7: Demo
# =============================================================================
elif page == "🎮 Demo":
    st.markdown("## 🎮 Interactive Demo")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🚀 Run Sample Pipeline")
        if st.button("▶️ Run Pipeline Demo", type="primary", use_container_width=True):
            with st.spinner("Running AI pipeline..."):
                import time
                progress_bar = st.progress(0)
                steps = ["Reading Excel...", "Loading context...", "AI analyzing...", 
                        "Writing results...", "Logging...", "Complete!"]
                for i, step in enumerate(steps):
                    time.sleep(0.5)
                    progress_bar.progress((i + 1) / len(steps))
                    st.info(step)
                st.success("✅ Pipeline completed successfully!")
                st.balloons()
    
    with col2:
        st.markdown("### 📊 View Sample Results")
        if st.button("👁️ Show Sample Results", type="secondary", use_container_width=True):
            sample_results = pd.DataFrame({
                'Item': ['Record A', 'Record B', 'Record C', 'Record D'],
                'Original_Status': ['Pending', 'Pending', 'Pending', 'Pending'],
                'AI_Suggestion': ['Approve', 'Review', 'Approve', 'Flag'],
                'AI_Confidence': ['95%', '72%', '88%', '91%'],
                'AI_Rationale': [
                    'Matches standard criteria',
                    'Requires human verification',
                    'Standard entry',
                    'Potential issue detected'
                ]
            })
            st.dataframe(sample_results, use_container_width=True, hide_index=True)
            st.info("📝 This is mock data for demonstration purposes.")

# =============================================================================
# PAGE 8: Conclusion
# =============================================================================
elif page == "✅ Conclusion":
    st.markdown("## ✅ Conclusion")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Key Benefits")
        st.success("✅ **AI supports humans** — Never replaces human judgment")
        st.success("✅ **50% workload reduction** — From 50h to 25h per month")
        st.success("✅ **€13,500 annual savings** — Per reviewer, per year")
        st.success("✅ **Better consistency** — AI doesn't get tired or distracted")
        st.success("✅ **Full audit trail** — Every AI suggestion is logged")
    
    with col2:
        st.markdown("### 🚀 Next Steps")
        st.info("1️⃣ **Prototype completed** — Delivered")
        st.warning("2️⃣ **Request API access** — For internal systems")
        st.info("3️⃣ **Schedule pilot** — With review team")
        st.info("4️⃣ **Plan industrialization** — Full rollout")
    
    st.markdown("---")
    
    # Final summary metrics
    st.markdown("### 📊 The Numbers")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Before", "50h/mo")
    with col2:
        st.metric("After", "25h/mo")
    with col3:
        st.metric("Saved/mo", "25h")
    with col4:
        st.metric("Saved/yr", "300h")
    with col5:
        st.metric("€ Saved/yr", "13,500")
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                color: white; border-radius: 15px; font-size: 1.5rem;">
        💬 <strong>Questions? Let's discuss!</strong>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Agentic Excel Review**")
st.sidebar.markdown("Version 1.0 | 2025")

