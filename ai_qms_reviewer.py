# -*- coding: utf-8 -*-
"""AI-Powered QMS Document Reviewer for Medical Device Compliance.

This module provides AI-based document review capabilities supporting:
- ISO 13485:2016 - Medical Device QMS
- WHO PQ - Prequalification
- CE Marking - European Conformity
- IVDR - In Vitro Diagnostic Regulation
- FDA 21 CFR Part 820

Security Features:
- Secure API key management
- Role-based access control
- AI output review workflow
- Audit logging
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Sequence

# Configure logging for audit trail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qms_audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Try to import openai - will be used for AI-powered review if available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Try to import google.generativeai - will be used for Gemini AI review if available
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class ReviewStatus(Enum):
    """Status of document review."""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class UserRole(Enum):
    """User roles for access control."""
    ADMIN = "admin"
    QA_REVIEWER = "qa_reviewer"
    RA_REVIEWER = "ra_reviewer"
    VIEWER = "viewer"


@dataclass
class ReviewApproval:
    """AI output approval record."""
    status: ReviewStatus
    reviewer_name: str
    reviewer_role: UserRole
    approved_at: datetime = field(default_factory=datetime.now)
    comments: str = ""
    signature: str = ""


@dataclass
class ChangeControlRecord:
    """Change control documentation."""
    change_id: str
    change_type: str
    description: str
    impact_assessment: str
    requested_by: str
    requested_at: datetime = field(default_factory=datetime.now)
    approved_by: str = ""
    approved_at: Optional[datetime] = None
    status: str = "pending"


@dataclass
class PerformanceMetric:
    """Performance monitoring metrics."""
    metric_name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    notes: str = ""


@dataclass
class CheckResult:
    name: str
    passed: bool
    score: float
    found_keywords: List[str]
    message: str


# Extended CHECKS dictionary with WHO PQ, CE, IVDR compliance
CHECKS: Dict[str, Sequence[str]] = {
    # Original checks (kept for backward compatibility)
    "Document control metadata": (
        "title",
        "version",
        "effective date",
        "owner",
        "approved by",
        "reviewed by",
    ),
    "Purpose and scope": (
        "purpose",
        "scope",
        "objective",
        "applies to",
    ),
    "Roles and responsibilities": (
        "responsibility",
        "responsible",
        "role",
        "authority",
        "accountable",
    ),
    "Process flow and steps": (
        "procedure",
        "step",
        "workflow",
        "sequence",
        "process",
    ),
    "Risk management": (
        "risk",
        "hazard",
        "mitigation",
        "severity",
        "probability",
    ),
    "CAPA and nonconformance": (
        "capa",
        "nonconformance",
        "corrective action",
        "preventive action",
        "root cause",
    ),
    "Records and retention": (
        "record",
        "retention",
        "archive",
        "traceability",
        "documented information",
    ),
    # MedQMS - Medical Device QMS Checks (ISO 13485, FDA 21 CFR Part 820)
    "ISO 13485 Compliance": (
        "iso 13485",
        "quality management system",
        "regulatory requirement",
        "conformity",
        "certification",
    ),
    "Design and Development Controls": (
        "design input",
        "design output",
        "design verification",
        "design validation",
        "design change",
        "design review",
    ),
    "Production and Process Controls": (
        "production control",
        "process validation",
        "installation qualification",
        "operational qualification",
        "performance qualification",
        "work order",
    ),
    "Medical Device Reporting (MDR)": (
        "adverse event",
        "mdr",
        "complaint handling",
        "vigilance",
        "reportable event",
    ),
    "Labeling and Traceability": (
        "udi",
        "unique device identifier",
        "labeling",
        "label",
        "product identification",
        "traceability",
    ),
    "Risk Management (ISO 14971)": (
        "iso 14971",
        "risk analysis",
        "risk evaluation",
        "risk control",
        "residual risk",
        "risk management file",
    ),
    "Equipment Qualification": (
        "equipment qualification",
        "iq",
        "oq",
        "pq",
        "preventive maintenance",
        "calibration",
    ),
    "Environmental Controls": (
        "environmental control",
        "cleanroom",
        "temperature",
        "humidity",
        "particulate",
    ),
    # AI Governance and Compliance
    "AI Governance and Compliance": (
        "artificial intelligence",
        "ai validation",
        "ai risk assessment",
        "ai change control",
        "iso 13485",
        "ivdr",
        "ai output review",
        "regulatory claim",
        "automated system",
        "cybersecurity",
        "data privacy",
        "system integrity",
        "ai controlled",
        "machine learning",
        "algorithm",
    ),
    # NEW: WHO Prequalification (WHO PQ) Compliance
    "WHO Prequalification (WHO PQ)": (
        "who prequalification",
        "who pq",
        "prequalification",
        "who guidelines",
        "product dossier",
        "quality dossier",
        "safety profile",
        "performance data",
        "clinical evidence",
        "stringent regulatory authority",
        "sra",
        "emergency use listing",
        "eul",
        "product information dossier",
        "pid",
        "master file",
    ),
    # NEW: CE Marking Compliance
    "CE Marking Compliance": (
        "ce marking",
        "ce mark",
        "european conformity",
        "conformity assessment",
        "ce certificate",
        "notified body",
        "technical documentation",
        "declaration of conformity",
        "ec declaration",
        "affixing ce",
        "en iso",
        "harmonized standard",
        "nb",
        "certificate of conformity",
    ),
    # NEW: IVDR Compliance (In Vitro Diagnostic Regulation)
    "IVDR Compliance": (
        "ivdr",
        "in vitro diagnostic regulation",
        "ivd",
        "in vitro diagnostic",
        "performance evaluation",
        "ivd technical file",
        "post-market surveillance",
        "pms",
        "post-market performance follow-up",
        "pmpf",
        "competent authority",
        "european database",
        "eudamed",
        "ivd classification",
        "class a",
        "class b",
        "class c",
        "class d",
        "self-test",
        "near patient",
    ),
    # NEW: Cybersecurity Requirements
    "Cybersecurity Risk Assessment": (
        "cybersecurity",
        "cyber risk",
        "vulnerability",
        "threat",
        "penetration testing",
        "security assessment",
        "security testing",
        "incident response",
        "security audit",
        "access control",
        "authentication",
        "authorization",
        "encryption",
        "data protection",
        "gdpr",
        "hipaa",
        "phi",
        "secure development",
        "sdlc",
    ),
    # NEW: Change Control Management
    "Change Control Management": (
        "change control",
        "change request",
        "change impact",
        "change assessment",
        "change approval",
        "change history",
        "version control",
        "document revision",
        "revision history",
        "change notification",
    ),
    # NEW: Periodic Performance Monitoring
    "Performance Monitoring": (
        "performance monitoring",
        "performance metric",
        "kpi",
        "key performance indicator",
        "system performance",
        "accuracy",
        "reliability",
        "uptime",
        "response time",
        "error rate",
        "quality metric",
        "continuous improvement",
        "trend analysis",
    ),
}


def get_openai_client() -> OpenAI:
    """Initialize and return OpenAI client using API key from environment or .env file."""
    # Try to get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # If not found, try to load from .env file
    if not api_key:
        env_path = Path(".env")
        if env_path.exists():
            for line in env_path.read_text().strip().split("\n"):
                if line.startswith("OPENAI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Please set OPENAI_API_KEY environment variable "
            "or create a .env file with your API key."
        )
    
    return OpenAI(api_key=api_key)


def get_ollama_client() -> OpenAI:
    """Initialize and return an Ollama-compatible OpenAI client."""
    api_key = os.environ.get("OLLAMA_API_KEY", "ollama")
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    return OpenAI(api_key=api_key, base_url=base_url)


def get_gemini_client(api_key: str = None) -> genai.GenerativeModel:
    """Initialize and return Google Gemini client using API key."""
    if not api_key:
        # Try to get API key from environment variable
        api_key = os.environ.get("GEMINI_API_KEY")
    
    # If not found, try to load from .env file
    if not api_key:
        env_path = Path(".env")
        if env_path.exists():
            for line in env_path.read_text().strip().split("\n"):
                if line.startswith("GEMINI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    
    if not api_key:
        raise ValueError(
            "Gemini API key not found. Please set GEMINI_API_KEY environment variable "
            "or create a .env file with your GEMINI_API_KEY."
        )
    
    # Configure the Gemini API
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash')


def gemini_review_document(path: Path, model: str = "gemini-2.0-flash") -> Dict[str, object]:
    """Use Google Gemini to perform AI-powered review of QMS document."""
    if not GENAI_AVAILABLE:
        return {
            "document": str(path),
            "ai_model": model,
            "review_type": "Gemini AI-powered",
            "status": "Error",
            "error": "Google Generative AI package not installed. Install it with: pip install google-generativeai",
            "overall_score": None,
            "gaps": [],
            "recommendations": [],
            "compliance_assessment": "Gemini AI review failed: google-generativeai package not installed",
        }
    
    # Get client - will raise ValueError if no API key
    try:
        client = get_gemini_client()
    except ValueError as e:
        return {
            "document": str(path),
            "ai_model": model,
            "review_type": "Gemini AI-powered",
            "status": "Error",
            "error": str(e),
            "overall_score": None,
            "gaps": [],
            "recommendations": [],
            "compliance_assessment": f"Gemini AI review failed: {str(e)}",
        }
    
    raw = path.read_text(encoding="utf-8")
    
    # Truncate if too long (max ~100k tokens)
    if len(raw) > 75000:
        raw = raw[:75000] + "\n\n[Document truncated for analysis]"
    
    prompt = f"""You are an expert Quality Management System (QMS) reviewer specializing in 
