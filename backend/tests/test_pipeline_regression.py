import pytest
from core.governance import ValidationEngine, DecisionEngine
from schemas.outputs import AgentReport, Indicator

def create_report(confidence, indicators) -> AgentReport:
    return AgentReport(
        confidence=confidence,
        reasoning="Test reasoning",
        evidence_used=[],
        applied_indicators=[
            Indicator(id=f"TEST_{i}", severity=sev, category="TECH", description=desc)
            for i, (sev, desc) in enumerate(indicators)
        ]
    )

def test_safe_invoice():
    reports = {
        "ThreatAgent": create_report(90.0, [("NEUTRAL", "No threats found")]),
        "SourceAgent": create_report(85.0, [("POSITIVE", "Trusted domain")]),
        "EvidenceAgent": create_report(95.0, [("POSITIVE", "Valid contact info")])
    }
    is_valid, msg = ValidationEngine.validate_context(reports)
    assert is_valid == True
    
    decision = DecisionEngine.compute_decision(reports)
    assert decision["verdict"]["level"] == "SAFE"
    assert decision["final_trust_score"] > 80.0

def test_critical_phishing():
    reports = {
        "ThreatAgent": create_report(90.0, [("CRITICAL", "Brand spoofing detected")]),
        "SourceAgent": create_report(85.0, [("HIGH", "Suspicious TLD")]),
        "EvidenceAgent": create_report(50.0, [("LOW", "Sparse text")])
    }
    is_valid, msg = ValidationEngine.validate_context(reports)
    assert is_valid == True
    
    decision = DecisionEngine.compute_decision(reports)
    assert decision["verdict"]["level"] == "FRAUDULENT"
    assert decision["final_trust_score"] <= 20.0

def test_contradiction_detection():
    # Threat says CRITICAL, but Source says highly trusted POSITIVE
    reports = {
        "ThreatAgent": create_report(90.0, [("CRITICAL", "Phishing link detected")]),
        "SourceAgent": create_report(90.0, [("POSITIVE", "Highly trusted government domain")])
    }
    is_valid, msg = ValidationEngine.validate_context(reports)
    assert is_valid == False
    assert "Contradiction detected" in msg

def test_high_risk_suspicious():
    reports = {
        "ThreatAgent": create_report(80.0, [("HIGH", "Insecure connection requested")]),
        "SourceAgent": create_report(70.0, [("MODERATE", "Unknown reputation")]),
        "EvidenceAgent": create_report(60.0, [("NEUTRAL", "Standard text")])
    }
    decision = DecisionEngine.compute_decision(reports)
    assert decision["verdict"]["level"] == "HIGH RISK"
    assert decision["final_trust_score"] <= 40.0

def test_moderate_suspicious():
    reports = {
        "ThreatAgent": create_report(70.0, [("MODERATE", "Unusual language")]),
        "SourceAgent": create_report(60.0, [("NEUTRAL", "Unknown")]),
        "EvidenceAgent": create_report(50.0, [("NEUTRAL", "Unknown")])
    }
    decision = DecisionEngine.compute_decision(reports)
    assert decision["verdict"]["level"] == "SUSPICIOUS"
    assert 30.0 <= decision["final_trust_score"] <= 70.0

def test_neutral_baseline():
    reports = {
        "ThreatAgent": create_report(50.0, []),
        "SourceAgent": create_report(50.0, []),
        "EvidenceAgent": create_report(50.0, [])
    }
    decision = DecisionEngine.compute_decision(reports)
    assert decision["verdict"]["level"] == "SUSPICIOUS" # Baseline is 50, which is < 70, so suspicious
    assert decision["final_trust_score"] == 50.0

def test_mixed_signals_but_safe():
    reports = {
        "ThreatAgent": create_report(85.0, [("NEUTRAL", "Safe")]),
        "SourceAgent": create_report(80.0, [("MODERATE", "Slightly unknown")]),
        "EvidenceAgent": create_report(90.0, [("POSITIVE", "Verified facts"), ("POSITIVE", "Known entity")])
    }
    decision = DecisionEngine.compute_decision(reports)
    # base 50 + mod -10 + 20 + 20 = 80
    assert decision["verdict"]["level"] == "SAFE"
    assert decision["final_trust_score"] == 80.0

def test_confidence_averaging():
    reports = {
        "ThreatAgent": create_report(90.0, []),
        "SourceAgent": create_report(70.0, []),
        "EvidenceAgent": create_report(50.0, [])
    }
    decision = DecisionEngine.compute_decision(reports)
    assert decision["confidence_meter"] == 70.0
