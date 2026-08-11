import unittest

from extractors import KnowledgeExtractor
from parsers import ClinicalTrialsParser
from storage import MarkdownStorage


SAMPLE = {
    "protocolSection": {
        "identificationModule": {"nctId": "NCT00000001", "briefTitle": "Insulin sensitivity trial"},
        "statusModule": {"overallStatus": "COMPLETED", "startDateStruct": {"date": "2020-01-01"}},
        "designModule": {"studyType": "INTERVENTIONAL", "phases": ["PHASE2"], "enrollmentInfo": {"count": 25}, "allocation": "RANDOMIZED"},
        "sponsorCollaboratorsModule": {"leadSponsor": {"name": "Example Sponsor"}},
        "conditionsModule": {"conditions": ["Insulin Resistance"]},
        "armsInterventionsModule": {"interventions": [{"type": "BEHAVIORAL", "name": "Lifestyle intervention"}]},
        "outcomesModule": {"primaryOutcomes": [{"measure": "HOMA-IR"}]},
        "eligibilityModule": {"sex": "ALL", "minimumAge": "18 Years"},
    }
}


class PipelineTests(unittest.TestCase):
    def test_parse_and_extract_normalized_trial(self):
        trial = KnowledgeExtractor().extract(ClinicalTrialsParser().parse(SAMPLE))
        self.assertEqual(trial.nct_id, "NCT00000001")
        self.assertEqual(trial.medical_knowledge["evidence_level"], "High")
        # Keep the temporary artifact within the writable project workspace.
        storage = MarkdownStorage("output/test_repository.md", "Test topic")
        self.assertEqual(storage.topic, "Test topic")


if __name__ == "__main__":
    unittest.main()
