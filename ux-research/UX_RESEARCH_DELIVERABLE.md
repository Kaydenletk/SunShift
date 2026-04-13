# UX Research Deliverable: SunShift
**Loại:** Personas + Journey Maps + Usability Testing Framework
**Phương pháp:** Secondary research synthesis → Data-driven persona generation → Journey mapping
**Ngày:** 13 tháng 4, 2026
**Dựa trên:** RESEARCH_SYNTHESIS.md (4 hướng nghiên cứu, 20+ nguồn dữ liệu)

---

## I. PERSONAS CHI TIẾT

---

### PERSONA 1: Dr. Mai Nguyen — "Dr. Worried"
**Phân khúc:** Chủ phòng khám Y/Nha khoa Tampa Bay
**Mức ưu tiên:** ★★★★★ (SAM chính, willingness-to-pay cao nhất)

#### Thông tin cá nhân
| Thuộc tính | Chi tiết |
|------------|----------|
| **Tuổi** | 47 |
| **Nghề nghiệp** | Chủ phòng khám nha khoa, 3 nha sĩ + 8 nhân viên |
| **Khu vực** | South Tampa, FL |
| **Thu nhập phòng khám** | ~$1.2M/năm |
| **Tech proficiency** | 3/10 — dùng được EMR nhưng không hiểu IT infrastructure |
| **IT setup hiện tại** | 1 server Dell chạy Dentrix (EMR), NAS backup, MSP hợp đồng $800/tháng |
| **Nhà cung cấp điện** | TECO (Tampa Electric) |
| **Hóa đơn điện** | ~$450/tháng (bao gồm server + cooling) |

#### Quote đại diện
> *"Sau bão Milton, tôi không truy cập được hồ sơ bệnh nhân suốt 12 ngày. Mất $85,000 doanh thu và suýt bị kiện vì không cung cấp được lịch sử điều trị cho một ca cấp cứu chuyển viện."*

#### Psychographics

**Động lực (Motivations):**
1. **Bảo vệ bệnh nhân** — Dữ liệu y tế là tài sản quý nhất, không phải thiết bị
2. **Tuân thủ HIPAA** — Sợ bị phạt ($100–$50,000/vi phạm) hơn sợ mất tiền
3. **Sống sót qua mùa bão** — Milton 2024 là trải nghiệm thực tế, không phải giả thuyết
4. **Giảm phụ thuộc MSP** — Trả $800/tháng nhưng không biết MSP có backup đúng không

**Giá trị (Values):**
- An toàn bệnh nhân > Tiết kiệm chi phí
- Đơn giản > Nhiều tính năng
- Tự động hóa > Kiểm soát thủ công
- Chứng nhận/compliance > Lời hứa marketing

**Thái độ với công nghệ:**
- "Tôi không cần hiểu nó hoạt động thế nào. Tôi cần biết nó CÓ hoạt động."
- Quyết định mua dựa trên: peer recommendation từ bác sĩ khác, HIPAA compliance proof, demo trực tiếp
- Rào cản: sợ phức tạp, sợ migration rủi ro, không tin "cloud" an toàn bằng server ngay trước mặt

#### Nhu cầu & Mục tiêu

| Loại | Nhu cầu | Mức độ |
|------|---------|--------|
| **Chức năng** | Zero data loss khi bão đổ bộ | PHẢI CÓ |
| **Chức năng** | Backup tự động, không cần thao tác | PHẢI CÓ |
| **Chức năng** | HIPAA-compliant (BAA, mã hóa, audit log) | PHẢI CÓ |
| **Chức năng** | Khôi phục dữ liệu < 1 giờ | NÊN CÓ |
| **Cảm xúc** | Cảm giác "được bảo vệ" — an tâm khi mùa bão đến | PHẢI CÓ |
| **Cảm xúc** | Không cảm thấy ngu khi dùng dashboard | NÊN CÓ |
| **Xã hội** | Có thể nói với bệnh nhân "dữ liệu của bạn được bảo vệ cấp ngân hàng" | THÍCH CÓ |

#### Frustrations (Nỗi đau)

