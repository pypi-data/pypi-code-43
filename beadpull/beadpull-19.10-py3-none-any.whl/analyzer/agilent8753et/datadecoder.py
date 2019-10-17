import numpy as np
from typing import Optional


def decodeASCII(data: bytes, n: int, m: int = 3) -> np.ndarray:
    """decode ascii data string to numpy array"""
    output = np.empty([n, m])  # shape is n rows and m columns
    for i, j in enumerate(data.split(b"\n")):
        if i == n:
            break
        output[i] = np.fromstring(j, sep=",")
    return output


def decodeBin(data: bytes, n: int, dtype: str = ">f8") -> np.ndarray:
    """decode ascii data string to numpy array"""
    output = np.empty(2 * n)
    output = np.frombuffer(data, dtype=dtype)
    output = output.reshape(n, 2)
    return output


def decodeHeader(data: Optional[bytes]) -> int:
    """decode bin transaction header"""
    if data is None or data[0:2] != b"#A":
        return 0
    else:
        return np.frombuffer(data[2:4], dtype=">i2")
