"""
Simple test to verify pytest setup is working correctly
"""

import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.mark.unit
def test_pytest_setup():
    """Test that pytest is configured correctly"""
    assert True


@pytest.mark.unit
def test_python_version():
    """Test that we're using Python 3.11+"""
    assert sys.version_info >= (3, 11)


@pytest.mark.unit
def test_project_structure():
    """Test that project structure exists"""
    project_root = os.path.join(os.path.dirname(__file__), '..')
    
    # Check main directories exist
    assert os.path.exists(os.path.join(project_root, 'app'))
    assert os.path.exists(os.path.join(project_root, 'tests'))
    assert os.path.exists(os.path.join(project_root, 'requirements.txt'))


@pytest.mark.unit
def test_imports():
    """Test that we can import key modules"""
    try:
        import app.main
        import app.models.player
        import app.schemas.player
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import modules: {e}")


@pytest.mark.unit 
def test_dependencies():
    """Test that key dependencies are available"""
    try:
        import fastapi
        import sqlalchemy
        import pydantic
        import pytest
        assert True
    except ImportError as e:
        pytest.fail(f"Missing dependency: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
