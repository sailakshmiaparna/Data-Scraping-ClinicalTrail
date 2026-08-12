"""Append normalized Trial records to a portable Markdown repository."""

import json
import re
from pathlib import Path

from models import Trial


class MarkdownStorage:
    def __init__(self, output_file: str, topic: str):
        self.path = Path(output_file)
        self.topic = topic

    def existing_nct_ids(self) -> set[str]:
        if not self.path.exists():
            return set()
        content = self.path.read_text(encoding="utf-8")
        return set(re.findall(r"^NCT ID:\s*\n\s*(NCT\d+)", content, flags=re.MULTILINE))

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists() or not self.path.read_text(encoding="utf-8").strip():
            self.path.write_text(f"# Clinical Trial Knowledge Repository\n\nTopic:\n{self.topic}\n\n==========================================================\n", encoding="utf-8")

    @staticmethod
    def _lines(items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items if item) or "- Not reported"

    @staticmethod
    def _format_claims(claims: list[dict[str, str]]) -> str:
        if not claims:
            return "- Not reported"
        formatted = []
        for claim in claims:
            lines = [f"- Claim: {claim.get('claim', 'Not reported')}" ]
            for field in ("population", "intervention", "comparator", "outcome", "result"):
                value = claim.get(field)
                if value:
                    lines.append(f"  {field.capitalize()}: {value}")
            formatted.append("\n".join(lines))
        return "\n\n".join(formatted)

    def append(self, trial: Trial) -> None:
        knowledge = trial.medical_knowledge
        primary = [item["measure"] for item in trial.outcomes if item["type"] == "Primary"]
        secondary = [item["measure"] for item in trial.outcomes if item["type"] == "Secondary"]
        other = [item["measure"] for item in trial.outcomes if item["type"] == "Other"]
        results_summary = "Results available in the ClinicalTrials.gov record." if trial.results else "No posted results in the retrieved record."
        intervention = trial.interventions[0] if trial.interventions else {}
        locations = [", ".join(filter(None, [loc.get("facility", ""), loc.get("city", ""), loc.get("state", ""), loc.get("country", "")])) for loc in trial.locations]
        investigators = [person.get("name", "") for person in trial.investigators]
        block = f'''\n# Clinical Trial\n\nSource:\n{trial.source}\n\nNCT ID:\n{trial.nct_id}\n\nBrief Title:\n{trial.brief_title or "Not reported"}\n\nOfficial Title:\n{trial.official_title or "Not reported"}\n\nStudy Type:\n{trial.study_type or "Not reported"}\n\nStudy Status:\n{trial.study_status or "Not reported"}\n\nPhase:\n{", ".join(trial.phase) or "Not reported"}\n\nSponsor:\n{trial.sponsor or "Not reported"}\n\nCollaborators:\n{self._lines(trial.collaborators)}\n\nEnrollment:\n{trial.enrollment if trial.enrollment is not None else "Not reported"}\n\nStart Date:\n{trial.start_date or "Not reported"}\n\nCompletion Date:\n{trial.completion_date or "Not reported"}\n\nStudy URL:\n{trial.url}\n\n----------------------------------------------------------\n\n# Medical Information\n\nDiseases:\n{self._lines(knowledge.get("diseases", trial.conditions))}\n\nConditions:\n{self._lines(trial.conditions)}\n\nPopulation:\n{knowledge.get("population", "Not reported")}\n\nAge:\n{trial.eligibility.get("minimum_age", "Not reported")} to {trial.eligibility.get("maximum_age", "Not reported")}\n\nSex:\n{trial.eligibility.get("sex", "Not reported")}\n\nHealthy Volunteers:\n{trial.eligibility.get("healthy_volunteers", "Not reported")}\n\nBiomarkers:\n{self._lines(knowledge.get("biomarkers", []))}\n\n----------------------------------------------------------\n\n# Intervention\n\nIntervention Type:\n{intervention.get("type", "Not reported")}\n\nIntervention Name:\n{intervention.get("name", "Not reported")}\n\nDescription:\n{intervention.get("description", "Not reported")}\n\nComparator:\n{knowledge.get("comparator", "") or "Not reported"}\n\n----------------------------------------------------------\n\n# Outcomes\n\nPrimary Outcomes:\n{self._lines(primary)}\n\nSecondary Outcomes:\n{self._lines(secondary)}\n\nOther Outcomes:\n{self._lines(other)}\n\n----------------------------------------------------------\n\n# Results\n\nOverall Results:\n{results_summary}\n\nPrimary Outcome Results:\n{knowledge.get('primary_outcome_results', 'See ClinicalTrials.gov record for outcome data.')}\n\nSecondary Outcome Results:\n{knowledge.get('secondary_outcome_results', 'See ClinicalTrials.gov record for outcome data.')}\n\nAdverse Events:\n{"Reported in source results." if trial.results.get("adverseEventsModule") else "Not reported"}\n\n----------------------------------------------------------\n\n# Study Design\n\nAllocation:\n{trial.study_design.get("allocation", "Not reported")}\n\nIntervention Model:\n{trial.study_design.get("interventionModel", "Not reported")}\n\nMasking:\n{trial.study_design.get("maskingInfo", "Not reported")}\n\nPrimary Purpose:\n{trial.study_design.get("primaryPurpose", "Not reported")}\n\n----------------------------------------------------------\n\n# Evidence\n\nEvidence Type:\n{knowledge.get("evidence_type", "Not reported")}\n\nEvidence Level:\n{knowledge.get("evidence_level", "Not reported")}\n\nConfidence:\n{knowledge.get("confidence", "Not reported")}\n\nClaims:\n{self._format_claims(knowledge.get('claims', []))}\n\n----------------------------------------------------------\n\n# Investigators\n\nPrincipal Investigator:\n{next((person.get("name", "") for person in trial.investigators if "PRINCIPAL" in person.get("role", "").upper()), "Not reported")}\n\nStudy Officials:\n{self._lines(investigators)}\n\n----------------------------------------------------------\n\n# Locations\n\n{self._lines(locations)}\n\n----------------------------------------------------------\n\n# References\n\nClinicalTrials.gov:\n{trial.url}\n\n==========================================================\n'''
        with self.path.open("a", encoding="utf-8") as output:
            output.write(block)
