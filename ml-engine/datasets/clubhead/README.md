# Clubhead dataset

Panduan lengkap (langkah demi langkah): **[docs/clubhead-label-and-train.md](../../../docs/clubhead-label-and-train.md)**

Ringkas:

1. Box **hanya clubhead** di `to_label/` (Label Studio atau Roboflow)
2. Import `.txt` → `split_club_labels.py` → `train_clubhead.py --epochs 100`
3. Restart API; val mAP50 ≳ 0.60 sebelum overlay swing bisa dipercaya

Jangan train dari `_bootstrap_bak/` atau `bootstrap_club_labels.py`.
