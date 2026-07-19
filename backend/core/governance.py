from typing import List, Dict, Any, Tuple
from schemas.outputs import Indicator, AgentReport, VerdictInfo, TimelineEvent

class ValidationEngine:
    @staticmethod
    def validate_context(reports: Dict[str, AgentReport]) -> Tuple[bool, str]:
        """
        Returns (is_valid, reason_if_invalid)
        """
        has_critical = False
        has_high_confidence_positive = False
        
        for name, report in reports.items():
            for ind in report.applied_indicators:
                if ind.severity == "CRITICAL":
                    has_critical = True
                if ind.severity == "POSITIVE" and report.confidence > 80:
                    has_high_confidence_positive = True
                    
        # Contradiction detection
        if has_critical and has_high_confidence_positive:
            return False, "Contradiction detected: Critical risk found alongside high-confidence positive indicators."
            
        return True, "Valid"

class DecisionEngine:
    @staticmethod
    def compute_decision(reports: Dict[str, AgentReport]) -> Dict[str, Any]:
        base_score = 50.0
        score_modifiers = {
            "CRITICAL": -50.0,
            "HIGH": -25.0,
            "MODERATE": -10.0,
            "LOW": -5.0,
            "NEUTRAL": 0.0,
            "POSITIVE": 20.0
        }
        
        total_modifier = 0.0
        reasoning_tree = []
        highest_severity = "NEUTRAL"
        
        severity_rank = {"CRITICAL": 5, "HIGH": 4, "MODERATE": 3, "LOW": 2, "NEUTRAL": 1, "POSITIVE": 0}
        
        breakdown = {
            "threat_score": 100.0,
            "source_credibility": 100.0,
            "evidence_quality": 50.0,
            "technical_integrity": 100.0
        }
        
        confidences = [r.confidence for r in reports.values() if r.confidence > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        for agent_name, report in reports.items():
            agent_mod = 0.0
            for ind in report.applied_indicators:
                mod = score_modifiers.get(ind.severity, 0.0)
                total_modifier += mod
                agent_mod += mod
                
                reasoning_tree.append({
                    "agent": agent_name.replace("Agent", ""),
                    "finding": ind.description,
                    "impact": ind.severity
                })
                
                if severity_rank.get(ind.severity, 0) > severity_rank.get(highest_severity, 0):
                    highest_severity = ind.severity
                    
            if "Threat" in agent_name:
                breakdown["threat_score"] = max(0.0, min(100.0, 100.0 + agent_mod))
            elif "Source" in agent_name:
                breakdown["source_credibility"] = max(0.0, min(100.0, 100.0 + agent_mod))
            elif "Evidence" in agent_name:
                breakdown["evidence_quality"] = max(0.0, min(100.0, 50.0 + agent_mod))
                
        final_score = max(0.0, min(100.0, base_score + total_modifier))
        
        # Strict mapping logic
        verdict_level = "SAFE"
        mascot_state = "success"
        color = "#059669"
        recommendation = "Proceed safely. No significant risks detected."
        
        if highest_severity == "CRITICAL":
            final_score = min(final_score, 20.0) # Cap score if critical
            verdict_level = "FRAUDULENT"
            mascot_state = "error"
            color = "#991B1B"
            recommendation = "Delete and block immediately. Do not engage."
        elif highest_severity == "HIGH":
            final_score = min(final_score, 40.0)
            verdict_level = "HIGH RISK"
            mascot_state = "error"
            color = "#EA580C"
            recommendation = "Exercise extreme caution. Do not share personal information."
        elif (highest_severity == "MODERATE" and final_score < 80) or final_score < 70:
            verdict_level = "SUSPICIOUS"
            mascot_state = "thinking"
            color = "#CA8A04"
            recommendation = "Verify the sender through a secondary channel before proceeding."
            
        return {
            "final_trust_score": final_score,
            "confidence_meter": avg_confidence,
            "verdict": {
                "level": verdict_level,
                "mascot_state": mascot_state,
                "color": color,
                "recommended_action": recommendation
            },
            "trust_breakdown": breakdown,
            "reasoning_tree": reasoning_tree
        }