1. **"MSP nói backup OK nhưng tôi không biết cách kiểm tra"** — Thiếu visibility vào trạng thái backup thực tế
2. **"HIPAA audit khiến tôi mất ngủ"** — Không chắc hệ thống hiện tại đáp ứng compliance
3. **"Sau Milton, FPL phục hồi điện khu tôi sau 11 ngày"** — Bất lực trước infrastructure failure
4. **"IT consultant nói cần $15K upgrade server nhưng tôi không biết có cần thật không"** — Thiếu knowledge để đánh giá lời tư vấn IT
5. **"Bảo hiểm chỉ cover thiết bị, không cover dữ liệu bị mất"** — Lỗ hổng bảo hiểm thực sự

#### Kịch bản sử dụng chính

**Kịch bản A: Ngày thường (80% thời gian)**
> Dr. Nguyen đến phòng khám lúc 7:30 sáng. SunShift dashboard trên màn hình reception hiển thị: "Last backup: 6:02 AM ✓ | All systems healthy ✓ | HIPAA compliant ✓". Cô nhìn qua 3 giây rồi bắt đầu ngày làm việc. Không cần thao tác gì.

**Kịch bản B: Cảnh báo bão (5% thời gian, nhưng 90% giá trị)**
> NHC phát cảnh báo bão Category 3 tiến vào Tampa Bay trong 48 giờ. SunShift tự động chuyển sang "Hurricane Shield Mode" — push notification đến phone Dr. Nguyen: "Hurricane Shield ACTIVATED. All patient records (127GB) uploading to AWS Ohio. ETA: 4 hours. You don't need to do anything." Cô đọc, gật đầu, tiếp tục chuẩn bị evacuation cho gia đình.

**Kịch bản C: Sau bão — Recovery (1% thời gian, 100% giá trị cảm xúc)**
> Bão đi qua. Phòng khám bị ngập nhẹ, server hỏng. Dr. Nguyen mở SunShift app trên phone từ nhà cha mẹ ở Orlando: "Your data is safe ✓ (127GB on AWS Ohio). Ready to restore when you are." Khi phòng khám sửa xong, cô mua server mới, SunShift restore toàn bộ trong 3 giờ. Zero data loss.

#### Design Implications cho SunShift

1. **Dashboard phải "traffic light" đơn giản** — Xanh/Vàng/Đỏ, không có biểu đồ phức tạp
2. **HIPAA badge hiển thị prominently** — "HIPAA Compliant ✓" phải là thứ đầu tiên họ thấy
3. **Push notifications rõ ràng, không jargon** — "Your data is safe" > "S3 sync completed to us-east-2"
4. **"Proof mode"** — Xuất báo cáo compliance cho HIPAA auditor 1 click
5. **Onboarding cần white-glove** — Có thể cần session setup với MSP hiện tại, không DIY

#### Confidence & Gaps

| Metric | Giá trị | Ghi chú |
|--------|---------|---------|
| **Sample size** | 25 data points (synthetic from research) | Cần primary interviews |
| **Confidence** | Medium — dựa trên secondary data + industry stats | |
| **Cần validate** | Willingness-to-pay chính xác, workflow EMR cụ thể, MSP relationship dynamics | |

---

### PERSONA 2: David Torres — "Attorney Always-On"
**Phân khúc:** Partner tại Law Firm nhỏ Tampa Bay
**Mức ưu tiên:** ★★★★★ (SAM chính, pain point cực mạnh)

#### Thông tin cá nhân
| Thuộc tính | Chi tiết |
|------------|----------|
| **Tuổi** | 42 |
| **Nghề nghiệp** | Managing Partner, firm 3 luật sư + 5 paralegal/staff |
| **Khu vực** | Downtown Tampa / Westshore |
| **Thu nhập firm** | ~$2M/năm |
| **Tech proficiency** | 5/10 — dùng cloud email, hiểu cơ bản về file server |
| **IT setup hiện tại** | File server Windows (15 năm case files ~2TB), local Exchange, VPN sơ sài |
| **Nhà cung cấp điện** | TECO |
| **Hóa đơn điện** | ~$600/tháng (server closet chạy 24/7 + AC riêng) |

#### Quote đại diện
> *"Nếu tôi miss một court filing deadline vì mất điện do bão, đó là malpractice. Không có luật sư nào được phép nói 'bão ạ' trước thẩm phán. Tôi có 15 năm case files trên server dưới gầm bàn — điều đó khiến tôi sợ hơn cả bão."*

#### Psychographics

