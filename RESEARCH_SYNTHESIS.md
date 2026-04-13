# Research Synthesis: SunShift — Hybrid Cloud System cho Doanh Nghiệp Nhỏ Florida

**Phương pháp:** Tổng hợp đa nguồn (Web Research, Dữ liệu chính phủ, Báo cáo ngành, Thống kê SBA/FEMA)
**Phạm vi:** Tampa Bay, Florida & Thị trường SMB toàn quốc
**Ngày:** 13 tháng 4, 2026
**Nghiên cứu viên:** Claude AI Research Agent (4 hướng nghiên cứu song song)

---

## I. TÓM TẮT ĐIỀU HÀNH (Executive Summary)

SunShift nhắm vào một "khoảng trống chết người" trong thị trường: **doanh nghiệp nhỏ Florida (5-50 nhân viên) đang chịu đồng thời hai gánh nặng tài chính — chi phí điện cao điểm mùa hè và rủi ro mất dữ liệu do bão lũ** — nhưng không có giải pháp hybrid cloud nào đủ đơn giản và rẻ để họ tiếp cận. Dữ liệu cho thấy: giá điện thương mại tại Tampa dao động **10.5–12.5¢/kWh**, với giờ cao điểm FPL có thể đẩy lên tới **27¢/kWh** (gấp 4.5x off-peak ~6¢/kWh). Trong khi đó, **40% doanh nghiệp nhỏ không bao giờ mở cửa lại sau thảm họa thiên nhiên** (FEMA), và chỉ **30% có kế hoạch khôi phục dữ liệu**. Thị trường hybrid cloud SMB đang tăng trưởng **14.6% CAGR** — nhanh hơn cả phân khúc enterprise — tạo cửa sổ cơ hội lớn.

---

## II. CHỦ ĐỀ NGHIÊN CỨU CHÍNH (Key Research Themes)

---

### Theme 1: Chi Phí Điện — "Thuế Ẩn" Của Doanh Nghiệp Nhỏ Tampa

**Mức độ nghiêm trọng:** ████████░░ 8/10
**Nguồn dữ liệu:** FPL, TECO, EnergySage, KilowattLogic, FL PSC

#### Bối cảnh giá điện Florida 2026

| Chỉ số | Giá trị |
|--------|---------|
| Giá điện thương mại trung bình Florida | **12.35¢/kWh** (EIA 2026) |
| FPL GSD-1 (Commercial) | **10.5–11.5¢/kWh** |
| TECO/Duke Energy (Tampa khu vực) | **11.0–12.5¢/kWh** |
| Giá điện dân dụ Tampa (TECO) | **$0.20/kWh** (~20¢) |
| Hóa đơn điện trung bình hộ gia đình Tampa | **$339/tháng** |
| Tỷ trọng demand charge trong bill thương mại | **30–40%** |

#### Giá điện Time-of-Use (TOU) — Nơi "đốt tiền" thực sự

**FPL Business Time-of-Use (GSDT-1):**
- **Giờ cao điểm (On-Peak):**
  - Mùa hè (1/4 – 31/10): **Trưa đến 9 giờ tối**, Thứ 2 – Thứ 6
  - Mùa đông (1/11 – 31/3): **6h–10h sáng & 6h–10h tối**, Thứ 2 – Thứ 6
- **Biên độ giá FPL TOU:** Từ **~6¢/kWh (off-peak)** đến **~27¢/kWh (on-peak)**
- **Chênh lệch:** On-peak đắt hơn **~4.5 lần** so với off-peak

**TECO (Tampa Electric):**
- Tăng giá 2–10% cho thương mại từ tháng 1/2026
- Đã có 4 đợt tăng giá trong 12 tháng qua
- Fixed rate: $0.15–$0.17/kWh cho khu vực dân dụng
- Demand charge đề xuất: ~**$19.62/billing kW**

#### Tác động lên văn phòng chạy máy chủ

> **Kịch bản:** Văn phòng nhỏ chạy 1 server rack (2-3 máy chủ + switch + UPS)
> - Công suất tiêu thụ: ~2-3 kW (bao gồm cooling)
> - Chi phí off-peak (6¢/kWh): **~$4.32/ngày** → **$130/tháng**
> - Chi phí on-peak (27¢/kWh, 9 tiếng): **~$7.29/ngày chỉ riêng giờ cao điểm**
> - **Tiết kiệm tiềm năng khi shift sang cloud giờ cao điểm: ~$100-150/tháng**

