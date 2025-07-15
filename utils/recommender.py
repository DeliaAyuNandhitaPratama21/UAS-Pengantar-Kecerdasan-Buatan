import pandas as pd
import json
import os
import random
import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset dari file CSV
def load_data():
    return pd.read_csv("data/dataset.csv")

# Fungsi utama untuk memberikan rekomendasi parfum berdasarkan input user
def recommend_parfum(df, input_data, top_n=3):
    # Gabungkan fitur kategori menjadi satu string per baris
    df['fitur'] = df['aktivitas'].astype(str) + " " + df['waktu'].astype(str) + " " + df['durasi'].astype(str)
    input_text = f"{input_data['aktivitas']} {input_data['waktu']} {input_data['durasi']}"

    # Ubah teks ke vektor dengan TF-IDF
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(df['fitur'].tolist() + [input_text])

    # Hitung Cosine Similarity antara input user dan data
    cosine_sim = cosine_similarity(vectors[-1], vectors[:-1])

    # Urutkan berdasarkan kemiripan tertinggi
    scores = list(enumerate(cosine_sim[0]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    top_candidates = scores[:20]  # ambil 20 kandidat teratas
    random.shuffle(top_candidates)  # acak agar hasil tidak selalu sama

    selected = []
    used_genders = set()

    # Pilih 3 parfum dengan gender berbeda (jika memungkinkan)
    for idx, _ in top_candidates:
        parfum = df.iloc[idx]
        gender = parfum['gender'].strip().lower()
        if gender not in used_genders:
            selected.append(parfum)
            used_genders.add(gender)
        if len(selected) == top_n:
            break

    # Tambahkan dari kandidat lain jika belum cukup 3
    if len(selected) < top_n:
        for idx, _ in top_candidates:
            parfum = df.iloc[idx]
            if not any(parfum['nama'] == s['nama'] for s in selected):
                selected.append(parfum)
            if len(selected) == top_n:
                break

    return pd.DataFrame(selected)

# Fungsi untuk membaca riwayat rekomendasi dari file
def load_history(path="history/user_history.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

# Fungsi menyimpan riwayat input + hasil rekomendasi
def save_history(data, results, path="history/user_history.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    history = load_history(path)

    data_with_results = data.copy()
    data_with_results["rekomendasi"] = results.to_dict(orient="records")
    data_with_results["timestamp"] = datetime.datetime.now().isoformat()

    history.append(data_with_results)

    with open(path, "w") as f:
        json.dump(history[-10:], f, indent=4)  # simpan 10 riwayat terakhir
