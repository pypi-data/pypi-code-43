import logging
from cf_loggers.elasticsearch.handler import ESLoggingHandler


def init_logger(logger_settings):
    logging.getLogger("elasticsearch").setLevel(logging.WARNING)
    logging.basicConfig(
        level=logger_settings.get("LEVEL", "INFO"),
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(name)s]   %(message)s",
        handlers=[
            logging.StreamHandler(),
            ESLoggingHandler(
                hosts=logger_settings['HOSTS'],
                index=logger_settings['INDEX'],
                doc_type=logger_settings.get('DOC_TYPE'),
                extra_data=logger_settings.get("EXTRA_DATA", {})
            )
        ])
