"""
Script to fetch and update conference data from upstream sources.
"""

import os
import sys
import logging
from pathlib import Path
import requests
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Upstream sources
SOURCES = {
    'security-conferences.yml': 'https://raw.githubusercontent.com/sec-deadlines/sec-deadlines.github.io/master/_data/conferences.yml'
}

# AI conferences from Hugging Face - individual files
AI_CONFERENCES_BASE_URL = 'https://raw.githubusercontent.com/huggingface/ai-deadlines/main/src/data/conferences'
AI_CONFERENCE_NAMES = [
    'aaai', 'aamas', 'acl', 'acm_mm', 'aistats', 'alt', 'cec', 'chi', 'cikm', 'coling',
    'collas', 'colm', 'colt', 'conll', 'corl', 'cpal', 'cvpr', 'ecai', 'eccv', 'ecir',
    'ecml_pkdd', 'emnlp', 'esann', 'eurographics', 'fg', 'icann', 'icassp', 'iccv', 'icdar',
    'icdm', 'iclr', 'icml', 'icomp', 'icra', 'ijcai', 'ijcnlp_and_aacl', 'ijcnn', 'interspeech',
    'iros', 'iui', 'kdd', 'ksem', 'lrec', 'mathai', 'naacl', 'neurips', 'nlbse', 'rlc',
    'rss', 'sgp', 'siggraph', 'uai', 'wacv', 'wsdm', 'www'
]

# Data directory
DATA_DIR = Path(__file__).parent.parent / 'data'


