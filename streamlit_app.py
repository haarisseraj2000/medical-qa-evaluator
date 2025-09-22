"""
Medical Q&A Response Evaluator - Streamlit Web Interface
Interactive web application for medical response evaluation
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from src.medical_evaluator import MedicalEvaluator, RiskLevel
import json

# Page configuration
st.set_page_config(
    page_title="Medical Q&A Evaluator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize evaluator
@st.cache_resource
def get_evaluator():
    return MedicalEvaluator()

def create_score_gauge(score, title, color_scheme="RdYlGn"):
    """Create a gauge chart for scores"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        delta = {'reference': 80},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=300)
    return fig

def create_radar_chart(scores):
    """Create radar chart for all evaluation metrics"""
    categories = ['Clinical Accuracy', 'Safety Score', 'Completeness', 'Evidence Quality']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=list(scores.values()),
        theta=categories,
        fill='toself',
        name='Evaluation Scores'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        height=400
    )
    
    return fig

def get_risk_color(risk_level):
    """Get color for risk level"""
    colors = {
        RiskLevel.LOW: "🟢 #28a745",
        RiskLevel.MODERATE: "🟡 #ffc107", 
        RiskLevel.HIGH: "🟠 #fd7e14",
        RiskLevel.CRITICAL: "🔴 #dc3545"
    }
    return colors.get(risk_level, "#6c757d")