**Hàm ý cho SunShift:** Giá điện TOU của FPL tạo ra một "cửa sổ đốt tiền" rõ ràng từ **12h trưa đến 9h tối mùa hè** — đây chính xác là thời điểm SunShift cần di chuyển workload lên AWS. Cần lưu ý: TECO (nhà cung cấp chính tại Tampa) đã ngừng TOU cho dân dụ từ 2023, nhưng vẫn có cấu trúc demand charge cao cho thương mại.

---

### Theme 2: Bão Lũ — "Sát Thủ" Của Doanh Nghiệp Nhỏ

**Mức độ nghiêm trọng:** ██████████ 10/10
**Nguồn dữ liệu:** FEMA, SBA, NARA, Ponemon Institute, FL Division of Emergency Management

#### Thống kê thiệt hại — Con số "chết chóc"

| Chỉ số | Số liệu | Nguồn |
|--------|---------|-------|
| DN nhỏ KHÔNG BAO GIỜ mở lại sau thảm họa | **40%** | FEMA |
| DN mở lại nhưng đóng cửa trong 1 năm | **25%** | FEMA |
| **Tổng tỷ lệ thất bại** | **~60%** | FEMA |
| DN thất bại nếu không hoạt động lại trong 5 ngày | **90%** | SBA |
| DN có kế hoạch disaster recovery | Chỉ **30%** | Industry reports |
| DN bị underinsured (bảo hiểm không đủ) | **~40%** | Insurance Information Institute |
| DN thừa nhận mất dữ liệu gây thiệt hại lớn | **70%** | Ponemon |
| Backup thất bại khi recovery | **58%** | Industry reports |

#### Lịch sử cúp điện do bão tại Florida

| Bão | Năm | Số hộ mất điện | Thời gian phục hồi TB | Trường hợp nặng |
|-----|------|---------------|----------------------|-----------------|
| Andrew | 1992 | 1.4 triệu | 2–4 tuần | Đến 6 tuần |
| Irma | 2017 | **6.7 triệu** | 10–14 ngày | 3+ tuần |
| Michael | 2018 | 400K | 2–4 tuần | 6+ tuần (Mexico Beach) |
| Ian | 2022 | 2.6 triệu | 7–14 ngày | 3–4 tuần |
| **Milton** | **2024** | **~3.4 triệu** | **7–14 ngày** | **2–3 tuần** |

> **Lưu ý quan trọng:** Milton (2024) là cơn bão lớn đầu tiên tấn công trực tiếp Tampa Bay trong thời hiện đại. Hạ tầng điện ngầm tại Tampa, St. Petersburg bị ngập nước, kéo dài thời gian mất điện.

#### Chi phí downtime theo ngành

| Ngành | Thiệt hại/ngày | Rủi ro pháp lý |
|-------|----------------|-----------------|
| **Phòng khám y tế** (3-5 bác sĩ) | **$10,000–$50,000** | HIPAA fines: $100–$50,000/vi phạm |
| **Văn phòng luật** (5-10 luật sư) | **$8,000–$32,000** | Malpractice exposure, deadline tòa |
| **Studio thiết kế** | **$5,000–$20,000** | Mất file dự án = hàng trăm giờ |
| **Trung bình SMB** | **$8,000–$74,000/giờ** | IDC/Datto reports |

#### Lỗ hổng bảo hiểm — Những gì KHÔNG được bao phủ

Đây là phát hiện quan trọng nhất cho value proposition của SunShift:

1. **Thiệt hại do lũ lụt** — KHÔNG nằm trong bảo hiểm thương mại tiêu chuẩn (cần mua riêng NFIP)
2. **Mất/khôi phục dữ liệu số** — KHÔNG được bao phủ (cần rider "cyber" riêng)
3. **Hỏng thiết bị do đột biến điện** — KHÔNG nằm trong policy tiêu chuẩn
4. **Gián đoạn dịch vụ tiện ích** — Nếu tòa nhà ok nhưng mất điện khu vực → KHÔNG được bồi thường
5. **Vi phạm HIPAA/mất dữ liệu khách hàng** — KHÔNG nằm trong bảo hiểm tài sản
6. **Gián đoạn cloud service** — KHÔNG được bao phủ

> **Insight:** SunShift không chỉ là tool tiết kiệm điện — nó là **bảo hiểm dữ liệu thực tế** mà không có hãng bảo hiểm nào cung cấp.

---

