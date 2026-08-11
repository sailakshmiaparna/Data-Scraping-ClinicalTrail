from agents import Supervisor
from utils import get_logger, load_config


def main() -> None:
    logger = get_logger()
    config = load_config()
    stats = Supervisor(config, logger).run()
    logger.info("Run complete: processed=%s skipped=%s failed=%s", stats["processed"], stats["skipped"], stats["failed"])


if __name__ == "__main__":
    main()