**Động lực:**
1. **Không bao giờ miss court deadline** — Malpractice exposure là rủi ro existential
2. **Bảo mật client data** — FL Bar Rules yêu cầu bảo vệ thông tin khách hàng
3. **Giảm chi phí vận hành** — $600/tháng điện chỉ cho server closet là "tiền bỏ sông"
4. **Truy cập từ xa khi evacuate** — Milton buộc evacuate, không truy cập được file 10 ngày

**Giá trị:**
- Reliability > Cost savings (nhưng cost savings vẫn quan trọng)
- Client confidentiality = non-negotiable
- Professional reputation > Convenience
- "Always-on" access > Feature richness

**Thái độ với công nghệ:**
- Pragmatic adopter — sẽ dùng nếu giải quyết vấn đề cụ thể
- Quyết định mua: ROI analysis, peer recommendation từ luật sư khác, FL Bar Association endorsement
- Rào cản: sợ data breach, lo ngại cloud security, muốn kiểm soát physical access

#### Nhu cầu & Mục tiêu

| Loại | Nhu cầu | Mức độ |
|------|---------|--------|
| **Chức năng** | Truy cập case files từ bất kỳ đâu khi bão | PHẢI CÓ |
| **Chức năng** | File server tự động sync lên cloud | PHẢI CÓ |
| **Chức năng** | End-to-end encryption (FL Bar compliance) | PHẢI CÓ |
| **Chức năng** | Dashboard tiết kiệm điện — ROI rõ ràng | NÊN CÓ |
| **Cảm xúc** | Tự tin nói với client: "Dữ liệu bạn được bảo vệ tuyệt đối" | NÊN CÓ |
| **Cảm xúc** | Không lo lắng khi mùa bão đến | PHẢI CÓ |
| **Xã hội** | Được coi là firm "chuyên nghiệp, hiện đại" | THÍCH CÓ |

#### Frustrations

1. **"15 năm case files nằm trên 1 server không RAID"** — Biết rủi ro nhưng chưa có giải pháp affordable
2. **"Khi evacuate đi Orlando, tôi không access được file nào"** — VPN cần server on, server cần điện
3. **"Tiền điện server closet tăng 20% so với năm ngoái"** — TECO tăng giá 4 lần trong 12 tháng
4. **"IT guy nói backup lên tape, nhưng ai test restore đâu"** — 58% backup thất bại khi recovery (industry stat)
5. **"Tòa không cho extension vì bão — đã có precedent"** — Áp lực pháp lý thực tế

#### Kịch bản sử dụng chính

**Kịch bản A: TOU Energy Savings (ngày thường)**
> 11:55 AM. SunShift dashboard hiển thị: "Peak hours starting in 5 min. Shifting file sync to AWS Ohio. Estimated savings today: $4.80." David glance rồi tiếp tục soạn motion. Cuối tháng, dashboard: "You saved $142 this month on electricity."

**Kịch bản B: Hurricane Season Prep**
> Tháng 6, đầu mùa bão. SunShift gửi email: "Hurricane Season Report: Your 2.1TB of case files are fully synced to AWS Ohio. Last verified: today 3AM. Recovery time estimate: 6 hours." David forward email cho insurance broker.

**Kịch bản C: Active Hurricane — Remote Access**
> Bão đổ bộ. David evacuate đến Gainesville. Mở laptop, đăng nhập SunShift portal → truy cập toàn bộ case files trên cloud. File court motion đúng deadline từ Starbucks ở Gainesville. *Không miss deadline. Không malpractice.*

#### Design Implications

1. **Remote access portal phải works trên laptop + mobile** — Không chỉ dashboard, cần FILE ACCESS
2. **Energy savings dashboard là "hook" cho daily engagement** — "$X saved" giữ user quay lại hàng ngày
3. **"Court Deadline Protection" feature naming** — Nói đúng ngôn ngữ của luật sư
4. **Monthly savings report** — Exportable PDF cho firm's financial records
5. **File browser interface** — Phải navigate được cây thư mục quen thuộc, không phải S3 bucket view

#### Confidence & Gaps

| Metric | Giá trị |
|--------|---------|
| **Sample size** | 20 data points (synthetic) |
| **Confidence** | Medium |
| **Cần validate** | File access requirements cụ thể, VPN vs. web portal preference, court system integration needs |

---

### PERSONA 3: Carlos Reyes — "Number Cruncher"
**Phân khúc:** Chủ công ty kế toán Tampa Bay
**Mức ưu tiên:** ★★★★☆ (Secondary SAM, seasonal pain point mạnh)

