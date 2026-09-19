# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** L3A - Nhóm G20
**Thành viên:** Chu Văn Nhân - Nguyễn Khắc Quang - Dương Dương
**Ngày:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

### Bảng Phân Công Công Việc Nhóm (Dành cho nhóm 3 thành viên)

| STT | Thành viên | Vai trò / Mảng việc phụ trách | Nội dung công việc chi tiết & Chiến lược Benchmark |
|:---:|:---:|---|---|
| 1 | **Chu Văn Nhân** | **Report, Failure Analysis & Demo** | Gom kết quả chạy benchmark của 2 bạn kia. Phân tích A/B Testing (lọc `audience: student`), tìm ra 1 failure case và lo báo cáo `REPORT_NHOM.md`. Chạy benchmark trên chiến lược **FixedSizeChunker**. |
| 2 | **Nguyễn Khắc Quang** | **Data Collection, Metadata & Benchmark Queries** | Crawl 5-10 URLs, làm sạch file `.md`, điền đủ `sources.csv` và kiểm tra metadata `audience`. Viết 5 câu hỏi benchmark + đáp án chuẩn (có câu bắt buộc dùng filter `audience: student`). Chạy benchmark trên chiến lược **RecursiveChunker**. |
| 3 | **Dương Dương** | **Chunking Strategy & Baseline** | Chạy baseline so sánh 3 thuật toán cơ bản. Tự code thêm chiến lược chia theo tiêu đề (**HeadingChunker** / `SectionHeadingChunker`) và dùng nó làm chiến lược để chạy benchmark. |

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Dịch vụ & Quy định Đại học (University Services & Academic Regulations — K4-L3A)

**Tại sao nhóm chọn chủ đề này?**
> Nhóm chọn chủ đề Dịch vụ & Quy định Đại học (tập trung vào các quy chế học vụ, chính sách học phí, học bổng tuyển sinh VinUniversity, dịch vụ thư viện và thủ tục phúc khảo điểm) vì đây là miền dữ liệu thực tế, có cấu trúc điều khoản rõ ràng và tính phân cấp cao giữa các nhóm đối tượng thụ hưởng khác nhau (sinh viên, giảng viên). Việc xây dựng trợ lý hỏi đáp (RAG Agent) trên miền dữ liệu này đòi hỏi độ chính xác tuyệt đối, tránh hiện tượng nhầm lẫn giữa quy định của sinh viên và giảng viên, giúp nhóm kiểm chứng sâu sắc vai trò của việc lọc metadata và chiến lược chia nhỏ văn bản.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|--------------------|----------------------|:--------:|-----------------|
| 1 | `course-registration.md` (Quy trình Đăng ký Học phần và Môn Tiên quyết) | `https://registrar.vinuni.edu.vn/academics/class-schedule-course-registration/` | 2026-09-19 / 2026.3 | 2,513 | `audience: student`, `department: academic-affairs`, `category: academic-regulations` |
| 2 | `library-student.md` (Quy định Thư viện dành cho Sinh viên Đại học) | `https://library.vinuni.edu.vn/` | 2026-09-19 / 2026.2 | 2,389 | `audience: student`, `department: library`, `category: facilities` |
| 3 | `library-faculty.md` (Quy định Thư viện dành cho Giảng viên & Sau Đại học) | `https://library.vinuni.edu.vn/` | 2026-09-19 / 2026.2 | 1,933 | `audience: faculty`, `department: library`, `category: facilities` |
| 4 | `tuition-waiver.md` (Chính sách Hỗ trợ Tài chính Need-based Financial Aid) | `https://admissions.vinuni.edu.vn/scholarship-and-financial-aid/undergraduate-programs/financial-aids/` | 2026-09-19 / 2026.3 | 2,622 | `audience: student`, `department: finance`, `category: financial-aid` |
| 5 | `merit-scholarship.md` (Chính sách Học bổng Đại học VinUniversity) | `https://admissions.vinuni.edu.vn/scholarship-and-financial-aid/undergraduate-programs/scholarships/` | 2026-09-19 / 2026.4 | 3,149 | `audience: student`, `department: student-affairs`, `category: scholarship` |
| 6 | `exam-re-evaluation.md` (Quy trình Khiếu nại Điểm và Phúc khảo Bài thi) | `https://registrar.vinuni.edu.vn/forms-petitions/` | 2026-09-19 / 2026.2 | 2,685 | `audience: student`, `department: examination`, `category: academic-regulations` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.
- [x] Đã có file `data/university/sources.csv` khớp 1-1 với 6 tài liệu trong thư mục.
- [x] Phân loại `audience` đa dạng (`student`, `faculty`), đáp ứng trọn vẹn ràng buộc của biến thể K4-L3A.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|:----:|---------------|--------------------------------------------|
| `doc_id` | string | `merit-scholarship` | Định danh tài liệu gốc; bắt buộc cho việc truy vết nguồn và hàm `delete_document`. |
| `audience` | string | `student` / `faculty` | **Cực kỳ quan trọng**: Ngăn ngừa truy xuất nhầm quy chế của giảng viên khi sinh viên tra cứu và ngược lại. |
| `department` | string | `student-affairs`, `library` | Cho phép lọc theo đơn vị quản lý chuyên môn, tăng độ chính xác khi tìm kiếm nghiệp vụ chuyên biệt. |
| `category` | string | `scholarship`, `facilities` | Nhóm các tài liệu theo chuyên đề học vụ, hỗ trợ phân loại phân cấp. |
| `source_url` | string | `https://admissions.vinuni.edu.vn/...` | Minh bạch nguồn dữ liệu, phục vụ tiêu chí trích dẫn nguồn (Source Traceability). |
| `retrieved_at` | string | `2026-09-19` | Kiểm soát độ mới và thời hiệu áp dụng của quy định văn bản. |
| `document_version` | string | `2026.4` | Truy vết phiên bản sửa đổi của chính sách học vụ. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Nhóm chạy `ChunkingStrategyComparator().compare()` trên tài liệu trọng tâm `merit-scholarship.md` và tài liệu đối sánh `course-registration.md` với `chunk_size=200`:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|-----------------------|:--------------:|:-----------------:|--------------------------|
| **merit-scholarship.md** | FixedSizeChunker (`fixed_size`) | 16 | 194.9 ký tự | Kém: Cắt cơ học chia nhỏ giữa câu hoặc giữa tên loại học bổng và mức tài trợ. |
| | SentenceChunker (`by_sentences`) | 12 | 233.6 ký tự | Trung bình: Giữ trọn vẹn từng câu đơn, nhưng tách rời tiêu đề mục với nội dung điều kiện. |
| | RecursiveChunker (`recursive`) | 21 | 133.0 ký tự | Khá: Tôn trọng dấu ngắt dòng và đoạn văn, tuy nhiên một số danh sách gạch đầu dòng bị tách mảnh ngắn. |
| **course-registration.md** | FixedSizeChunker (`fixed_size`) | 8 | 194.8 ký tự | Kém: Điều khoản tiên quyết bị cắt đôi ở giữa điều kiện điểm chữ D. |
| | SentenceChunker (`by_sentences`) | 5 | 282.4 ký tự | Khá: Giữ được cấu trúc câu hoàn chỉnh về điều kiện 12-22 tín chỉ. |
| | RecursiveChunker (`recursive`) | 10 | 140.2 ký tự | Tốt: Cắt mạch lạc theo từng đề mục Điều 1, Điều 2, Điều 3. |

