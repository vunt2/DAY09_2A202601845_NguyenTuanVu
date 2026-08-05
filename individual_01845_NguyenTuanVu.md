# Member Role Report — Day 9: Multi Agent A2A

## 1. Thông tin cá nhân

| Thông tin       | Nội dung         |
| --------------- | ---------------- |
| Họ và tên       | Nguyễn Tuấn Vũ   |
| MSSV            | 2A202601845      |
| Khóa/Lớp        | K3               |
| Vai trò chính   | Lead / Multi-Agent Developer |
| Ngày hoàn thành | 2026-08-05       |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| ------------------ | ------------------ | -------------- | ----------------- | ------------------------------------- |
| Multi-Agent Pipeline | `src/pipeline.py`, `src/agents/` | `input/EC_001.json` ... `EC_050.json` | 50 file JSON trong `output/` | Complete (100%) |
| Data Access & Policy Engine | `src/data_loader.py`, `src/policy_engine.py` | 9 file CSV Olist trong `data/` | Data facts & Verified Evidence IDs | Complete (100%) |
| Verifier Quality Gate & Validator | `src/agents/verifier_agent.py`, `validate_submission.py` | Draft Resolution JSON | Grounded & Validated JSON | Complete (100%) |
| Packaging & Deliverables | `create_submission_zip.py` | `output/*.json` | `submission.zip` (50 JSONs) | Complete (100%) |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --------- | ----------------------------- | ------- |
| Thiết kế Kiến trúc & Tài liệu | Toàn bộ dự án | [`architecture.md`](file:///c:/AI20K/LABS/DAY09_2A202601845_NguyenTuanVu/architecture.md) & [`Guide_labs.md`](file:///c:/AI20K/LABS/DAY09_2A202601845_NguyenTuanVu/Guide_labs.md) |
| Cấu hình Môi trường & Metadata | Hệ thống & Báo cáo | [`.env`](file:///c:/AI20K/LABS/DAY09_2A202601845_NguyenTuanVu/.env), [`metadata.json`](file:///c:/AI20K/LABS/DAY09_2A202601845_NguyenTuanVu/metadata.json), [`trace.jsonl`](file:///c:/AI20K/LABS/DAY09_2A202601845_NguyenTuanVu/trace.jsonl) |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --------------------- | --------------------------- | ------------------------- | --------------- |
| Xử lý 50 ticket khiếu nại BTC | [`output/EC_001.json`](file:///c:/AI20K/LABS/DAY09_2A202601845_NguyenTuanVu/output/EC_001.json) | 50/50 file JSON đúng schema `EC_POLICY_V1` | `python validate_submission.py` |
| Thẩm định bằng chứng & Trace | [`trace.jsonl`](file:///c:/AI20K/LABS/DAY09_2A202601845_NguyenTuanVu/trace.jsonl) | 300 sự kiện vết handoff A2A | Audit qua `validate_submission.py` |
| Đóng gói Bài nộp | `submission.zip` | Đóng gói đúng 50 JSON | `python create_submission_zip.py` |

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Hệ thống cần điều tra 50 yêu cầu khiếu nại của khách hàng thương mại điện tử Olist (Brazil), phân tích các mốc giao hàng, trạng thái đơn, dòng thanh toán, áp dụng quy tắc chính sách `EC_POLICY_V1` và truy vết bằng chứng có thật trong dữ liệu (Grounding).

### Cách triển khai
Xây dựng mô hình **Supervisor-Worker kèm Quality Gate (Handoff Pipeline)** gồm 6 Agent:
1. **Coordinator Agent**: Nhận ticket, tạo `HandoffPacket`.
2. **Order & Seller Agent**: Tra cứu trạng thái đơn và hạn giao hàng của seller (`shipping_limit_date`).
3. **Payment Agent**: Đối soát giao dịch thanh toán và tổng tiền hàng + phí ship.
4. **Delivery Agent**: So sánh ngày giao thực tế với `order_estimated_delivery_date`.
5. **Policy Agent**: Đánh giá 6 quy tắc của `EC_POLICY_V1` theo đúng thứ tự ưu tiên.
6. **Verifier Agent**: Kiểm tra tính có thật của tất cả Evidence ID trong CSV (0% False Positive).

### Cách xác minh

```bash
python validate_submission.py
```

- **Kết quả mong đợi:** 50 file JSON trong `output/`, không lỗi schema, 100% Evidence ID tồn tại trong CSV.
- **Kết quả thực tế:** Xử lý 50 case thành công, 250 Evidence IDs verified 100% Valid, 300 log trace được tạo ra.
- **Artifact/log:** [`trace.jsonl`](file:///c:/AI20K/LABS/DAY09_2A202601845_NguyenTuanVu/trace.jsonl) & [`metadata.json`](file:///c:/AI20K/LABS/DAY09_2A202601845_NguyenTuanVu/metadata.json).

## 5. Một quyết định kỹ thuật quan trọng
- **Bối cảnh:** Lựa chọn cách thức xác minh Evidence IDs để tránh hallucination.
- **Phương án đã chọn:** Tích hợp **Verifier Agent (Quality Gate)** thẩm định độc lập đối chiếu từng ID với dữ liệu CSV Olist trước khi ghi đĩa.
- **Lý do:** Đảm bảo 100% tính Grounding, không bị trừ điểm vì False Positive Evidence.

## 6. Cam kết của thành viên
- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.

**Họ và tên:** Nguyễn Tuấn Vũ  
**Ngày xác nhận:** 2026-08-05