#### Thông tin cá nhân
| Thuộc tính | Chi tiết |
|------------|----------|
| **Tuổi** | 39 |
| **Nghề nghiệp** | CPA, firm 4 kế toán + 3 staff |
| **Khu vực** | Carrollwood, Tampa |
| **Thu nhập firm** | ~$1.5M/năm |
| **Tech proficiency** | 6/10 — quen dùng QuickBooks/Sage, hiểu networking cơ bản |
| **IT setup hiện tại** | Server chạy QuickBooks Enterprise, NAS 4TB cho client records |
| **Nhà cung cấp điện** | TECO |
| **Hóa đơn điện** | ~$380/tháng (bình thường), ~$550/tháng (mùa thuế Jan-Apr) |

#### Quote đại diện
> *"Từ tháng 1 đến tháng 4, server chạy 100% và hóa đơn điện tăng gấp đôi. Nếu mất dữ liệu tài chính của khách hàng, tôi mất license CPA. Đơn giản vậy thôi."*

#### Psychographics

**Động lực:**
1. **Bảo vệ dữ liệu tài chính** — Mất data = mất CPA license
2. **Xử lý workload mùa thuế** — 4 tháng cao điểm, server quá tải
3. **Giảm chi phí vận hành** — Cost-conscious hơn 2 personas trên
4. **SOX/regulatory compliance** — Client corporate cần audit trail

**Giá trị:**
- Chính xác > Tốc độ
- Tiết kiệm chi phí = ưu tiên cao (CPA mindset)
- ROI có thể đo lường > Promise mơ hồ
- Reliability qua cả năm, không chỉ mùa bão

**Đặc biệt — Mô hình sử dụng SEASONAL:**
```
Tháng 1-4 (Tax season):   ██████████ 100% — Server overload, cần cloud burst
Tháng 5-8 (Slow season):  ████░░░░░░ 40%  — Nhẹ nhàng, focus DR/backup
Tháng 9-10 (Extension):   ███████░░░ 70%  — Extension filings
Tháng 11-12 (Year-end):   █████░░░░░ 50%  — Year-end close, tax planning
```

#### Nhu cầu & Mục tiêu

| Loại | Nhu cầu | Mức độ |
|------|---------|--------|
| **Chức năng** | Cloud burst computing cho tax season | PHẢI CÓ |
| **Chức năng** | Automatic backup với audit trail | PHẢI CÓ |
| **Chức năng** | Energy cost tracking với ROI calculator | NÊN CÓ |
| **Chức năng** | Tích hợp QuickBooks Enterprise | THÍCH CÓ |
| **Cảm xúc** | "Tôi đang tiết kiệm X đô la" — cần số liệu cụ thể | PHẢI CÓ |
| **Cảm xúc** | Tự tin trước mùa bão VÀ mùa thuế | NÊN CÓ |

#### Frustrations

1. **"Server quá tải tháng 2-3, phải từ chối khách mới"** — Lost revenue do infrastructure limitation
2. **"Mua server mới chỉ để dùng 4 tháng/năm thì lãng phí"** — CapEx không hợp lý
3. **"Hóa đơn điện tháng 3 là $550 — gần gấp đôi bình thường"** — Cost spike seasonal
4. **"Backup tự động lúc 2AM nhưng chưa bao giờ test restore"** — False sense of security
5. **"Nếu bão đúng mùa thuế (Oct-Nov extension), chết chắc"** — Peak hurricane season overlap với tax extensions

#### Kịch bản sử dụng chính

**Kịch bản A: Tax Season Cloud Burst**
> Tháng 2. Firm nhận thêm 40 clients mới. Server QuickBooks chậm. SunShift tự động spin up EC2 instance ở Ohio, chạy QuickBooks Terminal Services. 3 kế toán remote connect, zero lag. Cuối tháng 4, SunShift scale down. Carlos chỉ trả tiền 4 tháng compute.

**Kịch bản B: Year-Round Energy Arbitrage**
> Dashboard hiển thị: "Q1 savings: $487 | Q2 savings: $312 | Hurricane Shield: Active ✓ | Next backup: 2 hours." Carlos export report, đưa cho bookkeeper ghi vào chi phí IT.

#### Design Implications