### Theme 3: Thị Trường Hybrid Cloud — Cơ Hội Chưa Được Khai Thác

**Mức độ cơ hội:** ████████░░ 8/10
**Nguồn dữ liệu:** Mordor Intelligence, Precedence Research, CloudZero, Allied Market Research

#### Quy mô & Tăng trưởng

| Chỉ số | Giá trị |
|--------|---------|
| Thị trường hybrid cloud toàn cầu (2025) | **$134–$169 tỷ** |
| Dự kiến 2026 | **$157–$194 tỷ** |
| CAGR tổng thể | **12.37%** (Mordor, 2026–2031) |
| **CAGR phân khúc SMB** | **14.6%** (nhanh hơn enterprise!) |
| Dự kiến 2034 | **$578.72 tỷ** |
| Thị phần enterprise vs SMB | 62.3% enterprise : 37.7% SMB |
| % workload SMB trên public cloud | **63%** |
| Tăng chi tiêu cloud YoY của SMB | **+31%** |

#### Đối thủ cạnh tranh — Và tại sao họ KHÔNG phục vụ SMB nhỏ

| Giải pháp | Giá khởi điểm | Đối tượng | Tại sao không phù hợp SMB nhỏ |
|-----------|--------------|-----------|------------------------------|
| **AWS Outposts** | ~$250K+ (hardware) | Enterprise 500+ NV | Quá đắt, quá phức tạp |
| **Azure Arc** | Phí quản lý/node | Mid-market+ | Cần đội IT chuyên trách |
| **Azure Stack HCI** | $10K-$20K+ | Mid-market | Yêu cầu hạ tầng riêng |
| **Nutanix** | $25K+ | Mid-market+ | Licensing phức tạp |
| **VMware Cloud** | Tùy license | Enterprise | Chi phí vận hành cao |
| **Wasabi + NAS** | $7/TB/tháng | Prosumer/SMB | Chỉ backup, không compute |

> **Khoảng trống thị trường:** Không có giải pháp nào tự động di chuyển workload dựa trên giá điện TOU + cảnh báo bão cho doanh nghiệp **5–50 nhân viên** với chi phí dưới **$200-500/tháng**.

#### Chi phí AWS tại Ohio (us-east-2) — Điểm đến của SunShift

| Dịch vụ | Giá (On-Demand) | Ghi chú |
|---------|-----------------|---------|
| EC2 t3.medium (2 vCPU, 4GB) | **~$0.0416/giờ** (~$30/tháng) | Tương đương 1 server nhỏ |
| EC2 t3.large (2 vCPU, 8GB) | ~$0.0832/giờ (~$60/tháng) | File server nhỏ |
| S3 Standard Storage | ~$0.023/GB/tháng | Lưu trữ backup |
| S3 Infrequent Access | ~$0.0125/GB/tháng | Backup dài hạn |
| Data Transfer Out (>100GB) | ~$0.09/GB | Chi phí "ẩn" cần tính |

> **Tính toán:** Chạy workload 6 tiếng/ngày (giờ cao điểm) trên t3.medium = 6 × $0.0416 = **$0.25/ngày** = **~$5.50/tháng** cho compute on-demand. So với chi phí điện on-peak tiết kiệm được (~$100-150/tháng) → **ROI rõ ràng**.

---

### Theme 4: Thị Trường Mục Tiêu — Tampa Bay & Florida SMB

**Quy mô tiềm năng:** ████████░░ 8/10
**Nguồn dữ liệu:** SBA, US Census, Tampa Bay Chamber, SBDC

#### Dữ liệu thị trường Florida

| Chỉ số | Giá trị |
|--------|---------|
| Tổng số doanh nghiệp nhỏ Florida | **3.5 triệu** (99.8% tổng DN) |
| Nhân viên tại DN nhỏ FL | **3.8 triệu** (39.6% lao động tư nhân) |
| Đơn đăng ký kinh doanh mới Tampa Bay/năm | **~90,000+** (tăng gấp đôi từ 2019) |
| Giao dịch mua bán DN Tampa Bay 2025 | 1,093 (giá trung vị $350K) |

#### Phân khúc ngành mục tiêu tại Tampa Bay

