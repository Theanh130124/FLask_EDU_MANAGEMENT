from datetime import datetime
from app import app , db
import cloudinary.uploader
from flask import flash
from app.models import  Semester , User , UserRole
from datetime import date



# Nếu tháng 1-5: Học kỳ vẫn thuộc năm học trước (ví dụ: 2023-2024, thì đây vẫn là năm 2023).
# Nếu tháng 6-12: Năm học mới đã bắt đầu (ví dụ: 2024-2025, thì đây là năm 2024).
def get_current_year():
    if datetime.now().month < 6:
        return datetime.now().year - 1
    return datetime.now().year

def get_current_semester():
    now = datetime.now()
    if now.month < 6:
        semester_name = "Học kỳ 2"
        year = now.year - 1
    else:
        semester_name = "Học kỳ 1"
        year = now.year
    return semester_name, year

def upload_to_cloudinary(file):
    try:
        upload_result = cloudinary.uploader.upload(file, folder="user_avatars/")
        return upload_result.get('secure_url')
    except Exception as e:
        flash(f"Lỗi tải lên Cloudinary: {e}")
        return None
def display_form_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Lỗi ở trường {field}: {error}", 'danger')  # Hiển thị lỗi lên giao diện

# def on_model_change_user(model, form, is_created):
#     if isinstance(model, User):
#         if model.user_role == UserRole.TEACHER:
#             teacher = Teacher(user_id=model.id)
#             db.session.add(teacher)
#         elif model.user_role == UserRole.ADMIN:
#             admin = Admin(user_id=model.id)
#             db.session.add(admin)
#         elif model.user_role == UserRole.STAFF:
#             staff = Staff(user_id=model.id)
#             db.session.add(staff)
#         db.session.commit()