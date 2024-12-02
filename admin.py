from flask_login import logout_user, current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin import expose, BaseView, Admin
from app.models import UserRole, Regulation, Subject, Teaching, Class, Profile, User, Student, Notification
from app import app, db, login
from flask import redirect
from app.controllers import hash_password


# De authen
class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN  # Phải có dòng sau này để người dùng STAFF không thể truy cập admin


class LoginUserView(BaseView):
    @expose('/')
    def index(self):
        return redirect('/login')
    def is_accessible(self):
        return not current_user.is_authenticated

class SubjectAdminView(AuthenticatedView):
    column_list = ['id', 'name', 'grade', 'number_of_15p', 'number_of_45p', 'teachings']
    column_labels = {
        'id': 'Mã',
        'name': 'Tên môn',
        'grade': 'Khối ',
        'number_of_15p': 'Số bài kiểm tra 15P',
        'number_of_45p': 'Số bài kiểm tra 45P',
        'teachings': 'Áp dụng cho'
    }
    column_filters = [
        'name',
        'grade',
        'number_of_15p',
        'number_of_45p',
    ]
    can_view_details = True

    # Format hiển thị cột 'teachings'
    def format_teachings(view, context, model, name):
        if model.teachings:
            return ', '.join(
                [f'Lớp: {t.class_id}, Học kỳ: {t.semester_id}, Giáo viên: {t.teacher_id}' for t in model.teachings])
        return 'Chưa áp dụng'

    column_formatters = {
        'teachings': format_teachings
    }


class RegulationsAdminView(AuthenticatedView):
    # Display class and student -> toString bên models -> displayname
    column_list = ['type', 'name', 'min_value', 'max_value', 'classes', 'students']

    column_labels = {
        'type': 'Loại quy định',
        'name': 'Tên quy định',
        'min_value': 'Giá trị tối thiểu',
        'max_value': 'Giá trị tối đa',
        'classes': 'Danh sách lớp',
        'students': 'Danh sách học sinh',
    }

    # Có thể xem chi tiết class và student
    column_details_list = ['type', 'name', 'min_value', 'max_value', 'classes', 'students']
    can_view_details = True


class UserView(AuthenticatedView):
    column_list = ['username', 'password', 'user_role', 'active', 'profile']
    # Phải loại bỏ học sinh khỏi profile ở đây
    column_labels = {
        'username': 'Tên đăng nhập',
        'password': 'Mật khẩu',
        'user_role': 'Vai trò',
        'active': 'Trạng thái',
        'profile': 'Họ tên người dùng'
    }
    column_filters = [
        'username',
        'user_role',
        'active',
    ]
    can_view_details = True

    # Lọc profile không liên quan đến học sinh
    def get_query(self):
        return self.session.query(self.model).filter(self.model.profile_id.notin_(
            self.session.query(Student.profile_id).distinct()
        ))

    # Hook sau
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.password = hash_password(form.password.data)
        elif form.password.data:
            model.password = hash_password(form.password.data)
        return super().on_model_change(form, model, is_created)


class ProfileView(AuthenticatedView):
    column_list = ['name', 'email', 'birthday', 'gender', 'address', 'phone']
    column_labels = {
        'name': 'Họ tên',
        'email': 'Email',
        'birthday': 'Ngày sinh',
        'gender': 'Giới tính',
        'address': 'Địa chỉ',
        'phone': 'Số điện thoại'
    }
    column_filters = [
        'name',
        'email',
        'address',
        'phone',
    ]
    can_view_details = True


class ClassCreateView(AuthenticatedView):
    column_list = ['name' ,'grade','amount','year','teacher_id','regulation_id']
    column_labels = {
        'name': 'Tên lớp',
        'grade': 'Khối',
        'amount': 'Sỉ số',
        'year': 'Năm học',
        'teacher_id': 'Giáo viên chủ nhiệm',
        'regulation_id': 'Quy định'
    }
    can_edit = False
    can_view_details = True
class NotificationView(AuthenticatedView):
    column_list = ['subject','content','created_at']
    column_labels =  {
        'subject':'Tiêu đề thông báo',
        'content':'Nội dung',
        'create_date':'Thời gian tạo'
    }
    can_view_details = True
admin = Admin(app, name='Quản lý học sinh ', template_mode='bootstrap4')

admin.add_view(RegulationsAdminView(Regulation, db.session, name="Chỉnh sửa quy định"))
admin.add_view(ClassCreateView(Class,db.session,name="Tạo lớp học"))
admin.add_view(SubjectAdminView(Subject, db.session, name="Quản lý môn học"))  # Thêm
admin.add_view(UserView(User, db.session, name='Người dùng'))
admin.add_view(ProfileView(Profile, db.session, name="Hồ sơ"))
admin.add_view(NotificationView(Notification , db.session,name="Quản lý thông báo"))
admin.add_view(LogoutView(name='Đăng xuất'))
admin.add_view(LoginUserView(name='Về trang đăng nhập người dùng'))

# Fix bug đăng xuất trả về login.html