### Chiến lược của từng thành viên

**Thành viên 1 — Chu Văn Nhân (Vai trò: Report, Failure Analysis & Demo)**
- **Loại chiến lược:** `FixedSizeChunker` (`chunk_size=300, overlap=50`)
- **Mô tả & lý do chọn cho chủ đề này:** Chiến lược cắt kích thước cố định với cơ chế cửa sổ trượt (sliding window). Ưu điểm là thời gian xử lý nhanh, kích thước chunk đồng đều tối ưu cho bộ nhớ nhúng vector, và độ chồng chéo 50 ký tự giúp giảm bớt rủi ro xé rách thông tin ở ranh giới cắt. Nhược điểm là thiếu hiểu biết về ngữ cảnh cấu trúc văn bản, dễ làm đứt đoạn câu và logic điều khoản.

**Thành viên 2 — Nguyễn Khắc Quang (Vai trò: Data Collection, Metadata & Benchmark Queries)**
- **Loại chiến lược:** `RecursiveChunker` (`chunk_size=300`)
- **Mô tả & lý do chọn:** Áp dụng thuật toán chia đệ quy ưu tiên từ ranh giới lớn đến nhỏ `["\n\n", "\n", ". ", " ", ""]`. Chiến lược này phù hợp với văn bản chính sách nhiều tầng mục, giữ nguyên các đoạn văn bản có nghĩa hoàn chỉnh trước khi hạ bậc xuống cấp độ câu, đồng thời có cơ chế gom (merge) các mảnh nhỏ liền kề để hạn chế chunk vụn.

