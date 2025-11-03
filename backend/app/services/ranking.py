from typing import List, Dict
import numpy as np

def mmr_select(
    query_emb: np.ndarray,
    docs: List[Dict],
    k: int = 8,
    lamb: float = 0.7,
) -> List[Dict]:
    if not docs:
        return []
    C = np.vstack([np.array(d["embedding"], dtype=np.float32) for d in docs])
    q = np.asarray(query_emb, dtype=np.float32)

    def _cos(a, b):
        return (a @ b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)

    rel = C @ q / (np.linalg.norm(C, axis=1) * np.linalg.norm(q) + 1e-8)  # (N,)
    selected, remaining = [], list(range(len(docs)))

    while remaining and len(selected) < k:
        if not selected:
            i = int(np.argmax(rel[remaining]))
            selected.append(remaining.pop(i))
            continue
        sel_mat = C[selected]  # (m, D)
        sim_to_S = (C[remaining] @ sel_mat.T) / (
            np.linalg.norm(C[remaining], axis=1, keepdims=True) *
            np.linalg.norm(sel_mat, axis=1, keepdims=True).T + 1e-8
        )
        max_sim_S = sim_to_S.max(axis=1)
        mmr = lamb * rel[remaining] - (1 - lamb) * max_sim_S
        i = int(np.argmax(mmr))
        selected.append(remaining.pop(i))

    return [docs[i] for i in selected]