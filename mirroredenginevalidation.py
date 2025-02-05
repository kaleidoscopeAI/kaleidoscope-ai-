# Mirrored Engine
class MirroredEngine:
    def __init__(self):
        self.memory_bank = []

    def validate_insights(self, insights):
        """Validates insights based on ethical and logical guidelines."""
        validated = []
        for insight in insights:
            if self._passes_guidelines(insight):
                validated.append({"insight": insight, "status": "approved"})
            else:
                validated.append({"insight": insight, "status": "rejected"})
        return validated

    def generate_alternative_perspectives(self, insights):
        """Creates speculative perspectives for validated insights."""
        alternatives = []
        for insight in insights:
            alternative = self._speculate_on_insight(insight)
            alternatives.append(alternative)
        return alternatives

    def _passes_guidelines(self, insight):
        """Placeholder for ethical and logical checks."""
        return True if "significance" in insight and insight["significance"] > 0.5 else False

    def _speculate_on_insight(self, insight):
        """Generate speculative insights by altering existing parameters."""
        speculative = {key: (value * 0.9 if isinstance(value, (int, float)) else value)
                       for key, value in insight.items()}
        speculative["type"] = f"speculative_{insight.get('type', 'unknown')}"
        return speculative

# Insight Validation System
class InsightValidator:
    def __init__(self):
        self.engine = MirroredEngine()

    def process_insights(self, insights):
        """Processes insights through validation and alternative perspective generation."""
        validated = self.engine.validate_insights(insights)
        speculative = self.engine.generate_alternative_perspectives([v["insight"] for v in validated if v["status"] == "approved"])
        return {
            "validated": validated,
            "speculative": speculative
        }

# Example Usage
if __name__ == "__main__":
    # Sample insights
    sample_insights = [
        {"type": "prediction", "significance": 0.8, "details": "High confidence result"},
        {"type": "analysis", "significance": 0.4, "details": "Low confidence result"}
    ]

    # Process insights
    validator = InsightValidator()
    results = validator.process_insights(sample_insights)

    # Display results
    print("\n=== Validated Insights ===")
    for validated in results["validated"]:
        print(validated)

    print("\n=== Speculative Perspectives ===")
    for speculative in results["speculative"]:
        print(speculative)
