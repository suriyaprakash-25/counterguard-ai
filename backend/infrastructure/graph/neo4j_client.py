import logging
from typing import Optional

try:
    from neo4j import Driver, GraphDatabase

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    Driver = object

from backend.settings import settings

logger = logging.getLogger(__name__)


class Neo4jClient:
    """
    Manages the lifecycle of the Neo4j database driver.
    Responsible for connectivity verification and providing sessions.
    """

    def __init__(self):
        self.driver: Optional[Driver] = None
        self.database = settings.NEO4J_DATABASE
        self.is_connected = False

    def connect(self) -> bool:
        """
        Initializes the driver and verifies connectivity.
        Returns True if successful, False otherwise.
        """
        if not NEO4J_AVAILABLE:
            logger.warning(
                "Neo4j driver is not installed. Graph operations will be mocked."
            )
            return False

        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
            )
            self.driver.verify_connectivity()
            self.is_connected = True
            logger.info(f"Neo4j connected. Database selected: '{self.database}'")
            self._initialize_constraints()
            return True
        except Exception as e:
            logger.warning(f"Connection failure to Neo4j at {settings.NEO4J_URI}: {e}")
            self.close()
            return False

    def _initialize_constraints(self):
        """Creates uniqueness constraints automatically during initialization."""
        if not self.driver or not self.is_connected:
            return

        # Unique constraints on standard labels
        constraints = [
            ("Seller", "id"),
            ("Phone", "id"),
            ("Email", "id"),
            ("Address", "id"),
            ("Marketplace", "id"),
            ("Product", "id"),
            ("Invoice", "id"),
            ("Image", "id"),
            ("Investigation", "id"),
        ]

        with self.session() as session:
            for label, property_name in constraints:
                query = f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.{property_name} IS UNIQUE"
                try:
                    session.run(query)
                    logger.debug(
                        f"Constraint creation verified for {label}.{property_name}"
                    )
                except Exception as e:
                    logger.debug(f"Constraint creation failed for {label}: {e}")

    def session(self, **kwargs):
        """
        Returns a Neo4j session. Passes the configured database name.
        """
        if not self.driver or not self.is_connected:
            raise RuntimeError("Neo4j client is not connected.")

        kwargs.setdefault("database", self.database)
        # In Community Edition, custom databases might not be supported easily,
        # but the driver accepts it. If it fails due to community edition,
        # we can default it back by removing it, but standard practice is to pass it.
        try:
            return self.driver.session(**kwargs)
        except Exception:
            # Fallback for systems that don't support multi-database strictly
            kwargs.pop("database", None)
            return self.driver.session(**kwargs)

    def close(self):
        """Closes the underlying driver cleanly."""
        if self.driver:
            self.driver.close()
        self.driver = None
        self.is_connected = False
        logger.info("Neo4j client closed.")
