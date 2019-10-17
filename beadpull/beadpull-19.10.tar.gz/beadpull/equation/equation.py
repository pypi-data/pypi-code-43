import numpy as np


def deltaF_Efield(
    data: np.ndarray, kE: float = 1, f0: float = 2856e6
) -> np.ndarray:
    """compute E field from frequency deviation"""
    data = np.real(data)
    df = np.abs(f0 - data)
    return np.sqrt(df / (2 * np.pi * kE * f0 ** 2))


def deltaF_Hfield(
    data: np.ndarray, kH: float = 1, f0: float = 2856e6, metal: bool = True
) -> np.ndarray:
    """compute H field from frequency deviation"""
    data = np.real(data)
    df = np.abs(data - f0)
    # if not metal:
    #     df = -1 * df
    return np.sqrt(df / (2 * np.pi * kH * f0 ** 2))


def deltaS_Efield(
    data: np.ndarray, kS: float = 1, f0: float = 2856e6
) -> np.ndarray:
    """compute E field from reflection deviation"""
    data = np.sqrt(np.abs(data - data[0]) / (2 * np.pi * kS * f0 ** 2))
    return data


def deltaS_EfieldPhase(data: np.ndarray,) -> np.ndarray:
    """compute E field phase from reflection deviation"""
    data = np.real(data)
    return (data - data[0]) / 2


def deltaPhi_Efield(
    data: np.ndarray, kE: float = 1, Ql: int = 1000, f0: float = 2856e6
) -> np.ndarray:
    """compute E field from phase deviation"""
    data = np.real(data)
    dphi = np.abs(data[0] - data)
    return np.sqrt(dphi / (4 * np.pi * kE * f0 * Ql))


def deltaPhi_Hfield(
    data: np.ndarray,
    kH: float = 1,
    Ql: int = 1000,
    f0: float = 2856e6,
    metal: bool = True,
) -> np.ndarray:
    """compute H field from phase deviation"""
    data = np.real(data)
    dphi = np.abs(data - data[0])
    # if not metal:
    #     dphi = -1 * dphi
    return np.sqrt(dphi / (4 * np.pi * kH * f0 * Ql))


def convertFreq(freq, unit):
    """convert frequency to current units"""
    if unit.upper() == "KHZ":
        freq = freq / 1e3
    elif unit.upper() == "MHZ":
        freq = freq / 1e6
    elif unit.upper() == "GHZ":
        freq = freq / 1e9
    return freq


def processFieldData(coords, data, field_metadata):
    if len(coords) == 0:
        return coords, data
    if field_metadata["field part"] == "electric":
        if field_metadata["strategy"] == "direct":
            data = deltaF_Efield(
                data=data,
                kE=field_metadata["electric formfactor"],
                f0=field_metadata["central frequency"],
            )
        else:
            if field_metadata["measure type"] == "reflection":
                data = deltaS_Efield(
                    data=data,
                    kS=field_metadata[
                        "formfactor for inderect reflection measurements"
                    ],
                    f0=field_metadata["central frequency"],
                )
            else:
                data = deltaPhi_Efield(
                    data=data,
                    kE=field_metadata["electric formfactor"],
                    Ql=field_metadata["Qload"],
                    f0=field_metadata["central frequency"],
                )
    elif field_metadata["field part"] == "magnetic":
        if field_metadata["strategy"] == "direct":
            data = deltaF_Hfield(
                data=data,
                kH=field_metadata["magnetic formfactor"],
                f0=field_metadata["central frequency"],
                metal=field_metadata["bead material"] == "metal",
            )
        else:
            if field_metadata["measure type"] == "reflection":
                data = data
            else:
                data = deltaPhi_Hfield(
                    data=data,
                    kH=field_metadata["electric formfactor"],
                    Ql=field_metadata["Qload"],
                    f0=field_metadata["central frequency"],
                    metal=field_metadata["bead material"] == "metal",
                )
    else:
        data = deltaS_EfieldPhase(data=data)
    return coords, data


def fieldRemoveDrift(coord, data, drift_first, drift_last):
    """remove data drift"""
    n1 = np.where(coord <= drift_first)[0]
    n2 = np.where(coord >= drift_last)[0]
    if len(n1) == 0 or len(n2) == 0:
        return coord, data
    x1 = np.max(coord[n1])
    x2 = np.min(coord[n2])
    y1 = np.mean(data[n1])
    y2 = np.mean(data[n2])
    coord = np.delete(np.delete(coord, n2), n1)
    coord = np.insert(coord, 0, x1)
    coord = np.append(coord, x2)
    data = np.delete(np.delete(data, n2), n1)
    data = np.insert(data, 0, y1)
    data = np.append(data, y2)
    data = data - ((y1 - y2) / (x1 - x2)) * (coord - x1)
    return coord, data