1. **ROI calculator phải prominent** — Carlos muốn thấy SỐ, không phải biểu tượng xanh lá
2. **Seasonal scaling controls** — "Tax Season Mode" toggle đơn giản
3. **Cost comparison view** — "Điện tháng này vs. tháng trước vs. nếu không có SunShift"
4. **Export reports** — PDF/CSV cho accounting records
5. **Pricing model linh hoạt** — Pay-per-use cho cloud burst, không flat fee quanh năm

#### Confidence & Gaps

| Metric | Giá trị |
|--------|---------|
| **Sample size** | 15 data points (synthetic) |
| **Confidence** | Medium-Low |
| **Cần validate** | QuickBooks cloud compatibility, actual tax season workload metrics, willingness to pay for seasonal vs. year-round |

---

## II. CUSTOMER JOURNEY MAPS

---

### Journey Map A: Dr. Worried — Từ "Chưa biết" đến "Không thể sống thiếu"

```
AWARENESS          CONSIDERATION        DECISION           ONBOARDING          DAILY USE           HURRICANE EVENT
(Tháng 1-2)       (Tháng 2-3)          (Tháng 3)          (Tháng 3-4)         (Tháng 4+)          (Mùa bão Jun-Nov)
     │                  │                   │                   │                   │                    │
     ▼                  ▼                   ▼                   ▼                   ▼                    ▼
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
│ Nghe BS  │    │ Xem demo     │    │ Ký hợp đồng  │    │ MSP cài đặt  │    │ Nhìn dash-   │    │ Hurricane Shield │
│ khác kể  │───▶│ tại hội thảo │───▶│ sau khi thấy │───▶│ agent on-    │───▶│ board 3 giây │───▶│ tự động kích    │
│ về mất   │    │ y khoa Tampa │    │ HIPAA badge  │    │ prem, test   │    │ mỗi sáng.    │    │ hoạt. Push       │
│ data sau │    │ Bay          │    │ + BAA        │    │ restore      │    │ "All Green." │    │ notification:    │
│ Milton   │    │              │    │              │    │              │    │              │    │ "Data Safe ✓"    │
└──────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────────┘
     │                  │                   │                   │                   │                    │
  FEELING:           FEELING:           FEELING:           FEELING:            FEELING:             FEELING:
  "Sợ hãi,          "Có hy vọng,       "Nhẹ nhõm,        "Hơi lo khi        "An tâm,             "Bình tĩnh, 
   lo lắng"          nhưng hoài nghi"   tin tưởng"        migrate data"      quên SunShift        không hoảng
                                                                              đang chạy"           như lần trước"
     │                  │                   │                   │                   │                    │
  TOUCHPOINT:        TOUCHPOINT:        TOUCHPOINT:        TOUCHPOINT:        TOUCHPOINT:          TOUCHPOINT:
  • Peer story       • Live demo        • Sales call       • MSP-assisted     • Dashboard          • Push notification
  • Social media     • HIPAA docs       • BAA signing      • Test restore     • Monthly email      • SMS alert
  • Tampa Bay Med    • Testimonial      • Trial period     • Go-live call     • Status badge       • Phone dashboard
    Association        video                                                    on reception TV
     │                  │                   │                   │                   │                    │
  PAIN POINT:        PAIN POINT:        PAIN POINT:        PAIN POINT:        PAIN POINT:          PAIN POINT:
  "Không biết        "Cloud có an       "Giá có hợp       "Sợ migrate        "Quên kiểm tra,     "Internet cũng
   bắt đầu           toàn bằng          lý? MSP hiện      làm mất data"      dựa hoàn toàn       mất khi bão?"
   từ đâu"           server tại chỗ?"   tại nói gì?"                          vào hệ thống"
     │                  │                   │                   │                   │                    │
  OPPORTUNITY:       OPPORTUNITY:       OPPORTUNITY:       OPPORTUNITY:       OPPORTUNITY:         OPPORTUNITY:
  Referral           "Your HIPAA        Bundle with        White-glove        "Proof Mode" —       Pre-cache critical
  program cho        compliance         existing MSP       onboarding         export compliance    data trên phone
  bác sĩ             score: A+"         contract           + supervised       report anytime       khi cảnh báo
                                                           test restore                            sớm
```

#### Metrics theo giai đoạn

