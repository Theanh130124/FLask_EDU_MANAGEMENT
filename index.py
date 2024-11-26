
from app.admin import *
from app import dao, login , app
from flask import render_template, redirect, request, flash, url_for , jsonify
from flask_login import current_user, login_required, logout_user, login_user

from app.dao import display_profile_data, update_user_info
from app.models import UserRole #Phải ghi là app.models để tránh lỗi profile
from form import AdmisionStudent , LoginForm , Info_Account
from decorators import role_only

from dao import create_student


#Index là home
#Làm cái nào trên cũng truyền info vào




# Tải người dùng lên

@login.user_loader
def user_load(user_id):
    return dao.load_user(user_id)
# import pdb
# pdb.set_trace()
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.user_role == UserRole.ADMIN:
            return redirect("/admin")
        return redirect("/home")
    return redirect('/login')

#Nếu truyền url_for sẽ vào index -> truyêền redirect thì vào router
@app.route('/home')
@login_required #Có cái này để gom user vào -> home
@role_only([UserRole.STAFF , UserRole.TEACHER])
def home():
    profile = dao.get_info_by_id(current_user.id)
    return render_template('index.html',  profile=profile)  # Trang home (index.html)


@app.route('/login', methods=['GET', 'POST'])
def login():
    mse = ""
    form = LoginForm()
    if request.method == "POST" and form.SubmitFieldLogin():
        username = form.username.data
        password = form.password.data
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)
            return redirect(url_for('index'))
        mse = "Tài khoản hoặc mật khẩu không đúng"
    return render_template('login.html', form=form, mse=mse)

@app.route('/logout', methods=['get'])
def logout_my_user():
    logout_user()
    return redirect('/login')


# import pdb
# pdb.set_trace()

#FIX ROLE_ONLY -> VÀ CÁI PROFILE PHẢI TRUYỀN VÀO LẠI




@app.route('/student/register', methods=['GET', 'POST'])
@login_required
@role_only([UserRole.STAFF])
def register():
    form_student = AdmisionStudent()
    profile = dao.get_info_by_id(current_user.id)

    if request.method == "POST" and form_student.submit():
        try:
            s = dao.create_student(form_student)
        except Exception as e:
            print(e)
            # min = regulation.get_regulation_by_name("Tiếp nhận học sinh").min
            # if (datetime.now().year - form_student.birth_date.data.year) < min:
            #     return render_template("register_student.html", form_student=form_student,mse="Tuổi không phù hợp")

            # send_mail(subject="Thông báo nhập học ", student_name=s.profile.name, recipients=[s.profile.email])
            flash("Đã xảy ra lỗi khi tạo học sinh", "error")  # Thêm thông báo lỗi
            return render_template("register_student.html", form_student=form_student, profile=profile)
        if s:
            flash("Tạo học sinh thành công!", "success")  # Thông báo thành công
            return redirect("/index")
    return render_template("register_student.html", form_student=form_student, profile=profile)

@app.route('/acc_info', methods=['GET', 'POST'])
@login_required
@role_only([UserRole.STAFF, UserRole.TEACHER])
def info_acc():
    form_account = Info_Account()
    profile = dao.get_info_by_id(current_user.id)
    user = current_user

    if form_account.validate_on_submit():
        display_profile_data(profile, form_account)
        # Cập nhật thông tin người dùng
        update_user_info(profile, form_account)

        # Nếu là yêu cầu AJAX, trả về dữ liệu dưới dạng JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'status': 'success',
                'avatar_url': user.avatar_url
            })

        flash('Thông tin của bạn đã được cập nhật!', 'success')
        return redirect('/acc_info')
    display_profile_data(profile, form_account)

    return render_template('acc_info.html', form_account=form_account, profile=profile , current_user=current_user)
if __name__ == '__main__':
    app.run(debug=True) #Lên pythonanywhere nhớ để Falsse