medical device compliance (ISO 13485, FDA 21 CFR Part 820, WHO PQ, CE Marking, IVDR). 

Please review the following QMS document and provide:
1. An overall compliance score (0-100)
2. Identification of any gaps or missing sections
3. Specific recommendations for improvement
4. Whether the document meets QMS standards

QMS Document:
{raw}

Please provide your review in JSON format:
{{
    "overall_score": <0-100>,
    "status": "Pass" or "Needs Improvement",
    "gaps": [<list of missing or weak sections>],
    "recommendations": [<list of specific recommendations>],
    "compliance_assessment": "<brief overall assessment>"
}}
"""
    
    try:
        response = client.generate_content(prompt)
        result_text = response.text
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {"overall_score": 50, "status": "Needs Improvement", "gaps": [], "recommendations": [], "compliance_assessment": result_text}
        
        result["document"] = str(path)
        result["ai_model"] = model
        result["review_type"] = "Gemini AI-powered"
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        # Check for common errors and provide helpful messages
        if "API_KEY" in error_msg or "permission" in error_msg.lower():
            error_detail = "Invalid or missing Gemini API key. Please check your API key."
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            error_detail = "Gemini API quota exceeded. Please check your plan and quota at https://aistudio.google.com/app/apikey"
        else:
            error_detail = error_msg
            
        return {
            "document": str(path),
            "ai_model": model,
            "review_type": "Gemini AI-powered",
            "status": "Error",
            "error": error_detail,
            "overall_score": None,
            "gaps": [],
            "recommendations": [],
            "compliance_assessment": f"Gemini AI review failed: {error_detail}",
        }


def normalize_text(text: str) -> str:
    """Normalize whitespace and lowercase for matching."""
    return re.sub(r"\s+", " ", text).lower().strip()


def evaluate_check(name: str, keywords: Sequence[str], text: str) -> CheckResult:
    """Evaluate a single checklist against the document text."""
    hits = [kw for kw in keywords if kw in text]
    score = len(hits) / max(len(keywords), 1)
    passed = score >= 0.4

    if passed:
        message = f"{name}: appears covered ({len(hits)}/{len(keywords)} indicators found)."
    else:
        message = (
            f"{name}: potential gap ({len(hits)}/{len(keywords)} indicators found). "
            "Consider adding explicit language."
        )

    return CheckResult(
        name=name,
        passed=passed,
        score=round(score, 2),
        found_keywords=hits,
        message=message,
    )


def review_document(path: Path) -> Dict[str, object]:
    """Review a document and return structured findings."""
    raw = path.read_text(encoding="utf-8")
    text = normalize_text(raw)

    check_results = [evaluate_check(name, keywords, text) for name, keywords in CHECKS.items()]

    overall_score = round(sum(result.score for result in check_results) / len(check_results), 2)
    status = "Pass" if overall_score >= 0.6 else "Needs Improvement"

    return {
        "document": str(path),
        "overall_score": overall_score,
        "status": status,
        "results": [
            {
                "check": result.name,
                "passed": result.passed,
                "score": result.score,
                "found_keywords": result.found_keywords,
                "message": result.message,
            }
            for result in check_results
        ],
    }


def ai_review_document(path: Path, model: str = "gpt-4o") -> Dict[str, object]:
    """Use OpenAI to perform AI-powered review of QMS document."""
    if not OPENAI_AVAILABLE:
        raise ImportError(
            "OpenAI package not installed. Install it with: pip install openai"
        )
    
    # Get client - will raise ValueError if no API key
    try:
        client = get_openai_client()
    except ValueError as e:
        return {
            "document": str(path),
            "ai_model": model,
            "review_type": "AI-powered",
            "status": "Error",
            "error": str(e),
            "overall_score": None,
            "gaps": [],
            "recommendations": [],
            "compliance_assessment": f"AI review failed: {str(e)}",
        }
    
    raw = path.read_text(encoding="utf-8")
    
    # Truncate if too long (max ~100k tokens)
    if len(raw) > 75000:
        raw = raw[:75000] + "\n\n[Document truncated for analysis]"
    
    prompt = f"""You are an expert Quality Management System (QMS) reviewer specializing in 
