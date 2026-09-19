# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Dương Dương
**Nhóm:** G20
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Khi hai đoạn văn bản có độ tương tự cosine cao, các vector biểu diễn chúng hướng gần giống nhau. Điều này thường có nghĩa là hai đoạn văn có nội dung, chủ đề hoặc ý nghĩa tương tự nhau, dù chúng không nhất thiết sử dụng cùng từ ngữ.

**Ví dụ có độ tương tự CAO:**
- Câu A: “Sinh viên có thể mượn sách tại thư viện.”
- Câu B: “Thư viện cho phép sinh viên mượn tài liệu.”
- Tại sao tương đồng: Hai câu dùng cách diễn đạt khác nhau nhưng cùng nói về việc sinh viên mượn tài liệu tại thư viện.

**Ví dụ có độ tương tự THẤP:**
- Câu A: “Sinh viên có thể mượn sách tại thư viện.”
- Câu B: “Hôm nay trời mưa rất lớn.”
- Tại sao khác: Hai câu nói về những chủ đề hoàn toàn khác nhau nên vector của chúng có hướng khác nhau và độ tương tự cosine thấp.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity thường được ưu tiên hơn khoảng cách Euclid đối với text embeddings vì cosine tập trung vào mẫu đặc trưng và ý nghĩa của văn bản, thay vì độ lớn tuyệt đối của vector. Hai câu sử dụng từ ngữ khác nhau vẫn có thể chung ý nghĩa, khoảng cách Euclid xem chúng là khá xa trong khi cosine vẫn nhận ra rằng chúng có hướng tương tự.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* (10000-50)/(500-50)

> *Đáp án:* 23

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Độ chồng chéo tăng 100, số lượng chunk tăng thêm 2. Nếu một câu hoặc một ý quan trọng nằm đúng vị trí bị chia, phần nội dung chồng chéo sẽ giúp cả hai chunk vẫn chứa đủ thông tin liên quan.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng biểu thức chính quy `(?<=[.!?]) +|(?<=\.)\r?\n` để nhận biết ranh giới câu sau dấu chấm, dấu chấm than, dấu hỏi hoặc dấu chấm ở cuối dòng. Sau khi tách, các câu được gom theo `max_sentences_per_chunk`, nối lại bằng một khoảng trắng và loại bỏ khoảng trắng thừa. Với chuỗi rỗng hoặc chỉ gồm khoảng trắng, hàm trả về danh sách rỗng; giá trị số câu tối đa cũng luôn được giới hạn tối thiểu là 1.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán lần lượt thử các dấu phân cách theo độ ưu tiên `"\n\n"`, `"\n"`, `". "`, `" "`, rồi ghép các phần liên tiếp sao cho mỗi chunk không vượt quá `chunk_size`; phần nào vẫn quá dài sẽ được xử lý đệ quy bằng dấu phân cách tiếp theo. Trường hợp cơ sở là đoạn văn đã không vượt kích thước thì trả về ngay sau khi `strip`; nếu hết dấu phân cách hoặc gặp chuỗi phân cách rỗng, văn bản được cắt cứng theo số ký tự. Chuỗi rỗng hoặc chỉ có khoảng trắng trả về danh sách rỗng.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> `add_documents` chuẩn hóa mỗi tài liệu thành một record gồm mã nội bộ duy nhất, nội dung, metadata có thêm `doc_id` và vector embedding. Record được thêm vào collection ChromaDB nếu thư viện khả dụng, nếu không sẽ lưu trong danh sách in-memory. Khi tìm kiếm, câu truy vấn được embedding một lần, tính tích vô hướng với từng vector tài liệu, sau đó sắp xếp điểm giảm dần và lấy tối đa `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc metadata trước rồi mới tính độ tương tự, nhờ đó chỉ các record thỏa mãn toàn bộ cặp khóa–giá trị mới tham gia xếp hạng; nếu không truyền bộ lọc thì hàm dùng lại `search`. `delete_document` tìm tất cả chunk có `metadata["doc_id"]` trùng với mã tài liệu và xóa chúng khỏi ChromaDB hoặc danh sách in-memory. Hàm trả về `True` khi thực sự có dữ liệu bị xóa và `False` nếu không tìm thấy tài liệu.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Hàm `answer` truy xuất tối đa `top_k` chunk liên quan nhất, lấy trường `content` và nối chúng bằng hai ký tự xuống dòng để tạo phần ngữ cảnh. Prompt gồm chỉ dẫn chỉ được trả lời dựa trên ngữ cảnh, yêu cầu nói không biết nếu thiếu thông tin, tiếp theo là các phần `Context`, `Question` và `Answer`. Prompt hoàn chỉnh được truyền cho `llm_fn`, và kết quả của mô hình được trả về trực tiếp.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================================================== test session starts ==============================================================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\PC\AppData\Local\Programs\Python\Python314\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\PC\K4-L3A-DuongDuong-2A202602498
plugins: anyio-4.15.1, mock-3.15.1
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                                                      [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                                                               [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                                                        [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                                                         [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                                                              [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED                                              [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                                                    [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                                                     [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                                                   [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                                                     [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                                                     [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                                                [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                                                            [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                                                      [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED                                             [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                                                 [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED                                           [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                                                 [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                                                     [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                                                       [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                                                         [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                                                               [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                                                    [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                                                      [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED                                          [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                                                       [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                                                [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                                                               [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                                                          [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                                                      [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                                                 [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                                                     [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                                                           [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                                                     [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED                                  [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                                                [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED                                               [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED                                   [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED                                              [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED                                       [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED                             [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED                                 [100%]

============================================================== 42 passed in 0.09s ===============================================================
```