def fetch_conference_data(url: str) -> dict:
    """
    Fetch conference data from upstream URL.

    Args:
        url: URL to fetch YAML data from

    Returns:
        Parsed YAML data as dictionary

    Raises:
        requests.RequestException: If fetch fails
        yaml.YAMLError: If YAML parsing fails
    """
    logger.info(f"Fetching data from {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = yaml.safe_load(response.text)
    logger.info(f"Successfully fetched and parsed data ({len(response.text)} bytes)")
    return data


def validate_conference_data(data: dict, filename: str) -> bool:
    """
    Validate that conference data has expected structure.

    Args:
        data: Parsed YAML data
        filename: Name of the file being validated

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(data, list):
        logger.error(f"Expected list of conferences, got {type(data)}")
        return False

    if len(data) == 0:
        logger.error("Conference list is empty")
        return False

    # Check that first few items have expected fields
    required_fields = {'name', 'deadline'}
    for i, conf in enumerate(data[:3]):  # Check first 3 conferences
        if not isinstance(conf, dict):
            logger.error(f"Conference {i} is not a dictionary")
            return False

        missing_fields = required_fields - set(conf.keys())
        if missing_fields:
            logger.warning(f"Conference {i} missing fields: {missing_fields}")

    logger.info(f"Validation passed: {len(data)} conferences found")
    return True


def save_conference_data(data: dict, filename: str) -> bool:
    """
    Save conference data to file.

    Args:
        data: Conference data to save
        filename: Name of the file to save to

    Returns:
        True if successful, False otherwise
    """
    filepath = DATA_DIR / filename

    try:
        # Create backup of existing file
        if filepath.exists():
            backup_path = filepath.with_suffix('.yml.backup')
            filepath.rename(backup_path)
            logger.info(f"Created backup: {backup_path}")

        # Write new data
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

        logger.info(f"Successfully saved to {filepath}")

        # Remove backup on success
        if backup_path.exists():
            backup_path.unlink()

        return True

    except Exception as e:
        logger.error(f"Failed to save {filename}: {e}")

        # Restore backup if save failed
        backup_path = filepath.with_suffix('.yml.backup')
        if backup_path.exists():
            backup_path.rename(filepath)
            logger.info("Restored from backup")

        return False


def fetch_ai_conferences() -> list:
    """
    Fetch all AI conferences from Hugging Face individual files.

    Returns:
        Consolidated list of AI conferences, or empty list on failure
    """
    consolidated_conferences = []
    failed_conferences = []

    logger.info(f"Fetching {len(AI_CONFERENCE_NAMES)} AI conferences from Hugging Face")

    for conf_name in AI_CONFERENCE_NAMES:
        url = f"{AI_CONFERENCES_BASE_URL}/{conf_name}.yml"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            conf_data = yaml.safe_load(response.text)

            # Add conference data to consolidated list
            if isinstance(conf_data, dict):
                consolidated_conferences.append(conf_data)
            elif isinstance(conf_data, list):
                consolidated_conferences.extend(conf_data)

        except requests.RequestException as e:
            failed_conferences.append(conf_name)
            logger.debug(f"Failed to fetch {conf_name}: {e}")
        except yaml.YAMLError as e:
            failed_conferences.append(conf_name)
            logger.debug(f"Failed to parse {conf_name}: {e}")

    logger.info(f"Successfully fetched {len(consolidated_conferences)} AI conferences")
    if failed_conferences:
        logger.warning(f"Failed to fetch {len(failed_conferences)} conferences: {', '.join(failed_conferences[:5])}{'...' if len(failed_conferences) > 5 else ''}")

    return consolidated_conferences


def update_ai_conferences() -> bool:
    """
    Update AI conferences by fetching and consolidating individual files.

    Returns:
        True if successful, False otherwise
    """
    filename = 'ai-conferences.yml'

    try:
        logger.info(f"Updating {filename}")

        # Fetch all AI conferences
        data = fetch_ai_conferences()

        if not data:
            logger.error(f"No AI conference data fetched, keeping existing data")
            return False

        # Validate data
        if not validate_conference_data(data, filename):
            logger.error(f"Validation failed for {filename}, keeping existing data")
            return False

        # Save data
        if not save_conference_data(data, filename):
            logger.error(f"Save failed for {filename}, keeping existing data")
            return False

        return True

    except Exception as e:
        logger.error(f"Unexpected error updating {filename}: {e}")
        logger.info("Keeping existing data")
        return False


def update_single_source(filename: str, url: str) -> bool:
    """
    Update a single conference data source.

    Args:
        filename: Name of the file to update
        url: URL to fetch data from

    Returns:
        True if successful, False otherwise
    """
    try:
        # Fetch data
        data = fetch_conference_data(url)

        # Validate data
        if not validate_conference_data(data, filename):
            logger.error(f"Validation failed for {filename}, keeping existing data")
            return False

        # Save data
        if not save_conference_data(data, filename):
            logger.error(f"Save failed for {filename}, keeping existing data")
            return False

        return True

    except requests.RequestException as e:
        logger.error(f"Network error fetching {filename}: {e}")
        logger.info("Keeping existing data")
        return False

    except yaml.YAMLError as e:
        logger.error(f"YAML parse error for {filename}: {e}")
        logger.info("Keeping existing data")
        return False

    except Exception as e:
        logger.error(f"Unexpected error updating {filename}: {e}")
        logger.info("Keeping existing data")
        return False


def main():
    """Main function to update all conference data sources."""
    logger.info("Starting conference data update")

    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    success_count = 0
    total_count = len(SOURCES) + 1  # +1 for AI conferences

    # Update AI conferences
    logger.info(f"\n{'='*60}")
    logger.info(f"Updating ai-conferences.yml")
    logger.info(f"{'='*60}")

    if update_ai_conferences():
        success_count += 1
        logger.info(f"✓ ai-conferences.yml updated successfully")
    else:
        logger.warning(f"✗ ai-conferences.yml update failed")

    # Update other sources
    for filename, url in SOURCES.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Updating {filename}")
        logger.info(f"{'='*60}")

        if update_single_source(filename, url):
            success_count += 1
            logger.info(f"✓ {filename} updated successfully")
        else:
            logger.warning(f"✗ {filename} update failed")

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"Update complete: {success_count}/{total_count} sources updated")
    logger.info(f"{'='*60}")

    # Exit with appropriate code
    if success_count == 0:
        logger.error("All updates failed")
        sys.exit(1)
    elif success_count < total_count:
        logger.warning("Some updates failed")
        sys.exit(0)  # Don't fail workflow, partial success is acceptable
    else:
        logger.info("All updates successful")
        sys.exit(0)


if __name__ == '__main__':
    main()
