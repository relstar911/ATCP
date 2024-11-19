import asyncio
import functools
from typing import Callable, Any
import pytest
import signal

def stable_test(timeout: int = 5):
    """
    Decorator für stabile async P2P Tests mit forciertem Timeout.
    """
    def decorator(test_func: Callable) -> Callable:
        @functools.wraps(test_func)
        async def wrapper(*args, **kwargs) -> Any:
            # Signal-Handler für harte Timeouts
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Test forcefully terminated after {timeout} seconds")
            
            # Setup signal
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
            
            try:
                # Run test with asyncio timeout
                async with asyncio.timeout(timeout):
                    result = await test_func(*args, **kwargs)
                    return result
            except asyncio.TimeoutError:
                pytest.fail(f"Test timed out after {timeout} seconds")
            except Exception as e:
                pytest.fail(f"Test failed with error: {str(e)}")
            finally:
                # Cancel signal
                signal.alarm(0)
                # Aggressive cleanup
                tasks = [t for t in asyncio.all_tasks() 
                        if t is not asyncio.current_task()]
                for task in tasks:
                    task.cancel()
                    try:
                        await asyncio.wait_for(task, 0.1)
                    except (asyncio.CancelledError, asyncio.TimeoutError):
                        pass
        return wrapper
    return decorator 