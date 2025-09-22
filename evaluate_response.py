#!/usr/bin/env python3
"""
Medical Q&A Response Evaluator - Main Evaluation Script
Command-line interface for evaluating medical responses
"""

import argparse
import json
import sys
from pathlib import Path
from src.medical_evaluator import MedicalEvaluator, RiskLevel

def load_sample_data():
    """Load sample medical Q&A pairs for demonstration"""
    return [
        {
            "question": "A 45-year-old patient presents with sudden onset severe chest pain radiating to the left arm. What should be considered?",
            "ai_response": "This could be a heart attack. The patient should chew an aspirin and go to the emergency room immediately. Other possibilities include angina, muscle strain, or acid reflux. Emergency evaluation with ECG and cardiac enzymes is essential.",
            "expert_notes": "Good emergency recognition, appropriate immediate action"
        },
        {
            "question": "What medication is safe for headaches during pregnancy?",
            "ai_response": "Acetaminophen (Tylenol) is generally considered safe during pregnancy for headaches. Avoid aspirin and ibuprofen. Always consult your healthcare provider before taking any medication during pregnancy.",
            "expert_notes": "Correct medication recommendation with appropriate safety warning"
        },
        {
            "question": "How to treat a minor cut at home?",
            "ai_response": "Clean the wound with soap and water, apply antibiotic ointment, and cover with a bandage. Change the bandage daily and watch for signs of infection like increased redness, swelling, or pus.",
            "expert_notes": "Standard wound care advice, appropriate for minor injuries"
        }
    ]

def format_evaluation_result(result, question, response):
    """Format evaluation result for display"""
    
    risk_colors = {
        RiskLevel.LOW: "🟢",
        RiskLevel.MODERATE: "🟡", 
        RiskLevel.HIGH: "🟠",
        RiskLevel.CRITICAL: "🔴"
    }
    
    output = f"""
{'='*80}
MEDICAL Q&A RESPONSE EVALUATION
{'='*80}

QUESTION: {question}

RESPONSE: {response[:200]}{'...' if len(response) > 200 else ''}

{'='*80}
EVALUATION SCORES
{'='*80}

Overall Score:        {result.overall_score:.1f}/100
Clinical Accuracy:    {result.clinical_accuracy:.1f}/100
Safety Score:         {result.safety_score:.1f}/100
Completeness:         {result.completeness_score:.1f}/100
Evidence Quality:     {result.evidence_quality:.1f}/100

Risk Level:           {risk_colors[result.risk_level]} {result.risk_level.value.upper()}

{'='*80}
DETAILED FEEDBACK
{'='*80}
"""

    if result.identified_errors:
        output += "\n🚨 IDENTIFIED ERRORS:\n"
        for error in result.identified_errors:
            output += f"  • {error}\n"
    
    if result.safety_concerns:
        output += "\n⚠️  SAFETY CONCERNS:\n"
        for concern in result.safety_concerns:
            output += f"  • {concern}\n"
    
    if result.missing_elements:
        output += "\n📋 MISSING ELEMENTS:\n"
        for element in result.missing_elements:
            output += f"  • {element}\n"
    
    if result.recommendations:
        output += "\n💡 RECOMMENDATIONS:\n"
        for rec in result.recommendations:
            output += f"  • {rec}\n"
    
    output += "\n" + "="*80 + "\n"
    
    return output

def evaluate_single_response(question, response, evaluator):
    """Evaluate a single Q&A pair"""
    result = evaluator.evaluate_response(question, response)
    return format_evaluation_result(result, question, response)

def run_demo_evaluation():
    """Run demonstration with sample data"""
    print("🏥 Medical Q&A Response Evaluator - Demo Mode")
    print("="*80)
    
    evaluator = MedicalEvaluator()
    sample_data = load_sample_data()
    
    for i, item in enumerate(sample_data, 1):
        print(f"\nSAMPLE {i}/{len(sample_data)}")
        result = evaluator.evaluate_response(
            item["question"], 
            item["ai_response"]
        )
        
        output = format_evaluation_result(
            result, 
            item["question"], 
            item["ai_response"]
        )
        print(output)
        
        if i < len(sample_data):
            input("Press Enter to continue to next sample...")

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate medical Q&A responses for clinical accuracy and safety"
    )
    
    parser.add_argument(
        "--question", 
        type=str, 
        help="Medical question to evaluate"
    )
    
    parser.add_argument(
        "--response", 
        type=str, 
        help="AI response to evaluate (text or file path)"
    )
    
    parser.add_argument(
        "--demo", 
        action="store_true", 
        help="Run demonstration with sample data"
    )
    
    parser.add_argument(
        "--output", 
        type=str, 
        help="Output file for evaluation results (JSON format)"
    )
    
    args = parser.parse_args()
    
    if args.demo:
        run_demo_evaluation()
        return
    
    if not args.question or not args.response:
        print("Error: Both --question and --response are required (or use --demo)")
        parser.print_help()
        sys.exit(1)
    
    # Load response from file if it's a file path
    response_text = args.response
    if Path(args.response).exists():
        with open(args.response, 'r') as f:
            response_text = f.read()
    
    # Evaluate the response
    evaluator = MedicalEvaluator()
    result = evaluator.evaluate_response(args.question, response_text)
    
    # Display results
    output = format_evaluation_result(result, args.question, response_text)
    print(output)
    
    # Save to file if requested
    if args.output:
        result_dict = {
            "question": args.question,
            "response": response_text,
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
        
        with open(args.output, 'w') as f:
            json.dump(result_dict, f, indent=2)
        
        print(f"Results saved to: {args.output}")

if __name__ == "__main__":
    main()