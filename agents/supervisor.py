"""Pipeline orchestration only."""

from collectors import ClinicalTrialsCollector
from extractors import KnowledgeExtractor
from parsers import ClinicalTrialsParser
from storage import MarkdownStorage
from utils import Checkpoint


class Supervisor:
    def __init__(self, config, logger):
        self.config, self.logger = config, logger
        self.collector = ClinicalTrialsCollector(config, logger)
        self.parser = ClinicalTrialsParser()
        self.extractor = KnowledgeExtractor()
        self.storage = MarkdownStorage(config["output"]["file"], config["topic"])
        self.checkpoint = Checkpoint(config["output"]["checkpoint"])

    def run(self) -> dict[str, int]:
        self.storage.initialize()
        checkpoint = self.checkpoint.load()
        prior_processed = checkpoint.get("processed", 0)
        known_ids = self.storage.existing_nct_ids()
        stats = {"processed": 0, "skipped": 0, "failed": 0}
        if checkpoint.get("completed"):
            self.logger.info("Collection already completed. Remove output/checkpoint.json to run a fresh collection.")
            return stats
        for studies, next_token in self.collector.paginate(checkpoint.get("next_page_token")):
            for raw in studies:
                nct_id = raw.get("protocolSection", {}).get("identificationModule", {}).get("nctId", "unknown")
                if nct_id in known_ids:
                    stats["skipped"] += 1
                    continue
                try:
                    trial = self.extractor.extract(self.parser.parse(raw))
                    if not trial.nct_id:
                        raise ValueError("Study has no NCT ID")
                    self.storage.append(trial)
                    known_ids.add(trial.nct_id)
                    stats["processed"] += 1
                except Exception as error:  # A malformed single record must not halt collection.
                    self.logger.exception("Failed trial %s: %s", nct_id, error)
                    checkpoint.setdefault("failed_nct_ids", []).append(nct_id)
                    stats["failed"] += 1
            checkpoint.update({"next_page_token": next_token, "processed": prior_processed + stats["processed"], "completed": not bool(next_token)})
            self.checkpoint.save(checkpoint)
            self.logger.info("Checkpoint saved: processed=%s skipped=%s failed=%s", stats["processed"], stats["skipped"], stats["failed"])
        return stats
