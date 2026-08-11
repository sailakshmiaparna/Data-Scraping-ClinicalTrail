"""Translate ClinicalTrials.gov v2 JSON into the canonical Trial model."""

from typing import Any

from models import Trial


def _text(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("date") or value.get("value") or "")
    return str(value or "")


class ClinicalTrialsParser:
    source_name = "ClinicalTrials.gov"

    def parse(self, raw: dict[str, Any]) -> Trial:
        protocol = raw.get("protocolSection", {})
        identification = protocol.get("identificationModule", {})
        status = protocol.get("statusModule", {})
        design = protocol.get("designModule", {})
        contacts = protocol.get("contactsLocationsModule", {})
        sponsor = protocol.get("sponsorCollaboratorsModule", {})
        conditions = protocol.get("conditionsModule", {})
        arms = protocol.get("armsInterventionsModule", {})
        outcomes = protocol.get("outcomesModule", {})
        eligibility = protocol.get("eligibilityModule", {})
        officials = contacts.get("overallOfficials", [])
        enrollment = design.get("enrollmentInfo", {}).get("count")
        return Trial(
            source=self.source_name,
            nct_id=identification.get("nctId", ""),
            brief_title=identification.get("briefTitle", ""),
            official_title=identification.get("officialTitle", ""),
            study_type=design.get("studyType", ""),
            study_status=status.get("overallStatus", ""),
            phase=design.get("phases", []),
            sponsor=sponsor.get("leadSponsor", {}).get("name", ""),
            collaborators=[item.get("name", "") for item in sponsor.get("collaborators", [])],
            enrollment=enrollment if isinstance(enrollment, int) else None,
            conditions=conditions.get("conditions", []),
            interventions=[{"type": item.get("type", ""), "name": item.get("name", ""), "description": item.get("description", "")} for item in arms.get("interventions", [])],
            outcomes=self._outcomes(outcomes),
            eligibility={"criteria": eligibility.get("eligibilityCriteria", ""), "sex": eligibility.get("sex", ""), "minimum_age": eligibility.get("minimumAge", ""), "maximum_age": eligibility.get("maximumAge", ""), "healthy_volunteers": eligibility.get("healthyVolunteers", "")},
            study_design={key: design.get(key, "") for key in ("allocation", "interventionModel", "primaryPurpose", "maskingInfo", "observationalModel", "timePerspective")},
            locations=[self._location(item) for item in contacts.get("locations", [])],
            investigators=[{"name": item.get("name", ""), "role": item.get("role", ""), "affiliation": item.get("affiliation", "")} for item in officials],
            start_date=_text(status.get("startDateStruct")),
            completion_date=_text(status.get("completionDateStruct")),
            results=raw.get("resultsSection", {}),
            url=f"https://clinicaltrials.gov/study/{identification.get('nctId', '')}",
        )

    @staticmethod
    def _outcomes(module: dict[str, Any]) -> list[dict[str, str]]:
        records = []
        for kind, key in (("Primary", "primaryOutcomes"), ("Secondary", "secondaryOutcomes"), ("Other", "otherOutcomes")):
            records.extend({"type": kind, "measure": item.get("measure", ""), "description": item.get("description", ""), "time_frame": item.get("timeFrame", "")} for item in module.get(key, []))
        return records

    @staticmethod
    def _location(item: dict[str, Any]) -> dict[str, str]:
        return {key: item.get(key, "") for key in ("facility", "city", "state", "country", "zip")}
