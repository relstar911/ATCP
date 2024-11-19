import pytest
from src.edge.validator.model_validator import ModelValidator, ValidationStatus

@pytest.fixture
def valid_model_data():
    return {
        'model_id': 'test_model_1',
        'version': '1.0.0',
        'parameters': {'param1': 0.1, 'param2': 0.2},
        'metrics': {
            'accuracy': 0.98
        },
        'resources': {
            'memory_usage_mb': 512,
            'latency_ms': 50
        }
    }

@pytest.fixture
def invalid_model_data():
    return {
        'model_id': 'test_model_2',
        'metrics': {
            'accuracy': 0.85  # Below threshold
        },
        'resources': {
            'memory_usage_mb': 2048,  # Above threshold
            'latency_ms': 150  # Above threshold
        }
    }

@pytest.mark.asyncio
async def test_validate_valid_model(valid_model_data):
    validator = ModelValidator()
    result = await validator.validate(valid_model_data)
    
    assert result.status == ValidationStatus.PASSED
    assert result.score >= 0.95
    assert result.errors is None
    assert isinstance(result.metrics, dict)

@pytest.mark.asyncio
async def test_validate_invalid_model(invalid_model_data):
    validator = ModelValidator()
    result = await validator.validate(invalid_model_data)
    
    assert result.status == ValidationStatus.FAILED
    assert result.score < 0.95
    assert result.errors is not None
    assert len(result.errors) > 0
    assert isinstance(result.metrics, dict)

@pytest.mark.asyncio
async def test_validate_empty_model():
    validator = ModelValidator()
    result = await validator.validate({})
    
    assert result.status == ValidationStatus.FAILED
    assert result.score == 0.0
    assert result.errors is not None
    assert len(result.errors) > 0 