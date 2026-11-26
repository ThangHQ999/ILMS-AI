# Học liệu mẫu để kiểm tra parser và chunker

Đây là nội dung minh họa do dự án tạo để kiểm tra tiền xử lý, không phải học liệu đã được giảng viên duyệt.

## Khóa ứng viên

Một khóa ứng viên là một siêu khóa tối thiểu theo quan hệ bao hàm. Tối thiểu nghĩa là không thể bỏ bất kỳ thuộc tính nào mà tập còn lại vẫn là siêu khóa; không có nghĩa mọi khóa ứng viên đều có cùng số thuộc tính.

Điều kiện: việc xác định khóa phải xét các ràng buộc của lược đồ quan hệ, không chỉ dựa vào các hàng đang có trong một bảng mẫu.

Lưu ý ngắn: Không đồng nhất khóa ứng viên với khóa chính.

## Bảng minh họa

| Mã sinh viên | Mã môn | Điểm |
|---|---|---|
| SV01 | MH01 | 8 |
| SV01 | MH02 | 9 |

## Code cần giữ indentation

```python
def tong_doan(a, left, right):
    total = 0
    for index in range(left, right + 1):
        total += a[index]
    return total
```

## Bài tập chưa có lời giải

Cho R(A, B, C, D, E) và F = {A → BC, B → D, CD → E, E → A}.
Hãy tìm tất cả các khóa ứng viên. Tài liệu mẫu này không cung cấp lời giải.

## Unicode và công thức

Chuỗi kiểm tra: tiếng Việt, α, β, ∅, →, emoji 🎓.
Độ phức tạp của hàm cộng đoạn ở trên là O(right − left + 1).