def main():
    st.title("🏥 Medical Q&A Response Evaluator")
    st.markdown("**Expert-level evaluation system for AI-generated medical responses**")
    
    # Sidebar
    st.sidebar.header("📋 Evaluation Options")
    
    # Sample data option
    use_sample = st.sidebar.checkbox("Use Sample Data", value=False)
    
    if use_sample:
        sample_questions = {
            "Chest Pain Emergency": "A 45-year-old patient presents with sudden onset severe chest pain radiating to the left arm. What should be considered?",
            "Pregnancy Medication": "What medication is safe for headaches during pregnancy?",
            "Minor Wound Care": "How to treat a minor cut at home?",
            "Pediatric Fever": "My 2-year-old has a fever of 102°F. What should I do?"
        }
        
        selected_sample = st.sidebar.selectbox("Select Sample Question", list(sample_questions.keys()))
        question = sample_questions[selected_sample]
        
        sample_responses = {
            "Chest Pain Emergency": "This could be a heart attack. The patient should chew an aspirin and go to the emergency room immediately. Other possibilities include angina, muscle strain, or acid reflux. Emergency evaluation with ECG and cardiac enzymes is essential.",
            "Pregnancy Medication": "Acetaminophen (Tylenol) is generally considered safe during pregnancy for headaches. Avoid aspirin and ibuprofen. Always consult your healthcare provider before taking any medication during pregnancy.",
            "Minor Wound Care": "Clean the wound with soap and water, apply antibiotic ointment, and cover with a bandage. Change the bandage daily and watch for signs of infection like increased redness, swelling, or pus.",
            "Pediatric Fever": "For a 2-year-old with 102°F fever, give age-appropriate acetaminophen or ibuprofen. Ensure adequate hydration. If fever persists >3 days, child appears very ill, or has difficulty breathing, seek immediate medical attention."
        }
        
        response = sample_responses[selected_sample]
        
    else:
        # Manual input
        question = st.text_area(
            "Medical Question",
            placeholder="Enter the medical question that was asked...",
            height=100
        )
        
        response = st.text_area(
            "AI Response to Evaluate",
            placeholder="Enter the AI-generated response to evaluate...",
            height=200
        )
    
    # Evaluation button
    if st.button("🔍 Evaluate Response", type="primary"):
        if not question or not response:
            st.error("Please provide both a question and response to evaluate.")
            return
        
        # Show loading spinner
        with st.spinner("Evaluating medical response..."):
            evaluator = get_evaluator()
            result = evaluator.evaluate_response(question, response)
        
        # Display results
        st.header("📊 Evaluation Results")
        
        # Overall score and risk level
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Overall Score", 
                f"{result.overall_score:.1f}/100",
                delta=f"{result.overall_score - 75:.1f}" if result.overall_score != 75 else None
            )
        
        with col2:
            risk_color = get_risk_color(result.risk_level)
            st.markdown(f"**Risk Level:** {risk_color.split()[0]} {result.risk_level.value.upper()}")
        
        # Score breakdown
        st.subheader("📈 Score Breakdown")
        
        # Create gauge charts
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            fig1 = create_score_gauge(result.clinical_accuracy, "Clinical Accuracy")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = create_score_gauge(result.safety_score, "Safety Score")
            st.plotly_chart(fig2, use_container_width=True)
        
        with col3:
            fig3 = create_score_gauge(result.completeness_score, "Completeness")
            st.plotly_chart(fig3, use_container_width=True)
        
        with col4:
            fig4 = create_score_gauge(result.evidence_quality, "Evidence Quality")
            st.plotly_chart(fig4, use_container_width=True)
        
        # Radar chart
        st.subheader("🎯 Performance Overview")
        scores = {
            'Clinical Accuracy': result.clinical_accuracy,
            'Safety Score': result.safety_score,
            'Completeness': result.completeness_score,
            'Evidence Quality': result.evidence_quality
        }
        
        radar_fig = create_radar_chart(scores)
        st.plotly_chart(radar_fig, use_container_width=True)
        
        # Detailed feedback
        st.header("📋 Detailed Feedback")
        
        # Create tabs for different feedback types
        tab1, tab2, tab3, tab4 = st.tabs(["🚨 Errors", "⚠️ Safety Concerns", "📝 Missing Elements", "💡 Recommendations"])
        
        with tab1:
            if result.identified_errors:
                for error in result.identified_errors:
                    st.error(f"• {error}")
            else:
                st.success("No significant errors identified!")
        
        with tab2:
            if result.safety_concerns:
                for concern in result.safety_concerns:
                    st.warning(f"• {concern}")
            else:
                st.success("No major safety concerns identified!")
        
        with tab3:
            if result.missing_elements:
                for element in result.missing_elements:
                    st.info(f"• {element}")
            else:
                st.success("Response appears comprehensive!")
        
        with tab4:
            if result.recommendations:
                for rec in result.recommendations:
                    st.info(f"• {rec}")
            else:
                st.success("Response meets quality standards!")
        
        # Export results
        st.header("📤 Export Results")
        
        result_dict = {
            "question": question,
            "response": response,
            "evaluation": {
                "overall_score": result.overall_score,
                "clinical_accuracy": result.clinical_accuracy,
                "safety_score": result.safety_score,
                "completeness_score": result.completeness_score,
                "evidence_quality": result.evidence_quality,
                "risk_level": result.risk_level.value,
                "identified_errors": result.identified_errors,
                "missing_elements": result.missing_elements,
                "safety_concerns": result.safety_concerns,
                "recommendations": result.recommendations
            }
        }
        
        st.download_button(
            label="📥 Download Evaluation Report (JSON)",
            data=json.dumps(result_dict, indent=2),
            file_name=f"medical_evaluation_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

    # Information sidebar
    st.sidebar.markdown("---")
    st.sidebar.header("ℹ️ About This Tool")
    st.sidebar.markdown("""
    This evaluation system assesses AI-generated medical responses across four key dimensions:
    
    **🎯 Clinical Accuracy**
    - Medical correctness
    - Evidence-based content
    - Appropriate terminology
    
    **🛡️ Safety Score**
    - Patient safety implications
    - Risk identification
    - Contraindication warnings
    
    **📋 Completeness**
    - Differential diagnosis
    - Comprehensive coverage
    - Required elements
    
    **📚 Evidence Quality**
    - Research backing
    - Appropriate uncertainty
    - Clinical guidelines
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Built for medical AI training roles**")
    st.sidebar.markdown("*Demonstrates expert evaluation capabilities*")

if __name__ == "__main__":
    main()