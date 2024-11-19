import pytest
import asyncio
from src.edge.preprocessor.data_preprocessor import DataPreprocessor

@pytest.fixture
def preprocessor():
    return DataPreprocessor()

@pytest.fixture
def sample_data():
    return {
        "input_data": [1, 2, 3, 4, 5],
        "metadata": {
            "type": "numeric",
            "source": "test"
        }
    }

@pytest.mark.asyncio
async def test_preprocess_valid_data(preprocessor, sample_data):
    result = await preprocessor.preprocess(sample_data)
    assert result["status"] == "success"
    assert "processed_data" in result
    assert result["processed_data"] == sample_data

@pytest.mark.asyncio
async def test_preprocess_empty_data(preprocessor):
    result = await preprocessor.preprocess({})
    assert result["status"] == "success"
    assert "processed_data" in result
    assert result["processed_data"] == {}

@pytest.mark.asyncio
async def test_preprocess_none_data(preprocessor):
    result = await preprocessor.preprocess(None)
    assert result["status"] == "error"
    assert "error" in result

@pytest.mark.asyncio
async def test_queue_processing(preprocessor):
    # Test mehrere Datensätze in der Queue
    data_items = [
        {"data": [i]} for i in range(5)
    ]
    
    results = []
    for data in data_items:
        result = await preprocessor.preprocess(data)
        results.append(result)
    
    assert len(results) == 5
    assert all(result["status"] == "success" for result in results)

@pytest.mark.asyncio
async def test_concurrent_processing(preprocessor):
    # Test gleichzeitige Verarbeitung
    data_items = [
        {"data": [i]} for i in range(10)
    ]
    
    tasks = [
        preprocessor.preprocess(data) for data in data_items
    ]
    
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 10
    assert all(result["status"] == "success" for result in results)

@pytest.mark.asyncio
async def test_preprocessor_stats(preprocessor, sample_data):
    # Verarbeite einige Daten
    await preprocessor.preprocess(sample_data)
    await preprocessor.preprocess(sample_data)
    
    # Prüfe Statistiken
    stats = preprocessor.get_stats()
    
    assert stats["processed_count"] == 2
    assert stats["last_processed"] is not None
    assert isinstance(stats["queue_size"], int) 

@pytest.mark.asyncio
async def test_queue_processing_error(preprocessor):
    # Simuliere einen Fehler während der Verarbeitung
    async def failing_process():
        raise Exception("Queue processing error")
    
    # Ersetze die _process_queue Methode temporär
    original_method = preprocessor._process_queue
    preprocessor._process_queue = failing_process
    
    # Versuche Daten zu verarbeiten
    result = await preprocessor.preprocess({"test": "data"})
    
    # Überprüfe, dass der Fehler korrekt behandelt wurde
    assert result["status"] == "error"
    assert "Queue processing error" in result.get("error", "")
    assert preprocessor.is_processing == False
    
    # Stelle original wieder her
    preprocessor._process_queue = original_method