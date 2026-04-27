import json
import logging
from pathlib import Path
import networkx as nx
import tomli

from forge.core.config import get_settings

logger = logging.getLogger(__name__)

_graph = None
_domain_config = None


def load_domain_config() -> dict:
    """Load domain configuration from TOML files."""
    global _domain_config
    if _domain_config is not None:
        return _domain_config

    _domain_config = {
        "stages": {},
        "screens": {},
        "entities": {},
        "roles": {}
    }

    try:
        settings = get_settings()
        domain_path = Path(settings.features_repo_path).parent / "reference" / "config" / "domain"

        if not domain_path.exists():
            logger.warning(f"Domain config path does not exist: {domain_path}")
            return _domain_config

        # Load all TOML files from domain directory
        toml_files = list(domain_path.glob("*.toml"))
        if not toml_files:
            logger.warning(f"No TOML files found in {domain_path}")
            return _domain_config

        for toml_file in toml_files:
            try:
                with open(toml_file, "rb") as f:
                    config = tomli.load(f)

                    # Extract stages
                    if "stages" in config:
                        for stage_name, stage_data in config["stages"].items():
                            _domain_config["stages"][stage_name] = stage_data

                    # Extract screens
                    if "screens" in config:
                        for screen_name, screen_data in config["screens"].items():
                            _domain_config["screens"][screen_name] = screen_data

                    # Extract entities
                    if "entities" in config:
                        for entity_name, entity_data in config["entities"].items():
                            _domain_config["entities"][entity_name] = entity_data

                    # Extract roles
                    if "roles" in config:
                        for role_name, role_data in config["roles"].items():
                            _domain_config["roles"][role_name] = role_data

            except Exception as e:
                logger.error(f"Error loading TOML file {toml_file}: {e}")
                continue

        logger.info(f"Loaded domain config from {len(toml_files)} TOML files")
        logger.debug(f"Stages: {list(_domain_config['stages'].keys())}")
        logger.debug(f"Screens: {list(_domain_config['screens'].keys())}")
        logger.debug(f"Entities: {list(_domain_config['entities'].keys())}")
        logger.debug(f"Roles: {list(_domain_config['roles'].keys())}")

    except Exception as e:
        logger.error(f"Error loading domain config: {e}")

    return _domain_config


def load_domain_graph() -> nx.DiGraph:
    """Load domain knowledge graph from TOML files.

    Builds: Stage → Screen → Entity → Role hierarchy
    """
    global _graph
    if _graph is not None:
        return _graph

    _graph = nx.DiGraph()
    config = load_domain_config()

    try:
        # Add stage nodes
        for stage_name in config.get("stages", {}).keys():
            _graph.add_node(stage_name, node_type="stage")

        # Add screen nodes and stage→screen edges
        for screen_name, screen_data in config.get("screens", {}).items():
            _graph.add_node(screen_name, node_type="screen")

            # Connect to applicable stages
            applicable_stages = screen_data.get("applicable_stages", [])
            for stage in applicable_stages:
                if stage in _graph.nodes():
                    _graph.add_edge(stage, screen_name, relation="has_screen")

        # Add entity nodes and screen→entity edges
        for entity_name, entity_data in config.get("entities", {}).items():
            _graph.add_node(entity_name, node_type="entity")

            # Connect to applicable screens
            applicable_screens = entity_data.get("applicable_screens", [])
            for screen in applicable_screens:
                if screen in _graph.nodes():
                    _graph.add_edge(screen, entity_name, relation="has_entity")

        # Add role nodes and entity→role edges
        for role_name, role_data in config.get("roles", {}).items():
            _graph.add_node(role_name, node_type="role")

            # Connect to applicable entities
            applicable_entities = role_data.get("applicable_entities", [])
            for entity in applicable_entities:
                if entity in _graph.nodes():
                    _graph.add_edge(entity, role_name, relation="has_role")

        logger.info(
            f"Domain graph loaded: {_graph.number_of_nodes()} nodes, {_graph.number_of_edges()} edges"
        )

    except Exception as e:
        logger.error(f"Error building domain graph: {e}")
        _graph = nx.DiGraph()

    return _graph


def validate_step(step_text: str, stage: str, screen: str) -> str:
    """
    Validate step against domain graph.
    Checks if (stage, screen) combination is valid.
    Returns [ROLE_GAP] marker if validation fails, None otherwise.
    """
    if not stage or not screen:
        return None

    try:
        graph = load_domain_graph()

        # Check if stage node exists
        if stage not in graph.nodes():
            logger.debug(f"Stage '{stage}' not found in domain graph")
            return None

        # Check if screen node exists
        if screen not in graph.nodes():
            logger.debug(f"Screen '{screen}' not found in domain graph")
            return None

        # Check if stage connects to screen
        if not nx.has_path(graph, stage, screen):
            logger.debug(f"No path from stage '{stage}' to screen '{screen}' in domain graph")
            return "[ROLE_GAP]"

        # Extract entity roles from step text (simple pattern: capital words that match known entities)
        config = load_domain_config()
        known_entities = set(config.get("entities", {}).keys())
        step_words = step_text.split()
        mentioned_entities = {word for word in step_words if word in known_entities}

        if mentioned_entities:
            # Verify mentioned entities are applicable to the screen
            for entity in mentioned_entities:
                if entity not in graph.nodes():
                    logger.debug(f"Entity '{entity}' mentioned in step but not in domain graph")
                    return "[ROLE_GAP]"

                if not nx.has_path(graph, screen, entity):
                    logger.debug(f"Entity '{entity}' not applicable to screen '{screen}'")
                    return "[ROLE_GAP]"

        return None

    except Exception as e:
        logger.error(f"Error validating step: {e}")
        return None