| Giai đoạn | KPI | Target |
|------------|-----|--------|
| Awareness | Referral rate từ existing customers | >30% |
| Consideration | Demo → Trial conversion | >40% |
| Decision | Trial → Paid conversion | >60% |
| Onboarding | Time to first successful backup | <4 hours |
| Onboarding | Time to tested restore | <24 hours |
| Daily Use | Dashboard daily active check | >80% weekdays |
| Daily Use | Monthly churn | <3% |
| Hurricane | Data safe confirmation time | <15 min after alert |
| Hurricane | Post-storm NPS | >70 |

---

### Journey Map B: Attorney Always-On — "Malpractice Prevention Journey"

```
TRIGGER             RESEARCH            EVALUATE           BUY & SETUP         USE DAILY           CRISIS MODE
(Hurricane near-    (1-2 weeks)         (1 week)           (1-2 weeks)         (Ongoing)           (Hurricane/Outage)
 miss or peer                                                                   
 story)                                                                         
     │                  │                   │                   │                   │                    │
     ▼                  ▼                   ▼                   ▼                   ▼                    ▼
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
│ Near-miss│    │ Google:      │    │ Compare vs   │    │ IT setup +   │    │ Check energy │    │ Evacuate.        │
│ with     │───▶│ "law firm    │───▶│ Backblaze,   │───▶│ 2TB file     │───▶│ savings      │───▶│ Open laptop at   │
│ Milton — │    │ disaster     │    │ Azure. See   │    │ server sync. │    │ dashboard    │    │ hotel. Access    │
│ couldn't │    │ recovery     │    │ SunShift is  │    │ Test VPN     │    │ daily. See   │    │ all case files   │
│ file     │    │ Tampa"       │    │ only one     │    │ remote       │    │ "$142 saved  │    │ via SunShift     │
│ motion   │    │              │    │ with energy  │    │ access.      │    │ this month"  │    │ portal. File     │
│          │    │              │    │ + hurricane  │    │              │    │              │    │ motion on time.  │
└──────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────────┘
     │                  │                   │                   │                   │                    │
  FEELING:           FEELING:           FEELING:           FEELING:            FEELING:             FEELING:
  "Panic —           "Overwhelmed       "This is the       "Nervous about     "Good ROI.           "Thank God.
   this can't        by enterprise      only thing that    2TB migration      Worth every          This paid for
   happen            solutions I        makes sense        taking long"       dollar."             itself."
   again"            can't afford"      for my size"
     │                  │                   │                   │                   │                    │
  OPPORTUNITY:       OPPORTUNITY:       OPPORTUNITY:       OPPORTUNITY:       OPPORTUNITY:         OPPORTUNITY:
  SEO + content      "SMB-sized         Side-by-side       Progress bar       "Court Deadline      Remote file
  marketing for      pricing" page      comparison vs      + ETA for          Protection Score"    browser — 
  "law firm DR"      + ROI calculator   enterprise         initial sync       gamification         feels like
  keywords                              solutions                                                  local server
```

---

### Journey Map C: Number Cruncher — "Seasonal Scaling Journey"

```
TRIGGER             EVALUATE            BUY                TAX SEASON          OFF-SEASON          HURRICANE
(Jan server         (1-2 weeks)         (Before tax        (Jan-Apr)           (May-Dec)           (Jun-Nov overlap)
 slowdown)                              season)
     │                  │                   │                   │                   │                    │
     ▼                  ▼                   ▼                   ▼                   ▼                    ▼
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
│ Server   │    │ Calculate    │    │ Subscribe.   │    │ Cloud burst  │    │ Minimal      │    │ "Tax extension   │
│ can't    │───▶│ cost of new  │───▶│ Tax season   │───▶│ active.      │───▶│ usage.       │───▶│ deadline Oct 15  │
│ handle   │    │ server vs    │    │ plan starts  │    │ 3 extra      │    │ Energy       │    │ + Hurricane =    │
│ 40 new   │    │ SunShift     │    │ immediately. │    │ cloud desks. │    │ arbitrage    │    │ nightmare        │
│ clients  │    │ seasonal.    │    │ Pay-as-you-  │    │ Zero lag.    │    │ only. $89/mo │    │ scenario.        │
│          │    │ SunShift     │    │ scale.       │    │ $350/mo      │    │              │    │ SunShift handles │
│          │    │ wins on ROI  │    │              │    │              │    │              │    │ both."           │
└──────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────────┘
     │                  │                   │                   │                   │                    │
  FEELING:           FEELING:           FEELING:           FEELING:            FEELING:             FEELING:
  "Frustrated —      "Skeptical but     "Makes sense       "Why didn't I      "Is it worth         "This is exactly
   losing revenue    the math           financially.       do this sooner?    keeping?"            why I kept it."
   to hardware"      checks out"        Low risk."         Huge difference."  → ROI report
                                                                              keeps them
```

