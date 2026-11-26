-- ==============================================================================
-- ILMS — BỘ DỮ LIỆU MẪU PHONG PHÚ CHUẨN ĐẠI HỌC VIỆT NAM (PTIT CONTEXT)
-- Hệ quản trị CSDL: MySQL 8.0+ (UTF8MB4, BINARY(16) UUID)
-- Tổng số bảng: 37 bảng (431 bản ghi liên kết chặt chẽ 100% khóa ngoại)
-- Mô hình phân quyền 2 tầng:
--   1. System Role (bảng roles): Chỉ gồm ROLE_ADMIN và ROLE_USER
--   2. Class Role (bảng class_members): OWNER, TEACHER, STUDENT theo từng lớp
-- Mật khẩu mặc định cho mọi tài khoản (BCrypt 10 rounds của 'Password@123'):
--   $2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy
-- ==============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ==============================================================================
-- PHẦN 1: HỆ THỐNG PHÂN QUYỀN VÀ NGƯỜI DÙNG (Bảng 1, 2, 3, 4, 37)
-- ==============================================================================

-- 1. Bảng roles (Chỉ gồm 2 vai trò cấp hệ thống: ROLE_ADMIN và ROLE_USER)
INSERT INTO `roles` (`id`, `code`, `name`, `description`, `created_at`, `updated_at`) VALUES
(UNHEX('11111111111111111111111111111111'), 'ROLE_ADMIN', 'Quản trị viên hệ thống', 'Toàn quyền quản trị người dùng, danh mục học phần, phòng học và cấu hình hệ thống ILMS', NOW(), NOW()),
(UNHEX('22222222222222222222222222222222'), 'ROLE_USER', 'Người dùng tiêu chuẩn', 'Tài khoản người dùng chung (vai trò Chủ lớp / Giảng viên / Sinh viên được định nghĩa theo từng lớp trong bảng class_members)', NOW(), NOW());

-- 3. Bảng permissions (16 quyền hạn chi tiết theo từng phân hệ)
INSERT INTO `permissions` (`id`, `code`, `name`, `module`, `description`, `created_at`, `updated_at`) VALUES
(UNHEX('00000000000000000000000000000001'), 'USER_VIEW', 'Xem người dùng', 'USER', 'Xem thông tin hồ sơ người dùng trong hệ thống', NOW(), NOW()),
(UNHEX('00000000000000000000000000000002'), 'USER_MANAGE', 'Quản lý người dùng', 'USER', 'Tạo mới, khóa, mở khóa và cấp quyền tài khoản hệ thống', NOW(), NOW()),
(UNHEX('00000000000000000000000000000003'), 'COURSE_CREATE', 'Tạo khóa học', 'COURSE', 'Khởi tạo môn học/khóa học mới trong danh mục đào tạo', NOW(), NOW()),
(UNHEX('00000000000000000000000000000004'), 'COURSE_UPDATE', 'Cập nhật khóa học', 'COURSE', 'Chỉnh sửa đề cương, chương và bài giảng khóa học', NOW(), NOW()),
(UNHEX('00000000000000000000000000000005'), 'COURSE_DELETE', 'Xóa khóa học', 'COURSE', 'Xóa mềm học phần khỏi danh mục đào tạo', NOW(), NOW()),
(UNHEX('00000000000000000000000000000006'), 'COURSE_VIEW', 'Xem khóa học', 'COURSE', 'Xem danh sách và nội dung chi tiết khóa học', NOW(), NOW()),
(UNHEX('00000000000000000000000000000007'), 'CLASS_CREATE', 'Tạo lớp học', 'CLASS', 'Mở lớp học phần mới và cấu hình mã tham gia lớp', NOW(), NOW()),
(UNHEX('00000000000000000000000000000008'), 'CLASS_UPDATE', 'Quản lý lớp học', 'CLASS', 'Cập nhật thông tin lớp, duyệt thành viên và gửi lời mời', NOW(), NOW()),
(UNHEX('00000000000000000000000000000009'), 'CLASS_VIEW', 'Xem lớp học', 'CLASS', 'Truy cập không gian lớp học, lịch học và thông báo', NOW(), NOW()),
(UNHEX('00000000000000000000000000000010'), 'MATERIAL_UPLOAD', 'Tải lên tài liệu', 'MATERIAL', 'Đăng tải slide, giáo trình và tài liệu tham khảo', NOW(), NOW()),
(UNHEX('00000000000000000000000000000011'), 'ASSESSMENT_MANAGE', 'Quản lý đánh giá & bài tập', 'ASSESSMENT', 'Giao bài tập, tạo kỳ đánh giá và chấm điểm bài nộp', NOW(), NOW()),
(UNHEX('00000000000000000000000000000012'), 'SUBMISSION_CREATE', 'Nộp bài tập', 'ASSESSMENT', 'Nộp bài tập về nhà, bài tập lớn và làm bài trắc nghiệm', NOW(), NOW()),
(UNHEX('00000000000000000000000000000013'), 'QUESTION_BANK_MANAGE', 'Quản lý ngân hàng câu hỏi', 'EXAM', 'Thêm, sửa, duyệt câu hỏi và tổ chức kỳ thi/quiz', NOW(), NOW()),
(UNHEX('00000000000000000000000000000014'), 'ATTENDANCE_MANAGE', 'Quản lý điểm danh', 'ATTENDANCE', 'Tạo buổi học và điểm danh sinh viên', NOW(), NOW()),
(UNHEX('00000000000000000000000000000015'), 'AI_ASSISTANT_USE', 'Sử dụng trợ lý AI', 'AI', 'Trò chuyện với AI Tutor và xem bản đồ nhiệt kiến thức cá nhân', NOW(), NOW()),
(UNHEX('00000000000000000000000000000016'), 'SYSTEM_CONFIG', 'Cấu hình hệ thống', 'SYSTEM', 'Quản lý phòng học, ca học và tham số vận hành toàn trường', NOW(), NOW());

-- 4. Bảng role_permissions (Liên kết Vai trò hệ thống - Quyền hạn)
INSERT INTO `role_permissions` (`role_id`, `permission_id`, `created_at`) VALUES
-- ROLE_ADMIN: Toàn bộ 16 quyền
(UNHEX('11111111111111111111111111111111'), UNHEX('00000000000000000000000000000001'), NOW()),
(UNHEX('11111111111111111111111111111111'), UNHEX('00000000000000000000000000000002'), NOW()),
(UNHEX('11111111111111111111111111111111'), UNHEX('00000000000000000000000000000003'), NOW()),
(UNHEX('11111111111111111111111111111111'), UNHEX('00000000000000000000000000000004'), NOW()),
(UNHEX('11111111111111111111111111111111'), UNHEX('00000000000000000000000000000005'), NOW()),
(UNHEX('11111111111111111111111111111111'), UNHEX('00000000000000000000000000000006'), NOW()),
(UNHEX('11111111111111111111111111111111'), UNHEX('00000000000000000000000000000007'), NOW()),
(UNHEX('11111111111111111111111111111111'), UNHEX('00000000000000000000000000000008'), NOW()),
(UNHEX('11111111111111111111111111111111'), UNHEX('00000000000000000000000000000009'), NOW()),
(UNHEX('11111111111111111111111111111111'), UNHEX('00000000000000000000000000000010'), NOW()),
(UNHEX('11111111111111111111111111111111'), UNHEX('00000000000000000000000000000011'), NOW()),
(UNHEX('11111111111111111111111111111111'), UNHEX('00000000000000000000000000000012'), NOW()),
(UNHEX('11111111111111111111111111111111'), UNHEX('00000000000000000000000000000013'), NOW()),
(UNHEX('11111111111111111111111111111111'), UNHEX('00000000000000000000000000000014'), NOW()),
(UNHEX('11111111111111111111111111111111'), UNHEX('00000000000000000000000000000015'), NOW()),
(UNHEX('11111111111111111111111111111111'), UNHEX('00000000000000000000000000000016'), NOW()),
-- ROLE_USER: Quyền cơ bản cho người dùng (quyền chi tiết trong từng lớp được kiểm tra qua class_members)
(UNHEX('22222222222222222222222222222222'), UNHEX('00000000000000000000000000000001'), NOW()),
(UNHEX('22222222222222222222222222222222'), UNHEX('00000000000000000000000000000004'), NOW()),
(UNHEX('22222222222222222222222222222222'), UNHEX('00000000000000000000000000000006'), NOW()),
(UNHEX('22222222222222222222222222222222'), UNHEX('00000000000000000000000000000007'), NOW()),
(UNHEX('22222222222222222222222222222222'), UNHEX('00000000000000000000000000000008'), NOW()),
(UNHEX('22222222222222222222222222222222'), UNHEX('00000000000000000000000000000009'), NOW()),
(UNHEX('22222222222222222222222222222222'), UNHEX('00000000000000000000000000000010'), NOW()),
(UNHEX('22222222222222222222222222222222'), UNHEX('00000000000000000000000000000011'), NOW()),
(UNHEX('22222222222222222222222222222222'), UNHEX('00000000000000000000000000000012'), NOW()),
(UNHEX('22222222222222222222222222222222'), UNHEX('00000000000000000000000000000013'), NOW()),
(UNHEX('22222222222222222222222222222222'), UNHEX('00000000000000000000000000000014'), NOW()),
(UNHEX('22222222222222222222222222222222'), UNHEX('00000000000000000000000000000015'), NOW());

