"""Deterministic clinical knowledge extraction from a normalized Trial."""

import re

from models import Trial


class KnowledgeExtractor:
    BIOMARKERS = ("HbA1c", "fasting glucose", "insulin", "HOMA-IR", "triglycerides", "HDL", "LDL", "BMI", "waist circumference", "body weight")
    RISK_FACTORS = ("obesity", "physical inactivity", "poor diet", "sleep disturbance", "sedentary behavior", "overweight")

    @staticmethod
    def _matches(terms: tuple[str, ...], text: str) -> list[str]:
        return [term for term in terms if re.search(rf"\b{re.escape(term)}\b", text, re.I)]

    def extract(self, trial: Trial) -> Trial:
        corpus = " ".join([trial.brief_title, trial.official_title, *trial.conditions, trial.eligibility.get("criteria", ""), *[str(x) for x in trial.outcomes]])
        primary = [outcome["measure"] for outcome in trial.outcomes if outcome["type"] == "Primary"]
        intervention_names = [item["name"] for item in trial.interventions]
        comparator = next((name for name in intervention_names if re.search(r"placebo|usual care|control|comparator|sham|no intervention", name, re.I)), "")
        evidence_type, evidence_level = self._evidence(trial)
        trial.medical_knowledge = {
            "diseases": trial.conditions,
            "biomarkers": self._matches(self.BIOMARKERS, corpus),
            "population": self._population(trial),
            "risk_factors": self._matches(self.RISK_FACTORS, corpus),
            "interventions": intervention_names,
            "comparator": comparator,
            "outcomes": primary,
            "claims": self._claims(trial, primary, comparator),
            "evidence_type": evidence_type,
            "evidence_level": evidence_level,
            "confidence": "High" if evidence_level == "High" and trial.results else "Moderate" if evidence_level == "High" else "Limited",
        }
        return trial

    @staticmethod
    def _population(trial: Trial) -> str:
        criteria = trial.eligibility.get("criteria", "").strip()
        return criteria[:800] if criteria else "Not reported"

    @staticmethod
    def _evidence(trial: Trial) -> tuple[str, str]:
        allocation = str(trial.study_design.get("allocation", ""))
        if trial.study_type == "INTERVENTIONAL" and allocation == "RANDOMIZED":
            return "Randomized Controlled Trial", "High"
        if trial.study_type == "INTERVENTIONAL":
            return "Interventional Study", "Moderate"
        if trial.study_type == "OBSERVATIONAL":
            return "Observational Study", "Moderate"
        return trial.study_type.title() or "Not reported", "Limited"

    @staticmethod
    def _claims(trial: Trial, outcomes: list[str], comparator: str) -> list[dict[str, str]]:
        if not trial.interventions or not outcomes:
            return []
        return [{"claim": "The study evaluates the listed intervention(s) for its specified primary outcome(s).", "population": trial.eligibility.get("minimum_age", "Not reported"), "intervention": ", ".join(item["name"] for item in trial.interventions), "comparator": comparator or "Not reported", "outcome": ", ".join(outcomes), "result": "See registered results when available."}]
