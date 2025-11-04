from __future__ import annotations
import numpy as np
from typing import List, Tuple

def ahp_weights_from_pairwise(pairwise: np.ndarray) -> np.ndarray:
    assert pairwise.shape[0] == pairwise.shape[1], "Pairwise matrix must be square"
    gm = np.prod(pairwise, axis=1)**(1.0 / pairwise.shape[0])
    w = gm / np.sum(gm)
    return w

def saw_score(matrix: np.ndarray, types: List[str], weights: np.ndarray) -> np.ndarray:
    X = matrix.astype(float).copy()
    n_alt, n_crit = X.shape
    N = np.zeros_like(X, dtype=float)
    for j in range(n_crit):
        col = X[:, j]
        if np.all(col == col[0]):
            N[:, j] = 1.0
            continue
        if types[j].lower() == "benefit":
            N[:, j] = (col - col.min()) / (col.max() - col.min())
        else:
            N[:, j] = (col.max() - col) / (col.max() - col.min())
    return N @ weights

def topsis_score(matrix: np.ndarray, types: List[str], weights: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    X = matrix.astype(float).copy()
    n_alt, n_crit = X.shape
    denom = np.sqrt((X ** 2).sum(axis=0))
    denom[denom == 0] = 1.0
    R = X / denom
    W = R * weights  
    ideal_pos = np.zeros(n_crit)
    ideal_neg = np.zeros(n_crit)
    for j in range(n_crit):
        if types[j].lower() == "benefit":
            ideal_pos[j] = W[:, j].max()
            ideal_neg[j] = W[:, j].min()
        else:
            ideal_pos[j] = W[:, j].min()
            ideal_neg[j] = W[:, j].max()
    d_pos = np.sqrt(((W - ideal_pos) ** 2).sum(axis=1))
    d_neg = np.sqrt(((W - ideal_neg) ** 2).sum(axis=1))
    scores = d_neg / (d_pos + d_neg + 1e-12)
    return scores, ideal_pos, ideal_neg