**Thành viên 3 — Dương Dương (Vai trò: Chunking Strategy & Baseline)**
- **Loại chiến lược:** Custom `SectionHeadingChunker` / `HeadingChunker` (`max_chunk_size=500`)
- **Mô tả & lý do chọn:** Thiết kế tùy biến dành riêng cho văn bản pháp quy đại học (đáp ứng yêu cầu bắt buộc của biến thể K4-L3A). Chiến lược nhận diện các tiêu đề `## Heading` hoặc `## Điều x` để tạo thành các khối tri thức độc lập. Nếu một section dài quá `max_chunk_size`, nó sẽ tự động đệ quy chia nhỏ nhưng vẫn giữ tính mạch lạc của điều khoản.
- **Code snippet:**
```python
import re
from src.chunking import RecursiveChunker

class SectionHeadingChunker:
    """Chiến lược chunking theo cấu trúc tiêu đề mục (Heading/Section) cho quy định đại học."""
    def __init__(self, max_chunk_size: int = 500):
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text.strip():
            return []
        # Tách theo các tiêu đề mục markdown ##
        sections = re.split(r'(?=\n##\s+)', text.strip())
        chunks = []
        for sec in sections:
            sec = sec.strip()
            if not sec:
                continue
            if len(sec) <= self.max_chunk_size:
                chunks.append(sec)
            else:
                # Đệ quy chia nhỏ các section dài
                sub_chunks = RecursiveChunker(chunk_size=self.max_chunk_size).chunk(sec)
                chunks.extend(sub_chunks)
        return chunks
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Vai trò phụ trách | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|------------|-------------------|-----------------------|:--------------------:|-----------|----------|
| **Chu Văn Nhân** | Report, Failure Analysis & Demo | `FixedSizeChunker` (300, 50) | 6 / 10 | Kích thước đồng nhất, xử lý nhanh, không sợ chunk quá khổ. | Cắt ngang câu tùy tiện, làm đứt đoạn logic điều kiện học bổng. |
| **Nguyễn Khắc Quang** | Data Collection & Benchmark Queries | `RecursiveChunker` (300) | 8 / 10 | Tôn trọng ranh giới đoạn văn và câu, ngữ cảnh tự nhiên. | Có thể tách tiêu đề mục khỏi danh sách điều kiện nếu đoạn dài. |
| **Dương Dương** | Chunking Strategy & Baseline | `SectionHeadingChunker` (500) | 10 / 10 | Giữ trọn vẹn ngữ cảnh của từng điều mục/chính sách trong 1 chunk. | Kích thước chunk không đồng đều theo độ dài heading. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **`SectionHeadingChunker` (kết hợp Recursive fallback)** là chiến lược vượt trội nhất cho chủ đề quy định và dịch vụ đại học. Bản thân các văn bản quy chế, chính sách học bổng (như tài liệu `merit-scholarship.md`) vốn đã được biên soạn theo cấu trúc điều khoản logic chặt chẽ (Ví dụ: Mục 2 chứa trọn vẹn 4 hạng mục học bổng tài năng, Mục 5 chứa đủ 3 tiêu chí duy trì học bổng). Việc gom toàn bộ một section thành một chunk đảm bảo LLM nhận được đầy đủ ngữ cảnh (từ tên học bổng, tỷ lệ % hỗ trợ đến điều kiện tiên quyết đi kèm) mà không bị phân mảnh thành nhiều chunk rời rạc.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-----------------|---------------------------------|---------------------------|
| 1 | Hệ thống đăng ký học phần VinUniversity tự động kiểm tra điều kiện gì và thời hạn thêm môn học (add course) là khi nào? | Hệ thống tự động kiểm tra điều kiện tiên quyết (Prerequisites); thời hạn thêm môn học muộn nhất là trước ngày làm việc thứ 10 của học kỳ chính thức. | `course-registration` (Mục 2 & 3) |
| 2 | Sinh viên đại học (undergraduate) được mượn tối đa bao nhiêu tài liệu thư viện và trong thời hạn bao lâu? *(Cần lọc `audience: student`)* | Sinh viên đại học được mượn tối đa 3 tài liệu trong thời hạn 2 tuần (14 ngày), được phép gia hạn 1 lần thêm 1 tuần (7 ngày). | `library-student` (Điều 2) |
| 3 | Các mức học bổng tài năng (Merit-based Scholarships) của VinUniversity gồm những loại nào và mức hỗ trợ cao nhất là gì? | Gồm 4 mức: President's Excellence (100% học phí và sinh hoạt phí), Provost's Merit (100%), Dean's Distinction (80-90%), và Discipline's Honor (50-70%). | `merit-scholarship` (Mục 2) |
| 4 | Chương trình Hỗ trợ tài chính Need-based Financial Aid của VinUniversity có thể hỗ trợ tối đa bao nhiêu phần trăm học phí? | Hỗ trợ tài chính có thể lên tới 100% học phí và được kết hợp cùng học bổng tài năng (tổng không quá 100% học phí). | `tuition-waiver` (Mục 2) |
| 5 | Quy trình khiếu nại điểm thi (Grade Appeal) áp dụng cho loại điểm nào và bước đầu tiên sinh viên cần làm là gì? | Áp dụng đối với điểm tổng kết môn học chính thức (Final Course Grades); bước đầu tiên sinh viên phải gửi email trao đổi trực tiếp với Giảng viên phụ trách môn học. | `exam-re-evaluation` (Mục 1 & 2) |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|---------------------------------|:-------------------------------:|---------|
| 1 | Đăng ký học phần và điều kiện tiên quyết | `SectionHeadingChunker` | Có (Top 1) | Chunk Mục 2 & 3 chứa trọn vẹn quy định điều kiện tiên quyết và mốc 10 ngày làm việc. |
| 2 | Hạn mức mượn sách thư viện sinh viên đại học | `SectionHeadingChunker` + Filter | Có (Top 1) | Lọc `audience=student` giúp loại bỏ hoàn toàn quy định của giảng viên (5 tài liệu, 30 ngày). |
| 3 | Các mức học bổng tài năng VinUniversity | `SectionHeadingChunker` | Có (Top 1) | Toàn bộ 4 loại học bổng và mức trợ cấp 35% nằm trọn vẹn trong chunk Mục 2. |
| 4 | Mức hỗ trợ tài chính Need-based | `RecursiveChunker` / `Heading` | Có (Top 1) | Trích xuất chính xác quy định hỗ trợ lên tới 100% học phí và kết hợp học bổng tài năng. |
| 5 | Quy trình khiếu nại điểm thi và bước đầu tiên | `SectionHeadingChunker` | Có (Top 1) | Trả về Mục 1 & 2 với phạm vi Final Course Grade và yêu cầu trao đổi trực tiếp với giảng viên. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Lọc bằng metadata đóng vai trò quyết định, đặc biệt ở Câu hỏi 2 (Dịch vụ thư viện).** Trong thử nghiệm A/B:
> - **Khi KHÔNG lọc metadata:** Vì câu hỏi sử dụng từ ngữ chung chung ("mượn sách thư viện"), hệ thống truy xuất lẫn lộn cả tài liệu `library-faculty.md` (5 tài liệu, 30 ngày) và `library-student.md` (3 tài liệu, 14 ngày). Agent dễ bị nhầm lẫn và trả lời sai hạn mức của sinh viên thành hạn mức của giảng viên.
> - **Khi CÓ lọc `metadata_filter={"audience": "student"}`:** Toàn bộ tài liệu dành cho giảng viên bị loại bỏ ngay từ bước tiền lọc (pre-filtering), bảo đảm 100% các ứng viên trả về trong top-3 đều là quy chế áp dụng cho sinh viên.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **Sức mạnh của Semantic Structure-aware Chunking:** Đối với văn bản pháp quy đại học, chiến lược chia nhỏ theo cấu trúc tài liệu (`SectionHeadingChunker`) vượt trội hoàn toàn so với các phương pháp chia theo độ dài ký tự cơ học (`FixedSizeChunker`) nhờ giữ nguyên vẹn cặp thực thể "Điều kiện — Quyền lợi".
2. **Vai trò cốt lõi của Pre-filtering Metadata:** Chứng minh thực nghiệm rằng việc lọc metadata trước khi tính vector similarity là giải pháp duy nhất giúp loại bỏ nhiễu giữa các nhóm đối tượng người dùng khác nhau trong cùng một tổ chức.
3. **Sự khác biệt giữa Cú pháp bề mặt và Ý nghĩa ngữ nghĩa:** Bài học từ việc so sánh giữa `MockEmbedder` (băm MD5 ngẫu nhiên) và Embedding ngữ nghĩa thực sự, khẳng định mô hình RAG phụ thuộc mật thiết vào không gian biểu diễn học sâu.

**Bài học rút ra khi so sánh trong nhóm:**
> Trên cùng một tập dữ liệu văn bản đại học, việc lựa chọn chiến lược chunking khác nhau tạo ra sự phân hóa rất lớn về chất lượng context đưa vào prompt của LLM. `FixedSizeChunker` dù đơn giản nhưng tạo ra rủi ro thông tin bị cắt cụt đầu đuôi; trong khi `SectionHeadingChunker` biến mỗi chunk thành một tài liệu vi mô (micro-document) hoàn chỉnh, giúp agent dễ dàng trích xuất câu trả lời chuẩn xác và trích dẫn số thứ tự nguồn minh bạch.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> 1. **Gắn thêm metadata động cấp độ Chunk (Chunk-level metadata):** Ngoài metadata của file, nhóm sẽ tự động trích xuất tiêu đề mục (`section_title`) và gắn vào metadata của từng chunk con để khi truy xuất top-k, agent biết chính xác chunk đó thuộc "Điều nào" mà không cần nhìn toàn bộ văn bản.
> 2. **Tích hợp mô hình Embedder Đa ngữ cục bộ (Local Multilingual Embedder):** Sử dụng `paraphrase-multilingual-MiniLM-L12-v2` để tối ưu hóa không gian vector nhúng tiếng Việt cho kho dữ liệu quy định đại học.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|:----------------:|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