---

## III. USABILITY TESTING FRAMEWORK

---

### A. Testing Goals

| # | Goal | Metric | Target |
|---|------|--------|--------|
| 1 | Người dùng low-tech (Dr. Worried) hiểu trạng thái hệ thống | Task completion rate: đọc dashboard status | >95% |
| 2 | Setup wizard hoàn thành không cần hỗ trợ IT | Unassisted completion rate | >60% (with MSP: >95%) |
| 3 | "Hurricane Shield" activation hiểu được ngay | Time to understand notification | <10 seconds |
| 4 | Restore process tin cậy | Perceived confidence during restore | >8/10 |
| 5 | Energy savings dashboard tạo engagement | Users check savings weekly | >70% |

### B. Testing Methodology

#### Phase 1: Concept Testing (Pre-MVP)
**Khi nào:** Trước khi code
**Với ai:** 5-8 people (mix Dr. Worried + Attorney)
**Phương pháp:** Clickable prototype (Figma)
**Kịch bản test:**

1. **"Bạn vừa nghe về SunShift. Nhìn vào landing page này 30 giây. SunShift làm gì?"**
   - Đo: First impression accuracy
   - Pass: >80% hiểu đúng value proposition

2. **"Mở dashboard. Hệ thống bạn có ổn không?"**
   - Đo: Time to answer, accuracy
   - Pass: <5 seconds, >90% trả lời đúng

3. **"Bạn nhận được notification bão đang đến. Bạn cần làm gì?"**
   - Đo: Perceived need-to-act (should be: nothing)
   - Pass: >80% hiểu "không cần làm gì, hệ thống tự xử lý"

4. **"Bão qua rồi. Server hỏng. Khôi phục dữ liệu."**
   - Đo: Task completion on restore flow
   - Pass: >70% unassisted completion

#### Phase 2: Prototype Testing (MVP Alpha)
**Khi nào:** Sau MVP đầu tiên
**Với ai:** 8-12 people (đại diện 3 personas)
**Phương pháp:** Moderated usability testing + Think-aloud protocol

**Task Scenarios:**

| # | Task | Persona | Success Criteria | Priority |
|---|------|---------|-----------------|----------|
| T1 | Complete initial setup wizard | All | <15 min, no errors | P0 |
| T2 | Read dashboard and explain system status | Dr. Worried | Correct interpretation in <10s | P0 |
| T3 | Find and understand "Hurricane Shield" status | All | Found in <30s, understood purpose | P0 |
| T4 | View energy savings this month | Attorney, Accountant | Found in <20s, understood metric | P1 |
| T5 | Trigger manual backup | Dr. Worried | Completed in <3 clicks | P1 |
| T6 | Export HIPAA compliance report | Dr. Worried | Found + exported in <60s | P1 |
| T7 | Access files remotely (simulate evacuation) | Attorney | Login + navigate to file in <2 min | P0 |
| T8 | View cost comparison report | Accountant | Found + understood in <30s | P2 |
| T9 | Simulate restore after hurricane | All | Complete flow in <5 min | P0 |
| T10 | Understand billing/usage breakdown | Accountant | Correct interpretation | P2 |

#### Phase 3: Beta Testing (Pre-Launch)
**Khi nào:** 2-4 tuần trước launch
**Với ai:** 15-25 real businesses (Tampa Bay)
**Phương pháp:** Unmoderated real-world usage + surveys + interviews

**Đo lường:**
- System Usability Scale (SUS) — target: >72 (above average)
- Net Promoter Score (NPS) — target: >50
- Task success rate across all core flows — target: >85%
- Time-on-task cho dashboard check — target: <10s
- Support ticket rate — target: <2 per user in first month

### C. Recruitment Criteria

| Persona | Tiêu chí tuyển | Số lượng | Kênh tuyển |
|---------|---------------|----------|------------|
| Dr. Worried | Chủ phòng khám <15 NV, Tampa Bay, có on-prem server | 5-8 | Tampa Bay Medical Association, SBDC |
| Attorney | Partner tại firm <20 NV, Tampa Bay, có file server | 3-5 | Hillsborough County Bar Association |
| Accountant | CPA firm <25 NV, Tampa Bay, seasonal workload | 3-4 | FL Institute of CPAs Tampa chapter |