| Ngành | Đặc điểm | Nhu cầu IT | Mức độ phù hợp SunShift |
|-------|---------|------------|------------------------|
| **Phòng khám Y/Nha khoa** | Dữ liệu HIPAA, EHR | Server EMR, backup bệnh nhân | ★★★★★ |
| **Văn phòng Luật** | Tài liệu mật, deadline tòa | File server, email server | ★★★★★ |
| **Công ty Kế toán** | Dữ liệu tài chính, mùa thuế | Server kế toán, backup | ★★★★☆ |
| **Studio Thiết kế** | File lớn, project collaboration | NAS, render server | ★★★★☆ |
| **Công ty Tech nhỏ** | Code repos, staging servers | Dev servers, CI/CD | ★★★☆☆ |

#### Hạ tầng IT hiện tại của SMB mục tiêu

- **Đa số** dùng: Server tại chỗ (on-prem), NAS devices, local file shares
- Chỉ **~37%** SMB có dedicated IT staff → phần lớn dùng **MSP (Managed Service Provider)**
- Chi tiêu IT trung bình SMB (5-50 NV): **$500–$2,000/tháng/nhân viên** (bao gồm mọi thứ)
- Florida là thị trường điện **fully regulated** — không có lựa chọn nhà cung cấp điện

#### Yêu cầu pháp lý ảnh hưởng đến quyết định

| Quy định | Áp dụng cho | Yêu cầu chính | Ảnh hưởng đến SunShift |
|----------|------------|---------------|----------------------|
| **HIPAA** | Phòng khám, nha khoa | Mã hóa dữ liệu, audit trail, BAA | SunShift cần HIPAA-compliant |
| **FL Bar Rules** | Văn phòng luật | Bảo mật thông tin khách hàng | Mã hóa end-to-end |
| **SOX/PCI** | Kế toán, bán lẻ | Kiểm soát truy cập, log | Compliance logging |
| **FL Statute 501.171** | Mọi DN tại FL | Thông báo data breach trong 30 ngày | Incident response plan |

---

## III. INSIGHTS → CƠ HỘI (Insights → Opportunities)

| # | Insight (Điều chúng ta học được) | Cơ hội (Điều chúng ta có thể làm) | Tác động | Nỗ lực |
|---|----------------------------------|-----------------------------------|----------|--------|
| 1 | FPL TOU chênh lệch **4.5x** giữa peak/off-peak → "cửa sổ đốt tiền" 9 tiếng/ngày | Tự động di chuyển workload lên AWS Ohio trong giờ peak, tạo ROI ngay lập tức | **Cao** | Trung bình |
| 2 | **60%** SMB thất bại sau thảm họa; chỉ 30% có DR plan | Bán SunShift như "bảo hiểm dữ liệu" — thứ mà không hãng bảo hiểm nào cover | **Rất Cao** | Trung bình |
| 3 | Bão Milton (2024) gây mất điện 3.4 triệu hộ → Tampa Bay giờ đây **biết** nguy hiểm | Cơ hội marketing dựa trên trauma thực tế, không cần educate thị trường | **Cao** | Thấp |
| 4 | Phòng khám mất **$10K-50K/ngày** downtime + rủi ro HIPAA fine $50K/vi phạm | Gói "SunShift Healthcare" với HIPAA compliance → premium pricing hợp lý | **Rất Cao** | Cao |
| 5 | Không có đối thủ nào phục vụ SMB <50 NV với hybrid cloud tự động dưới $500/tháng | **Blue ocean** — SunShift có thể định nghĩa category mới | **Rất Cao** | Cao |
| 6 | SMB cloud spend tăng **31% YoY**; CAGR phân khúc SMB **14.6%** | Thị trường đang di chuyển đúng hướng SunShift — tailwind mạnh | **Cao** | N/A |
| 7 | 58% backup thất bại khi recovery → niềm tin vào backup truyền thống thấp | SunShift cần demo "1-click restore" để tạo khác biệt vs backup thông thường | **Cao** | Trung bình |
| 8 | TECO không có TOU cho residential, nhưng demand charge cao cho commercial | Messaging cần focus vào **demand charge reduction**, không chỉ TOU savings | **Trung bình** | Thấp |

---

## IV. PHÂN KHÚC NGƯỜI DÙNG (User Segments)