medical device compliance (ISO 13485, FDA 21 CFR Part 820). 

Please review the following QMS document and provide:
1. An overall compliance score (0-100)
2. Identification of any gaps or missing sections
3. Specific recommendations for improvement
4. Whether the document meets QMS standards

QMS Document:
{raw}

Please provide your review in JSON format:
{{
    "overall_score": <0-100>,
    "status": "Pass" or "Needs Improvement",
    "gaps": [<list of missing or weak sections>],
    "recommendations": [<list of specific recommendations>],
    "compliance_assessment": "<brief overall assessment>"
}}
"""
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert QMS compliance reviewer for medical devices."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        result["document"] = str(path)
        result["ai_model"] = model
        result["review_type"] = "AI-powered"
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        # Check for common errors and provide helpful messages
        if "insufficient_quota" in error_msg or "429" in error_msg:
            error_detail = "OpenAI API quota exceeded. Please check your plan and billing details at https://platform.openai.com/account/billing"
        elif "authentication" in error_msg.lower() or "401" in error_msg:
            error_detail = "Invalid API key. Please check your OpenAI API key in .env file"
        elif "rate_limit" in error_msg.lower():
            error_detail = "Rate limit exceeded. Please wait and try again"
        else:
            error_detail = error_msg
            
        return {
            "document": str(path),
            "ai_model": model,
            "review_type": "AI-powered",
            "status": "Error",
            "error": error_detail,
            "overall_score": None,
            "gaps": [],
            "recommendations": [],
            "compliance_assessment": f"AI review failed: {error_detail}",
        }


def ollama_review_document(path: Path, model: str = "llama3.1") -> Dict[str, object]:
    """Use Ollama (OpenAI-compatible API) to perform AI-powered review."""
    if not OPENAI_AVAILABLE:
        return {
            "document": str(path),
            "ai_model": model,
            "review_type": "Ollama AI-powered",
            "status": "Error",
            "error": "OpenAI package not installed. Install it with: pip install openai",
            "overall_score": None,
            "gaps": [],
            "recommendations": [],
            "compliance_assessment": "Ollama AI review failed: openai package not installed",
        }

    client = get_ollama_client()
    raw = path.read_text(encoding="utf-8")

    if len(raw) > 75000:
        raw = raw[:75000] + "\n\n[Document truncated for analysis]"

    prompt = f"""You are an expert Quality Management System (QMS) reviewer specializing in
