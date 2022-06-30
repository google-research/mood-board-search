# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
