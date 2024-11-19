from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

class ValidationStatus(Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"

@dataclass
class ValidationResult:
    status: ValidationStatus
    score: float
    metrics: Dict[str, float]
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None

class ModelValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_queue = asyncio.Queue()
        self.validation_thresholds = {
            "accuracy": 0.95,
            "latency_ms": 100,
            "memory_usage_mb": 1024
        }
    
    async def validate(self, model_data: Dict[str, Any]) -> ValidationResult:
        """
        Führt eine leichtgewichtige Validierung des Modells durch.

        Args:
            model_data: Dict mit Modell-Daten und Metriken

        Returns:
            ValidationResult: Ergebnis der Validierung
        """
        try:
            self.logger.info(f"Starting validation for model: {model_data.get('model_id', 'unknown')}")
            
            # Basis-Validierungsprüfungen
            validation_checks = await asyncio.gather(
                self._validate_model_structure(model_data),
                self._validate_performance_metrics(model_data),
                self._validate_resource_usage(model_data)
            )
            
            # Aggregiere Ergebnisse
            passed_all = all(check['passed'] for check in validation_checks)
            
            # Wenn die Strukturvalidierung fehlschlägt, setze Score auf 0
            if not validation_checks[0]['passed']:
                total_score = 0.0
            else:
                total_score = sum(check['score'] for check in validation_checks) / len(validation_checks)
            
            # Sammle Metriken
            combined_metrics = {}
            errors = []
            warnings = []
            
            for check in validation_checks:
                combined_metrics.update(check.get('metrics', {}))
                errors.extend(check.get('errors', []))
                warnings.extend(check.get('warnings', []))
            
            status = ValidationStatus.PASSED if passed_all else ValidationStatus.FAILED
            
            return ValidationResult(
                status=status,
                score=total_score,
                metrics=combined_metrics,
                errors=errors if errors else None,
                warnings=warnings if warnings else None
            )
            
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}", exc_info=True)
            return ValidationResult(
                status=ValidationStatus.ERROR,
                score=0.0,
                metrics={},
                errors=[str(e)]
            )

    async def _validate_model_structure(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """berprüft die Struktur des Modells."""
        required_fields = ['model_id', 'version', 'parameters']
        errors = []
        warnings = []
        
        for field in required_fields:
            if field not in model_data:
                errors.append(f"Missing required field: {field}")
        
        return {
            'passed': len(errors) == 0,
            'score': 1.0 if len(errors) == 0 else 0.0,
            'metrics': {'structure_score': 1.0 if len(errors) == 0 else 0.0},
            'errors': errors,
            'warnings': warnings
        }

    async def _validate_performance_metrics(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Überprüft die Performance-Metriken des Modells."""
        metrics = model_data.get('metrics', {})
        errors = []
        warnings = []
        
        if 'accuracy' in metrics:
            if metrics['accuracy'] < self.validation_thresholds['accuracy']:
                errors.append(f"Accuracy below threshold: {metrics['accuracy']}")
        else:
            warnings.append("No accuracy metric provided")
            
        return {
            'passed': len(errors) == 0,
            'score': metrics.get('accuracy', 0.0),
            'metrics': {'performance_score': metrics.get('accuracy', 0.0)},
            'errors': errors,
            'warnings': warnings
        }

    async def _validate_resource_usage(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Überprüft die Ressourcennutzung des Modells."""
        resources = model_data.get('resources', {})
        errors = []
        warnings = []
        
        if 'memory_usage_mb' in resources:
            if resources['memory_usage_mb'] > self.validation_thresholds['memory_usage_mb']:
                warnings.append(f"High memory usage: {resources['memory_usage_mb']}MB")
                
        if 'latency_ms' in resources:
            if resources['latency_ms'] > self.validation_thresholds['latency_ms']:
                warnings.append(f"High latency: {resources['latency_ms']}ms")
                
        return {
            'passed': len(errors) == 0,
            'score': 1.0 if len(warnings) == 0 else 0.8,
            'metrics': {'resource_score': 1.0 if len(warnings) == 0 else 0.8},
            'errors': errors,
            'warnings': warnings
        } 