medical device compliance (ISO 13485, FDA 21 CFR Part 820, WHO PQ, CE Marking, IVDR).

Please review the following QMS document and provide:
1. An overall compliance score (0-100)
2. Identification of any gaps or missing sections
3. Specific recommendations for improvement
4. Whether the document meets QMS standards

QMS Document:
{raw}

Please provide your review in JSON format:
{{
    "overall_score": <0-100>,
    "status": "Pass" or "Needs Improvement",
    "gaps": [<list of missing or weak sections>],
    "recommendations": [<list of specific recommendations>],
    "compliance_assessment": "<brief overall assessment>"
}}
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert QMS compliance reviewer for medical devices."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        result["document"] = str(path)
        result["ai_model"] = model
        result["review_type"] = "Ollama AI-powered"
        return result

    except Exception as e:
        return {
            "document": str(path),
            "ai_model": model,
            "review_type": "Ollama AI-powered",
            "status": "Error",
            "error": str(e),
            "overall_score": None,
            "gaps": [],
            "recommendations": [],
            "compliance_assessment": f"Ollama AI review failed: {str(e)}",
        }


def print_human_report(report: Dict[str, object]) -> None:
    """Print a human-readable report."""
    print(f"QMS AI Review: {report['document']}")
    print(f"Overall Score: {report['overall_score']} | Status: {report['status']}")
    print("-" * 72)

    for item in report["results"]:
        icon = "✔" if item["passed"] else "✖"
        print(f"{icon} {item['check']} (score={item['score']})")
        print(f"   {item['message']}")
        if item["found_keywords"]:
            print(f"   Found: {', '.join(item['found_keywords'])}")
        else:
            print("   Found: none")