**Số lượng bài test vượt qua (pass):** 42/42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Các điểm thực tế được tính bằng `LocalEmbedder` (`paraphrase-multilingual-MiniLM-L12-v2`) và `compute_similarity`; tôi quy ước điểm từ `0.5` trở lên là tương tự cao.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Python là một ngôn ngữ lập trình." | "Python được sử dụng để phát triển phần mềm." | cao | 0.8562 | Có |
| 2 | "Học máy giúp máy tính học từ dữ liệu." | "Machine learning sử dụng dữ liệu để huấn luyện mô hình." | cao | 0.6019 | Có |
| 3 | "Trời hôm nay có mưa." | "Cơ sở dữ liệu vector lưu trữ embedding." | thấp | 0.0363 | Có |
| 4 | "Sinh viên có thể mượn sách tại thư viện." | "Người học được phép mượn tài liệu." | cao | 0.7786 | Có |
| 5 | "Mèo là động vật có vú." | "Máy tính sử dụng bộ xử lý trung tâm." | thấp | 0.1213 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất là cặp câu tiếng Việt và tiếng Anh về học máy vẫn có độ tương tự cao dù chúng gần như không có từ ngữ giống nhau. Điều này cho thấy embeddings không chỉ so sánh từ khóa bề mặt mà còn biểu diễn ý nghĩa của câu trong không gian vector, thậm chí có thể nhận biết nội dung tương đồng giữa nhiều ngôn ngữ.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

Tôi chạy benchmark bằng chiến lược cá nhân `SectionHeadingChunker(max_chunk_size=500)` với `RecursiveChunker` làm phương án chia nhỏ dự phòng và dùng `LocalEmbedder`. Riêng câu hỏi thư viện áp dụng tiền lọc `metadata_filter={"audience": "student"}` như thiết kế chung của nhóm.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Hệ thống đăng ký học phần VinUniversity tự động kiểm tra điều kiện gì và thời hạn thêm môn học là khi nào? | Phần giới thiệu chính sách khiếu nại điểm và phúc khảo bài thi. | 0.6542 | Không | Không đủ ngữ cảnh trong top-3 để xác định đồng thời điều kiện tiên quyết và thời hạn thêm môn; đáp án chuẩn là hệ thống kiểm tra điều kiện tiên quyết và hạn thêm môn là trước ngày làm việc thứ 10. |
| 2 | Sinh viên đại học được mượn tối đa bao nhiêu tài liệu thư viện và trong thời hạn bao lâu? | Điều 2 của quy định thư viện: tối đa 3 tài liệu trong 2 tuần, được gia hạn một lần thêm 1 tuần. | 0.7503 | Có | Sinh viên đại học được mượn tối đa 3 tài liệu trong 14 ngày và có thể gia hạn một lần thêm 7 ngày. |
| 3 | Các mức học bổng tài năng của VinUniversity gồm những loại nào và mức hỗ trợ cao nhất là gì? | Mục 3 về các học bổng khuyến khích đặc biệt được cộng dồn, như WIT và Vinschool–VinUni. | 0.7360 | Không | Chunk đúng ở top-2 cho biết bốn mức gồm President's Excellence, Provost's Merit, Dean's Distinction và Discipline's Honor; cao nhất là 100% học phí và sinh hoạt phí. |
| 4 | Hỗ trợ tài chính Need-based Financial Aid có thể hỗ trợ tối đa bao nhiêu phần trăm học phí? | Phần giới thiệu mục tiêu của chương trình hỗ trợ tài chính theo nhu cầu. | 0.7636 | Có | Chunk đúng ở top-2 cho biết mức hỗ trợ có thể lên tới 100% học phí và tổng hỗ trợ sau khi kết hợp học bổng không vượt quá 100%. |
| 5 | Khiếu nại điểm thi áp dụng cho loại điểm nào và bước đầu tiên sinh viên cần làm là gì? | Nội dung bước nộp Grade Appeal Form và bằng chứng cho đơn vị AQA. | 0.7127 | Có | Các chunk top-2 và top-3 cho biết quy trình áp dụng với điểm tổng kết môn học; bước đầu tiên là gửi email trao đổi trực tiếp với giảng viên phụ trách. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Qua phần so sánh của nhóm, tôi học được rằng `RecursiveChunker` giữ ranh giới đoạn và câu tốt hơn cách cắt cố định, còn metadata pre-filtering có thể quyết định độ chính xác khi hai tài liệu có nội dung gần giống nhưng dành cho đối tượng khác nhau. Thử nghiệm câu hỏi thư viện cho thấy lọc `audience: student` giúp loại bỏ quy định dành cho giảng viên trước khi xếp hạng vector. Tôi cũng nhận ra chiến lược theo tiêu đề cần gắn thêm `section_title` vào metadata để các truy vấn chứa nhiều điều kiện tìm đúng section ổn định hơn.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5/ 5 |
| Hướng tiếp cận của tôi (My Approach) | 10/ 10 |
| Hoàn thiện code (Core Implementation — tests) | 30/ 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 8 / 10 |
| **Tổng phần cá nhân** | **58 / 60** |
