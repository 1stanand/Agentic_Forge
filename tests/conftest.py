"""Pytest configuration and shared fixtures."""
import pytest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from forge.core.config import get_settings
from forge.core.db import get_conn, release_conn, get_cursor


@pytest.fixture(scope="session")
def settings():
    """Get application settings."""
    return get_settings()


@pytest.fixture
def db_connection():
    """Provide a database connection for tests."""
    conn = get_conn()
    yield conn
    release_conn(conn)


@pytest.fixture
def csv_sample_cas():
    """Sample CAS JIRA CSV for testing."""
    return """Summary,Description,Acceptance Criteria,Comments
Test Case 1,"Create a new guarantor","- Guarantor name is required
- SSN must be valid","Sample test data"
"""


@pytest.fixture
def csv_sample_complex():
    """Complex CAS JIRA CSV with multiple acceptance criteria."""
    return """Summary,Description,Acceptance Criteria,Comments
Delete Guarantor,"User can delete a guarantor from the system","Given user is on Delete Guarantor page
When user enters guarantor ID
And user clicks Delete button
Then guarantor is removed from system
And confirmation message is shown","Complex test case"
"""


@pytest.fixture
def feature_file_template():
    """Template for generated feature files."""
    return """Feature: Test Feature
  Background:
    Given user is on CAS Login Page

  Scenario: Test Scenario
    Given test precondition
    When user performs action
    Then result is verified
"""