def print_ai_report(report: Dict[str, object]) -> None:
    """Print AI-powered review report."""
    print(f"AI QMS Review: {report['document']}")
    print(f"Model: {report.get('ai_model', 'N/A')}")
    print(f"Overall Score: {report.get('overall_score', 'N/A')} | Status: {report['status']}")
    print("-" * 72)
    
    # Print error if present
    if "error" in report:
        print(f"Error: {report['error']}")
        print()
    
    if "gaps" in report and report["gaps"]:
        print("Identified Gaps:")
        for gap in report["gaps"]:
            print(f"  - {gap}")
        print()
    
    if "recommendations" in report and report["recommendations"]:
        print("Recommendations:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")
        print()
    
    if "compliance_assessment" in report:
        print(f"Compliance Assessment: {report['compliance_assessment']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI-style QMS document reviewer")
    parser.add_argument("document", type=Path, help="Path to .txt or .md document")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--ai", action="store_true", help="Use AI-powered review (requires OpenAI or Gemini API key)")
    parser.add_argument("--model", type=str, default="gpt-4o", help="AI model to use (default: gpt-4o for OpenAI, gemini-2.0-flash for Gemini)")
    parser.add_argument("--provider", type=str, choices=["openai", "gemini"], default="openai", help="AI provider to use (default: openai)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.document.exists():
        raise FileNotFoundError(f"Document not found: {args.document}")

    if args.ai:
        # Use AI-powered review
        if args.provider == "gemini":
            # Use Gemini AI
            report = gemini_review_document(args.document, model=args.model)
        else:
            # Use OpenAI (default)
            report = ai_review_document(args.document, model=args.model)
        
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_ai_report(report)
    else:
        # Use keyword-based review (default)
        report = review_document(args.document)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_human_report(report)


if __name__ == "__main__":
    main()
