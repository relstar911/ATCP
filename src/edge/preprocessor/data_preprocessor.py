from typing import Any, Dict, Optional
import asyncio
import logging
from datetime import datetime

class DataPreprocessor:
    def __init__(self):
        self.processing_queue = asyncio.Queue()
        self.is_processing = False
        self.logger = logging.getLogger(__name__)
        self.processed_count = 0
        self.last_processed = None

    async def preprocess(self, data: Any) -> Dict[str, Any]:
        """
        Vorverarbeitung der eingehenden Daten.

        Args:
            data: Eingangsdaten für die Vorverarbeitung

        Returns:
            Dict mit Status und verarbeiteten Daten oder Fehlermeldung
        """
        try:
            if data is None:
                raise ValueError("Input data cannot be None")

            self.logger.info(f"Preprocessing data batch {self.processed_count + 1}")
            
            # Füge Daten zur Verarbeitungsqueue hinzu
            await self.processing_queue.put(data)
            
            if not self.is_processing:
                await self._process_queue()
            
            self.processed_count += 1
            self.last_processed = datetime.now()
            
            return {
                "status": "success",
                "processed_data": data,
                "timestamp": self.last_processed.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Preprocessing error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _process_queue(self) -> None:
        """
        Verarbeitet Elemente in der Queue.
        """
        self.is_processing = True
        try:
            while not self.processing_queue.empty():
                data = await self.processing_queue.get()
                # Hier könnte später komplexere Vorverarbeitung implementiert werden
                await asyncio.sleep(0.1)  # Simulierte Verarbeitung
                self.processing_queue.task_done()
                
        except Exception as e:
            self.logger.error(f"Queue processing error: {str(e)}", exc_info=True)
        finally:
            self.is_processing = False

    def get_stats(self) -> Dict[str, Any]:
        """
        Liefert Statistiken über die Vorverarbeitung.
        """
        return {
            "processed_count": self.processed_count,
            "last_processed": self.last_processed.isoformat() if self.last_processed else None,
            "queue_size": self.processing_queue.qsize()
        } 