**Incentive:** $100 gift card + 3 tháng SunShift miễn phí khi launch

### D. Accessibility Considerations

Personas SunShift có đặc thù:
- **Age range 35-57** — Font size minimum 16px, high contrast
- **Low tech proficiency (Dr. Worried: 3/10)** — No jargon, visual indicators, minimal interaction
- **High stress context (hurricane)** — UI phải hoạt động khi người dùng đang panic
- **Mobile usage during emergency** — Touch targets 48px+, offline capability for status

---

## IV. DESIGN PRINCIPLES (Rút ra từ Personas + Journeys)

### 1. "Invisible until needed"
SunShift ngày thường phải "biến mất" — dashboard 3 giây rồi quên. Nhưng khi bão đến, SunShift phải là thứ DUY NHẤT người dùng nghĩ đến.

### 2. "No jargon, ever"
- ❌ "S3 sync to us-east-2 completed"
- ✅ "Your data is safe in Ohio"
- ❌ "EC2 instance provisioned for workload migration"
- ✅ "Cloud computer is ready for your files"

### 3. "Show the money"
Mọi persona đều muốn thấy ROI. Dashboard phải hiển thị "$X saved this month" prominently. Accountant persona đặc biệt cần số liệu chính xác.

### 4. "Trust through proof"
- HIPAA badge hiển thị 24/7
- "Last backup: 3 hours ago ✓" — luôn visible
- "Restore tested: passed ✓" — automated restore testing
- Compliance report exportable 1 click

### 5. "One-hand, one-eye"
Trong hurricane event, user có thể đang lái xe evacuate, đang ở shelter, đang stress. UI phải:
- Readable ở 1 glance
- Operable với 1 tay (mobile)
- Reassuring, không alarming

---

## V. NEXT STEPS — UX RESEARCH ROADMAP

| # | Action | Timeline | Effort | Impact |
|---|--------|----------|--------|--------|
| 1 | **Validate personas qua primary interviews** (10-15 cuộc) | 2-3 tuần | Cao | Rất Cao |
| 2 | **Wireframe MVP dashboard** dựa trên design principles | 1 tuần | Trung bình | Cao |
| 3 | **Concept test** wireframes với 5-8 people | 1 tuần | Trung bình | Cao |
| 4 | **Iterate** dựa trên feedback | 1 tuần | Thấp | Cao |
| 5 | **Prototype** high-fidelity trong Figma | 1-2 tuần | Cao | Trung bình |
| 6 | **Usability test** prototype (Phase 2) | 1 tuần | Trung bình | Rất Cao |
| 7 | **Finalize UX spec** cho development | 1 tuần | Trung bình | Cao |

**Tổng timeline UX research → UX spec:** ~8-10 tuần

---

## VI. APPENDIX: PERSONA COMPARISON MATRIX

| Dimension | Dr. Worried | Attorney Always-On | Number Cruncher |
|-----------|-------------|-------------------|-----------------|
| **Primary driver** | Fear (HIPAA + data loss) | Obligation (court deadlines) | ROI (cost savings) |
| **Emotional trigger** | "My patients' data..." | "Malpractice exposure..." | "The math checks out..." |
| **Tech comfort** | Low (3/10) | Medium (5/10) | Medium-High (6/10) |
| **Decision maker** | Self (practice owner) | Managing partner | Self (CPA owner) |
| **Influencer** | MSP + peer doctors | FL Bar + peer attorneys | Peer CPAs + industry press |
| **Willingness to pay** | $300-500/mo | $200-400/mo | $100-350/mo (seasonal) |
| **Key feature** | HIPAA compliance + DR | Remote file access + DR | Seasonal scaling + savings |
| **Onboarding need** | White-glove (MSP-assisted) | Guided (self + IT) | Self-service (with ROI calc) |
| **Daily engagement** | Glance at status (3s) | Check savings + status | Check ROI numbers |
| **Crisis behavior** | Passive (trust system) | Active (needs file access) | Active (needs compute) |
| **Churn risk** | Low (compliance lock-in) | Medium (if no hurricane) | High (seasonal value only) |
| **Upsell path** | Telehealth cloud | eDiscovery/archival | Tax software cloud hosting |
