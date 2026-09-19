from src import LocalEmbedder, compute_similarity

pairs = [
    (
        "Python là một ngôn ngữ lập trình.",
        "Python được sử dụng để phát triển phần mềm.",
    ),
    (
        "Học máy giúp máy tính học từ dữ liệu.",
        "Machine learning sử dụng dữ liệu để huấn luyện mô hình.",
    ),
    (
        "Trời hôm nay có mưa.",
        "Cơ sở dữ liệu vector lưu trữ embedding.",
    ),

    ("Sinh viên có thể mượn sách tại thư viện.",
     "Người học được phép mượn tài liệu.",
     ),

    ("Mèo là động vật có vú.",
     "Máy tính sử dụng bộ xử lý trung tâm.",
    ),
]

embedder = LocalEmbedder()

for index, (sentence_a, sentence_b) in enumerate(pairs, start=1):
    score = compute_similarity(embedder(sentence_a), embedder(sentence_b))
    level = "cao" if score >= 0.5 else "thấp"
    print(f"Cặp {index}: {score:.4f} — {level}")