-- 2. Bảng users (20 người dùng: 2 Admin, 5 Giảng viên, 13 Sinh viên)
INSERT INTO `users` (`id`, `role_id`, `first_name`, `middle_name`, `last_name`, `email`, `password`, `status`, `created_at`, `updated_at`) VALUES
-- 2 Quản trị viên (ROLE_ADMIN)
(UNHEX('AAAAAAAAAAAAAAAA0000000000000001'), UNHEX('11111111111111111111111111111111'), 'Quân', 'Minh', 'Đỗ', 'admin@ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
(UNHEX('AAAAAAAAAAAAAAAA0000000000000002'), UNHEX('11111111111111111111111111111111'), 'Anh', 'Thị Mai', 'Nguyễn', 'maianh.admin@ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
-- 5 Giảng viên (ROLE_USER ở hệ thống, giữ vai trò OWNER/TEACHER trong class_members)
(UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), UNHEX('22222222222222222222222222222222'), 'Hương', 'Thị', 'Trần', 'huongtt@ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
(UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), UNHEX('22222222222222222222222222222222'), 'Tuấn', 'Anh', 'Lê', 'tuanla@ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
(UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDF'), UNHEX('22222222222222222222222222222222'), 'Hiếu', 'Văn', 'Nguyễn', 'hieunv@ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
(UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD0'), UNHEX('22222222222222222222222222222222'), 'Khánh', 'Quốc', 'Phạm', 'khanhpq@ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
(UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD1'), UNHEX('22222222222222222222222222222222'), 'Bích', 'Thị Ngọc', 'Vũ', 'bichvtn@ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
-- 13 Sinh viên (ROLE_USER ở hệ thống, giữ vai trò STUDENT trong class_members)
(UNHEX('12345678901234567890123456789012'), UNHEX('22222222222222222222222222222222'), 'Nam', 'Hoàng', 'Nguyễn', 'namnh.b24dccn101@stu.ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
(UNHEX('12345678901234567890123456789013'), UNHEX('22222222222222222222222222222222'), 'Linh', 'Phương', 'Phạm', 'linhpp.b24dccn102@stu.ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
(UNHEX('12345678901234567890123456789014'), UNHEX('22222222222222222222222222222222'), 'Đức', 'Văn', 'Vũ', 'ducvv.b24dccn103@stu.ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
(UNHEX('12345678901234567890123456789015'), UNHEX('22222222222222222222222222222222'), 'Trang', 'Thu', 'Hoàng', 'tranght.b24dccn104@stu.ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'PENDING', NOW(), NOW()),
(UNHEX('12345678901234567890123456789016'), UNHEX('22222222222222222222222222222222'), 'Khôi', 'Minh', 'Trần', 'khoitm.b24dccn105@stu.ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
(UNHEX('12345678901234567890123456789017'), UNHEX('22222222222222222222222222222222'), 'Ánh', 'Ngọc', 'Lê', 'anhln.b24dccn106@stu.ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
(UNHEX('12345678901234567890123456789018'), UNHEX('22222222222222222222222222222222'), 'Bảo', 'Quốc', 'Đặng', 'baodq.b24dccn107@stu.ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
(UNHEX('12345678901234567890123456789019'), UNHEX('22222222222222222222222222222222'), 'Tâm', 'Thị Thanh', 'Bùi', 'tambtt.b24dccn108@stu.ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
(UNHEX('12345678901234567890123456789020'), UNHEX('22222222222222222222222222222222'), 'Huy', 'Gia', 'Ngô', 'huyng.b24dccn109@stu.ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
(UNHEX('12345678901234567890123456789021'), UNHEX('22222222222222222222222222222222'), 'Dương', 'Thùy', 'Đinh', 'duongdt.b24dccn110@stu.ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
(UNHEX('12345678901234567890123456789022'), UNHEX('22222222222222222222222222222222'), 'Kiệt', 'Tuấn', 'Lý', 'kietlt.b24dcat015@stu.ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
(UNHEX('12345678901234567890123456789023'), UNHEX('22222222222222222222222222222222'), 'Vy', 'Khánh', 'Hà', 'vyhk.b24dckh022@stu.ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ACTIVE', NOW(), NOW()),
(UNHEX('12345678901234567890123456789024'), UNHEX('22222222222222222222222222222222'), 'Nghĩa', 'Trọng', 'Phan', 'nghiapt.b24dccn199@stu.ptit.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'LOCKED', NOW(), NOW());

-- 37. Bảng verification_tokens (10 bản ghi đủ các loại token và trạng thái)
INSERT INTO `verification_tokens` (`id`, `user_id`, `token`, `email`, `type`, `status`, `expires_at`, `created_at`) VALUES
(UNHEX('F2F2F2F2F2F2F2F2F2F2F2F2F2F2F201'), UNHEX('12345678901234567890123456789012'), 'verify-email-namnh-2026', 'namnh.b24dccn101@stu.ptit.edu.vn', 'EMAIL_VERIFICATION', 'VERIFIED', '2026-09-01 23:59:59', NOW()),
(UNHEX('F2F2F2F2F2F2F2F2F2F2F2F2F2F2F202'), UNHEX('12345678901234567890123456789013'), 'verify-email-linhpp-2026', 'linhpp.b24dccn102@stu.ptit.edu.vn', 'EMAIL_VERIFICATION', 'VERIFIED', '2026-09-01 23:59:59', NOW()),
(UNHEX('F2F2F2F2F2F2F2F2F2F2F2F2F2F2F203'), UNHEX('12345678901234567890123456789014'), 'verify-email-ducvv-2026', 'ducvv.b24dccn103@stu.ptit.edu.vn', 'EMAIL_VERIFICATION', 'VERIFIED', '2026-09-01 23:59:59', NOW()),
(UNHEX('F2F2F2F2F2F2F2F2F2F2F2F2F2F2F204'), UNHEX('12345678901234567890123456789015'), 'verify-email-tranght-2026', 'tranght.b24dccn104@stu.ptit.edu.vn', 'EMAIL_VERIFICATION', 'PENDING', '2026-11-15 23:59:59', NOW()),
(UNHEX('F2F2F2F2F2F2F2F2F2F2F2F2F2F2F205'), UNHEX('12345678901234567890123456789013'), 'reset-pwd-linhpp-8899', 'linhpp.b24dccn102@stu.ptit.edu.vn', 'RESET_PASSWORD', 'VERIFIED', '2026-10-05 12:00:00', NOW()),
(UNHEX('F2F2F2F2F2F2F2F2F2F2F2F2F2F2F206'), UNHEX('12345678901234567890123456789016'), 'reset-pwd-khoitm-1102', 'khoitm.b24dccn105@stu.ptit.edu.vn', 'RESET_PASSWORD', 'EXPIRED', '2026-09-20 08:30:00', NOW()),
(UNHEX('F2F2F2F2F2F2F2F2F2F2F2F2F2F2F207'), UNHEX('12345678901234567890123456789018'), 'reset-pwd-baodq-4410', 'baodq.b24dccn107@stu.ptit.edu.vn', 'RESET_PASSWORD', 'PENDING', '2026-10-25 18:00:00', NOW()),
(UNHEX('F2F2F2F2F2F2F2F2F2F2F2F2F2F2F208'), UNHEX('12345678901234567890123456789024'), 'reset-pwd-nghiapt-0001', 'nghiapt.b24dccn199@stu.ptit.edu.vn', 'RESET_PASSWORD', 'REVOKED', '2026-09-10 10:00:00', NOW()),
(UNHEX('F2F2F2F2F2F2F2F2F2F2F2F2F2F2F209'), UNHEX('12345678901234567890123456789022'), 'verify-email-kietlt-2026', 'kietlt.b24dcat015@stu.ptit.edu.vn', 'EMAIL_VERIFICATION', 'VERIFIED', '2026-09-02 23:59:59', NOW()),
(UNHEX('F2F2F2F2F2F2F2F2F2F2F2F2F2F2F210'), UNHEX('12345678901234567890123456789023'), 'verify-email-vyhk-2026', 'vyhk.b24dckh022@stu.ptit.edu.vn', 'EMAIL_VERIFICATION', 'VERIFIED', '2026-09-02 23:59:59', NOW());


-- ==============================================================================
-- PHẦN 2: QUẢN LÝ KHÓA HỌC VÀ LỚP HỌC (Bảng 5, 6, 7, 8, 9, 10, 24, 26)
-- ==============================================================================

-- 5. Bảng courses (6 học phần đại học chuẩn chương trình CNTT / KHMT / ATTT)
INSERT INTO `courses` (`id`, `course_code`, `name`, `description`, `visibility`, `owner_id`, `created_at`, `updated_at`) VALUES
(UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), 'INT1306', 'Cơ sở dữ liệu', 'Học phần cung cấp kiến thức nền tảng về mô hình dữ liệu thực thể - liên kết (ERD), mô hình quan hệ, đại số quan hệ, ngôn ngữ truy vấn SQL, phụ thuộc hàm và chuẩn hóa cơ sở dữ liệu (1NF, 2NF, 3NF, BCNF).', 'PUBLIC', UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), NOW(), NOW()),
(UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFE'), 'INT1434', 'Lập trình Web với Spring Boot & Next.js', 'Phát triển hệ thống Web doanh nghiệp theo kiến trúc phân tầng với Spring Boot 3.3, Spring Security JWT HttpOnly Cookie, JPA Specification, Flyway và giao diện Next.js App Router.', 'PUBLIC', UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), NOW(), NOW()),
(UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFD'), 'INT1303', 'Cấu trúc dữ liệu và Giải thuật', 'Nghiên cứu các cấu trúc dữ liệu cốt lõi (Danh sách liên kết, Ngăn xếp, Hàng đợi, Cây nhị phân tìm kiếm, Cây AVL, Bảng băm, Đồ thị) và các kỹ thuật thiết kế thuật toán (Chia để trị, Tham lam, Quy hoạch động).', 'PUBLIC', UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDF'), NOW(), NOW()),
(UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFC'), 'INT1405', 'Trí tuệ nhân tạo và Ứng dụng LLM', 'Nhập môn Trí tuệ nhân tạo, tìm kiếm có thông tin (A*), học máy cơ bản, xử lý ngôn ngữ tự nhiên và xây dựng hệ thống Retrieval-Augmented Generation (RAG) với mô hình ngôn ngữ lớn.', 'PUBLIC', UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD1'), NOW(), NOW()),
(UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFB'), 'INT1332', 'Mạng máy tính và Truyền số liệu', 'Kiến trúc phân tầng OSI và TCP/IP, định tuyến gói tin (OSPF, BGP), giao thức tầng giao vận (TCP/UDP), DNS, HTTP/3 và bảo mật mạng cơ bản.', 'PUBLIC', UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD0'), NOW(), NOW()),
(UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFA'), 'INT1450', 'Chuyên đề Hệ quản trị CSDL Phân tán & Hiệu năng cao', 'Chuyên đề nâng cao nội bộ dành cho nhóm nghiên cứu tối ưu hóa truy vấn, đánh chỉ mục B+Tree, phân mảnh dữ liệu, nhân bản và giao dịch phân tán 2PC.', 'PRIVATE', UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), NOW(), NOW());

-- 6. Bảng classes (6 lớp học tín chỉ)
INSERT INTO `classes` (`id`, `class_code`, `name`, `title`, `description`, `visibility`, `require_approval`, `is_code_active`, `owner_id`, `start_at`, `end_at`, `created_at`, `updated_at`) VALUES
(UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), 'INT1306-01', 'Lớp D24CQCN01-B (Nhóm 01)', 'Cơ sở dữ liệu - Học kỳ I (2026-2027) - Nhóm 01', 'Lớp tín chỉ môn Cơ sở dữ liệu sáng Thứ Bảy dành cho sinh viên khóa D24 ngành Công nghệ thông tin 1.', 'PUBLIC', 1, 1, UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), '2026-08-15', '2026-12-30', NOW(), NOW()),
(UNHEX('AAAA1111AAAA1111AAAA1111AAAA1112'), 'INT1306-02', 'Lớp D24CQCN02-B (Nhóm 02)', 'Cơ sở dữ liệu - Học kỳ I (2026-2027) - Nhóm 02', 'Lớp tín chỉ môn Cơ sở dữ liệu chiều Thứ Bảy dành cho sinh viên khóa D24 ngành Công nghệ thông tin 2.', 'PUBLIC', 0, 1, UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), '2026-08-15', '2026-12-30', NOW(), NOW()),
(UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), 'INT1434-01', 'Lớp D24CQCN01-B (Web Nhóm 01)', 'Lập trình Web với Spring Boot & Next.js - Học kỳ I (2026-2027)', 'Lớp học phần thực hành phát triển dự án Web Fullstack theo nhóm 3-4 sinh viên.', 'PRIVATE', 1, 1, UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), '2026-08-15', '2026-12-30', NOW(), NOW()),
(UNHEX('AAAA1111AAAA1111AAAA1111AAAA3333'), 'INT1303-01', 'Lớp D24CQCN03-B (CTDL Nhóm 01)', 'Cấu trúc dữ liệu và Giải thuật - Học kỳ I (2026-2027)', 'Lớp học lý thuyết kết hợp chấm bài tự động các bài toán cấu trúc dữ liệu và giải thuật.', 'PUBLIC', 0, 1, UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDF'), '2026-08-15', '2026-12-30', NOW(), NOW()),
(UNHEX('AAAA1111AAAA1111AAAA1111AAAA4444'), 'INT1405-01', 'Lớp D24CQKH01-B (AI & LLM Nhóm 01)', 'Trí tuệ nhân tạo và Ứng dụng LLM - Học kỳ I (2026-2027)', 'Lớp chuyên ngành Khoa học máy tính & Trí tuệ nhân tạo ứng dụng.', 'PUBLIC', 1, 1, UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD1'), '2026-08-15', '2026-12-30', NOW(), NOW()),
(UNHEX('AAAA1111AAAA1111AAAA1111AAAA5555'), 'INT1332-01', 'Lớp D24CQAT01-B (Mạng MT Nhóm 01)', 'Mạng máy tính và Truyền số liệu - Học kỳ I (2026-2027)', 'Lớp chuyên ngành An toàn thông tin thực hành cấu hình định tuyến và phân tích gói tin Wireshark.', 'PRIVATE', 1, 0, UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD0'), '2026-08-15', '2026-12-30', NOW(), NOW());

-- 8. Bảng class_courses (Liên kết Lớp học - Khóa học)
INSERT INTO `class_courses` (`id`, `class_id`, `course_id`, `assigned_at`, `status`) VALUES
(UNHEX('CCCC1111CCCC1111CCCC1111CCCC1111'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), NOW(), 'ACTIVE'),
(UNHEX('CCCC1111CCCC1111CCCC1111CCCC1112'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFA'), NOW(), 'ACTIVE'),
(UNHEX('CCCC1111CCCC1111CCCC1111CCCC1113'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1112'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), NOW(), 'ACTIVE'),
(UNHEX('CCCC1111CCCC1111CCCC1111CCCC2222'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFE'), NOW(), 'ACTIVE'),
(UNHEX('CCCC1111CCCC1111CCCC1111CCCC3333'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA3333'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFD'), NOW(), 'ACTIVE'),
(UNHEX('CCCC1111CCCC1111CCCC1111CCCC4444'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA4444'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFC'), NOW(), 'ACTIVE'),
(UNHEX('CCCC1111CCCC1111CCCC1111CCCC5555'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA5555'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFB'), NOW(), 'ACTIVE');

-- 7. Bảng class_members (32 bản ghi thành viên lớp — thể hiện rõ tính linh hoạt của OWNER / TEACHER / STUDENT)
INSERT INTO `class_members` (`id`, `class_id`, `user_id`, `role`, `status`, `joined_at`) VALUES
-- Lớp 1: INT1306-01 (Cơ sở dữ liệu Nhóm 01 — 1 OWNER, 1 TEACHER trợ giảng, 8 STUDENT)
(UNHEX('BBBB1111BBBB1111BBBB1111BBBB1101'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'OWNER', 'ACTIVE', NOW()),
(UNHEX('BBBB1111BBBB1111BBBB1111BBBB1102'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 'TEACHER', 'ACTIVE', NOW()),
(UNHEX('BBBB2222BBBB2222BBBB2222BBBB2222'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('12345678901234567890123456789012'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB2222BBBB2222BBBB2222BBBB2223'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('12345678901234567890123456789013'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB2222BBBB2222BBBB2222BBBB2224'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('12345678901234567890123456789014'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB2222BBBB2222BBBB2222BBBB2225'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('12345678901234567890123456789016'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB2222BBBB2222BBBB2222BBBB2226'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('12345678901234567890123456789017'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB2222BBBB2222BBBB2222BBBB2227'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('12345678901234567890123456789018'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB2222BBBB2222BBBB2222BBBB2228'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('12345678901234567890123456789019'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB2222BBBB2222BBBB2222BBBB2229'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('12345678901234567890123456789020'), 'STUDENT', 'PENDING', NOW()),
-- Lớp 2: INT1306-02 (Cơ sở dữ liệu Nhóm 02 — 1 OWNER, 4 STUDENT)
(UNHEX('BBBB1112BBBB1112BBBB1112BBBB1101'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1112'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'OWNER', 'ACTIVE', NOW()),
(UNHEX('BBBB1112BBBB1112BBBB1112BBBB1102'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1112'), UNHEX('12345678901234567890123456789021'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB1112BBBB1112BBBB1112BBBB1103'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1112'), UNHEX('12345678901234567890123456789022'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB1112BBBB1112BBBB1112BBBB1104'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1112'), UNHEX('12345678901234567890123456789023'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB1112BBBB1112BBBB1112BBBB1105'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1112'), UNHEX('12345678901234567890123456789015'), 'STUDENT', 'PENDING', NOW()),
-- Lớp 3: INT1434-01 (Lập trình Web — 1 OWNER, 1 TEACHER, 6 STUDENT)
(UNHEX('BBBB3333BBBB3333BBBB3333BBBB3301'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 'OWNER', 'ACTIVE', NOW()),
(UNHEX('BBBB3333BBBB3333BBBB3333BBBB3302'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'TEACHER', 'ACTIVE', NOW()),
(UNHEX('BBBB3333BBBB3333BBBB3333BBBB3303'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('12345678901234567890123456789012'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB3333BBBB3333BBBB3333BBBB3304'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('12345678901234567890123456789013'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB3333BBBB3333BBBB3333BBBB3305'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('12345678901234567890123456789014'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB3333BBBB3333BBBB3333BBBB3306'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('12345678901234567890123456789016'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB3333BBBB3333BBBB3333BBBB3307'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('12345678901234567890123456789017'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB3333BBBB3333BBBB3333BBBB3308'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('12345678901234567890123456789018'), 'STUDENT', 'ACTIVE', NOW()),
-- Lớp 4: INT1303-01 (CTDL & Giải thuật — 1 OWNER, 4 STUDENT)
(UNHEX('BBBB4444BBBB4444BBBB4444BBBB4401'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA3333'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDF'), 'OWNER', 'ACTIVE', NOW()),
(UNHEX('BBBB4444BBBB4444BBBB4444BBBB4402'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA3333'), UNHEX('12345678901234567890123456789012'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB4444BBBB4444BBBB4444BBBB4403'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA3333'), UNHEX('12345678901234567890123456789019'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB4444BBBB4444BBBB4444BBBB4404'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA3333'), UNHEX('12345678901234567890123456789020'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB4444BBBB4444BBBB4444BBBB4405'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA3333'), UNHEX('12345678901234567890123456789021'), 'STUDENT', 'ACTIVE', NOW()),
-- Lớp 5: INT1405-01 (AI & LLM — TS. Bích là OWNER, ThS. Khánh tham gia làm STUDENT bồi dưỡng, SV Nguyễn Hoàng Nam làm TEACHER trợ giảng)
(UNHEX('BBBB5555BBBB5555BBBB5555BBBB5501'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA4444'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD1'), 'OWNER', 'ACTIVE', NOW()),
(UNHEX('BBBB5555BBBB5555BBBB5555BBBB5502'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA4444'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD0'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB5555BBBB5555BBBB5555BBBB5503'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA4444'), UNHEX('12345678901234567890123456789023'), 'STUDENT', 'ACTIVE', NOW()),
(UNHEX('BBBB5555BBBB5555BBBB5555BBBB5504'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA4444'), UNHEX('12345678901234567890123456789012'), 'TEACHER', 'ACTIVE', NOW()),
-- Lớp 6: INT1332-01 (Mạng máy tính — ThS. Khánh là OWNER, Lý Tuấn Kiệt là STUDENT)
(UNHEX('BBBB6666BBBB6666BBBB6666BBBB6601'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA5555'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD0'), 'OWNER', 'ACTIVE', NOW()),
(UNHEX('BBBB6666BBBB6666BBBB6666BBBB6602'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA5555'), UNHEX('12345678901234567890123456789022'), 'STUDENT', 'ACTIVE', NOW());

-- 9. Bảng chapters (12 chương học trải đều qua các môn)
INSERT INTO `chapters` (`id`, `course_id`, `title`, `description`, `order_index`, `is_published`, `created_at`, `updated_at`) VALUES
-- Môn INT1306: Cơ sở dữ liệu (4 chương)
(UNHEX('DDDD1111DDDD1111DDDD1111DDDD1111'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), 'Chương 1: Tổng quan về Hệ quản trị Cơ sở dữ liệu', 'Các khái niệm cơ bản về CSDL, Hệ QTCSDL, kiến trúc 3 mức ANSI/SPARC và mô hình thực thể - liên kết (ERD).', 1, 1, NOW(), NOW()),
(UNHEX('DDDD1111DDDD1111DDDD1111DDDD2222'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), 'Chương 2: Mô hình dữ liệu quan hệ và Ngôn ngữ SQL', 'Quan hệ, bộ, thuộc tính, khóa chính, khóa ngoại, đại số quan hệ và truy vấn SQL trên MySQL 8.0.', 2, 1, NOW(), NOW()),
(UNHEX('DDDD1111DDDD1111DDDD1111DDDD3333'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), 'Chương 3: Phụ thuộc hàm và Chuẩn hóa Cơ sở dữ liệu', 'Phụ thuộc hàm, hệ tiên đề Armstrong, bao đóng tập thuộc tính và các dạng chuẩn 1NF, 2NF, 3NF, BCNF.', 3, 1, NOW(), NOW()),
(UNHEX('DDDD1111DDDD1111DDDD1111DDDD4444'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), 'Chương 4: Giao dịch (Transaction), Khóa (Locking) và Tối ưu hóa Index', 'Tính chất ACID của giao dịch, các mức cô lập (Isolation Levels), chỉ mục B+Tree và tối ưu hóa kế hoạch thực thi truy vấn.', 4, 1, NOW(), NOW()),
-- Môn INT1434: Lập trình Web với Spring Boot & Next.js (3 chương)
(UNHEX('DDDD2222DDDD2222DDDD2222DDDD1111'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFE'), 'Chương 1: Kiến trúc Phân tầng trong Spring Boot 3 & RESTful API', 'Tổ chức Controller, Service, Repository, DTO, ModelMapper, Bean Validation và xử lý ngoại lệ tập trung với @RestControllerAdvice.', 1, 1, NOW(), NOW()),
(UNHEX('DDDD2222DDDD2222DDDD2222DDDD2222'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFE'), 'Chương 2: Spring Data JPA, Flyway Migration & Bảo mật JWT HttpOnly Cookie', 'Quản lý phiên bản schema với Flyway, phòng chống lỗi N+1 query, xác thực JWT qua HttpOnly Cookie và phân quyền RBAC 2 tầng.', 2, 1, NOW(), NOW()),
(UNHEX('DDDD2222DDDD2222DDDD2222DDDD3333'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFE'), 'Chương 3: Xây dựng Frontend Hiện đại với Next.js App Router & TanStack Query', 'Kiến trúc Feature-Driven, Server vs Client Components, quản lý trạng thái với TanStack Query + Zustand và kiểm chứng form với React Hook Form + Zod.', 3, 1, NOW(), NOW()),
-- Môn INT1303: Cấu trúc dữ liệu và Giải thuật (3 chương)
(UNHEX('DDDD3333DDDD3333DDDD3333DDDD1111'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFD'), 'Chương 1: Đánh giá độ phức tạp thuật toán, Đệ quy và Sắp xếp', 'Ký hiệu tiệm cận Big-O, Big-Omega, Big-Theta và các thuật toán QuickSort, MergeSort, HeapSort.', 1, 1, NOW(), NOW()),
(UNHEX('DDDD3333DDDD3333DDDD3333DDDD2222'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFD'), 'Chương 2: Cấu trúc Cây (BST, AVL) và Bảng băm (Hash Table)', 'Cây nhị phân tìm kiếm, phép quay cân bằng cây AVL và xử lý đụng độ trong bảng băm.', 2, 1, NOW(), NOW()),
(UNHEX('DDDD3333DDDD3333DDDD3333DDDD3333'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFD'), 'Chương 3: Lý thuyết Đồ thị và Quy hoạch động', 'Duyệt đồ thị BFS/DFS, tìm đường đi ngắn nhất Dijkstra, Bellman-Ford, cây khung nhỏ nhất Kruskal/Prim và bài toán cái túi (Knapsack).', 3, 1, NOW(), NOW()),
-- Môn INT1405: Trí tuệ nhân tạo và Ứng dụng LLM (2 chương)
(UNHEX('DDDD4444DDDD4444DDDD4444DDDD1111'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFC'), 'Chương 1: Giải thuật tìm kiếm A*, Minimax và Học máy cơ sở', 'Không gian trạng thái, hàm đánh giá heuristic, mạng nơ-ron nhân tạo và huấn luyện mô hình phân loại.', 1, 1, NOW(), NOW()),
(UNHEX('DDDD4444DDDD4444DDDD4444DDDD2222'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFC'), 'Chương 2: Vector Embedding và Kiến trúc RAG cho Hệ thống Giáo dục', 'Chia nhỏ văn bản (Chunking), biểu diễn ngữ nghĩa bằng Vector Embedding, tìm kiếm tương đồng và kết hợp ngữ cảnh vào LLM.', 2, 1, NOW(), NOW());

-- 10. Bảng lessons (16 bài học chi tiết)
INSERT INTO `lessons` (`id`, `chapter_id`, `title`, `content`, `lesson_type`, `video_url`, `duration_minutes`, `order_index`, `is_published`, `created_at`, `updated_at`) VALUES
-- Bài học môn Cơ sở dữ liệu
(UNHEX('EEEE1111EEEE1111EEEE1111EEEE1111'), UNHEX('DDDD1111DDDD1111DDDD1111DDDD1111'), 'Bài 1.1: Khái niệm CSDL và Kiến trúc 3 lược đồ ANSI/SPARC', '<p>Tìm hiểu sự khác biệt giữa hệ thống xử lý file truyền thống và Hệ quản trị CSDL (DBMS), cùng 3 mức trừu tượng: Lược đồ ngoài, Lược đồ quan niệm và Lược đồ trong.</p>', 'VIDEO', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 45, 1, 1, NOW(), NOW()),
(UNHEX('EEEE1111EEEE1111EEEE1111EEEE1112'), UNHEX('DDDD1111DDDD1111DDDD1111DDDD1111'), 'Bài 1.2: Thiết kế sơ đồ Thực thể - Liên kết (ERD) và Chuyển đổi sang Quan hệ', '<p>Hướng dẫn xác định tập thực thể mạnh/yếu, thuộc tính khóa, thuộc tính đa trị, mối kết hợp 1-1, 1-N, N-N và 7 quy tắc ánh xạ sang lược đồ quan hệ.</p>', 'VIDEO', 'https://www.youtube.com/watch?v=QpdhBUYk7Kk', 55, 2, 1, NOW(), NOW()),
(UNHEX('EEEE1111EEEE1111EEEE1111EEEE2221'), UNHEX('DDDD1111DDDD1111DDDD1111DDDD2222'), 'Bài 2.1: Đại số quan hệ và Các phép toán Tập hợp, Kết nối (Join)', '<p>Phép chọn (Sigma), phép chiếu (Pi), tích Đề-các, phép kết nối tự nhiên (Natural Join), kết nối ngoài (Outer Join) và phép chia quan hệ.</p>', 'VIDEO', 'https://www.youtube.com/watch?v=7S_tz1z_5bA', 50, 1, 1, NOW(), NOW()),
(UNHEX('EEEE1111EEEE1111EEEE1111EEEE2222'), UNHEX('DDDD1111DDDD1111DDDD1111DDDD2222'), 'Bài 2.2: Truy vấn SQL nâng cao với GROUP BY, HAVING, Subquery và Window Functions', '<p>Thực hành viết câu lệnh SQL phức tạp trên MySQL 8.0: CTE (WITH clause), ROW_NUMBER(), RANK(), DENSE_RANK() và tối ưu điều kiện lọc.</p>', 'VIDEO', 'https://www.youtube.com/watch?v=HXV3zeQKqGY', 65, 2, 1, NOW(), NOW()),
(UNHEX('EEEE1111EEEE1111EEEE1111EEEE3331'), UNHEX('DDDD1111DDDD1111DDDD1111DDDD3333'), 'Bài 3.1: Phụ thuộc hàm, Hệ tiên đề Armstrong và Bao đóng tập thuộc tính', '<p>Định nghĩa phụ thuộc hàm X -> Y, 3 tiên đề Armstrong (Phản xạ, Gia tăng, Bắc cầu), thuật toán tìm bao đóng X+ và xác định tất cả các khóa ứng viên của lược đồ.</p>', 'VIDEO', 'https://www.youtube.com/watch?v=GFQaEYEc8_8', 60, 1, 1, NOW(), NOW()),
(UNHEX('EEEE1111EEEE1111EEEE1111EEEE3332'), UNHEX('DDDD1111DDDD1111DDDD1111DDDD3333'), 'Bài 3.2: Các dạng chuẩn 1NF, 2NF, 3NF, BCNF và Phân rã Bảo toàn thông tin', '<p>Phân biệt phụ thuộc hàm bộ phận (vi phạm 2NF) và phụ thuộc hàm bắc cầu (vi phạm 3NF), cùng thuật toán kiểm tra phép tách không mất thông tin (Lossless-join decomposition).</p>', 'VIDEO', 'https://www.youtube.com/watch?v=UrYLYV7WSHM', 60, 2, 1, NOW(), NOW()),
(UNHEX('EEEE1111EEEE1111EEEE1111EEEE4441'), UNHEX('DDDD1111DDDD1111DDDD1111DDDD4444'), 'Bài 4.1: Giao dịch ACID, Mức cô lập (Isolation Levels) và Chỉ mục B+Tree', '<p>Phân tích các hiện tượng đọc bẩn (Dirty Read), đọc không lặp lại (Non-repeatable Read), đọc bóng ma (Phantom Read) và cấu trúc cây B+Tree trong InnoDB.</p>', 'VIDEO', 'https://www.youtube.com/watch?v=aZjYr87r1b8', 55, 1, 1, NOW(), NOW()),
-- Bài học môn Lập trình Web
(UNHEX('EEEE2222EEEE2222EEEE2222EEEE1111'), UNHEX('DDDD2222DDDD2222DDDD2222DDDD1111'), 'Bài 1.1: Thiết kế RESTful API chuẩn với ApiResponse, PageResponse và GlobalExceptionHandler', '<p>Chuẩn hóa cấu trúc phản hồi JSON giữa Spring Boot và Next.js, tách biệt DTO và Entity, xử lý lỗi tập trung qua ErrorCode và SuccessCode.</p>', 'VIDEO', 'https://www.youtube.com/watch?v=vtPkZShrvXQ', 50, 1, 1, NOW(), NOW()),
(UNHEX('EEEE2222EEEE2222EEEE2222EEEE2221'), UNHEX('DDDD2222DDDD2222DDDD2222DDDD2222'), 'Bài 2.1: Xác thực JWT qua HttpOnly Cookie và Phân quyền 2 tầng (System Role + Class Role)', '<p>Cài đặt JwtAuthenticationFilter tự động làm mới token, kết hợp @PreAuthorize cho quyền hệ thống và kiểm tra vai trò OWNER/TEACHER/STUDENT trong bảng class_members.</p>', 'VIDEO', 'https://www.youtube.com/watch?v=KxqlJblhzfI', 65, 1, 1, NOW(), NOW()),
(UNHEX('EEEE2222EEEE2222EEEE2222EEEE2222'), UNHEX('DDDD2222DDDD2222DDDD2222DDDD2222'), 'Bài 2.2: Phòng chống lỗi N+1 Query trong Hibernate khi tắt Open-Session-In-View', '<p>Tại sao phải đặt spring.jpa.open-in-view=false và cách sử dụng @EntityGraph, JOIN FETCH cùng JPA Specification cho truy vấn động.</p>', 'VIDEO', 'https://www.youtube.com/watch?v=8SGI_XS5OPw', 55, 2, 1, NOW(), NOW()),
(UNHEX('EEEE2222EEEE2222EEEE2222EEEE3331'), UNHEX('DDDD2222DDDD2222DDDD2222DDDD3333'), 'Bài 3.1: Kiến trúc Feature-Driven trên Next.js App Router với TanStack Query & Zod', '<p>Tổ chức thư mục src/features/<name>, quản lý Query Key Factory, xác thực dữ liệu hai chiều với Zod schema và xử lý trạng thái bất đồng bộ.</p>', 'VIDEO', 'https://www.youtube.com/watch?v=wm5gMKuwSYk', 60, 1, 1, NOW(), NOW()),
-- Bài học môn CTDL & Giải thuật
(UNHEX('EEEE3333EEEE3333EEEE3333EEEE1111'), UNHEX('DDDD3333DDDD3333DDDD3333DDDD1111'), 'Bài 1.1: Phân tích độ phức tạp tiệm cận và Thuật toán QuickSort, MergeSort', '<p>Định lý thợ (Master Theorem) cho hệ thức đệ quy và so sánh trường hợp xấu nhất/trung bình của QuickSort với MergeSort.</p>', 'VIDEO', 'https://www.youtube.com/watch?v=Hoixgm4-P4M', 50, 1, 1, NOW(), NOW()),
(UNHEX('EEEE3333EEEE3333EEEE3333EEEE2221'), UNHEX('DDDD3333DDDD3333DDDD3333DDDD2222'), 'Bài 2.1: Cây nhị phân tìm kiếm cân bằng AVL và các phép quay LL, RR, LR, RL', '<p>Cài đặt thao tác thêm/xóa nút trên cây AVL bảo đảm chiều cao luôn đạt O(log N).</p>', 'VIDEO', 'https://www.youtube.com/watch?v=jDM6_TnYIqE', 55, 1, 1, NOW(), NOW()),
(UNHEX('EEEE3333EEEE3333EEEE3333EEEE3331'), UNHEX('DDDD3333DDDD3333DDDD3333DDDD3333'), 'Bài 3.1: Thuật toán Dijkstra với Hàng đợi ưu tiên (Priority Queue) và Quy hoạch động', '<p>Tìm đường đi ngắn nhất từ một đỉnh nguồn trên đồ thị trọng số không âm và giải bài toán cái túi 0/1 bằng bảng quy hoạch động.</p>', 'VIDEO', 'https://www.youtube.com/watch?v=XB4MIexjvY0', 60, 1, 1, NOW(), NOW()),
-- Bài học môn Trí tuệ nhân tạo & LLM
(UNHEX('EEEE4444EEEE4444EEEE4444EEEE1111'), UNHEX('DDDD4444DDDD4444DDDD4444DDDD1111'), 'Bài 1.1: Giải thuật tìm kiếm A* (A-Star) và tính chấp nhận được của hàm Heuristic', '<p>Chứng minh tính tối ưu của giải thuật A* khi hàm đánh giá h(n) không vượt quá chi phí thực tế h*(n).</p>', 'VIDEO', 'https://www.youtube.com/watch?v=ySN5Wnu88nE', 45, 1, 1, NOW(), NOW()),
(UNHEX('EEEE4444EEEE4444EEEE4444EEEE2221'), UNHEX('DDDD4444DDDD4444DDDD4444DDDD2222'), 'Bài 2.1: Xây dựng hệ thống Hỏi đáp Giáo trình thông minh với RAG và Bản đồ nhiệt Kiến thức', '<p>Quy trình băm nhỏ tài liệu học tập (material_chunks), truy xuất đoạn văn liên quan và tổng hợp câu trả lời có trích dẫn nguồn chính xác.</p>', 'VIDEO', 'https://www.youtube.com/watch?v=T-D1OfcDW1M', 65, 1, 1, NOW(), NOW());

-- 24. Bảng class_announcements (8 thông báo lớp học thực tế)
INSERT INTO `class_announcements` (`id`, `class_id`, `author_id`, `title`, `content`, `is_pinned`, `created_at`, `updated_at`) VALUES
(UNHEX('D1D1D1D1D1D1D1D1D1D1D1D1D1D1D101'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'Thông báo lịch kiểm tra giữa kỳ môn Cơ sở dữ liệu (INT1306-01)', 'Chào các em, lớp INT1306-01 sẽ làm bài kiểm tra giữa kỳ vào Kíp 1 sáng Thứ Bảy tuần tới tại phòng 301-A2. Nội dung ôn tập gồm: Thiết kế ERD, Đại số quan hệ, Truy vấn SQL và Chuẩn hóa lược đồ đến 3NF/BCNF. Các em mang theo thẻ sinh viên và có mặt trước 10 phút!', 1, NOW(), NOW()),
(UNHEX('D1D1D1D1D1D1D1D1D1D1D1D1D1D1D102'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'Hướng dẫn đăng ký đề tài Bài tập lớn & Quy chuẩn nộp báo cáo', 'Mỗi nhóm từ 3-4 sinh viên đăng ký 1 đề tài thiết kế CSDL thực tế (Hệ thống LMS, Quản lý Bệnh viện, Sàn Thương mại điện tử, Quản lý Thư viện số). Báo cáo bắt buộc phải có sơ đồ ERD, từ điển dữ liệu, chứng minh các bảng đạt chuẩn 3NF và file script Flyway/MySQL.', 1, NOW(), NOW()),
(UNHEX('D1D1D1D1D1D1D1D1D1D1D1D1D1D1D103'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 'Lịch phụ đạo thực hành SQL & Giải đáp bài tập Phụ thuộc hàm', 'Thầy Tuấn sẽ mở buổi chữa bài tập thực hành truy vấn SQL nâng cao và thuật toán tìm phủ tối thiểu tại Phòng Lab 402-A3 vào Kíp 2 Thứ Bảy tuần này. Các em chủ động cài đặt sẵn MySQL 8.0 và DBeaver trên máy cá nhân.', 0, NOW(), NOW()),
(UNHEX('D1D1D1D1D1D1D1D1D1D1D1D1D1D1D104'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 'Quy định kiến trúc code bắt buộc cho Đồ án môn Lập trình Web (INT1434)', 'Tất cả các nhóm thực hiện đồ án bắt buộc tuân thủ tài liệu ARCHITECTURE.md: Backend Spring Boot không bao giờ trả trực tiếp Entity ra Controller mà phải bọc trong ApiResponse<T>, còn Frontend Next.js chỉ gọi API qua tầng Service + TanStack Query và validate bằng Zod.', 1, NOW(), NOW()),
(UNHEX('D1D1D1D1D1D1D1D1D1D1D1D1D1D1D105'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 'Lịch bảo vệ tiến độ lần 1 (Milestone 1: Database Flyway & Auth RBAC)', 'Thứ Tư tuần sau các nhóm sẽ demo trực tiếp luồng Đăng nhập JWT HttpOnly Cookie, tự động Refresh Token và phân quyền 2 tầng (ROLE_ADMIN/ROLE_USER kết hợp vai trò trong lớp).', 0, NOW(), NOW()),
(UNHEX('D1D1D1D1D1D1D1D1D1D1D1D1D1D1D106'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA3333'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDF'), 'Mở cổng luyện tập Trắc nghiệm & Bài tập Đồ thị Dijkstra, Cây AVL', 'Thầy đã cập nhật bộ câu hỏi trắc nghiệm và bài tập lập trình Chương 2 & Chương 3 trên hệ thống ILMS. Các em hoàn thành trước 23:59 Chủ Nhật để hệ thống AI tổng hợp bản đồ nhiệt kiến thức trước kỳ thi.', 1, NOW(), NOW()),
(UNHEX('D1D1D1D1D1D1D1D1D1D1D1D1D1D1D107'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA4444'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD1'), 'Tài liệu đọc thêm về Kiến trúc RAG và Đánh giá độ chính xác câu trả lời LLM', 'Cô đã tải lên slide và bài báo khoa học về kỹ thuật Chunking, Hybrid Search (BM25 + Dense Vector) và chống ảo giác (Hallucination) cho LLM trong mục Tài liệu học tập Chương 2.', 1, NOW(), NOW()),
(UNHEX('D1D1D1D1D1D1D1D1D1D1D1D1D1D1D108'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA5555'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD0'), 'Nhắc nhở chuẩn bị bài Lab phân tích bắt gói tin TCP 3-Way Handshake', 'Buổi thực hành tới tại Lab 501-A3 các em sẽ thực hiện bắt gói tin thực tế bằng Wireshark để phân tích cờ SYN, SYN-ACK, ACK và cơ chế chống tắc nghẽn TCP.', 1, NOW(), NOW());

-- 26. Bảng invitations (8 lời mời tham gia lớp học đủ trạng thái PENDING, ACCEPTED, REJECTED)
INSERT INTO `invitations` (`id`, `class_id`, `invite_by`, `email`, `role`, `token`, `status`, `expires_at`, `created_at`) VALUES
(UNHEX('F1F1F1F1F1F1F1F1F1F1F1F1F1F1F101'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'tranght.b24dccn104@stu.ptit.edu.vn', 'STUDENT', 'inv-int1306-tranght-2026', 'PENDING', '2026-10-30 23:59:59', NOW()),
(UNHEX('F1F1F1F1F1F1F1F1F1F1F1F1F1F1F102'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'tuanla@ptit.edu.vn', 'TEACHER', 'inv-int1306-tuanla-2026', 'ACCEPTED', '2026-09-01 23:59:59', NOW()),
(UNHEX('F1F1F1F1F1F1F1F1F1F1F1F1F1F1F103'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 'huongtt@ptit.edu.vn', 'TEACHER', 'inv-int1434-huongtt-2026', 'ACCEPTED', '2026-09-01 23:59:59', NOW()),
(UNHEX('F1F1F1F1F1F1F1F1F1F1F1F1F1F1F104'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 'tambtt.b24dccn108@stu.ptit.edu.vn', 'STUDENT', 'inv-int1434-tambtt-2026', 'PENDING', '2026-10-28 23:59:59', NOW()),
(UNHEX('F1F1F1F1F1F1F1F1F1F1F1F1F1F1F105'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 'kietlt.b24dcat015@stu.ptit.edu.vn', 'STUDENT', 'inv-int1434-kietlt-2026', 'REJECTED', '2026-09-15 23:59:59', NOW()),
(UNHEX('F1F1F1F1F1F1F1F1F1F1F1F1F1F1F106'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA4444'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD1'), 'namnh.b24dccn101@stu.ptit.edu.vn', 'STUDENT', 'inv-int1405-namnh-2026', 'PENDING', '2026-11-05 23:59:59', NOW()),
(UNHEX('F1F1F1F1F1F1F1F1F1F1F1F1F1F1F107'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA4444'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD1'), 'khanhpq@ptit.edu.vn', 'STUDENT', 'inv-int1405-khanhpq-2026', 'ACCEPTED', '2026-09-05 23:59:59', NOW()),
(UNHEX('F1F1F1F1F1F1F1F1F1F1F1F1F1F1F108'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA5555'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD0'), 'ducvv.b24dccn103@stu.ptit.edu.vn', 'STUDENT', 'inv-int1332-ducvv-2026', 'PENDING', '2026-11-10 23:59:59', NOW());


-- ==============================================================================
-- PHẦN 3: LỊCH TRÌNH VÀ ĐIỂM DANH (Bảng 33, 36, 20, 19)
-- ==============================================================================

-- 33. Bảng rooms (6 phòng học & phòng Lab thực hành tại cơ sở Hà Đông - PTIT)
INSERT INTO `rooms` (`id`, `name`, `type`, `description`) VALUES
(UNHEX('1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A01'), 'Phòng 301-A2', 'THEORY', 'Phòng học lý thuyết tầng 3 nhà A2 (sức chứa 90 sinh viên, trang bị máy chiếu Laser và âm thanh không dây)'),
(UNHEX('1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A02'), 'Phòng 405-A2', 'THEORY', 'Phòng học lý thuyết tầng 4 nhà A2 (sức chứa 70 sinh viên)'),
(UNHEX('1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A03'), 'Hội trường 101-A1', 'HALL', 'Giảng đường lớn tầng 1 nhà A1 (sức chứa 200 sinh viên, phục vụ học ghép và hội thảo chuyên đề AI)'),
(UNHEX('1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A04'), 'Phòng Lab 402-A3', 'LAB', 'Phòng máy thực hành CSDL & Công nghệ phần mềm tầng 4 nhà A3 (45 máy Core i7, RAM 32GB, MySQL 8.0, Docker, IntelliJ IDEA)'),
(UNHEX('1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A05'), 'Phòng Lab 501-A3', 'LAB', 'Phòng thực hành Mạng máy tính & An toàn thông tin tầng 5 nhà A3 (trang bị Router/Switch Cisco và máy trạm Kali/Ubuntu)'),
(UNHEX('1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A06'), 'Phòng Lab AI 601-A3', 'LAB', 'Phòng thí nghiệm Trí tuệ nhân tạo & Khoa học dữ liệu tầng 6 nhà A3 (máy chủ GPU NVIDIA phục vụ huấn luyện mô hình và RAG)');

-- 36. Bảng time_slots (6 kíp học tiêu chuẩn trong ngày từ 07:00 đến 19:50)
INSERT INTO `time_slots` (`id`, `name`, `start_time`, `end_time`, `start_shift`, `end_shift`, `created_at`, `updated_at`) VALUES
(UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A01'), 'Kíp 1 (Tiết 1 - 2)', '07:00:00', '08:50:00', 1, 2, NOW(), NOW()),
(UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A02'), 'Kíp 2 (Tiết 3 - 4)', '09:00:00', '10:50:00', 3, 4, NOW(), NOW()),
(UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A03'), 'Kíp 3 (Tiết 5 - 6)', '12:00:00', '13:50:00', 5, 6, NOW(), NOW()),
(UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A04'), 'Kíp 4 (Tiết 7 - 8)', '14:00:00', '15:50:00', 7, 8, NOW(), NOW()),
(UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A05'), 'Kíp 5 (Tiết 9 - 10)', '16:00:00', '17:50:00', 9, 10, NOW(), NOW()),
(UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A06'), 'Kíp 6 (Tiết 11 - 12)', '18:00:00', '19:50:00', 11, 12, NOW(), NOW());

-- 20. Bảng lesson_sessions (10 buổi học trải đều các lớp)
INSERT INTO `lesson_sessions` (`id`, `room_id`, `class_id`, `time_slot_id`, `session_date`, `note`) VALUES
(UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A01'), UNHEX('1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A01'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A01'), '2026-09-19', 'Buổi 1 (CSDL Nhóm 01): Tổng quan Hệ QTCSDL và Thiết kế sơ đồ Thực thể - Liên kết (ERD)'),
(UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A02'), UNHEX('1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A01'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A01'), '2026-09-26', 'Buổi 2 (CSDL Nhóm 01): Mô hình dữ liệu quan hệ, Đại số quan hệ và Ràng buộc toàn vẹn'),
(UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A03'), UNHEX('1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A04'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A02'), '2026-10-03', 'Buổi 3 (CSDL Nhóm 01): Thực hành truy vấn SQL nâng cao (JOIN, GROUP BY, HAVING, Subquery) tại Lab 402-A3'),
(UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A04'), UNHEX('1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A01'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A01'), '2026-10-10', 'Buổi 4 (CSDL Nhóm 01): Phụ thuộc hàm, Tiên đề Armstrong và Chuẩn hóa 1NF, 2NF, 3NF, BCNF'),
(UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A05'), UNHEX('1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A04'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A04'), '2026-10-07', 'Buổi 1 (Web Nhóm 01): Khởi tạo dự án Spring Boot 3.3, cấu hình Flyway, MySQL 8.0 và kiến trúc phân tầng'),
(UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A06'), UNHEX('1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A04'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A04'), '2026-10-14', 'Buổi 2 (Web Nhóm 01): Thực hành Spring Security JWT HttpOnly Cookie và kết nối Next.js App Router'),
(UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A07'), UNHEX('1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A02'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA3333'), UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A02'), '2026-10-08', 'Buổi 1 (CTDL Nhóm 01): Cây nhị phân tìm kiếm cân bằng AVL và Bảng băm'),
(UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A08'), UNHEX('1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A02'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA3333'), UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A02'), '2026-10-15', 'Buổi 2 (CTDL Nhóm 01): Thuật toán tìm đường đi ngắn nhất Dijkstra và Quy hoạch động'),
(UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A09'), UNHEX('1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A06'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA4444'), UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A05'), '2026-10-12', 'Buổi 1 (AI & LLM Nhóm 01): Thực hành xây dựng RAG Pipeline và Vector Embedding tại Lab AI 601-A3'),
(UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A10'), UNHEX('1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A05'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA5555'), UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A03'), '2026-10-13', 'Buổi 1 (Mạng MT Nhóm 01): Phân tích gói tin TCP/UDP và định tuyến OSPF trên Cisco Packet Tracer');

-- 19. Bảng attendances (24 bản ghi điểm danh chi tiết đủ trạng thái PRESENT, LATE, ABSENT, EXCUSED)
INSERT INTO `attendances` (`id`, `session_id`, `user_id`, `status`, `check_in_time`, `note`, `created_at`, `updated_at`) VALUES
-- Điểm danh Buổi 1 CSDL (2026-09-19)
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A01'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A01'), UNHEX('12345678901234567890123456789012'), 'PRESENT', '2026-09-19 06:50:12', 'Đi học đúng giờ', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A02'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A01'), UNHEX('12345678901234567890123456789013'), 'PRESENT', '2026-09-19 06:54:30', 'Đi học đúng giờ', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A03'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A01'), UNHEX('12345678901234567890123456789014'), 'PRESENT', '2026-09-19 06:57:00', 'Đi học đúng giờ', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A04'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A01'), UNHEX('12345678901234567890123456789016'), 'PRESENT', '2026-09-19 06:58:15', 'Đi học đúng giờ', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A05'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A01'), UNHEX('12345678901234567890123456789017'), 'PRESENT', '2026-09-19 06:59:00', 'Đi học đúng giờ', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A06'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A01'), UNHEX('12345678901234567890123456789018'), 'LATE', '2026-09-19 07:18:40', 'Đến muộn 18 phút do hỏng xe buýt tuyến 02', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A07'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A01'), UNHEX('12345678901234567890123456789019'), 'PRESENT', '2026-09-19 06:53:20', 'Đi học đúng giờ', NOW(), NOW()),
-- Điểm danh Buổi 3 Thực hành SQL (2026-10-03)
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A08'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A03'), UNHEX('12345678901234567890123456789012'), 'PRESENT', '2026-10-03 08:52:00', 'Hoàn thành 10/10 câu truy vấn thực hành tại lớp', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A09'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A03'), UNHEX('12345678901234567890123456789013'), 'PRESENT', '2026-10-03 08:55:10', 'Hoàn thành tốt bài thực hành', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A10'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A03'), UNHEX('12345678901234567890123456789014'), 'LATE', '2026-10-03 09:15:30', 'Đến muộn 15 phút do mưa lớn đường Nguyễn Trãi', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A11'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A03'), UNHEX('12345678901234567890123456789016'), 'PRESENT', '2026-10-03 08:50:45', 'Hỗ trợ các bạn trong nhóm cấu hình Docker MySQL', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A12'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A03'), UNHEX('12345678901234567890123456789017'), 'EXCUSED', NULL, 'Xin nghỉ có phép (tham gia đội tuyển Olympic Tin học sinh viên toàn quốc)', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A13'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A03'), UNHEX('12345678901234567890123456789018'), 'ABSENT', NULL, 'Vắng mặt không lý do', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A14'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A03'), UNHEX('12345678901234567890123456789019'), 'PRESENT', '2026-10-03 08:56:00', 'Đi học đúng giờ', NOW(), NOW()),
-- Điểm danh Buổi 4 CSDL (2026-10-10)
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A15'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A04'), UNHEX('12345678901234567890123456789012'), 'PRESENT', '2026-10-10 06:51:00', 'Phát biểu xây dựng bài tích cực trên bảng', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A16'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A04'), UNHEX('12345678901234567890123456789013'), 'PRESENT', '2026-10-10 06:55:20', 'Đi học đúng giờ', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A17'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A04'), UNHEX('12345678901234567890123456789014'), 'PRESENT', '2026-10-10 06:57:10', 'Đi học đúng giờ', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A18'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A04'), UNHEX('12345678901234567890123456789016'), 'PRESENT', '2026-10-10 06:53:00', 'Đi học đúng giờ', NOW(), NOW()),
-- Điểm danh Lớp Lập trình Web Buổi 2 (2026-10-14)
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A19'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A06'), UNHEX('12345678901234567890123456789012'), 'PRESENT', '2026-10-14 13:52:00', 'Demo thành công luồng JWT HttpOnly Cookie', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A20'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A06'), UNHEX('12345678901234567890123456789013'), 'PRESENT', '2026-10-14 13:54:00', 'Hoàn thành cấu hình TanStack Query + Zod', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A21'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A06'), UNHEX('12345678901234567890123456789014'), 'PRESENT', '2026-10-14 13:56:30', 'Có mặt đầy đủ', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A22'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A06'), UNHEX('12345678901234567890123456789016'), 'PRESENT', '2026-10-14 13:51:15', 'Có mặt đầy đủ', NOW(), NOW()),
-- Điểm danh Lớp CTDL & Giải thuật Buổi 1 (2026-10-08)
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A23'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A07'), UNHEX('12345678901234567890123456789012'), 'PRESENT', '2026-10-08 08:53:00', 'Đi học đúng giờ', NOW(), NOW()),
(UNHEX('4A4A4A4A4A4A4A4A4A4A4A4A4A4A4A24'), UNHEX('3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A07'), UNHEX('12345678901234567890123456789019'), 'PRESENT', '2026-10-08 08:55:00', 'Đi học đúng giờ', NOW(), NOW());


-- ==============================================================================
-- PHẦN 4: TÀI LIỆU, BÀI TẬP VÀ ĐÁNH GIÁ (Bảng 11, 15, 12, 13, 14, 25)
-- ==============================================================================

-- 11. Bảng materials (10 tài liệu học tập đa dạng định dạng: pdf, pptx, sql, zip)
INSERT INTO `materials` (`id`, `course_id`, `lesson_id`, `uploaded_by`, `title`, `description`, `file_url`, `file_type`, `file_size_bytes`, `is_downloadable`, `created_at`, `updated_at`) VALUES
(UNHEX('FFFF1111FFFF1111FFFF1111FFFF1101'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), UNHEX('EEEE1111EEEE1111EEEE1111EEEE1111'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'Slide Chương 1 - Tổng quan Hệ QTCSDL & Kiến trúc ANSI-SPARC.pdf', 'Bài giảng chính thức Chương 1 môn Cơ sở dữ liệu (Khoa CNTT1 - PTIT).', 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/materials/csdl_chuong1_tong_quan.pdf', 'pdf', 3145728, 1, NOW(), NOW()),
(UNHEX('FFFF1111FFFF1111FFFF1111FFFF1102'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), UNHEX('EEEE1111EEEE1111EEEE1111EEEE1112'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'Hướng dẫn Thiết kế ERD và 7 Quy tắc Ánh xạ sang Lược đồ Quan hệ.pdf', 'Tài liệu chi tiết kèm 5 bài toán mẫu thiết kế ERD (Quản lý đào tạo tín chỉ, Bệnh viện, Thương mại điện tử).', 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/materials/csdl_chuong1_erd_mapping.pdf', 'pdf', 4194304, 1, NOW(), NOW()),
(UNHEX('FFFF1111FFFF1111FFFF1111FFFF1103'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), UNHEX('EEEE1111EEEE1111EEEE1111EEEE2222'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'Script CSDL mẫu Quản lý Học tập & 50 Câu truy vấn SQL mẫu.sql', 'File script khởi tạo bảng và dữ liệu mẫu trên MySQL 8.0 để sinh viên thực hành JOIN, GROUP BY và Window Functions.', 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/materials/csdl_chuong2_practice_mysql8.sql', 'sql', 524288, 1, NOW(), NOW()),
(UNHEX('FFFF1111FFFF1111FFFF1111FFFF1104'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), UNHEX('EEEE1111EEEE1111EEEE1111EEEE3332'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'Chuyên đề Phụ thuộc hàm, Tiên đề Armstrong & Chuẩn hóa 1NF-2NF-3NF-BCNF.pdf', 'Tài liệu trọng tâm ôn thi giữa kỳ và cuối kỳ phần Phụ thuộc hàm, tìm phủ tối thiểu và phân rã lược đồ.', 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/materials/csdl_chuong3_chuan_hoa_3nf_bcnf.pdf', 'pdf', 5242880, 1, NOW(), NOW()),
(UNHEX('FFFF1111FFFF1111FFFF1111FFFF1105'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), UNHEX('EEEE1111EEEE1111EEEE1111EEEE4441'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'Slide Chương 4 - Giao dịch ACID, Isolation Levels & B+Tree Index.pptx', 'Slide trình chiếu minh họa cơ chế khóa (Locking), MVCC trong InnoDB và cấu trúc chỉ mục B+Tree.', 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/materials/csdl_chuong4_acid_btree.pptx', 'pptx', 6291456, 1, NOW(), NOW()),
(UNHEX('FFFF1111FFFF1111FFFF1111FFFF1106'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFE'), UNHEX('EEEE2222EEEE2222EEEE2222EEEE1111'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 'Tài liệu Kiến trúc Enterprise Spring Boot 3.3 & Next.js App Router.pdf', 'Chuẩn kiến trúc dự án thực tế: quy ước ApiResponse<T>, PageResponse<T>, GlobalExceptionHandler và Feature-Driven Frontend.', 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/materials/web_architecture_guideline.pdf', 'pdf', 2621440, 1, NOW(), NOW()),
(UNHEX('FFFF1111FFFF1111FFFF1111FFFF1107'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFE'), UNHEX('EEEE2222EEEE2222EEEE2222EEEE2221'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 'Source code mẫu Xác thực JWT HttpOnly Cookie & RBAC 2 tầng.zip', 'Project mẫu cấu hình Spring Security 6, TokenProvider, CookieUtils và bộ lọc JwtAuthenticationFilter.', 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/materials/web_spring_jwt_cookie_demo.zip', 'zip', 8388608, 1, NOW(), NOW()),
(UNHEX('FFFF1111FFFF1111FFFF1111FFFF1108'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFD'), UNHEX('EEEE3333EEEE3333EEEE3333EEEE2221'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDF'), 'Giáo trình Cấu trúc dữ liệu Cây AVL, B-Tree và Bảng băm.pdf', 'Phân tích chi tiết 4 phép quay đơn/kép cân bằng cây AVL và bảng độ phức tạp thuật toán.', 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/materials/ctdl_avl_hashtable.pdf', 'pdf', 3670016, 1, NOW(), NOW()),
(UNHEX('FFFF1111FFFF1111FFFF1111FFFF1109'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFD'), UNHEX('EEEE3333EEEE3333EEEE3333EEEE3331'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDF'), 'Tuyển tập 30 bài toán Đồ thị Dijkstra, BFS/DFS và Quy hoạch động.pdf', 'Tổng hợp đề bài và hướng dẫn giải thuật toán đồ thị, quy hoạch động chuẩn thi Olympic Tin học và ICPC.', 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/materials/ctdl_dijkstra_dp_problems.pdf', 'pdf', 4718592, 1, NOW(), NOW()),
(UNHEX('FFFF1111FFFF1111FFFF1111FFFF1110'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFC'), UNHEX('EEEE4444EEEE4444EEEE4444EEEE2221'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD1'), 'Chuyên đề Thiết kế RAG Pipeline & Knowledge Heatmap cho EdTech.pdf', 'Hướng dẫn xây dựng hệ thống trợ lý học tập thông minh dựa trên tài liệu môn học và đánh giá mức độ thành thạo.', 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/materials/ai_rag_knowledge_heatmap.pdf', 'pdf', 5767168, 1, NOW(), NOW());

-- 15. Bảng assignments (8 bài tập về nhà gắn với từng bài học)
INSERT INTO `assignments` (`id`, `lesson_id`, `title`, `description`, `max_score`, `due_date`, `allow_late_submission`, `file_attachment_url`, `created_at`, `updated_at`) VALUES
(UNHEX('DDDD3333DDDD3333DDDD3333DDDD3301'), UNHEX('EEEE1111EEEE1111EEEE1111EEEE1112'), 'Bài tập số 1: Thiết kế sơ đồ ERD và Ánh xạ sang Lược đồ Quan hệ cho Hệ thống Quản lý Bệnh viện', 'Xác định các thực thể (Bệnh nhân, Bác sĩ, Khoa, Hồ sơ khám, Đơn thuốc, Thuốc), thuộc tính khóa, bản số liên kết và chuyển đổi sang các bảng quan hệ có đầy đủ khóa chính/khóa ngoại.', 10.00, '2026-10-05', 1, 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/assignments/bt1_erd_benh_vien.pdf', NOW(), NOW()),
(UNHEX('DDDD3333DDDD3333DDDD3333DDDD3302'), UNHEX('EEEE1111EEEE1111EEEE1111EEEE2222'), 'Bài tập số 2: Thực hành 20 câu truy vấn SQL nâng cao trên MySQL 8.0', 'Viết câu lệnh SQL giải quyết các yêu cầu thống kê doanh thu, tìm top 3 sinh viên điểm cao nhất mỗi lớp bằng DENSE_RANK() và tìm các học phần chưa có sinh viên đăng ký.', 10.00, '2026-10-15', 1, 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/assignments/bt2_sql_nang_cao.pdf', NOW(), NOW()),
(UNHEX('DDDD3333DDDD3333DDDD3333DDDD3303'), UNHEX('EEEE1111EEEE1111EEEE1111EEEE3332'), 'Bài tập số 3: Tìm phủ tối thiểu, Khóa ứng viên và Phân rã lược đồ về chuẩn 3NF/BCNF', 'Cho lược đồ quan hệ R(A,B,C,D,E,G) và tập phụ thuộc hàm F = {AB -> C, C -> A, BC -> D, ACD -> B, D -> EG, BE -> C}. Hãy tìm tất cả khóa ứng viên và phân rã R về 3NF vừa bảo toàn thông tin vừa bảo toàn phụ thuộc hàm.', 10.00, '2026-10-25', 1, 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/assignments/bt3_chuan_hoa_3nf.pdf', NOW(), NOW()),
(UNHEX('DDDD3333DDDD3333DDDD3333DDDD3304'), UNHEX('EEEE1111EEEE1111EEEE1111EEEE4441'), 'Bài tập số 4: Phân tích Lịch biểu Giao dịch (Schedule) và Tối ưu hóa Composite Index', 'Kiểm tra tính khả tuần tự xung đột (Conflict-Serializable) bằng đồ thị ưu tiên và thiết kế Composite Index tối ưu cho bảng class_members, attendances.', 10.00, '2026-11-05', 0, 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/assignments/bt4_transaction_index.pdf', NOW(), NOW()),
(UNHEX('DDDD3333DDDD3333DDDD3333DDDD3305'), UNHEX('EEEE2222EEEE2222EEEE2222EEEE2221'), 'Bài tập Web số 1: Xây dựng Module Quản lý Lớp học với Spring Security & Phân quyền 2 tầng', 'Triển khai đầy đủ Entity, Repository, Specification, DTO, Service, Controller cho phép giảng viên tạo lớp, mời sinh viên qua email và kiểm tra quyền OWNER/TEACHER/STUDENT.', 10.00, '2026-10-28', 1, 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/assignments/bt_web1_rbac_class.pdf', NOW(), NOW()),
(UNHEX('DDDD3333DDDD3333DDDD3333DDDD3306'), UNHEX('EEEE2222EEEE2222EEEE2222EEEE3331'), 'Bài tập Web số 2: Tích hợp TanStack Query, React Hook Form và Zod cho trang Danh sách Khóa học', 'Xây dựng feature courses trên Next.js App Router có phân trang URL searchParams, lọc theo trạng thái và xử lý đủ 4 trạng thái Loading Skeleton, Error, Empty, Success.', 10.00, '2026-11-10', 1, 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/assignments/bt_web2_nextjs_courses.pdf', NOW(), NOW()),
(UNHEX('DDDD3333DDDD3333DDDD3333DDDD3307'), UNHEX('EEEE3333EEEE3333EEEE3333EEEE3331'), 'Bài tập CTDL: Cài đặt thuật toán Dijkstra tìm đường đi ngắn nhất và truy vết đường đi', 'Cài đặt bằng Java hoặc C++ sử dụng PriorityQueue với độ phức tạp O((V + E) log V) và giải bài toán mạng lưới giao thông nội đô Hà Nội.', 10.00, '2026-10-30', 1, 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/assignments/bt_ctdl_dijkstra.pdf', NOW(), NOW()),
(UNHEX('DDDD3333DDDD3333DDDD3333DDDD3308'), UNHEX('EEEE4444EEEE4444EEEE4444EEEE2221'), 'Bài tập AI: Thiết kế bộ Chia nhỏ Tài liệu (Text Chunker) và Prompt Chống ảo giác cho RAG', 'Viết chương trình chia giáo trình PDF thành các đoạn 150-300 tokens có gối đầu (overlap) và thiết kế system prompt yêu cầu AI chỉ trả lời dựa trên ngữ cảnh được cung cấp.', 10.00, '2026-11-12', 1, 'https://res.cloudinary.com/ilms-ptit/raw/upload/v1/assignments/bt_ai_rag_chunking.pdf', NOW(), NOW());

-- 12. Bảng assessments (6 kỳ đánh giá / Bài tập lớn của các lớp)
INSERT INTO `assessments` (`id`, `class_id`, `course_id`, `created_by`, `title`, `created_at`, `updated_at`) VALUES
(UNHEX('AAAA4444AAAA4444AAAA4444AAAA4401'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'Báo cáo Bài tập lớn Giai đoạn 1: Thiết kế ERD & Chuẩn hóa 3NF cho Hệ thống Quản lý Học tập Thông minh ILMS', NOW(), NOW()),
(UNHEX('AAAA4444AAAA4444AAAA4444AAAA4402'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'Bài kiểm tra Thực hành Truy vấn SQL & Tối ưu hóa Chỉ mục trên MySQL 8.0', NOW(), NOW()),
(UNHEX('AAAA4444AAAA4444AAAA4444AAAA4403'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1112'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'Báo cáo Bài tập lớn: Thiết kế Cơ sở dữ liệu Hệ thống Quản lý Thư viện Số Học viện', NOW(), NOW()),
(UNHEX('AAAA4444AAAA4444AAAA4444AAAA4404'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFE'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 'Đồ án Giữa kỳ: Xây dựng REST API Quản lý Khóa học & Lớp học với Spring Boot 3.3 + Flyway', NOW(), NOW()),
(UNHEX('AAAA4444AAAA4444AAAA4444AAAA4405'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA3333'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFD'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDF'), 'Bài kiểm tra Lập trình: Cây nhị phân tìm kiếm cân bằng AVL & Đồ thị Dijkstra', NOW(), NOW()),
(UNHEX('AAAA4444AAAA4444AAAA4444AAAA4406'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA4444'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFC'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD1'), 'Đồ án Chuyên ngành: Xây dựng Trợ lý Học tập RAG & Phân tích Bản đồ nhiệt Kiến thức', NOW(), NOW());

-- 13. Bảng submissions (12 bài nộp thực tế của nhiều sinh viên)
INSERT INTO `submissions` (`id`, `assessment_id`, `user_id`, `attempt_number`, `max_attempts`, `status`, `submission_text`, `submitted_at`) VALUES
-- Bài nộp ở lớp CSDL Nhóm 01 (Assessment AAAA...4401)
(UNHEX('BBBB4444BBBB4444BBBB4444BBBB4401'), UNHEX('AAAA4444AAAA4444AAAA4444AAAA4401'), UNHEX('12345678901234567890123456789012'), 1, 3, 'GRADED', 'Thưa cô, nhóm em (Nguyễn Hoàng Nam) xin nộp báo cáo đặc tả ERD và chứng minh chuẩn 3NF cho hệ thống ILMS gồm 37 bảng. Chúng em đã tách bảng role_permissions và class_members để loại bỏ hoàn toàn phụ thuộc hàm bộ phận và bắc cầu.', NOW()),
(UNHEX('BBBB4444BBBB4444BBBB4444BBBB4402'), UNHEX('AAAA4444AAAA4444AAAA4444AAAA4401'), UNHEX('12345678901234567890123456789013'), 1, 3, 'GRADED', 'Em Phạm Phương Linh nộp báo cáo thiết kế CSDL hệ thống Quản lý Bệnh viện Đa khoa kèm đầy đủ sơ đồ ERD, ánh xạ lược đồ quan hệ và script tạo bảng MySQL 8.0.', NOW()),
(UNHEX('BBBB4444BBBB4444BBBB4444BBBB4403'), UNHEX('AAAA4444AAAA4444AAAA4444AAAA4401'), UNHEX('12345678901234567890123456789014'), 2, 3, 'GRADED', 'Em Vũ Văn Đức nộp bản cập nhật lần 2 sau khi đã bổ sung khóa ngoại BINARY(16) và tách bảng chi tiết hóa đơn để đạt chuẩn 3NF.', NOW()),
(UNHEX('BBBB4444BBBB4444BBBB4444BBBB4404'), UNHEX('AAAA4444AAAA4444AAAA4444AAAA4401'), UNHEX('12345678901234567890123456789016'), 1, 3, 'GRADED', 'Em Trần Minh Khôi nộp báo cáo thiết kế CSDL Sàn Thương mại Điện tử B2C gồm 24 bảng, có phân tích chiến lược đánh chỉ mục B+Tree cho tìm kiếm sản phẩm.', NOW()),
(UNHEX('BBBB4444BBBB4444BBBB4444BBBB4405'), UNHEX('AAAA4444AAAA4444AAAA4444AAAA4401'), UNHEX('12345678901234567890123456789017'), 1, 3, 'GRADED', 'Em Lê Ngọc Ánh nộp bài thiết kế CSDL Hệ thống Đặt vé Máy bay trực tuyến kèm kiểm chứng phép tách bảo toàn thông tin.', NOW()),
(UNHEX('BBBB4444BBBB4444BBBB4444BBBB4406'), UNHEX('AAAA4444AAAA4444AAAA4444AAAA4401'), UNHEX('12345678901234567890123456789018'), 1, 3, 'SUBMITTED', 'Em Đặng Quốc Bảo nộp báo cáo thiết kế CSDL Quản lý Chuỗi Cửa hàng Bán lẻ (nộp bổ sung phần chứng minh BCNF).', NOW()),
-- Bài nộp ở bài Kiểm tra SQL (Assessment AAAA...4402)
(UNHEX('BBBB4444BBBB4444BBBB4444BBBB4407'), UNHEX('AAAA4444AAAA4444AAAA4444AAAA4402'), UNHEX('12345678901234567890123456789012'), 1, 2, 'GRADED', 'Bài làm 20 câu truy vấn SQL sử dụng CTE, Window Functions (DENSE_RANK) và EXPLAIN ANALYZE tối ưu hóa JOIN.', NOW()),
(UNHEX('BBBB4444BBBB4444BBBB4444BBBB4408'), UNHEX('AAAA4444AAAA4444AAAA4444AAAA4402'), UNHEX('12345678901234567890123456789013'), 1, 2, 'GRADED', 'Bài làm thực hành truy vấn SQL và thiết kế Composite Index cho bảng điểm danh.', NOW()),
-- Bài nộp ở lớp Lập trình Web (Assessment AAAA...4404)
(UNHEX('BBBB4444BBBB4444BBBB4444BBBB4409'), UNHEX('AAAA4444AAAA4444AAAA4444AAAA4404'), UNHEX('12345678901234567890123456789012'), 1, 3, 'GRADED', 'Link repository Backend Spring Boot 3.3.4: đã hoàn thiện AuthController, ClassController, ClassMemberController, Flyway 37 migrations và bộ JUnit 5 test đạt 100% pass.', NOW()),
(UNHEX('BBBB4444BBBB4444BBBB4444BBBB4410'), UNHEX('AAAA4444AAAA4444AAAA4444AAAA4404'), UNHEX('12345678901234567890123456789016'), 1, 3, 'GRADED', 'Nộp đồ án giữa kỳ Web: hoàn thành đầy đủ API khóa học, phân trang PageResponse<T>, JPA Specification và tích hợp Swagger OpenAPI.', NOW()),
-- Bài nộp ở lớp CTDL & Giải thuật (Assessment AAAA...4405)
(UNHEX('BBBB4444BBBB4444BBBB4444BBBB4411'), UNHEX('AAAA4444AAAA4444AAAA4444AAAA4405'), UNHEX('12345678901234567890123456789012'), 1, 3, 'GRADED', 'Cài đặt hoàn chỉnh class AVLTree<T> và thuật toán Dijkstra dùng PriorityQueue, vượt qua toàn bộ 50/50 test cases trong 120ms.', NOW()),
-- Bài nộp ở lớp AI & LLM (Assessment AAAA...4406)
(UNHEX('BBBB4444BBBB4444BBBB4444BBBB4412'), UNHEX('AAAA4444AAAA4444AAAA4444AAAA4406'), UNHEX('12345678901234567890123456789023'), 1, 2, 'SUBMITTED', 'Em Hà Khánh Vy nộp báo cáo thực nghiệm hệ thống RAG tiếng Việt cho giáo trình Cơ sở dữ liệu kèm đánh giá độ chính xác Faithfulness & Context Recall.', NOW());

-- 14. Bảng gradings (10 bản ghi chấm điểm kèm nhận xét chi tiết của giảng viên)
INSERT INTO `gradings` (`id`, `submission_id`, `grader_id`, `score`, `feedback`, `graded_at`, `created_at`, `updated_at`) VALUES
(UNHEX('CCCC3333CCCC3333CCCC3333CCCC3301'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4401'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 8.50, 'Thiết kế lược đồ quan hệ 37 bảng rất chặt chẽ, sử dụng khóa BINARY(16) đồng nhất. Phần giải thích lý do tách vai trò lớp học ra bảng class_members tốt, tuy nhiên cần trình bày rõ hơn bước tìm phủ tối thiểu ở Chương 3.', NOW(), NOW(), NOW()),
(UNHEX('CCCC3333CCCC3333CCCC3333CCCC3302'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4402'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 9.25, 'Báo cáo xuất sắc! Sơ đồ ERD chuẩn ký hiệu Crow-Foot, xác định đúng thực thể yếu và chứng minh đạt chuẩn BCNF rất thuyết phục.', NOW(), NOW(), NOW()),
(UNHEX('CCCC3333CCCC3333CCCC3333CCCC3303'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4403'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 7.75, 'Bản nộp lần 2 đã khắc phục được lỗi phụ thuộc hàm bắc cầu ở bảng Hóa đơn. Cần chú ý đặt tên ràng buộc khóa ngoại theo đúng chuẩn fk_<table_con>_<table_cha>.', NOW(), NOW(), NOW()),
(UNHEX('CCCC3333CCCC3333CCCC3333CCCC3304'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4404'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 9.00, 'Phân tích thiết kế CSDL Thương mại điện tử sâu sắc, đặc biệt phần đánh giá hiệu năng Composite Index rất thực tế.', NOW(), NOW(), NOW()),
(UNHEX('CCCC3333CCCC3333CCCC3333CCCC3305'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4405'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 9.50, 'Bài làm hoàn hảo, trình bày thuật toán kiểm tra phép tách bảo toàn thông tin bằng bảng Chase rất rõ ràng.', NOW(), NOW(), NOW()),
(UNHEX('CCCC3333CCCC3333CCCC3333CCCC3306'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4407'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 9.00, 'Viết truy vấn SQL tối ưu, sử dụng CTE và DENSE_RANK() chính xác.', NOW(), NOW(), NOW()),
(UNHEX('CCCC3333CCCC3333CCCC3333CCCC3307'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4408'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 8.75, 'Các câu lệnh JOIN và GROUP BY HAVING chuẩn xác, giải thích kế hoạch thực thi EXPLAIN tốt.', NOW(), NOW(), NOW()),
(UNHEX('CCCC3333CCCC3333CCCC3333CCCC3308'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4409'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 9.50, 'Tuân thủ tuyệt đối kiến trúc phân tầng, tách biệt rõ System Role và Class Role, xử lý ngoại lệ qua GlobalExceptionHandler và viết Unit Test rất đầy đủ.', NOW(), NOW(), NOW()),
(UNHEX('CCCC3333CCCC3333CCCC3333CCCC3309'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4410'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 8.80, 'Code sạch, áp dụng tốt JPA Specification cho tìm kiếm động và chuẩn hóa phản hồi ApiResponse<PageResponse<T>>.', NOW(), NOW(), NOW()),
(UNHEX('CCCC3333CCCC3333CCCC3333CCCC3310'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4411'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDF'), 9.20, 'Cài đặt cây AVL và thuật toán Dijkstra tối ưu về bộ nhớ và thời gian chạy.', NOW(), NOW(), NOW());

-- 25. Bảng grade_reports (14 bảng điểm tổng hợp của sinh viên ở các lớp)
INSERT INTO `grade_reports` (`id`, `class_member_id`, `attendance_score`, `midterm_score`, `final_score`, `created_at`, `updated_at`) VALUES
-- Bảng điểm lớp CSDL Nhóm 01
(UNHEX('E1E1E1E1E1E1E1E1E1E1E1E1E1E1E101'), UNHEX('BBBB2222BBBB2222BBBB2222BBBB2222'), 10.00, 8.50, 9.00, NOW(), NOW()),
(UNHEX('E1E1E1E1E1E1E1E1E1E1E1E1E1E1E102'), UNHEX('BBBB2222BBBB2222BBBB2222BBBB2223'), 10.00, 9.25, 9.50, NOW(), NOW()),
(UNHEX('E1E1E1E1E1E1E1E1E1E1E1E1E1E1E103'), UNHEX('BBBB2222BBBB2222BBBB2222BBBB2224'), 9.00, 7.75, 8.00, NOW(), NOW()),
(UNHEX('E1E1E1E1E1E1E1E1E1E1E1E1E1E1E104'), UNHEX('BBBB2222BBBB2222BBBB2222BBBB2225'), 10.00, 9.00, 9.25, NOW(), NOW()),
(UNHEX('E1E1E1E1E1E1E1E1E1E1E1E1E1E1E105'), UNHEX('BBBB2222BBBB2222BBBB2222BBBB2226'), 10.00, 9.50, 9.50, NOW(), NOW()),
(UNHEX('E1E1E1E1E1E1E1E1E1E1E1E1E1E1E106'), UNHEX('BBBB2222BBBB2222BBBB2222BBBB2227'), 7.50, 6.50, NULL, NOW(), NOW()),
(UNHEX('E1E1E1E1E1E1E1E1E1E1E1E1E1E1E107'), UNHEX('BBBB2222BBBB2222BBBB2222BBBB2228'), 10.00, 8.25, 8.50, NOW(), NOW()),
-- Bảng điểm lớp Lập trình Web Nhóm 01
(UNHEX('E1E1E1E1E1E1E1E1E1E1E1E1E1E1E108'), UNHEX('BBBB3333BBBB3333BBBB3333BBBB3303'), 10.00, 9.50, NULL, NOW(), NOW()),
(UNHEX('E1E1E1E1E1E1E1E1E1E1E1E1E1E1E109'), UNHEX('BBBB3333BBBB3333BBBB3333BBBB3304'), 10.00, 9.00, NULL, NOW(), NOW()),
(UNHEX('E1E1E1E1E1E1E1E1E1E1E1E1E1E1E110'), UNHEX('BBBB3333BBBB3333BBBB3333BBBB3305'), 9.50, 8.00, NULL, NOW(), NOW()),
(UNHEX('E1E1E1E1E1E1E1E1E1E1E1E1E1E1E111'), UNHEX('BBBB3333BBBB3333BBBB3333BBBB3306'), 10.00, 8.80, NULL, NOW(), NOW()),
-- Bảng điểm lớp CTDL & Giải thuật Nhóm 01
(UNHEX('E1E1E1E1E1E1E1E1E1E1E1E1E1E1E112'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4402'), 10.00, 9.20, 9.00, NOW(), NOW()),
(UNHEX('E1E1E1E1E1E1E1E1E1E1E1E1E1E1E113'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4403'), 9.50, 8.00, 8.50, NOW(), NOW()),
(UNHEX('E1E1E1E1E1E1E1E1E1E1E1E1E1E1E114'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4404'), 9.00, 7.50, 7.75, NOW(), NOW());


-- ==============================================================================
-- PHẦN 5: NGÂN HÀNG CÂU HỎI VÀ THI CỬ (Bảng 18, 28, 16, 17, 32, 31, 30, 29)
-- ==============================================================================

-- 18. Bảng questions (12 câu hỏi ngân hàng đa dạng môn học, độ khó và nguồn tạo)
INSERT INTO `questions` (`id`, `course_id`, `chapter_id`, `created_by`, `question_text`, `question_type`, `difficulty`, `explanation`, `source_type`, `is_verified_by_teacher`, `created_at`, `updated_at`) VALUES
-- Câu hỏi môn Cơ sở dữ liệu (6 câu)
(UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A01'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), UNHEX('DDDD1111DDDD1111DDDD1111DDDD2222'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'Trong mô hình cơ sở dữ liệu quan hệ, ràng buộc toàn vẹn thực thể (Entity Integrity) quy định điều gì đối với khóa chính (Primary Key)?', 'SINGLE_CHOICE', 'EASY', 'Theo ràng buộc toàn vẹn thực thể, mọi thuộc tính tham gia vào khóa chính của một quan hệ cơ sở không được phép nhận giá trị rỗng (NULL) và phải phân biệt giữa các bộ.', 'MANUAL', 1, NOW(), NOW()),
(UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A02'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), UNHEX('DDDD1111DDDD1111DDDD1111DDDD2222'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'Phép kết nối nào trong SQL trả về tất cả các bản ghi từ bảng bên trái và các bản ghi khớp từ bảng bên phải (nếu không khớp thì các cột bảng bên phải nhận giá trị NULL)?', 'SINGLE_CHOICE', 'EASY', 'LEFT OUTER JOIN (hay LEFT JOIN) giữ lại toàn bộ các dòng của bảng bên trái và ghép các dòng thỏa mãn điều kiện kết nối ở bảng bên phải.', 'MANUAL', 1, NOW(), NOW()),
(UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A03'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), UNHEX('DDDD1111DDDD1111DDDD1111DDDD3333'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'Một lược đồ quan hệ R ở dạng chuẩn 2 (2NF) sẽ đạt dạng chuẩn 3 (3NF) khi và chỉ khi thỏa mãn điều kiện nào sau đây?', 'SINGLE_CHOICE', 'MEDIUM', 'Lược đồ quan hệ R ở 3NF nếu nó đã ở 2NF và mọi thuộc tính không khóa đều không phụ thuộc hàm bắc cầu (Transitive Dependency) vào bất kỳ khóa dự tuyển nào của R.', 'MANUAL', 1, NOW(), NOW()),
(UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A04'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), UNHEX('DDDD1111DDDD1111DDDD1111DDDD3333'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'Cho lược đồ quan hệ R(A, B, C, D) với tập phụ thuộc hàm F = {AB -> C, C -> D, D -> A}. Hỏi lược đồ R đạt dạng chuẩn cao nhất nào?', 'SINGLE_CHOICE', 'HARD', 'Các khóa dự tuyển của R là AB, BC, BD. Vì mọi thuộc tính A, B, C, D đều tham gia vào ít nhất một khóa dự tuyển (đều là thuộc tính khóa) nên R đạt chuẩn 3NF, nhưng vi phạm BCNF vì C -> D và D -> A có vế trái không phải là siêu khóa.', 'MANUAL', 1, NOW(), NOW()),
(UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A05'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), UNHEX('DDDD1111DDDD1111DDDD1111DDDD4444'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'Trong hệ quản trị CSDL MySQL (InnoDB), mức cô lập giao dịch (Isolation Level) mặc định là mức nào?', 'SINGLE_CHOICE', 'MEDIUM', 'InnoDB sử dụng mức cô lập mặc định là REPEATABLE READ kết hợp cơ chế đa phiên bản (MVCC) và Next-Key Locking.', 'AI_GENERATED', 1, NOW(), NOW()),
(UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A06'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), UNHEX('DDDD1111DDDD1111DDDD1111DDDD4444'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'), 'Tại sao cấu trúc cây B+Tree lại được ưu tiên sử dụng làm chỉ mục (Index) trong các hệ quản trị CSDL quan hệ hơn so với cây nhị phân tìm kiếm (BST)?', 'SINGLE_CHOICE', 'HARD', 'Cây B+Tree có bậc (fan-out) rất lớn giúp chiều cao cây cực thấp (thường chỉ 3-4 tầng cho hàng chục triệu bản ghi), tối ưu số lần đọc khối đĩa (Disk I/O), đồng thời các nút lá liên kết tuần tự rất hiệu quả cho truy vấn khoảng (Range Query).', 'AI_GENERATED', 1, NOW(), NOW()),
-- Câu hỏi môn Lập trình Web (3 câu)
(UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A07'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFE'), UNHEX('DDDD2222DDDD2222DDDD2222DDDD2222'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 'Lợi ích bảo mật lớn nhất của việc lưu trữ JWT Access Token và Refresh Token trong HttpOnly Cookie so với localStorage là gì?', 'SINGLE_CHOICE', 'MEDIUM', 'Cookie có cờ HttpOnly không thể bị truy cập bởi mã JavaScript thông qua document.cookie, giúp ngăn chặn việc đánh cắp token khi xảy ra lỗ hổng Cross-Site Scripting (XSS).', 'MANUAL', 1, NOW(), NOW()),
(UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A08'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFE'), UNHEX('DDDD2222DDDD2222DDDD2222DDDD2222'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 'Khi đặt cấu hình spring.jpa.open-in-view=false trong Spring Boot, giải pháp nào giúp tránh lỗi LazyInitializationException và bài toán N+1 Query khi đọc quan hệ @ManyToOne / @OneToMany?', 'SINGLE_CHOICE', 'MEDIUM', 'Sử dụng @EntityGraph hoặc mệnh đề JOIN FETCH trong Repository bên trong phương thức Service có gắn @Transactional(readOnly = true) trước khi ánh xạ sang DTO.', 'MANUAL', 1, NOW(), NOW()),
(UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A09'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFE'), UNHEX('DDDD2222DDDD2222DDDD2222DDDD1111'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'), 'Tại sao trong kiến trúc phân tầng Spring Boot, Controller tuyệt đối không nên trả trực tiếp đối tượng JPA Entity về cho Client?', 'SINGLE_CHOICE', 'EASY', 'Trả trực tiếp Entity dễ làm lộ các trường nhạy cảm (như password hash), gây lỗi vòng lặp vô hạn khi serialize JSON hai chiều và làm gãy hợp đồng API của Frontend khi thay đổi cấu trúc bảng DB.', 'MANUAL', 1, NOW(), NOW()),
-- Câu hỏi môn CTDL & Giải thuật (2 câu)
(UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A10'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFD'), UNHEX('DDDD3333DDDD3333DDDD3333DDDD1111'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDF'), 'Độ phức tạp thời gian trong trường hợp xấu nhất (Worst-case) và trung bình (Average-case) của thuật toán sắp xếp nhanh (QuickSort) lần lượt là bao nhiêu?', 'SINGLE_CHOICE', 'EASY', 'QuickSort có độ phức tạp trung bình là O(N log N), nhưng trong trường hợp xấu nhất (khi mảng đã sắp xếp và chọn chốt ở đầu/cuối) độ phức tạp suy biến thành O(N^2).', 'MANUAL', 1, NOW(), NOW()),
(UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A11'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFD'), UNHEX('DDDD3333DDDD3333DDDD3333DDDD3333'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDF'), 'Thuật toán Dijkstra tìm đường đi ngắn nhất từ một đỉnh nguồn không đảm bảo kết quả đúng trong trường hợp nào sau đây?', 'SINGLE_CHOICE', 'MEDIUM', 'Thuật toán tham lam Dijkstra giả định khoảng cách đến đỉnh đã đóng là tối ưu nên sẽ chạy sai nếu đồ thị có cạnh mang trọng số âm (cần dùng Bellman-Ford).', 'MANUAL', 1, NOW(), NOW()),
-- Câu hỏi môn Trí tuệ nhân tạo & LLM (1 câu)
(UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A12'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFC'), UNHEX('DDDD4444DDDD4444DDDD4444DDDD2222'), UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD1'), 'Trong kiến trúc Retrieval-Augmented Generation (RAG), bước nào đóng vai trò giảm thiểu hiện tượng ảo giác (Hallucination) của mô hình ngôn ngữ lớn (LLM)?', 'SINGLE_CHOICE', 'MEDIUM', 'Truy xuất các đoạn tài liệu chuẩn xác nhất (Top-K chunks) từ cơ sở dữ liệu Vector và ép LLM chỉ tổng hợp câu trả lời dựa trên ngữ cảnh được cung cấp.', 'AI_GENERATED', 1, NOW(), NOW());

-- 28. Bảng question_concepts (12 liên kết câu hỏi với khái niệm kiến thức)
INSERT INTO `question_concepts` (`id`, `question_id`, `concept_id`, `relevance_weight`) VALUES
(UNHEX('6A6A6A6A6A6A6A6A6A6A6A6A6A6A6A01'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A01'), 'KHOA_CHINH', 1.00),
(UNHEX('6A6A6A6A6A6A6A6A6A6A6A6A6A6A6A02'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A02'), 'SQL_JOIN', 1.00),
(UNHEX('6A6A6A6A6A6A6A6A6A6A6A6A6A6A6A03'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A03'), 'CHUAN_HOA_3NF', 1.00),
(UNHEX('6A6A6A6A6A6A6A6A6A6A6A6A6A6A6A04'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A04'), 'CHUAN_HOA_BCNF', 1.00),
(UNHEX('6A6A6A6A6A6A6A6A6A6A6A6A6A6A6A05'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A05'), 'TRANSACTION_ACID', 1.00),
(UNHEX('6A6A6A6A6A6A6A6A6A6A6A6A6A6A6A06'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A06'), 'INDEX_BTREE', 1.00),
(UNHEX('6A6A6A6A6A6A6A6A6A6A6A6A6A6A6A07'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A07'), 'SPRING_SECURITY_JWT', 1.00),
(UNHEX('6A6A6A6A6A6A6A6A6A6A6A6A6A6A6A08'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A08'), 'JPA_N_PLUS_1', 1.00),
(UNHEX('6A6A6A6A6A6A6A6A6A6A6A6A6A6A6A09'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A09'), 'DTO_PATTERN', 1.00),
(UNHEX('6A6A6A6A6A6A6A6A6A6A6A6A6A6A6A10'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A10'), 'QUICKSORT', 1.00),
(UNHEX('6A6A6A6A6A6A6A6A6A6A6A6A6A6A6A11'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A11'), 'DIJKSTRA', 1.00),
(UNHEX('6A6A6A6A6A6A6A6A6A6A6A6A6A6A6A12'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A12'), 'RAG_EMBEDDING', 1.00);

-- 16. Bảng exams (4 kỳ thi chính thức)
INSERT INTO `exams` (`id`, `description`, `exam_type`, `duration_minutes`, `total_score`, `start_time`, `end_time`, `is_published`, `created_at`, `updated_at`) VALUES
(UNHEX('7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A01'), 'Kỳ thi Giữa kỳ môn Cơ sở dữ liệu (INT1306) - Học kỳ I năm học 2026-2027', 'MIDTERM', 45, 10.00, '2026-10-24 07:30:00', '2026-10-24 08:15:00', 1, NOW(), NOW()),
(UNHEX('7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A02'), 'Kỳ thi Kết thúc học phần môn Cơ sở dữ liệu (INT1306) - Học kỳ I năm học 2026-2027', 'FINAL', 60, 10.00, '2026-12-25 08:00:00', '2026-12-25 09:00:00', 1, NOW(), NOW()),
(UNHEX('7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A03'), 'Kỳ thi Giữa kỳ môn Lập trình Web với Spring Boot & Next.js (INT1434)', 'MIDTERM', 45, 10.00, '2026-10-28 14:00:00', '2026-10-28 14:45:00', 1, NOW(), NOW()),
(UNHEX('7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A04'), 'Kỳ thi Kết thúc học phần môn Cấu trúc dữ liệu và Giải thuật (INT1303)', 'FINAL', 60, 10.00, '2026-12-27 09:00:00', '2026-12-27 10:00:00', 1, NOW(), NOW());

-- 17. Bảng exam_questions (13 bản ghi gán câu hỏi vào đề thi)
INSERT INTO `exam_questions` (`id`, `exam_id`, `question_id`, `score`, `order_index`, `added_method`, `created_at`) VALUES
-- Đề thi Giữa kỳ CSDL (4 câu x 2.5 điểm)
(UNHEX('8A8A8A8A8A8A8A8A8A8A8A8A8A8A8A01'), UNHEX('7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A01'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A01'), 2.50, 1, 'MANUAL', NOW()),
(UNHEX('8A8A8A8A8A8A8A8A8A8A8A8A8A8A8A02'), UNHEX('7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A01'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A02'), 2.50, 2, 'MANUAL', NOW()),
(UNHEX('8A8A8A8A8A8A8A8A8A8A8A8A8A8A8A03'), UNHEX('7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A01'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A03'), 2.50, 3, 'MANUAL', NOW()),
(UNHEX('8A8A8A8A8A8A8A8A8A8A8A8A8A8A8A04'), UNHEX('7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A01'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A04'), 2.50, 4, 'MANUAL', NOW()),
-- Đề thi Cuối kỳ CSDL (4 câu)
(UNHEX('8A8A8A8A8A8A8A8A8A8A8A8A8A8A8A05'), UNHEX('7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A02'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A03'), 2.50, 1, 'MANUAL', NOW()),
(UNHEX('8A8A8A8A8A8A8A8A8A8A8A8A8A8A8A06'), UNHEX('7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A02'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A04'), 2.50, 2, 'MANUAL', NOW()),
(UNHEX('8A8A8A8A8A8A8A8A8A8A8A8A8A8A8A07'), UNHEX('7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A02'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A05'), 2.50, 3, 'AI_GENERATED', NOW()),
(UNHEX('8A8A8A8A8A8A8A8A8A8A8A8A8A8A8A08'), UNHEX('7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A02'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A06'), 2.50, 4, 'AI_GENERATED', NOW()),
-- Đề thi Giữa kỳ Lập trình Web (3 câu)
(UNHEX('8A8A8A8A8A8A8A8A8A8A8A8A8A8A8A09'), UNHEX('7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A03'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A07'), 3.50, 1, 'MANUAL', NOW()),
(UNHEX('8A8A8A8A8A8A8A8A8A8A8A8A8A8A8A10'), UNHEX('7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A03'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A08'), 3.50, 2, 'MANUAL', NOW()),
(UNHEX('8A8A8A8A8A8A8A8A8A8A8A8A8A8A8A11'), UNHEX('7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A03'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A09'), 3.00, 3, 'MANUAL', NOW()),
-- Đề thi Cuối kỳ CTDL (2 câu)
(UNHEX('8A8A8A8A8A8A8A8A8A8A8A8A8A8A8A12'), UNHEX('7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A04'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A10'), 5.00, 1, 'MANUAL', NOW()),
(UNHEX('8A8A8A8A8A8A8A8A8A8A8A8A8A8A8A13'), UNHEX('7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A04'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A11'), 5.00, 2, 'MANUAL', NOW());

-- 32. Bảng quizzes (4 bài kiểm tra trắc nghiệm nhanh theo chương/bài học)
INSERT INTO `quizzes` (`id`, `class_id`, `lesson_id`, `course_id`, `title`, `duration_minutes`, `passing_score`, `max_attempts`, `is_published`, `created_at`, `updated_at`) VALUES
(UNHEX('9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A01'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('EEEE1111EEEE1111EEEE1111EEEE3332'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), 'Quiz 1: Ràng buộc toàn vẹn, Truy vấn JOIN và Chuẩn hóa 3NF/BCNF', 15, 5.00, 2, 1, NOW(), NOW()),
(UNHEX('9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A02'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA1111'), UNHEX('EEEE1111EEEE1111EEEE1111EEEE4441'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFF'), 'Quiz 2: Giao dịch ACID, Isolation Levels và Chỉ mục B+Tree', 15, 5.00, 2, 1, NOW(), NOW()),
(UNHEX('9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A03'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA2222'), UNHEX('EEEE2222EEEE2222EEEE2222EEEE2221'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFE'), 'Quiz Web: Bảo mật JWT HttpOnly Cookie, DTO Pattern và Xử lý N+1 Query', 20, 6.00, 2, 1, NOW(), NOW()),
(UNHEX('9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A04'), UNHEX('AAAA1111AAAA1111AAAA1111AAAA3333'), UNHEX('EEEE3333EEEE3333EEEE3333EEEE3331'), UNHEX('EEEEEEEEEEEEEEEEFFFFFFFFFFFFFFFD'), 'Quiz CTDL: Độ phức tạp QuickSort và Thuật toán Đồ thị Dijkstra', 15, 5.00, 3, 1, NOW(), NOW());

-- 31. Bảng quiz_questions (9 câu hỏi trong các bài Quiz)
INSERT INTO `quiz_questions` (`id`, `quiz_id`, `bank_question_id`, `question_text`, `question_type`, `score`, `order_index`, `created_at`) VALUES
-- Câu hỏi thuộc Quiz 1 CSDL (4 câu x 2.5 điểm)
(UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A101'), UNHEX('9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A01'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A01'), 'Trong mô hình cơ sở dữ liệu quan hệ, ràng buộc toàn vẹn thực thể quy định điều gì đối với khóa chính?', 'SINGLE_CHOICE', 2.50, 1, NOW()),
(UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A102'), UNHEX('9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A01'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A02'), 'Phép kết nối nào trong SQL trả về toàn bộ bản ghi từ bảng bên trái và các bản ghi khớp từ bảng bên phải?', 'SINGLE_CHOICE', 2.50, 2, NOW()),
(UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A103'), UNHEX('9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A01'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A03'), 'Một lược đồ quan hệ R ở 2NF sẽ đạt chuẩn 3NF khi thỏa mãn điều kiện nào?', 'SINGLE_CHOICE', 2.50, 3, NOW()),
(UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A104'), UNHEX('9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A01'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A04'), 'Cho R(A,B,C,D) với F = {AB -> C, C -> D, D -> A}. Dạng chuẩn cao nhất của R là gì?', 'SINGLE_CHOICE', 2.50, 4, NOW()),
-- Câu hỏi thuộc Quiz 2 CSDL (2 câu x 5.0 điểm)
(UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A105'), UNHEX('9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A02'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A05'), 'Trong MySQL (InnoDB), mức cô lập giao dịch mặc định là mức nào?', 'SINGLE_CHOICE', 5.00, 1, NOW()),
(UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A106'), UNHEX('9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A02'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A06'), 'Tại sao cây B+Tree được ưu tiên làm chỉ mục trong CSDL quan hệ hơn cây BST?', 'SINGLE_CHOICE', 5.00, 2, NOW()),
-- Câu hỏi thuộc Quiz 3 Lập trình Web (3 câu)
(UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A107'), UNHEX('9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A03'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A07'), 'Lợi ích bảo mật lớn nhất của việc lưu JWT trong HttpOnly Cookie so với localStorage là gì?', 'SINGLE_CHOICE', 3.50, 1, NOW()),
(UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A108'), UNHEX('9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A03'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A08'), 'Khi đặt spring.jpa.open-in-view=false, giải pháp nào tránh được lỗi LazyInitializationException và N+1 Query?', 'SINGLE_CHOICE', 3.50, 2, NOW()),
(UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A109'), UNHEX('9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A03'), UNHEX('5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A09'), 'Tại sao Controller không nên trả trực tiếp đối tượng JPA Entity về cho Client?', 'SINGLE_CHOICE', 3.00, 3, NOW());

-- 30. Bảng quiz_options (28 phương án lựa chọn đầy đủ cho 9 câu hỏi Quiz)
INSERT INTO `quiz_options` (`id`, `question_id`, `option_text`, `is_correct`, `order_index`) VALUES
-- Câu 1 (A1...101)
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B101'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A101'), 'Các thuộc tính khóa chính phải duy nhất và không được phép nhận giá trị NULL', 1, 1),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B102'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A101'), 'Khóa chính có thể chứa tối đa một giá trị NULL duy nhất', 0, 2),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B103'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A101'), 'Khóa chính bắt buộc phải là kiểu số nguyên tự tăng (AUTO_INCREMENT)', 0, 3),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B104'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A101'), 'Một bảng có thể có nhiều khóa chính khác nhau cùng lúc', 0, 4),
-- Câu 2 (A1...102)
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B105'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A102'), 'INNER JOIN', 0, 1),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B106'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A102'), 'LEFT OUTER JOIN (LEFT JOIN)', 1, 2),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B107'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A102'), 'RIGHT OUTER JOIN (RIGHT JOIN)', 0, 3),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B108'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A102'), 'CROSS JOIN', 0, 4),
-- Câu 3 (A1...103)
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B109'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A103'), 'Không có thuộc tính không khóa nào phụ thuộc hàm bắc cầu vào khóa dự tuyển', 1, 1),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B110'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A103'), 'Mọi thuộc tính đều nhận giá trị nguyên tố (Atomic)', 0, 2),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B111'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A103'), 'Lược đồ chỉ có duy nhất một khóa chính đơn gồm 1 thuộc tính', 0, 3),
-- Câu 4 (A1...104)
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B112'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A104'), 'Dạng chuẩn 1 (1NF)', 0, 1),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B113'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A104'), 'Dạng chuẩn 2 (2NF)', 0, 2),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B114'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A104'), 'Dạng chuẩn 3 (3NF) nhưng chưa đạt BCNF', 1, 3),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B115'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A104'), 'Dạng chuẩn Boyce-Codd (BCNF)', 0, 4),
-- Câu 5 (A1...105)
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B116'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A105'), 'READ UNCOMMITTED', 0, 1),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B117'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A105'), 'READ COMMITTED', 0, 2),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B118'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A105'), 'REPEATABLE READ', 1, 3),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B119'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A105'), 'SERIALIZABLE', 0, 4),
-- Câu 6 (A1...106)
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B120'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A106'), 'B+Tree có chiều cao thấp giúp giảm số lần đọc đĩa (Disk I/O) và các nút lá liên kết tuần tự hỗ trợ quét khoảng rất nhanh', 1, 1),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B121'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A106'), 'B+Tree không bao giờ cần cân bằng lại khi thêm hoặc xóa bản ghi', 0, 2),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B122'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A106'), 'B+Tree chỉ lưu dữ liệu trên RAM nên không tốn dung lượng ổ cứng', 0, 3),
-- Câu 7 (A1...107)
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B123'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A107'), 'Ngăn chặn mã độc JavaScript đọc trộm token qua document.cookie khi xảy ra tấn công XSS', 1, 1),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B124'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A107'), 'Giúp token không bao giờ bị hết hạn', 0, 2),
-- Câu 8 (A1...108)
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B125'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A108'), 'Dùng @EntityGraph hoặc JOIN FETCH trong Repository bên trong phương thức Service có @Transactional', 1, 1),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B126'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A108'), 'Đổi toàn bộ quan hệ trong tất cả Entity sang FetchType.EAGER', 0, 2),
-- Câu 9 (A1...109)
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B127'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A109'), 'Tránh lộ dữ liệu nhạy cảm, tránh đệ quy JSON vô hạn và tách biệt hợp đồng API khỏi cấu trúc bảng DB', 1, 1),
(UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B128'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A109'), 'Vì Spring Boot không hỗ trợ serialize đối tượng @Entity sang JSON', 0, 2);

-- 29. Bảng quiz_answers (12 câu trả lời trắc nghiệm thực tế của sinh viên)
INSERT INTO `quiz_answers` (`id`, `submission_id`, `question_id`, `selected_option_id`, `answer_text`, `is_correct`, `earned_score`) VALUES
-- Bài làm của Nguyễn Hoàng Nam (BBBB...4401)
(UNHEX('C1C1C1C1C1C1C1C1C1C1C1C1C1C1C101'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4401'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A101'), UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B101'), NULL, 1, 2.50),
(UNHEX('C1C1C1C1C1C1C1C1C1C1C1C1C1C1C102'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4401'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A102'), UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B106'), NULL, 1, 2.50),
(UNHEX('C1C1C1C1C1C1C1C1C1C1C1C1C1C1C103'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4401'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A103'), UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B109'), NULL, 1, 2.50),
(UNHEX('C1C1C1C1C1C1C1C1C1C1C1C1C1C1C104'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4401'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A104'), UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B115'), NULL, 0, 0.00),
-- Bài làm của Phạm Phương Linh (BBBB...4402) — đúng cả 4 câu
(UNHEX('C1C1C1C1C1C1C1C1C1C1C1C1C1C1C105'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4402'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A101'), UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B101'), NULL, 1, 2.50),
(UNHEX('C1C1C1C1C1C1C1C1C1C1C1C1C1C1C106'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4402'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A102'), UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B106'), NULL, 1, 2.50),
(UNHEX('C1C1C1C1C1C1C1C1C1C1C1C1C1C1C107'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4402'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A103'), UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B109'), NULL, 1, 2.50),
(UNHEX('C1C1C1C1C1C1C1C1C1C1C1C1C1C1C108'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4402'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A104'), UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B114'), NULL, 1, 2.50),
-- Bài làm của Vũ Văn Đức (BBBB...4403)
(UNHEX('C1C1C1C1C1C1C1C1C1C1C1C1C1C1C109'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4403'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A101'), UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B101'), NULL, 1, 2.50),
(UNHEX('C1C1C1C1C1C1C1C1C1C1C1C1C1C1C110'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4403'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A102'), UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B105'), NULL, 0, 0.00),
(UNHEX('C1C1C1C1C1C1C1C1C1C1C1C1C1C1C111'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4403'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A103'), UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B110'), NULL, 0, 0.00),
(UNHEX('C1C1C1C1C1C1C1C1C1C1C1C1C1C1C112'), UNHEX('BBBB4444BBBB4444BBBB4444BBBB4403'), UNHEX('A1A1A1A1A1A1A1A1A1A1A1A1A1A1A104'), UNHEX('B1B1B1B1B1B1B1B1B1B1B1B1B1B1B114'), NULL, 1, 2.50);


-- ==============================================================================
-- PHẦN 6: HỆ THỐNG AI & TRACKING (Bảng 21, 22, 23, 27, 34, 35)
-- ==============================================================================

-- 21. Bảng ai_chat_sessions (6 phiên hỏi đáp với Trợ lý AI học tập)
INSERT INTO `socratic_chat_sessions` (
    `id`,
    `student_id`,
    `teacher_id`,
    `title`,
    `subject`,
    `active_canonical_code`,
    `active_process_id`,
    `active_exercise_id`,
    `current_step_number`,
    `is_completed`,
    `stuck_count`,
    `parent_canonical_code`,
    `created_at`,
    `updated_at`
) VALUES
-- Phiên 1: Nguyễn Hoàng Nam (namnh) học với Gia sư Socratic lớp cô Trần Thị Hương (INT1306) — Đã hoàn thành 3/3 bước
(
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C01'),
    UNHEX('12345678901234567890123456789012'),
    UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'),
    'Phân biệt dạng chuẩn 3NF và BCNF khi có nhiều khóa ứng viên chồng lấn',
    'INT1306',
    'CHUAN_HOA_BCNF',
    UNHEX('77889900112233445566778899AABB01'),
    UNHEX('8899AABB112233445566778899AABB01'),
    3,
    1,
    0,
    'CHUAN_HOA_BCNF',
    '2026-10-20 08:15:00',
    '2026-10-20 08:28:45'
),
-- Phiên 2: Phạm Phương Linh (linhpp) học với Gia sư Socratic lớp cô Trần Thị Hương (INT1306) — Đã hoàn thành 2/2 bước
(
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C02'),
    UNHEX('12345678901234567890123456789013'),
    UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'),
    'Cách tối ưu câu lệnh SQL lấy Top 3 sinh viên mỗi lớp bằng DENSE_RANK()',
    'INT1306',
    'SQL_JOIN',
    UNHEX('77889900112233445566778899AABB02'),
    UNHEX('8899AABB112233445566778899AABB02'),
    2,
    1,
    1,
    'SQL_JOIN',
    '2026-10-20 10:05:00',
    '2026-10-20 10:18:20'
),
-- Phiên 3: Vũ Văn Đức (ducvv) học với Gia sư Socratic lớp cô Trần Thị Hương (INT1306) — Đang dừng ở bước 2/3 (chưa hoàn thành)
(
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C03'),
    UNHEX('12345678901234567890123456789014'),
    UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'),
    'Nhận diện nhanh phụ thuộc hàm bộ phận (2NF) và phụ thuộc bắc cầu (3NF)',
    'INT1306',
    'CHUAN_HOA_3NF',
    UNHEX('77889900112233445566778899AABB03'),
    NULL,
    2,
    0,
    1,
    'CHUAN_HOA_3NF',
    '2026-10-20 14:30:00',
    '2026-10-20 14:42:10'
),
-- Phiên 4: Trần Minh Khôi (khoitm) học với Gia sư Socratic lớp thầy Lê Anh Tuấn (INT1434) — Đã hoàn thành 2/2 bước
(
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C04'),
    UNHEX('12345678901234567890123456789016'),
    UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'),
    'Khắc phục lỗi LazyInitializationException và N+1 Query trong Spring Data JPA',
    'INT1434',
    'JPA_N_PLUS_1',
    UNHEX('77889900112233445566778899AABB04'),
    UNHEX('8899AABB112233445566778899AABB04'),
    2,
    1,
    3,
    'JPA_N_PLUS_1',
    '2026-10-20 19:10:00',
    '2026-10-20 19:24:00'
),
-- Phiên 5: Bùi Thị Thanh Tâm (tambtt) học với Gia sư Socratic lớp thầy Nguyễn Văn Hiếu (INT1303) — Đã hoàn thành 2/2 bước
(
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C05'),
    UNHEX('12345678901234567890123456789019'),
    UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDF'),
    'Phản ví dụ chứng minh thuật toán Dijkstra chạy sai khi đồ thị có cạnh âm',
    'INT1303',
    'DIJKSTRA',
    UNHEX('77889900112233445566778899AABB05'),
    NULL,
    2,
    1,
    2,
    'DIJKSTRA',
    '2026-10-21 09:00:00',
    '2026-10-21 09:15:30'
),
-- Phiên 6: Hà Khánh Vy (vyhk) học với Gia sư Socratic lớp cô Vũ Thị Ngọc Bích (INT1405) — Đang ở bước 2/3 (chưa hoàn thành)
(
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C06'),
    UNHEX('12345678901234567890123456789023'),
    UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD1'),
    'Thiết kế tham số chunk_size và chunk_overlap cho RAG giáo trình tiếng Việt',
    'INT1405',
    'RAG_EMBEDDING',
    UNHEX('77889900112233445566778899AABB06'),
    UNHEX('8899AABB112233445566778899AABB06'),
    2,
    0,
    0,
    'RAG_EMBEDDING',
    '2026-10-21 15:20:00',
    '2026-10-21 15:35:00'
);
-- 22. Bảng ai_chat_messages (12 tin nhắn hội thoại chi tiết giữa Sinh viên và AI Tutor)
INSERT INTO `socratic_chat_messages` (
    `id`,
    `session_id`,
    `role`,
    `content`,
    `step_number_at_turn`,
    `referenced_chunk_ids`,
    `referenced_node_ids`,
    `user_feedback`,
    `feedback_rating`,
    `created_at`,
    `updated_at`
) VALUES
-- ------------------------------------------------------------------------------
-- HỘI THOẠI 1 (Phiên 1C...01): Nam hỏi về câu Quiz R(A,B,C,D) đạt 3NF nhưng vi phạm BCNF (4 tin nhắn qua 3 bước)
-- ------------------------------------------------------------------------------
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C01'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C01'),
    'USER',
    'Trong bài Quiz 1 vừa rồi mình bị sai câu R(A,B,C,D) với F = {AB -> C, C -> D, D -> A}. Tại sao lược đồ này đạt 3NF nhưng lại không đạt BCNF vậy AI?',
    1,
    '[]',
    '[]',
    NULL,
    NULL,
    '2026-10-20 08:15:10',
    '2026-10-20 08:15:10'
),
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C02'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C01'),
    'ASSISTANT',
    'Chào Nam! Câu hỏi này rất hay vì đây là bẫy kinh điển khi lược đồ có nhiều khóa ứng viên chồng lấn. Mình cùng đi từng bước nhé!
**Bước 1/3**: Dựa vào tập phụ thuộc hàm `F = {AB -> C, C -> D, D -> A}`, bạn hãy thử tính bao đóng và liệt kê tất cả các **khóa dự tuyển (Candidate Keys)** của `R(A,B,C,D)`. Từ đó cho mình biết những thuộc tính nào trong `A, B, C, D` là **thuộc tính khóa (Prime Attribute)**?',
    1,
    '["8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c04", "8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c05"]',
    '["CHUAN_HOA_BCNF", "CHUAN_HOA_3NF", "77889900-1122-3344-5566-778899aabb01", "b0000000-1122-3344-5566-778899aabb01"]',
    NULL,
    NULL,
    '2026-10-20 08:15:18',
    '2026-10-20 08:15:18'
),
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C03'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C01'),
    'USER',
    'Vì B không xuất hiện ở vế phải nào nên mọi khóa phải chứa B. Mình tính bao đóng thấy (AB)+ = ABCD, (BC)+ = BCDA, (BD)+ = BDAC. Vậy có 3 khóa dự tuyển là AB, BC, BD nên cả 4 thuộc tính A, B, C, D đều là thuộc tính khóa luôn!',
    2,
    '[]',
    '[]',
    NULL,
    NULL,
    '2026-10-20 08:21:05',
    '2026-10-20 08:21:05'
),
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C04'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C01'),
    'ASSISTANT',
    'Chính xác 100%! Bạn đã tự mở được nút thắt quan trọng nhất rồi đấy:
1. **Tại sao R đạt 3NF?**: Theo định nghĩa **3NF**, một phụ thuộc hàm `X -> Y` được chấp nhận nếu `X` là siêu khóa **HOẶC `Y` là thuộc tính khóa**. Vì cả `A, B, C, D` đều là thuộc tính khóa (không có thuộc tính không khóa nào tồn tại), nên mọi phụ thuộc hàm trong `F` đều tự động thỏa mãn **3NF**.
2. **Tại sao R vi phạm BCNF?**: Chuẩn **BCNF** khắt khe hơn, yêu cầu với mọi `X -> Y` không tầm thường thì **vế trái `X` bắt buộc phải là siêu khóa**. Ở đây hai phụ thuộc `C -> D` và `D -> A` có vế trái `C` và `D` chỉ gồm 1 thuộc tính (không chứa `B` nên không thể là siêu khóa), dẫn tới `R` vi phạm **BCNF**!
Chúc mừng Nam đã hoàn thành xuất sắc cả 3 bước suy luận!',
    3,
    '["8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c04", "8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c05"]',
    '["CHUAN_HOA_BCNF", "CHUAN_HOA_3NF", "d0000000-1122-3344-5566-778899aabb01", "a0000000-1122-3344-5566-778899aabb01"]',
    'Cách AI hỏi gợi ý tìm khóa dự tuyển trước giúp mình nhớ bản chất luôn, không bao giờ chọn nhầm nữa!',
    'LIKE',
    '2026-10-20 08:28:45',
    '2026-10-20 08:28:45'
),

-- ------------------------------------------------------------------------------
-- HỘI THOẠI 2 (Phiên 1C...02): Linh hỏi về lấy Top 3 điểm cao nhất mỗi lớp bằng Window Function (4 tin nhắn)
-- ------------------------------------------------------------------------------
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C05'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C02'),
    'USER',
    'Trong Bài tập số 2 môn CSDL yêu cầu tìm Top 3 sinh viên có điểm cao nhất mỗi lớp trên MySQL 8.0, mình phân vân chưa biết nên dùng ROW_NUMBER(), RANK() hay DENSE_RANK()?',
    1,
    '[]',
    '[]',
    NULL,
    NULL,
    '2026-10-20 10:05:12',
    '2026-10-20 10:05:12'
),
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C06'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C02'),
    'ASSISTANT',
    'Chào Linh! Để chọn đúng hàm cửa sổ (Window Function), chúng ta hãy xét một tình huống thực tế ở **Bước 1/2** nhé:
Giả sử trong lớp `INT1306-01` có 4 sinh viên với số điểm lần lượt là **`9.5`, `9.5`, `9.0`, `8.5`**. Nếu đề bài yêu cầu lấy các sinh viên thuộc **3 mức điểm cao nhất của lớp**, theo Linh bạn đạt `8.5` điểm có xứng đáng nằm trong danh sách Top 3 mức điểm cao nhất không, và ba hàm `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()` sẽ đánh số thứ hạng cho dãy `[9.5, 9.5, 9.0, 8.5]` khác nhau thế nào?',
    1,
    '["8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c02"]',
    '["SQL_JOIN", "WINDOW_FUNCTION_DENSE_RANK", "77889900-1122-3344-5566-778899aabb02", "b0000000-1122-3344-5566-778899aabb04"]',
    NULL,
    NULL,
    '2026-10-20 10:05:25',
    '2026-10-20 10:05:25'
),
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C07'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C02'),
    'USER',
    'À! Với [9.5, 9.5, 9.0, 8.5] thì ROW_NUMBER() đánh số [1, 2, 3, 4], RANK() bị nhảy cóc thành [1, 1, 3, 4] làm mất bạn 8.5 khi lọc <= 3, còn DENSE_RANK() đánh số [1, 1, 2, 3] nên giữ được trọn vẹn cả 3 mức điểm cao nhất!',
    2,
    '[]',
    '[]',
    NULL,
    NULL,
    '2026-10-20 10:14:00',
    '2026-10-20 10:14:00'
),
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C08'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C02'),
    'ASSISTANT',
    'Quá chuẩn luôn Linh ơi! Bạn đã tự phân biệt được sự khác nhau cốt lõi của cả 3 hàm rồi.
Ở **Bước 2/2 (Hoàn thiện câu lệnh SQL)**, vì MySQL không cho phép đặt trực tiếp hàm cửa sổ trong mệnh đề `WHERE`, bạn chỉ cần bọc `DENSE_RANK()` vào trong một **CTE (`WITH`)** như sau:
```sql
WITH RankedStudents AS (
    SELECT class_id, user_id, final_score,
           DENSE_RANK() OVER (PARTITION BY class_id ORDER BY final_score DESC) AS rnk
    FROM grade_reports
)
SELECT * FROM RankedStudents WHERE rnk <= 3;
```
Bạn đã hoàn thành trọn vẹn bài toán này rồi!',
    2,
    '["8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c02"]',
    '["SQL_JOIN", "WINDOW_FUNCTION_DENSE_RANK", "e0000000-1122-3344-5566-778899aabb01"]',
    'Ví dụ dãy điểm [9.5, 9.5, 9.0, 8.5] quá trực quan, giúp mình tự suy ra ngay!',
    '5',
    '2026-10-20 10:18:20',
    '2026-10-20 10:18:20'
),

-- ------------------------------------------------------------------------------
-- HỘI THOẠI 3 (Phiên 1C...03): Đức đang luyện phân biệt vi phạm 2NF vs 3NF (4 tin nhắn — đang dừng ở bước 2/3)
-- ------------------------------------------------------------------------------
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C09'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C03'),
    'USER',
    'Mình rất hay bị nhầm giữa phụ thuộc hàm bộ phận (vi phạm 2NF) và phụ thuộc hàm bắc cầu (vi phạm 3NF). AI hướng dẫn mình cách nhìn nhanh trong đề thi với!',
    1,
    '[]',
    '[]',
    NULL,
    NULL,
    '2026-10-20 14:30:05',
    '2026-10-20 14:30:05'
),
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C10'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C03'),
    'ASSISTANT',
    'Chào Đức! Để không bao giờ nhầm giữa 2NF và 3NF, mình cùng kiểm tra **Bước 1/3** trên một lược đồ quen thuộc nhé:
Cho bảng `KetQuaHocTap(MaSV, MaMon, HoTenSV, Diem, MaKhoa, TenKhoa)` có khóa chính là cặp khóa ghép **`(MaSV, MaMon)`** và hai phụ thuộc hàm:
- `(1) MaSV -> HoTenSV`
- `(2) MaKhoa -> TenKhoa` (với `MaSV -> MaKhoa`)
Theo Đức, ở phụ thuộc `(1) MaSV -> HoTenSV`, vế trái `MaSV` có mối quan hệ gì với khóa chính `(MaSV, MaMon)`?',
    1,
    '["8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c03", "8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c04"]',
    '["CHUAN_HOA_2NF", "CHUAN_HOA_3NF", "77889900-1122-3344-5566-778899aabb03", "b0000000-1122-3344-5566-778899aabb06"]',
    NULL,
    NULL,
    '2026-10-20 14:30:18',
    '2026-10-20 14:30:18'
),
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C11'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C03'),
    'USER',
    'Ở (1) thì MaSV chỉ là một phần (tập con thực sự) của khóa ghép (MaSV, MaMon) thôi, nên HoTenSV phụ thuộc bộ phận vào khóa chính -> đây là vi phạm 2NF đúng không ạ?',
    1,
    '[]',
    '[]',
    NULL,
    NULL,
    '2026-10-20 14:38:40',
    '2026-10-20 14:38:40'
),
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C12'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C03'),
    'ASSISTANT',
    'Đúng chuẩn luôn Đức! **Một phần của khóa suy ra thuộc tính không khóa = Phụ thuộc bộ phận (Vi phạm 2NF)**.
Bây giờ mình sang **Bước 2/3** nhé: Nhìn vào phụ thuộc thứ hai `(2) MaKhoa -> TenKhoa`. Ở đây cả `MaKhoa` lẫn `TenKhoa` đều có phải là thuộc tính nằm trong khóa chính không? Và khi **một thuộc tính không khóa lại suy ra một thuộc tính không khóa khác**, ta gọi đó là vi phạm dạng chuẩn mấy và cần tách bảng thế nào?',
    2,
    '["8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c03", "8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c04"]',
    '["CHUAN_HOA_3NF", "PHU_THUOC_BAC_CAU", "77889900-1122-3344-5566-778899aabb03", "b0000000-1122-3344-5566-778899aabb07"]',
    'Hỏi từng bước thế này giúp mình phân biệt rõ hẳn vế trái của 2NF và 3NF!',
    'LIKE',
    '2026-10-20 14:42:10',
    '2026-10-20 14:42:10'
),

-- ------------------------------------------------------------------------------
-- HỘI THOẠI 4 (Phiên 1C...04): Khôi hỏi về lỗi LazyInitializationException & N+1 Query (4 tin nhắn)
-- ------------------------------------------------------------------------------
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C13'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C04'),
    'USER',
    'Khi mình đặt spring.jpa.open-in-view=false theo đúng chuẩn kiến trúc của thầy Tuấn thì lúc map ClassEntity sang ClassResponseDTO bị nổ lỗi LazyInitializationException ở trường owner. Mình xử lý sao cho chuẩn nhất?',
    1,
    '[]',
    '[]',
    NULL,
    NULL,
    '2026-10-20 19:10:15',
    '2026-10-20 19:10:15'
),
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C14'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C04'),
    'ASSISTANT',
    'Chào Khôi! Đây là tình huống thực tế mà mọi lập trình viên Spring Boot đều gặp khi tắt `open-in-view`.
Ở **Bước 1/2**, bạn hãy kiểm tra xem:
1. Hàm lấy danh sách lớp học trong `ClassService` của bạn đã gắn `@Transactional(readOnly = true)` để giữ Hibernate Session mở trong suốt lúc `modelMapper` chạy chưa?
2. Nếu bạn duyệt qua `10` bản ghi `ClassEntity` trong vòng lặp `stream().map()` và mỗi bản ghi lại gọi `classEntity.getOwner()`, Hibernate sẽ bắn ra bao nhiêu câu lệnh `SELECT` xuống MySQL?',
    1,
    '["8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c08"]',
    '["JPA_N_PLUS_1", "DTO_PATTERN", "77889900-1122-3344-5566-778899aabb04", "b0000000-1122-3344-5566-778899aabb09"]',
    NULL,
    NULL,
    '2026-10-20 19:10:28',
    '2026-10-20 19:10:28'
),
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C15'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C04'),
    'USER',
    'Mình chưa gắn @Transactional ở hàm đọc! Mà nếu chỉ thêm @Transactional rồi lặp qua 10 lớp để lấy owner thì nó sẽ bắn 1 câu SELECT lấy danh sách lớp + 10 câu SELECT lấy từng owner (tổng cộng 11 câu - đúng lỗi N+1 Query luôn)!',
    2,
    '[]',
    '[]',
    NULL,
    NULL,
    '2026-10-20 19:19:45',
    '2026-10-20 19:19:45'
),
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C16'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C04'),
    'ASSISTANT',
    'Bạn phát hiện cực kỳ nhạy bén! Do đó ở **Bước 2/2 (Giải pháp triệt để)**, bạn hãy kết hợp cả hai thao tác:
1. Gắn `@Transactional(readOnly = true)` trên phương thức ở `ClassService`.
2. Gắn thêm **`@EntityGraph(attributePaths = {"owner"})`** ngay trên hàm tìm kiếm trong `ClassRepository` (ví dụ `Page<ClassEntity> findAll(Specification<ClassEntity> spec, Pageable pageable)`).
Khi đó Hibernate sẽ tự động sinh **1 câu lệnh `LEFT JOIN users` duy nhất**, vừa dứt điểm `LazyInitializationException` vừa triệt tiêu hoàn toàn bài toán `N+1 Query`!',
    2,
    '["8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c08"]',
    '["JPA_N_PLUS_1", "e0000000-1122-3344-5566-778899aabb02"]',
    'Đã gắn @EntityGraph + @Transactional(readOnly = true), bật show-sql thấy chỉ còn đúng 1 câu JOIN!',
    '5',
    '2026-10-20 19:24:00',
    '2026-10-20 19:24:00'
),

-- ------------------------------------------------------------------------------
-- HỘI THOẠI 5 (Phiên 1C...05): Tâm xây dựng phản ví dụ đồ thị 3 đỉnh cho thuật toán Dijkstra (2 tin nhắn)
-- ------------------------------------------------------------------------------
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C17'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C05'),
    'USER',
    'Theo gợi ý ở bước 1 của AI, mình đã thử vẽ đồ thị có hướng 3 đỉnh A, B, C xuất phát từ A với cạnh A -> B = 5, A -> C = 2 và cạnh âm B -> C = -10. Khi đó Dijkstra chốt đỉnh C trước với d[C] = 2 nên bỏ lỡ đường đi A -> B -> C có tổng trọng số 5 + (-10) = -5 đúng không ạ?',
    2,
    '[]',
    '[]',
    NULL,
    NULL,
    '2026-10-21 09:12:00',
    '2026-10-21 09:12:00'
),
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C18'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C05'),
    'ASSISTANT',
    'Xuất sắc quá Tâm ơi! Phản ví dụ 3 đỉnh `A -> B (5)`, `A -> C (2)`, `B -> C (-10)` của bạn đã chứng minh trọn vẹn bản chất tham lam (Greedy) của **Dijkstra**:
- Vì `d[C] = 2 < d[B] = 5`, Dijkstra lấy `C` ra khỏi `PriorityQueue` trước và khẳng định không thể có đường đi nào qua `B` ngắn hơn `2` (điều này chỉ đúng khi mọi cạnh $\ge 0$).
- Khi xét tiếp `B`, cạnh âm `B -> C = -10` kéo tổng chi phí xuống `-5 < 2` làm phá vỡ giả thuyết tham lam. Với đồ thị có cạnh âm, bạn nhớ chuyển sang dùng **Bellman-Ford** nhé!',
    2,
    '["8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c11"]',
    '["DIJKSTRA", "a0000000-1122-3344-5566-778899aabb02"]',
    'Tự nghĩ ra phản ví dụ 3 đỉnh theo gợi ý của AI làm mình nhớ nguyên lý tham lam cực lâu!',
    'LIKE',
    '2026-10-21 09:15:30',
    '2026-10-21 09:15:30'
),

-- ------------------------------------------------------------------------------
-- HỘI THOẠI 6 (Phiên 1C...06): Vy trao đổi về thiết kế Chunking cho RAG tiếng Việt (2 tin nhắn — đang ở bước 2/3)
-- ------------------------------------------------------------------------------
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C19'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C06'),
    'USER',
    'Trong bài tập thiết kế Text Chunker cho giáo trình CSDL tiếng Việt, nếu mình đặt chunk_size = 300 tokens nhưng đặt chunk_overlap = 0 (không gối đầu) thì sẽ gặp rủi ro gì khi truy xuất vector vậy AI?',
    2,
    '[]',
    '[]',
    NULL,
    NULL,
    '2026-10-21 15:32:10',
    '2026-10-21 15:32:10'
),
(
    UNHEX('2C2C2C2C2C2C2C2C2C2C2C2C2C2C2C20'),
    UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C06'),
    'ASSISTANT',
    'Câu hỏi rất trúng trọng tâm thiết kế RAG đấy Vy!
Ở **Bước 2/3**, hãy thử hình dung một trang slide giáo trình CSDL có cấu trúc: **Cuối đoạn 1 nêu Định nghĩa Dạng chuẩn BCNF**, và **ngay đầu đoạn 2 nêu Ví dụ minh họa `R(A,B,C,D)`**. Nếu nhát cắt rơi đúng vào giữa hai đoạn mà `chunk_overlap = 0`, khi sinh viên hỏi *"Cho ví dụ về vi phạm BCNF"*, chuyện gì sẽ xảy ra với vector của Chunk 2 (chứa công thức `AB -> C, C -> D, D -> A` nhưng mất tiêu câu tiêu đề *"Ví dụ về BCNF"* ở cuối Chunk 1)? Từ đó theo Vy nên để tỷ lệ `chunk_overlap` khoảng bao nhiêu % của `chunk_size`?',
    2,
    '["8c8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c12"]',
    '["RAG_EMBEDDING", "77889900-1122-3344-5566-778899aabb06", "b0000000-1122-3344-5566-778899aabb14"]',
    'Gợi ý tình huống đứt câu giữa Định nghĩa và Ví dụ quá thực tế!',
    '5',
    '2026-10-21 15:35:00',
    '2026-10-21 15:35:00'
);


-- 34. Bảng student_error_patterns (8 mẫu lỗi sai thường gặp của học viên được AI phát hiện)
INSERT INTO `student_error_patterns` (`id`, `user_id`, `knowledge_entity_id`, `error_description`, `frequency`, `last_occurred_at`) VALUES
(UNHEX('4C4C4C4C4C4C4C4C4C4C4C4C4C4C4C01'), UNHEX('12345678901234567890123456789012'), 'CHUAN_HOA_BCNF', 'Nhầm lẫn điều kiện thuộc tính khóa ở vế phải của chuẩn 3NF với điều kiện siêu khóa bắt buộc ở vế trái của chuẩn BCNF khi lược đồ có nhiều khóa ứng viên chồng lấn.', 2, NOW()),
(UNHEX('4C4C4C4C4C4C4C4C4C4C4C4C4C4C4C02'), UNHEX('12345678901234567890123456789014'), 'CHUAN_HOA_3NF', 'Thường xuyên nhầm lẫn giữa phụ thuộc hàm bộ phận (vi phạm 2NF) và phụ thuộc hàm bắc cầu giữa hai thuộc tính không khóa (vi phạm 3NF).', 4, NOW()),
(UNHEX('4C4C4C4C4C4C4C4C4C4C4C4C4C4C4C03'), UNHEX('12345678901234567890123456789014'), 'SQL_JOIN', 'Dùng INNER JOIN thay vì LEFT JOIN khi đề bài yêu cầu thống kê cả các thực thể chưa phát sinh giao dịch (làm mất các dòng có giá trị COUNT = 0).', 3, NOW()),
(UNHEX('4C4C4C4C4C4C4C4C4C4C4C4C4C4C4C04'), UNHEX('12345678901234567890123456789016'), 'JPA_N_PLUS_1', 'Truy cập tập hợp quan hệ FetchType.LAZY bên trong vòng lặp stream().map() mà không dùng @EntityGraph hoặc JOIN FETCH.', 2, NOW()),
(UNHEX('4C4C4C4C4C4C4C4C4C4C4C4C4C4C4C05'), UNHEX('12345678901234567890123456789018'), 'TRANSACTION_ACID', 'Chưa phân biệt rõ hiện tượng Non-repeatable Read (do UPDATE) và Phantom Read (do INSERT/DELETE thêm dòng mới).', 3, NOW()),
(UNHEX('4C4C4C4C4C4C4C4C4C4C4C4C4C4C4C06'), UNHEX('12345678901234567890123456789019'), 'DIJKSTRA', 'Quên kiểm tra điều kiện bỏ qua các trạng thái cũ trong PriorityQueue (if d > dist[u] continue) làm tăng độ phức tạp thời gian.', 2, NOW()),
(UNHEX('4C4C4C4C4C4C4C4C4C4C4C4C4C4C4C07'), UNHEX('12345678901234567890123456789020'), 'QUICKSORT', 'Chọn phần tử chốt (Pivot) cố định ở đầu mảng dẫn tới bị quá thời gian (TLE) trên bộ test mảng đã sắp xếp tăng dần.', 3, NOW()),
(UNHEX('4C4C4C4C4C4C4C4C4C4C4C4C4C4C4C08'), UNHEX('12345678901234567890123456789021'), 'KHOA_CHINH', 'Quên kiểm tra bao đóng tập thuộc tính khi lược đồ có từ 2 khóa dự tuyển trở lên.', 2, NOW());

-- 35. Bảng student_knowledge_heatmaps (16 bản đồ nhiệt mức độ thành thạo kiến thức: 0.000 -> 1.000)
INSERT INTO `student_knowledge_heatmaps` (`id`, `user_id`, `knowledge_entity_id`, `mastery_level`, `last_assessed_at`, `created_at`) VALUES
-- Bản đồ nhiệt của Nguyễn Hoàng Nam (namnh)
(UNHEX('5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C01'), UNHEX('12345678901234567890123456789012'), 'KHOA_CHINH', 0.960, NOW(), NOW()),
(UNHEX('5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C02'), UNHEX('12345678901234567890123456789012'), 'SQL_JOIN', 0.920, NOW(), NOW()),
(UNHEX('5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C03'), UNHEX('12345678901234567890123456789012'), 'CHUAN_HOA_3NF', 0.880, NOW(), NOW()),
(UNHEX('5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C04'), UNHEX('12345678901234567890123456789012'), 'CHUAN_HOA_BCNF', 0.620, NOW(), NOW()),
(UNHEX('5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C05'), UNHEX('12345678901234567890123456789012'), 'SPRING_SECURITY_JWT', 0.950, NOW(), NOW()),
-- Bản đồ nhiệt của Phạm Phương Linh (linhpp)
(UNHEX('5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C06'), UNHEX('12345678901234567890123456789013'), 'KHOA_CHINH', 0.980, NOW(), NOW()),
(UNHEX('5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C07'), UNHEX('12345678901234567890123456789013'), 'SQL_JOIN', 0.950, NOW(), NOW()),
(UNHEX('5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C08'), UNHEX('12345678901234567890123456789013'), 'CHUAN_HOA_3NF', 0.940, NOW(), NOW()),
(UNHEX('5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C09'), UNHEX('12345678901234567890123456789013'), 'CHUAN_HOA_BCNF', 0.910, NOW(), NOW()),
-- Bản đồ nhiệt của Vũ Văn Đức (ducvv)
(UNHEX('5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C10'), UNHEX('12345678901234567890123456789014'), 'KHOA_CHINH', 0.850, NOW(), NOW()),
(UNHEX('5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C11'), UNHEX('12345678901234567890123456789014'), 'SQL_JOIN', 0.540, NOW(), NOW()),
(UNHEX('5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C12'), UNHEX('12345678901234567890123456789014'), 'CHUAN_HOA_3NF', 0.480, NOW(), NOW()),
-- Bản đồ nhiệt của Trần Minh Khôi, Đặng Quốc Bảo, Bùi Thị Thanh Tâm
(UNHEX('5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C13'), UNHEX('12345678901234567890123456789016'), 'JPA_N_PLUS_1', 0.720, NOW(), NOW()),
(UNHEX('5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C14'), UNHEX('12345678901234567890123456789016'), 'INDEX_BTREE', 0.930, NOW(), NOW()),
(UNHEX('5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C15'), UNHEX('12345678901234567890123456789018'), 'TRANSACTION_ACID', 0.420, NOW(), NOW()),
(UNHEX('5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C16'), UNHEX('12345678901234567890123456789019'), 'DIJKSTRA', 0.810, NOW(), NOW());

-- 23. Bảng ai_study_recommendations (8 khuyến nghị học tập cá nhân hóa từ AI)
INSERT INTO `ai_study_recommendations` (`id`, `user_id`, `knowledge_entity_id`, `priority_level`, `status`, `recommendation_note`, `created_at`, `updated_at`) VALUES
(UNHEX('7C7C7C7C7C7C7C7C7C7C7C7C7C7C7C01'), UNHEX('12345678901234567890123456789012'), 'CHUAN_HOA_BCNF', 'MEDIUM', 'PENDING', 'Bạn đã nắm rất chắc chuẩn 3NF (88%) nhưng còn nhầm trường hợp lược đồ có nhiều khóa ứng viên chồng lấn ở chuẩn BCNF (62%). Hãy xem lại Bài 3.2 (phút 35:00) và làm thêm 3 bài tập phân rã BCNF.', NOW(), NOW()),
(UNHEX('7C7C7C7C7C7C7C7C7C7C7C7C7C7C7C02'), UNHEX('12345678901234567890123456789014'), 'CHUAN_HOA_3NF', 'HIGH', 'IN_PROGRESS', 'Mức độ thành thạo Chuẩn hóa 3NF của bạn đang ở mức 48%. Bạn cần ôn lại cách tìm bao đóng tập thuộc tính X+ ở Bài 3.1 để phân biệt rõ thuộc tính khóa và thuộc tính không khóa trước kỳ thi giữa kỳ.', NOW(), NOW()),
(UNHEX('7C7C7C7C7C7C7C7C7C7C7C7C7C7C7C03'), UNHEX('12345678901234567890123456789014'), 'SQL_JOIN', 'HIGH', 'PENDING', 'Bạn hay dùng nhầm INNER JOIN thay cho LEFT JOIN trong các bài toán thống kê có giá trị bằng 0. Hãy chạy lại câu số 8 đến câu số 14 trong file Script thực hành Chương 2.', NOW(), NOW()),
(UNHEX('7C7C7C7C7C7C7C7C7C7C7C7C7C7C7C04'), UNHEX('12345678901234567890123456789016'), 'JPA_N_PLUS_1', 'MEDIUM', 'COMPLETED', 'Hãy bổ sung @EntityGraph vào các phương thức tìm kiếm danh sách lớp học trong ClassRepository để tránh phát sinh truy vấn con lặp lại.', NOW(), NOW()),
(UNHEX('7C7C7C7C7C7C7C7C7C7C7C7C7C7C7C05'), UNHEX('12345678901234567890123456789018'), 'TRANSACTION_ACID', 'HIGH', 'PENDING', 'Mức độ nắm vững Giao dịch & Mức cô lập của bạn đang thấp (42%). Hãy đọc kỹ Slide Chương 4 về sự khác biệt giữa READ COMMITTED và REPEATABLE READ trong InnoDB.', NOW(), NOW()),
(UNHEX('7C7C7C7C7C7C7C7C7C7C7C7C7C7C7C06'), UNHEX('12345678901234567890123456789019'), 'DIJKSTRA', 'LOW', 'PENDING', 'Bạn đã cài đặt đúng thuật toán Dijkstra (81%). Hãy luyện thêm bài toán tìm đường đi ngắn nhất thứ K (K-shortest paths) để nâng cao kỹ năng.', NOW(), NOW()),
(UNHEX('7C7C7C7C7C7C7C7C7C7C7C7C7C7C7C07'), UNHEX('12345678901234567890123456789013'), 'INDEX_BTREE', 'LOW', 'PENDING', 'Bạn đã hoàn thành xuất sắc phần Chuẩn hóa CSDL (>90%). Gợi ý tìm hiểu sâu thêm về Covering Index và Index Merge Optimization trong Chương 4.', NOW(), NOW()),
(UNHEX('7C7C7C7C7C7C7C7C7C7C7C7C7C7C7C08'), UNHEX('12345678901234567890123456789020'), 'QUICKSORT', 'MEDIUM', 'IN_PROGRESS', 'Hãy áp dụng kỹ thuật chọn chốt ngẫu nhiên (Randomized QuickSort) hoặc Median-of-Three để tránh độ phức tạp O(N^2) khi mảng đầu vào đã có thứ tự.', NOW(), NOW());

-- 27. Bảng material_chunks
-- Imported seed fixtures are unverified: no fabricated source hash/snapshot or teacher approval.
-- No material_publications row is created; publish only through the reviewed workflow.
INSERT INTO material_versions (
    id, material_id, version_number, source_hash, source_snapshot_url,
    parser_version, chunker_version, created_by
)
SELECT UNHEX(REPLACE(UUID(), '-', '')), m.id, 1, NULL, NULL,
       'seed-fixture', 'seed-fixture', m.uploaded_by
FROM materials m;

INSERT INTO `material_chunks` (
`id`,
    `material_id`,
    `owner_id`,
    `scope`,
    `subject`,
    `chunk_index`,
    `content`,
    `token_count`,
    `char_start`,
    `char_end`,
    `canonical_codes`,
    `extraction_status`,
    `extraction_error`,
    `extra_metadata`,
    `created_at`,
    `updated_at`,
    `material_version_id`
) VALUES
-- Chunk 1: Khóa chính & Ràng buộc toàn vẹn thực thể (Môn INT1306 - Bản chuẩn GLOBAL)
(
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C01'),
    UNHEX('FFFF1111FFFF1111FFFF1111FFFF1102'),
    UNHEX('AAAAAAAAAAAAAAAA0000000000000001'),
    'GLOBAL',
    'INT1306',
    0,
    'Ràng buộc toàn vẹn thực thể (Entity Integrity) và Khóa chính (Primary Key): Trong mô hình cơ sở dữ liệu quan hệ, một lược đồ quan hệ R có thể có nhiều khóa dự tuyển (Candidate Keys) là các siêu khóa tối tiểu. Quản trị viên CSDL chọn một khóa dự tuyển làm khóa chính (Primary Key). Ràng buộc toàn vẹn thực thể quy định mọi thuộc tính tham gia vào khóa chính tuyệt đối không được nhận giá trị rỗng (NOT NULL) và giá trị khóa chính phải duy nhất giữa các bộ.',
    142,
    0,
    468,
    '["KHOA_CHINH", "KHOA_UNG_VIEN", "RANG_BUOC_THUC_THE"]',
    'COMPLETED',
    NULL,
    '{"course_code": "INT1306", "chapter": "Chương 1: Thiết kế ERD & Ánh xạ Quan hệ", "page": 14, "section": "1.4. Ràng buộc khóa"}',
    NOW(),
    NOW()
,
    (SELECT v.id FROM material_versions v WHERE v.material_id = UNHEX('FFFF1111FFFF1111FFFF1111FFFF1102') AND v.version_number = 1)),
-- Chunk 2: Truy vấn SQL JOIN & Window Functions DENSE_RANK (Môn INT1306 - Học liệu TEACHER của cô Trần Thị Hương)
(
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C02'),
    UNHEX('FFFF1111FFFF1111FFFF1111FFFF1103'),
    UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'),
    'TEACHER',
    'INT1306',
    0,
    'Phân biệt INNER JOIN, LEFT OUTER JOIN và hàm cửa sổ DENSE_RANK() trên MySQL 8.0: Khi thống kê số lượng thực thể con (ví dụ đếm số sinh viên đăng ký mỗi học phần bao gồm cả học phần có 0 sinh viên), bắt buộc dùng LEFT JOIN từ bảng cha sang bảng con kết hợp COUNT(bảng_con.id). Khi xếp hạng lấy Top K điểm cao nhất mỗi lớp mà không muốn nhảy bậc thứ hạng khi có điểm trùng nhau, sử dụng DENSE_RANK() OVER (PARTITION BY class_id ORDER BY score DESC) bên trong biểu thức bảng chung (CTE WITH).',
    158,
    0,
    512,
    '["SQL_JOIN", "WINDOW_FUNCTION_DENSE_RANK"]',
    'COMPLETED',
    NULL,
    '{"course_code": "INT1306", "chapter": "Chương 2: Mô hình quan hệ và SQL", "page": 28, "section": "2.3. Outer Join & Window Functions"}',
    NOW(),
    NOW()
,
    (SELECT v.id FROM material_versions v WHERE v.material_id = UNHEX('FFFF1111FFFF1111FFFF1111FFFF1103') AND v.version_number = 1)),
-- Chunk 3: Định nghĩa Dạng chuẩn 2 (2NF) và Phụ thuộc hàm bộ phận (Môn INT1306 - Học liệu TEACHER của cô Trần Thị Hương)
(
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C03'),
    UNHEX('FFFF1111FFFF1111FFFF1111FFFF1104'),
    UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'),
    'TEACHER',
    'INT1306',
    0,
    'Định nghĩa Dạng chuẩn 2 (2NF): Một lược đồ quan hệ R ở dạng chuẩn 2 (2NF) nếu nó đã ở dạng chuẩn 1 (1NF) và mọi thuộc tính không khóa (Non-prime Attribute) của R đều phụ thuộc hàm đầy đủ vào mọi khóa dự tuyển của R. Nói cách khác, không tồn tại thuộc tính không khóa A nào chỉ phụ thuộc vào một tập con thực sự của một khóa dự tuyển K (vi phạm phụ thuộc hàm bộ phận - Partial Dependency). Lưu ý: Nếu mọi khóa dự tuyển của R đều chỉ gồm 1 thuộc tính đơn thì R ở 1NF chắc chắn đạt 2NF.',
    152,
    0,
    505,
    '["CHUAN_HOA_2NF", "CHUAN_HOA_3NF", "KHOA_CHINH"]',
    'COMPLETED',
    NULL,
    '{"course_code": "INT1306", "chapter": "Chương 3: Phụ thuộc hàm và Chuẩn hóa", "page": 9, "section": "3.2. Dạng chuẩn 2NF"}',
    NOW(),
    NOW()
,
    (SELECT v.id FROM material_versions v WHERE v.material_id = UNHEX('FFFF1111FFFF1111FFFF1111FFFF1104') AND v.version_number = 1)),
-- Chunk 4: Định nghĩa Dạng chuẩn 3 (3NF) và Phụ thuộc hàm bắc cầu (Môn INT1306 - Học liệu TEACHER của cô Trần Thị Hương)
(
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C04'),
    UNHEX('FFFF1111FFFF1111FFFF1111FFFF1104'),
    UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'),
    'TEACHER',
    'INT1306',
    1,
    'Định nghĩa Dạng chuẩn 3 (3NF): Một lược đồ quan hệ R ở dạng chuẩn 3 (3NF) nếu nó ở dạng chuẩn 2 (2NF) và không có bất kỳ thuộc tính không khóa nào của R phụ thuộc hàm bắc cầu (Transitive Dependency) vào một khóa dự tuyển bất kỳ của R. Phát biểu tương đương dùng để kiểm tra nhanh trong đề thi: Với mọi phụ thuộc hàm không tầm thường X -> A thỏa mãn trên R, HOẶC vế trái X là một siêu khóa của R, HOẶC vế phải A là một thuộc tính khóa (Prime Attribute - tức A tham gia vào ít nhất một khóa dự tuyển).',
    156,
    460,
    995,
    '["CHUAN_HOA_3NF", "PHU_THUOC_BAC_CAU"]',
    'COMPLETED',
    NULL,
    '{"course_code": "INT1306", "chapter": "Chương 3: Phụ thuộc hàm và Chuẩn hóa", "page": 15, "section": "3.3. Dạng chuẩn 3NF"}',
    NOW(),
    NOW()
,
    (SELECT v.id FROM material_versions v WHERE v.material_id = UNHEX('FFFF1111FFFF1111FFFF1111FFFF1104') AND v.version_number = 1)),
-- Chunk 5: Định nghĩa Dạng chuẩn Boyce-Codd (BCNF) và trường hợp nhiều khóa chồng lấn (Môn INT1306 - Học liệu TEACHER của cô Trần Thị Hương)
(
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C05'),
    UNHEX('FFFF1111FFFF1111FFFF1111FFFF1104'),
    UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'),
    'TEACHER',
    'INT1306',
    2,
    'Định nghĩa Dạng chuẩn Boyce-Codd (BCNF): Một lược đồ quan hệ R ở dạng chuẩn BCNF nếu với mọi phụ thuộc hàm không tầm thường X -> A thỏa mãn trên R, vế trái X bắt buộc phải là một siêu khóa (Superkey) của R. BCNF loại bỏ hoàn toàn điều kiện ân xá "A là thuộc tính khóa" của 3NF. Ví dụ điển hình: Cho R(A,B,C,D) với F = {AB -> C, C -> D, D -> A}, các khóa dự tuyển là AB, BC, BD nên mọi thuộc tính đều là thuộc tính khóa (R đạt 3NF), nhưng vì C và D không phải siêu khóa nên C -> D và D -> A vi phạm BCNF.',
    168,
    940,
    1510,
    '["CHUAN_HOA_BCNF", "CHUAN_HOA_3NF"]',
    'COMPLETED',
    NULL,
    '{"course_code": "INT1306", "chapter": "Chương 3: Phụ thuộc hàm và Chuẩn hóa", "page": 21, "section": "3.4. Dạng chuẩn BCNF"}',
    NOW(),
    NOW()
,
    (SELECT v.id FROM material_versions v WHERE v.material_id = UNHEX('FFFF1111FFFF1111FFFF1111FFFF1104') AND v.version_number = 1)),
-- Chunk 6: Giao dịch ACID & Mức cô lập giao dịch trong MySQL InnoDB (Môn INT1306 - Bản chuẩn GLOBAL)
(
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C06'),
    UNHEX('FFFF1111FFFF1111FFFF1111FFFF1105'),
    UNHEX('AAAAAAAAAAAAAAAA0000000000000001'),
    'GLOBAL',
    'INT1306',
    0,
    'Giao dịch ACID và 4 mức cô lập (Isolation Levels) trong MySQL InnoDB: Đọc bẩn (Dirty Read) xảy ra khi đọc dữ liệu chưa COMMIT; Đọc không lặp lại (Non-repeatable Read) xảy ra khi giao dịch khác UPDATE và COMMIT một dòng đang đọc; Đọc bóng ma (Phantom Read) xảy ra khi giao dịch khác INSERT hoặc DELETE làm thay đổi tập kết quả thỏa điều kiện WHERE. InnoDB đặt mức mặc định là REPEATABLE READ kết hợp cơ chế MVCC (Read View) và khóa Next-Key Lock để ngăn chặn cả Non-repeatable Read lẫn Phantom Read.',
    160,
    0,
    520,
    '["TRANSACTION_ACID", "ISOLATION_LEVELS"]',
    'COMPLETED',
    NULL,
    '{"course_code": "INT1306", "chapter": "Chương 4: Giao dịch và Chỉ mục", "page": 6, "section": "4.1. ACID & Isolation Levels"}',
    NOW(),
    NOW()
,
    (SELECT v.id FROM material_versions v WHERE v.material_id = UNHEX('FFFF1111FFFF1111FFFF1111FFFF1105') AND v.version_number = 1)),
-- Chunk 7: Cấu trúc chỉ mục B+Tree và Composite Index (Môn INT1306 - Học liệu TEACHER của cô Trần Thị Hương)
(
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C07'),
    UNHEX('FFFF1111FFFF1111FFFF1111FFFF1105'),
    UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDD'),
    'TEACHER',
    'INT1306',
    1,
    'Cấu trúc chỉ mục B+Tree trong InnoDB (MySQL 8.0): Khác với cây BST hay B-Tree truyền thống, cây B+Tree có hệ số phân nhánh (fan-out) rất lớn giúp chiều cao cây chỉ từ 3-4 tầng cho hàng chục triệu dòng, giảm tối đa số thao tác đọc đĩa (Disk I/O). Các nút trong (Internal Nodes) chỉ chứa khóa định hướng, còn toàn bộ dữ liệu hoặc khóa chính nằm ở nút lá (Leaf Nodes) nối với nhau bằng danh sách liên kết kép giúp truy vấn khoảng (BETWEEN, >, <, ORDER BY) cực nhanh.',
    154,
    480,
    980,
    '["INDEX_BTREE"]',
    'COMPLETED',
    NULL,
    '{"course_code": "INT1306", "chapter": "Chương 4: Giao dịch và Chỉ mục", "page": 18, "section": "4.3. Cấu trúc B+Tree Index"}',
    NOW(),
    NOW()
,
    (SELECT v.id FROM material_versions v WHERE v.material_id = UNHEX('FFFF1111FFFF1111FFFF1111FFFF1105') AND v.version_number = 1)),
-- Chunk 8: Kiến trúc Phân tầng, DTO Pattern & phòng chống N+1 Query trong Spring Boot (Môn INT1434 - Học liệu TEACHER của thầy Lê Anh Tuấn)
(
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C08'),
    UNHEX('FFFF1111FFFF1111FFFF1111FFFF1106'),
    UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'),
    'TEACHER',
    'INT1434',
    0,
    'Chuẩn kiến trúc Spring Boot 3.3 (DTO Pattern & Xử lý lỗi N+1 Query): Controller tuyệt đối không trả trực tiếp JPA Entity về Client nhằm tránh lộ trường nhạy cảm (password hash) và lỗi đệ quy JSON hai chiều, mà phải ánh xạ sang DTO bọc trong ApiResponse<T>. Khi cấu hình spring.jpa.open-in-view=false, để tránh LazyInitializationException và bài toán N+1 Query trên các quan hệ FetchType.LAZY, phải đặt @Transactional(readOnly = true) tại tầng Service kết hợp @EntityGraph(attributePaths = {...}) hoặc JOIN FETCH tại Repository.',
    164,
    0,
    540,
    '["DTO_PATTERN", "JPA_N_PLUS_1"]',
    'COMPLETED',
    NULL,
    '{"course_code": "INT1434", "chapter": "Chương 1 & 2: Kiến trúc Spring Boot & JPA", "page": 11, "section": "2.2. N+1 Query & EntityGraph"}',
    NOW(),
    NOW()
,
    (SELECT v.id FROM material_versions v WHERE v.material_id = UNHEX('FFFF1111FFFF1111FFFF1111FFFF1106') AND v.version_number = 1)),
-- Chunk 9: Bảo mật JWT qua HttpOnly Cookie & Phân quyền RBAC 2 tầng (Môn INT1434 - Học liệu TEACHER của thầy Lê Anh Tuấn)
(
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C09'),
    UNHEX('FFFF1111FFFF1111FFFF1111FFFF1107'),
    UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDE'),
    'TEACHER',
    'INT1434',
    0,
    'Xác thực JWT qua HttpOnly Cookie và Phân quyền 2 tầng trong ILMS: Lưu trữ Access Token và Refresh Token trong Cookie có cờ HttpOnly=true, Secure=true, SameSite=Lax giúp ngăn chặn hoàn toàn mã độc JavaScript đọc trộm token qua document.cookie khi xảy ra tấn công XSS. Hệ thống áp dụng RBAC 2 tầng: cấp hệ thống kiểm tra ROLE_ADMIN / ROLE_USER qua @PreAuthorize, còn cấp lớp học kiểm tra vai trò OWNER / TEACHER / STUDENT theo ngữ cảnh classId trong bảng class_members.',
    148,
    0,
    492,
    '["SPRING_SECURITY_JWT"]',
    'COMPLETED',
    NULL,
    '{"course_code": "INT1434", "chapter": "Chương 2: Bảo mật Spring Security 6", "page": 7, "section": "2.1. JWT HttpOnly Cookie & RBAC"}',
    NOW(),
    NOW()
,
    (SELECT v.id FROM material_versions v WHERE v.material_id = UNHEX('FFFF1111FFFF1111FFFF1111FFFF1107') AND v.version_number = 1)),
-- Chunk 10: Phân tích độ phức tạp QuickSort & Chọn chốt ngẫu nhiên (Môn INT1303 - Bản chuẩn GLOBAL)
(
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C10'),
    UNHEX('FFFF1111FFFF1111FFFF1111FFFF1108'),
    UNHEX('AAAAAAAAAAAAAAAA0000000000000001'),
    'GLOBAL',
    'INT1303',
    0,
    'Độ phức tạp thuật toán QuickSort và kỹ thuật chọn phần tử chốt (Pivot): QuickSort hoạt động theo chiến lược Chia để trị với độ phức tạp trung bình đạt O(N log N). Tuy nhiên nếu chọn Pivot cố định ở đầu hoặc cuối mảng trên dữ liệu đầu vào đã sắp xếp tăng/giảm dần, cây đệ quy bị lệch hoàn toàn làm độ phức tạp suy biến thành O(N^2) gây quá thời gian (TLE). Giải pháp chuẩn là chọn chốt ngẫu nhiên (Randomized Pivot) hoặc trung vị của 3 phần tử đầu - giữa - cuối (Median-of-Three).',
    150,
    0,
    498,
    '["QUICKSORT"]',
    'COMPLETED',
    NULL,
    '{"course_code": "INT1303", "chapter": "Chương 1: Đệ quy và Sắp xếp", "page": 19, "section": "1.3. Phân tích QuickSort"}',
    NOW(),
    NOW()
,
    (SELECT v.id FROM material_versions v WHERE v.material_id = UNHEX('FFFF1111FFFF1111FFFF1111FFFF1108') AND v.version_number = 1)),
-- Chunk 11: Thuật toán Dijkstra với PriorityQueue và điều kiện trọng số không âm (Môn INT1303 - Học liệu TEACHER của thầy Nguyễn Văn Hiếu)
(
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C11'),
    UNHEX('FFFF1111FFFF1111FFFF1111FFFF1109'),
    UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDDF'),
    'TEACHER',
    'INT1303',
    0,
    'Thuật toán Dijkstra tìm đường đi ngắn nhất từ một đỉnh nguồn u0: Sử dụng hàng đợi ưu tiên Min-Heap (PriorityQueue) lưu cặp (khoảng cách d[u], đỉnh u) với độ phức tạp O((V + E) log V). Khi lấy cặp (d, u) ra khỏi hàng đợi, bắt buộc kiểm tra điều kiện if (d > dist[u]) continue để bỏ qua trạng thái cũ. Vì chiến lược tham lam của Dijkstra giả định đỉnh đã đóng có khoảng cách tối ưu vĩnh viễn, thuật toán sẽ chạy sai nếu đồ thị có cạnh mang trọng số âm (khi đó phải dùng Bellman-Ford).',
    155,
    0,
    515,
    '["DIJKSTRA"]',
    'COMPLETED',
    NULL,
    '{"course_code": "INT1303", "chapter": "Chương 3: Lý thuyết Đồ thị", "page": 12, "section": "3.2. Thuật toán Dijkstra"}',
    NOW(),
    NOW()
,
    (SELECT v.id FROM material_versions v WHERE v.material_id = UNHEX('FFFF1111FFFF1111FFFF1111FFFF1109') AND v.version_number = 1)),
-- Chunk 12: Kiến trúc Hybrid RAG, Chunking & Chống ảo giác cho LLM (Môn INT1405 - Học liệu TEACHER của cô Vũ Thị Ngọc Bích)
(
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C12'),
    UNHEX('FFFF1111FFFF1111FFFF1111FFFF1110'),
    UNHEX('CCCCCCCCCCCCCCCCDDDDDDDDDDDDDDD1'),
    'TEACHER',
    'INT1405',
    0,
    'Chiến lược Chunking và chống ảo giác (Hallucination) trong hệ thống Hybrid RAG Giáo dục: Với giáo trình đại học tiếng Việt chứa nhiều định nghĩa và công thức, nên chia nhỏ văn bản theo cấu trúc đoạn văn với kích thước chunk_size từ 250 đến 512 tokens và độ gối đầu (chunk_overlap) từ 40 đến 64 tokens để bảo toàn ngữ cảnh giữa định nghĩa và ví dụ. Kết hợp truy xuất Vector trên ChromaDB với Đồ thị Tri thức Neo4j giúp Gia sư Socratic dẫn dắt từng bước chính xác mà không bịa đặt kiến thức.',
    156,
    0,
    518,
    '["RAG_EMBEDDING"]',
    'COMPLETED',
    NULL,
    '{"course_code": "INT1405", "chapter": "Chương 2: Vector Embedding và Kiến trúc RAG", "page": 16, "section": "2.1. Hybrid RAG Pipeline"}',
    NOW(),
    NOW()
,
    (SELECT v.id FROM material_versions v WHERE v.material_id = UNHEX('FFFF1111FFFF1111FFFF1111FFFF1110') AND v.version_number = 1));

-- INSERT INTO `student_misconceptions` (
--     `id`,
--     `student_id`,
--     `session_id`,
--     `canonical_code`,
--     `misconception_summary`,
--     `is_resolved`,
--     `created_at`
-- ) VALUES
-- -- Lỗi sai của Nguyễn Hoàng Nam (namnh) trong Phiên 1 (Đã giải quyết)
-- (
--     UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A01'),
--     UNHEX('12345678901234567890123456789012'),
--     UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C01'),
--     'CHUAN_HOA_BCNF',
--     'Sinh viên nhầm lẫn rằng nếu lược đồ quan hệ đã đạt 3NF thì sẽ tự động đạt BCNF mà không xét đến các phụ thuộc hàm có vế trái không phải là siêu khóa (trường hợp khóa ứng viên chồng lấn).',
--     1,
--     '2026-10-20 08:20:00'
-- ),
-- -- Lỗi sai của Phạm Phương Linh (linhpp) trong Phiên 2 (Đã giải quyết)
-- (
--     UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A02'),
--     UNHEX('12345678901234567890123456789013'),
--     UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C02'),
--     'SQL_JOIN',
--     'Sinh viên cố gắng sử dụng GROUP BY kết hợp với LIMIT để lấy Top 3, dẫn đến kết quả sai khi có nhiều sinh viên trùng điểm nhau (không dùng Window Function DENSE_RANK).',
--     1,
--     '2026-10-20 10:10:00'
-- ),
-- -- Lỗi sai của Vũ Văn Đức (ducvv) trong Phiên 3 (Chưa giải quyết - Phiên đang dừng)
-- (
--     UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A03'),
--     UNHEX('12345678901234567890123456789014'),
--     UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C03'),
--     'CHUAN_HOA_3NF',
--     'Sinh viên chưa phân biệt được thuộc tính khóa và thuộc tính không khóa, lầm tưởng phụ thuộc hàm X -> Y (với X là một phần của khóa) là phụ thuộc bắc cầu thay vì phụ thuộc bộ phận.',
--     0,
--     '2026-10-20 14:35:00'
-- ),
-- -- Lỗi sai của Trần Minh Khôi (khoitm) trong Phiên 4 (Đã giải quyết)
-- (
--     UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A04'),
--     UNHEX('12345678901234567890123456789016'),
--     UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C04'),
--     'JPA_N_PLUS_1',
--     'Sinh viên cho rằng đổi FetchType.LAZY sang FetchType.EAGER là cách tốt nhất để sửa lỗi LazyInitializationException, mà không nhận ra điều này sinh ra vấn đề N+1 Query làm sập hiệu năng.',
--     1,
--     '2026-10-20 19:15:00'
-- ),
-- -- Lỗi sai của Bùi Thị Thanh Tâm (tambtt) trong Phiên 5 (Đã giải quyết)
-- (
--     UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A05'),
--     UNHEX('12345678901234567890123456789019'),
--     UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C05'),
--     'DIJKSTRA',
--     'Sinh viên lầm tưởng thuật toán Dijkstra có thể tự sửa sai khi gặp đồ thị có trọng số cạnh âm nếu bỏ mảng visited đi, nhầm lẫn hoàn toàn sang cơ chế hoạt động của Bellman-Ford.',
--     1,
--     '2026-10-21 09:05:00'
-- ),
-- -- Lỗi sai của Hà Khánh Vy (vyhk) trong Phiên 6 (Chưa giải quyết - Phiên đang dừng)
-- (
--     UNHEX('2A2A2A2A2A2A2A2A2A2A2A2A2A2A2A06'),
--     UNHEX('12345678901234567890123456789023'),
--     UNHEX('1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C06'),
--     'RAG_EMBEDDING',
--     'Sinh viên cho rằng set chunk_size càng lớn (ví dụ 4000 tokens) thì AI đọc hiểu càng tốt, bỏ qua giới hạn max_tokens của embedding model và sự loãng thông tin (noise).',
--     0,
--     '2026-10-21 15:25:00'
-- );

INSERT INTO `topics` (
    `id`,
    `name`,
    `summary`,
    `concepts_included`
) VALUES

-- TOPIC 01: Khóa chính, khóa ứng viên
(
    UNHEX('9405577243834C02810DDD3FC687FDCE'),
    'Khóa chính, khóa ứng viên và toàn vẹn thực thể',
    'Tổng hợp cách xác định siêu khóa, khóa ứng viên và chọn khóa chính trong mô hình quan hệ. Làm rõ yêu cầu khóa chính duy nhất, không được NULL; liên hệ vai trò của khóa ứng viên trong việc kiểm tra phụ thuộc hàm khi chuẩn hóa.',
    JSON_ARRAY(
        'KHOA_CHINH',
        'KHOA_UNG_VIEN',
        'RANG_BUOC_THUC_THE'
    )
),

-- TOPIC 02: SQL JOIN
(
    UNHEX('67E310AFFDD742619E12F2B058CC32CC'),
    'Phép kết nối SQL: INNER JOIN và LEFT JOIN',
    'Phân biệt kết nối trong và kết nối ngoài khi truy vấn nhiều bảng. Trường hợp thống kê số lượng bản ghi con, sử dụng LEFT JOIN kết hợp COUNT(cột_id_của_bảng_con) để giữ cả bản ghi cha không có bản ghi con.',
    JSON_ARRAY('SQL_JOIN')
),

-- TOPIC 03: Window Functions
(
    UNHEX('754F06C257FF41D79E886A439DB02188'),
    'Truy vấn xếp hạng với DENSE_RANK và CTE',
    'Sử dụng DENSE_RANK() với PARTITION BY và ORDER BY để xếp hạng trong từng nhóm, không bỏ qua thứ hạng khi trùng điểm. Kết hợp WITH (CTE) để lọc Top K sau khi tính thứ hạng.',
    JSON_ARRAY('WINDOW_FUNCTION_DENSE_RANK')
),

-- TOPIC 04: Chuẩn hóa cơ sở dữ liệu
(
    UNHEX('67EF3283EAA6445590F66DC57616C0C2'),
    'Chuẩn hóa cơ sở dữ liệu: 2NF, 3NF và BCNF',
    'Hệ thống hóa ba dạng chuẩn trên cơ sở phụ thuộc hàm: 2NF loại bỏ phụ thuộc bộ phận của thuộc tính không khóa vào khóa ứng viên; 3NF xem xét phụ thuộc bắc cầu và điều kiện thuộc tính khóa; BCNF yêu cầu vế trái của mọi phụ thuộc hàm không tầm thường là siêu khóa. So sánh tình huống đạt 3NF nhưng vi phạm BCNF.',
    JSON_ARRAY(
        'CHUAN_HOA_2NF',
        'CHUAN_HOA_3NF',
        'PHU_THUOC_BAC_CAU',
        'CHUAN_HOA_BCNF'
    )
),

-- TOPIC 05: Transaction
(
    UNHEX('CD3BA8DE7C0D49E095E958080F0932F8'),
    'Giao dịch và mức cô lập trong MySQL InnoDB',
    'Giới thiệu giao dịch ACID gắn với các hiện tượng đọc bẩn, đọc không lặp lại và đọc bóng ma. Trình bày mức REPEATABLE READ mặc định cùng cơ chế MVCC, Read View và Next-Key Lock được đề cập trong học liệu InnoDB.',
    JSON_ARRAY(
        'TRANSACTION_ACID',
        'ISOLATION_LEVELS'
    )
),

-- TOPIC 06: B+Tree
(
    UNHEX('B5AE3D3BBB5D439FB78366D26791563A'),
    'Chỉ mục B+Tree và tối ưu truy vấn khoảng',
    'Mô tả cấu trúc chỉ mục B+Tree trong InnoDB: hệ số phân nhánh lớn, nút trong định hướng tìm kiếm, dữ liệu hoặc khóa chính tại nút lá, liên kết giữa các nút lá. Giải thích hiệu quả đối với truy vấn khoảng và sắp xếp.',
    JSON_ARRAY('INDEX_BTREE')
),

-- TOPIC 07: Spring Boot DTO
(
    UNHEX('CC01B903390A48AAAE729FC2A2CA4529'),
    'Thiết kế API Spring Boot theo DTO Pattern',
    'Tổ chức phản hồi API bằng DTO và ApiResponse thay vì trả trực tiếp JPA Entity. Nhấn mạnh việc hạn chế lộ dữ liệu nhạy cảm, tránh vòng lặp tuần tự hóa JSON và tách biệt hợp đồng API khỏi mô hình lưu trữ.',
    JSON_ARRAY('DTO_PATTERN')
),

-- TOPIC 08: JPA N+1
(
    UNHEX('0323414532534AB19DB19635CAD04D13'),
    'Khắc phục N+1 Query trong Spring Data JPA',
    'Phân tích vấn đề N+1 Query và LazyInitializationException khi tắt Open Session in View. Đề cập cách sử dụng @Transactional(readOnly = true) ở tầng Service, @EntityGraph hoặc JOIN FETCH để tải quan hệ phù hợp.',
    JSON_ARRAY('JPA_N_PLUS_1')
),

-- TOPIC 09: JWT và RBAC
(
    UNHEX('A1DA99FE12704A048630C5FF426CDFC8'),
    'Xác thực JWT HttpOnly Cookie và RBAC hai tầng',
    'Kết hợp xác thực bằng Access Token và Refresh Token lưu trong HttpOnly Cookie với kiểm tra vai trò. Phân biệt quyền hệ thống ROLE_ADMIN/ROLE_USER và vai trò lớp OWNER/TEACHER/STUDENT gắn với class_members.',
    JSON_ARRAY('SPRING_SECURITY_JWT')
),

-- TOPIC 10: QuickSort
(
    UNHEX('DD2E3C8AE0474F47A1EB7899150A6544'),
    'QuickSort: chiến lược chia để trị và chọn pivot',
    'Phân tích độ phức tạp trung bình O(N log N), trường hợp xấu O(N²) khi chọn pivot không phù hợp trên dữ liệu có thứ tự. Giới thiệu chọn pivot ngẫu nhiên và Median-of-Three để giảm nguy cơ cây đệ quy lệch.',
    JSON_ARRAY('QUICKSORT')
),

-- TOPIC 11: Dijkstra
(
    UNHEX('00FE0EC9D84E4B2F82B34DD7DB2FD3C2'),
    'Dijkstra với Priority Queue',
    'Trình bày tìm đường đi ngắn nhất từ một đỉnh nguồn bằng Min-Heap, cách loại bỏ phần tử cũ trong hàng đợi ưu tiên với điều kiện d > dist[u], độ phức tạp được nêu trong học liệu và giới hạn khi có cạnh trọng số âm.',
    JSON_ARRAY('DIJKSTRA')
),

-- TOPIC 12: RAG
(
    UNHEX('B0B8B1D1949C40629BEEA501DA9B30BD'),
    'Chunking và truy xuất ngữ cảnh bằng Hybrid RAG',
    'Tổ chức tài liệu thành các chunk có gối đầu để giữ mạch ngữ cảnh giữa định nghĩa và ví dụ. Kết hợp tìm kiếm vector bằng ChromaDB với đồ thị tri thức Neo4j nhằm cung cấp ngữ cảnh nguồn cho mô hình LLM khi trả lời câu hỏi học tập.',
    JSON_ARRAY('RAG_EMBEDDING')
);


INSERT INTO `topic_chunks` (
    `topic_id`,
    `chunk_id`
) VALUES

-- Topic 01 -> Chunk 01, 03
(
    UNHEX('9405577243834C02810DDD3FC687FDCE'),
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C01')
),
(
    UNHEX('9405577243834C02810DDD3FC687FDCE'),
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C03')
),

-- Topic 02 -> Chunk 02
(
    UNHEX('67E310AFFDD742619E12F2B058CC32CC'),
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C02')
),

-- Topic 03 -> Chunk 02
(
    UNHEX('754F06C257FF41D79E886A439DB02188'),
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C02')
),

-- Topic 04 -> Chunk 03, 04, 05
(
    UNHEX('67EF3283EAA6445590F66DC57616C0C2'),
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C03')
),
(
    UNHEX('67EF3283EAA6445590F66DC57616C0C2'),
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C04')
),
(
    UNHEX('67EF3283EAA6445590F66DC57616C0C2'),
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C05')
),

-- Topic 05 -> Chunk 06
(
    UNHEX('CD3BA8DE7C0D49E095E958080F0932F8'),
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C06')
),

-- Topic 06 -> Chunk 07
(
    UNHEX('B5AE3D3BBB5D439FB78366D26791563A'),
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C07')
),

-- Topic 07 -> Chunk 08
(
    UNHEX('CC01B903390A48AAAE729FC2A2CA4529'),
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C08')
),

-- Topic 08 -> Chunk 08
(
    UNHEX('0323414532534AB19DB19635CAD04D13'),
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C08')
),

-- Topic 09 -> Chunk 09
(
    UNHEX('A1DA99FE12704A048630C5FF426CDFC8'),
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C09')
),

-- Topic 10 -> Chunk 10
(
    UNHEX('DD2E3C8AE0474F47A1EB7899150A6544'),
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C10')
),

-- Topic 11 -> Chunk 11
(
    UNHEX('00FE0EC9D84E4B2F82B34DD7DB2FD3C2'),
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C11')
),

-- Topic 12 -> Chunk 12
(
    UNHEX('B0B8B1D1949C40629BEEA501DA9B30BD'),
    UNHEX('8C8C8C8C8C8C8C8C8C8C8C8C8C8C8C12')
);

SET FOREIGN_KEY_CHECKS = 1;
