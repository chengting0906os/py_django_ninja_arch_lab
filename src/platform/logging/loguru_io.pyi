from typing import Any, Callable, Optional, TypeVar, overload

from typing import ParamSpec

from src.platform.logging.loguru_io_config import GeneratorMethod

_P = ParamSpec('_P')
_T = TypeVar('_T')

class LoguruIO:
    def __init__(self, custom_logger: Any, reraise: bool = ...) -> None: ...
    def log_args_kwargs_content(
        self, *args: Any, yield_method: Optional[GeneratorMethod] = ..., **kwargs: Any
    ) -> None: ...
    def log_return_content(
        self, return_value: Any, yield_method: Optional[GeneratorMethod] = ...
    ) -> None: ...
    def mask_sensitive(self, data: Any) -> Any: ...
    def __call__(self, func: Callable[_P, _T]) -> Callable[_P, _T]: ...

    extra: dict[str, Any]
    depth: int
    reraise: bool

class Logger:
    base: Any

    @staticmethod
    @overload
    def io(func: Callable[_P, _T]) -> Callable[_P, _T]: ...
    @staticmethod
    @overload
    def io(
        func: None = ..., *, reraise: bool = ...
    ) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]: ...
