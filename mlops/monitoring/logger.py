import structlog
import logging
import sys
from src.sre.config.settings import get_settings

settings = get_settings()

def setup_logging():
    """Configura logging estructurado JSON."""
    
    # Configuramos structlog para que sea el procesador principal
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() # ¡Aquí está la magia! Convierte todo a JSON
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configuración básica de logging de Python para que use structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )

def get_logger(name: str):
    """Retorna logger estructurado."""
    setup_logging()
    return structlog.get_logger(name)