| Phân khúc | Đặc điểm | Nhu cầu chính | Sẵn sàng chi trả | Quy mô ước tính (Tampa Bay) |
|-----------|---------|---------------|-------------------|---------------------------|
| **"Dr. Worried"** — Phòng khám Y/Nha | 3-10 NV, chạy EMR server, ràng buộc HIPAA | DR plan + compliance | **$300-500/tháng** | ~2,000-3,000 practices |
| **"Attorney Always-On"** — VP Luật | 5-20 NV, file server lớn, deadline tòa | Zero-downtime + bảo mật | **$200-400/tháng** | ~1,500-2,500 firms |
| **"Creative Crisis"** — Studio thiết kế | 3-15 NV, file cỡ lớn, NAS | Backup file + render cloud | **$150-300/tháng** | ~500-1,000 studios |
| **"Number Cruncher"** — Kế toán/Tài chính | 5-25 NV, mùa thuế workload cao | Seasonal scaling + backup | **$200-400/tháng** | ~1,000-2,000 firms |
| **"Tech Startup"** — Startup/Tech nhỏ | 5-20 NV, đã hiểu cloud | Cost optimization | **$100-200/tháng** | ~500-1,000 companies |

**TAM (Tampa Bay) ước tính:** 5,500 – 9,500 doanh nghiệp mục tiêu
**SAM (ngay lập tức, Dr. Worried + Attorney):** 3,500 – 5,500 doanh nghiệp
**Doanh thu tiềm năng SAM:** $700K – $2.75M/tháng (ARR: $8.4M – $33M)

---

## V. KHUYẾN NGHỊ (Recommendations)

### 1. ★★★ ƯU TIÊN CAO NHẤT — Bắt đầu với "Hurricane Shield" Feature

**Lý do:** Dữ liệu cho thấy **nỗi đau bão lũ** là pain point mạnh nhất (60% failure rate, Milton trauma còn mới). Tính năng tự động backup lên AWS khi có cảnh báo bão là **USP dễ bán nhất** và có emotional resonance mạnh nhất tại Tampa Bay.

**Hành động:**
- Tích hợp API National Hurricane Center (NOAA) để trigger tự động
- Xây dựng "1-click disaster mode" — mã hóa + đẩy toàn bộ dữ liệu lên S3
- Demo với kịch bản: "Nếu Milton xảy ra lần nữa, dữ liệu bạn an toàn trong 15 phút"

### 2. ★★★ ƯU TIÊN CAO — HIPAA Compliance từ ngày 1

**Lý do:** Phòng khám y/nha khoa là phân khúc sẵn sàng trả giá cao nhất ($300-500/tháng) VÀ có nhu cầu pháp lý bắt buộc. HIPAA compliance là barrier to entry cho đối thủ.

**Hành động:**
- Mã hóa AES-256 at-rest và in-transit
- Signed BAA (Business Associate Agreement)
- Audit logging cho mọi data transfer
- SOC 2 Type II certification (dài hạn)

### 3. ★★☆ ƯU TIÊN TRUNG BÌNH — TOU Energy Arbitrage

**Lý do:** ROI rõ ràng ($100-150/tháng tiết kiệm) nhưng emotional pull yếu hơn hurricane protection. Tốt nhất khi bundle cùng hurricane feature.

**Hành động:**
- Tích hợp lịch TOU của FPL (12h-9h PM mùa hè)
- Tự động migrate lightweight workloads (file serving, email) sang AWS Ohio
- Dashboard hiển thị "Bạn đã tiết kiệm $X tháng này"

### 4. ★★☆ ƯU TIÊN TRUNG BÌNH — Partnership với MSP Tampa Bay

**Lý do:** Đa số SMB nhỏ không có IT staff → dựa vào MSP. MSP là kênh phân phối tự nhiên.

**Hành động:**
- Xây dựng MSP partner program với margin hấp dẫn (20-30%)
- Cung cấp white-label option
- Tham gia Tampa Bay Tech events, SBDC workshops

### 5. ★☆☆ ƯU TIÊN THẤP HƠN — Mở rộng ra toàn Florida

**Lý do:** Florida có 3.5 triệu SMB. Sau khi prove model tại Tampa Bay, mở rộng sang Miami-Dade, Jacksonville, Orlando.

---

## VI. CÂU HỎI CẦN NGHIÊN CỨU THÊM

1. **Giá điện chính xác của TECO commercial 2026** — PDF rate schedule không extract được; cần liên hệ trực tiếp TECO hoặc lấy từ FL PSC filing
2. **Bandwidth thực tế** — Tốc độ upload từ office Tampa lên AWS Ohio? Latency? Ảnh hưởng đến migration time?
3. **Phỏng vấn người dùng thực tế** — Cần 10-15 cuộc phỏng vấn với chủ phòng khám, luật sư, kế toán tại Tampa Bay để validate pain points
4. **Chi phí data transfer AWS** — $0.09/GB out có thể tích lũy lớn; cần tính toán TCO chính xác cho từng use case
5. **Quy trình mua của SMB** — Ai ra quyết định? Office manager? MSP? Chủ DN? Chu kỳ mua bao lâu?
6. **Đối thủ tiềm ẩn** — Các MSP lớn tại Tampa (như Savage Consulting, Tampa Dynamics) có đang offer giải pháp tương tự không?
7. **Tốc độ recovery thực tế** — Cần benchmark: bao lâu để restore 100GB, 500GB, 1TB từ S3 về on-prem mới?

