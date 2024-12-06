import json
from crypt import methods
from flask import request, jsonify
from app import  app
from app.dao import dao_student
from app.dao.dao_student import verify_student_phone_number


@app.route("/api/view_score/<int:student_id>", methods=['GET'])
def view_semester(studet_id):
    semester_id = request.args.get('semester_id')
    score = dao_student.view_score_student(studet_id ,semester_id)
    processed_cores = dao_student.preprocess_scores(score)
    return jsonify(processed_cores)
@app.route("/api/view_score/verify_number", methods=['POST'])
def verify_number():
    data = request.get_json()
    phone_number = data.get('phone_number')
    student_info = verify_student_phone_number(phone_number)
    if student_info:
        return  jsonify(student_info),200
    else:
        return  jsonify({'error':False,'message':'Không tìm thấy học sinh.'}) , 404