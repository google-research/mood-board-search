from typing import Any, TypeVar
from typing_extensions import Protocol


try:
    from numpy.typing import NDArray
except ImportError:
    # define our own NDArray type
    DType = TypeVar('DType', covariant=True)
    class _NDArray(Protocol[DType]):
        def __getitem__(self, key: Any) -> Any: ...
        def __getattribute__(self, name: str) -> Any: ...

    NDArray = _NDArray  # type: ignore


try:
    from numpy.typing import ArrayLike
except ImportError:
    ArrayLike = Any  # type: ignore

__all__ = ['NDArray', 'ArrayLike']