---

## VII. GHI CHÚ PHƯƠNG PHÁP (Methodology Notes)

### Nguồn dữ liệu
- **Cấp 1 (Chính phủ/Tổ chức):** FEMA, SBA, US Census, FL PSC, NOAA
- **Cấp 2 (Ngành):** Mordor Intelligence, Precedence Research, IDC, Gartner, Ponemon Institute, Insurance Information Institute
- **Cấp 3 (Báo chí/Blog):** EnergySage, KilowattLogic, WUSF, WFLA, Fox 13 Tampa Bay, Tampa Bay Business Weekly
- **Cấp 4 (Utilities):** FPL.com, TampaElectric.com, AWS Pricing

### Hạn chế
1. **Giá điện TOU cụ thể của TECO** không extract được từ PDF (encrypted format) — số liệu FPL TOU được sử dụng làm proxy
2. **Số liệu phòng khám/văn phòng luật Tampa Bay** là ước tính dựa trên dữ liệu Census + SBA state profile, không phải đếm chính xác
3. **FEMA 40% statistic** đã bị tranh cãi trong học thuật — một số nhà nghiên cứu cho rằng tỷ lệ thực tế thấp hơn khi kiểm soát DN đã có ý định đóng cửa
4. **Giá AWS** là on-demand pricing; Reserved Instances hoặc Savings Plans có thể giảm 30-60%
5. **TAM/SAM estimation** dựa trên extrapolation, cần primary research để validate

### Nguồn tham khảo chính
- [FPL Business Rate Options](https://www.fpl.com/rates/business-options.html)
- [TECO Rates](https://www.tampaelectric.com/rates/)
- [EnergySage Tampa Rates](https://www.energysage.com/local-data/electricity-cost/fl/hillsborough-county/tampa/)
- [KilowattLogic Florida Commercial](https://kilowattlogic.com/markets/florida)
- [SBA Florida 2025 Profile](https://advocacy.sba.gov/wp-content/uploads/2025/06/Florida_2025-State-Profile.pdf)
- [Hybrid Cloud Market - Mordor Intelligence](https://www.mordorintelligence.com/industry-reports/hybrid-cloud-market)
- [Hybrid Cloud Market - Precedence Research](https://www.precedenceresearch.com/hybrid-cloud-market)
- [FEMA Ready.gov Business](https://www.ready.gov/business)
- [Disaster Recovery Statistics - InvenioIT](https://invenioit.com/continuity/disaster-recovery-statistics/)
- [Cloud Computing Statistics - CloudZero](https://www.cloudzero.com/blog/cloud-computing-statistics/)
- [Tampa Bay Business Weekly - Economy 2025](https://tbbwmag.com/2025/12/03/tampa-economy-2025/)
- [BoostSuite - Florida Small Business Statistics](https://boostsuite.com/small-business-statistics/florida/)

---

## VIII. APPENDIX: POSITIONING STATEMENT (Tuyên bố Định vị)

> **Cho** các phòng khám y tế, văn phòng luật, và doanh nghiệp nhỏ tại Tampa Bay (5-50 nhân viên)
>
> **Đang gánh chịu** chi phí điện cao điểm mùa hè leo thang và nguy cơ mất toàn bộ dữ liệu khi bão đổ bộ
>
> **SunShift** là hệ thống hybrid cloud tự động
>
> **Giúp** tự động di chuyển dữ liệu và workload lên AWS khi giá điện tăng hoặc bão đe dọa, và mang về khi an toàn
>
> **Khác với** các giải pháp hybrid cloud enterprise (AWS Outposts, Azure Arc) hoặc backup đơn thuần (Wasabi, Backblaze)
>
> **SunShift** là giải pháp duy nhất được thiết kế riêng cho SMB Florida, tự động hóa hoàn toàn dựa trên giá điện TOU và cảnh báo bão thời gian thực, với mức giá dưới $500/tháng và không cần IT staff chuyên trách.
