
from flask import Flask, render_template, request,session,redirect,send_file
from flask.json import jsonify
import json
import sqlite3

db=sqlite3.connect("doctor_clients.db")
db=db.execute('''CREATE TABLE IF NOT EXISTS doctor_table
                    (Name TEXT NOT NULL,
                    Education TEXT NOT NULL,
                    Specialization TEXT NOT NULL,

                    Email TEXT NOT NULL,
                    Password TEXT NOT NULL,
                    Mobile_number INT NOT NULL,
                    Locality TEXT NOT NULL
                    )''')



db=db.execute('''CREATE TABLE IF NOT EXISTS patients
                    (First_Name TEXT NOT NULL,
                    Last_Name TEXT NOT NULL,
                    

                    Email TEXT NOT NULL,
                    Password TEXT NOT NULL,
                    Mobile_number INT UNIQUE NOT NULL
                    )''')


db=db.execute('''CREATE TABLE IF NOT EXISTS doctor_appointments
                    (Date INT NOT NULL,
                    Time INT NOT NULL,
                    Patient_mob_num INT NOT NULL,
                    Patient_Name TEXT NOT NULL,
                    Doctor_mob_num INT NOT NULL,
                    status INT DEFAULT 0
                    )''')


db=db.execute('''CREATE TABLE IF NOT EXISTS doctor_reports
                    (Patient_mob_num INT NOT NULL,
                    Doctor_mob_num INT NOT NULL,
                    Filename TEXT NOT NULL
                    )''')


db.close
app= Flask(__name__)
app.secret_key="secure"
@app.route("/")
def welcome():
    return render_template("client.html")

@app.route("/doctor/",methods =["get"])
def doctor():
    return render_template("doctor.html")



@app.route("/doctor_loginApi/", methods =["post"])
def doctor_loginApi(): 
    data= json.loads(request.data)
    # print(data)
    email_id =data["email"]
    password = data["passwrd"]
    db=sqlite3.connect("doctor_clients.db")
    # col1 = db.execute(f'''SELECT * FROM doctor_table WHERE Email = "{email_id}" AND Password ="{password}";''').fetchall()
    col = db.execute(f'''SELECT * FROM doctor_table WHERE Email = "{email_id}" AND Password ="{password}";''').fetchall()
    
    pswd_col =db.execute(f'''SELECT * FROM doctor_table WHERE Email = "{email_id}" AND Password!="{password}";''').fetchall()
    
    if len(col)>0:
        print(col[0][5])
        session["doctor"]=col[0][5]
        return jsonify(dict(msg ="Done"))
    
    elif len(pswd_col)>0:
        return jsonify(dict(msg ="password mistake"))
    else:
        return jsonify(dict(msg ="wertyu"))
        
    
 

@app.route("/doctor_register/",methods=["get"])
def doctor_register():
    return render_template("doctor_register.html")

@app.route("/doctor_registerApi/", methods=["post"])
def doctor_registerApi():
    # We will get the data in json string, json.loads converts the string into dictionary
    data = json.loads(request.data)
    print(data)
    name= data["name"]
    education=data["education"]
    specialization=data["specialization"]
    email_id =data["email_id"]
    password = data["pswd"]
    mob_numb=data["mobile_number"]
    locality=data["locality"]
    

    db = sqlite3.connect("doctor_clients.db")
    col = db.execute(f'''SELECT * FROM doctor_table WHERE Email = '{email_id}';''').fetchall()
    if len(col)==0:
        col=db.execute(f'''INSERT INTO doctor_table (Name,Education,Specialization,Email, Password,Mobile_number,Locality)
                        VALUES ('{name}','{education}','{specialization}','{email_id}', '{password}','{mob_numb}','{locality}');''')
        db.commit();
        return jsonify(dict(msg ="Done"))
    else:
        return jsonify( dict(msg= "werty"))

@app.route("/client/",methods =["get"])
def client():
    return render_template("client.html")




@app.route("/client_loginApi/", methods =["post"])
def client_loginApi(): 
    data= json.loads(request.data)
    print(data)
    number =data["pat_number"]
    password = data["passwrd"]
    session["phone"]=number
    db=sqlite3.connect("doctor_clients.db")
    col = db.execute(f'''SELECT * FROM patients WHERE Mobile_number = "{number}" AND Password="{password}";''').fetchall()
    
    pswd_col =db.execute(f'''SELECT * FROM patients WHERE Mobile_number = "{number}" AND Password!="{password}";''').fetchall()
    
    
    if len(col)>0:
        return jsonify(dict(msg ="Done"))
    elif len(pswd_col)>0:
        return jsonify(dict(msg ="password mistake"))
    else:
        return jsonify(dict(msg ="wewer"))



@app.route("/client_register/")
def client_register():
    return render_template("client_register.html")

@app.route("/client_registerApi/", methods=["post"])
def client_registerApi():
    # We will get the data in json string, json.loads converts the string into dictionary
    data = json.loads(request.data)
    # print(data)
    fname= data["fname"]
    lname= data["lname"]
    
    email_id =data["email"]
    password = data["password"]
    mob_numb=data["mobile_number"]
    

    db = sqlite3.connect("doctor_clients.db")
    col = db.execute(f'''SELECT * FROM patients WHERE Mobile_number = '{mob_numb}';''').fetchall()
    if len(col)==0:
        col=db.execute(f'''INSERT INTO patients (First_Name,Last_Name,Email, Password,Mobile_number)
                        VALUES ('{fname}','{lname}','{email_id}', '{password}','{mob_numb}');''')
        db.commit();
        
    
        return jsonify(dict(msg= "Done"))
    else:
        return jsonify(dict(msg= "ertyu"))

@app.route("/localities/",methods=["get"])
def localities():
    db = sqlite3.connect("doctor_clients.db")
    data = db.execute('''SELECT * FROM doctor_table''').fetchall() 
    print("Data : ",data)   
    return render_template("doctor_cards.html",data=data)

@app.route("/doctorList/<location>")
def doctor_list(location):
    db = sqlite3.connect("doctor_clients.db")
    data = db.execute(f'''SELECT Name,Mobile_number,Locality,Specialization FROM doctor_table WHERE Locality = '{location}';''').fetchall()
    # print(data)
    return render_template("doctor_cards.html",data=data)

@app.route("/fix_appointment/<doctor_number>/")
def fix_appointment(doctor_number):
   
    return render_template("fix_appointment.html",dnumber=doctor_number)


@app.route("/appointment_confirm/<doctor_number>/confirm/")
def appointment_confirm(doctor_number):
    if "phone" not in session:
        return redirect("/")
    date=request.args["date"]
    time=request.args["time"]
    # Getting doctor name
    db = sqlite3.connect("doctor_clients.db")
    doc_data=db.execute(f'''SELECT Name FROM doctor_table WHERE Mobile_number={doctor_number} ''').fetchone()
    doctor_name=doc_data[0]
    db.close()
    
    # getting patient name
    db = sqlite3.connect("doctor_clients.db")
    pat_data=db.execute(f'''SELECT First_Name FROM patients WHERE Mobile_number={session["phone"]} ''').fetchone()
    patient_name=pat_data[0]
    db.close()
    
    db = sqlite3.connect("doctor_clients.db")
    data=db.execute(f'''SELECT * FROM doctor_appointments WHERE Patient_mob_num='{session["phone"]}' and Date='{date}' ''').fetchall()
    if len(data)==0:
        db.execute(f'''INSERT INTO doctor_appointments (Date,Time,Patient_mob_num,Patient_Name, Doctor_mob_num)
                        VALUES ('{date}','{time}','{session["phone"]}', '{patient_name}','{doctor_number}');''')
        db.commit()
        db.close()    
    else:
        return render_template("appointment_already_booked.html",patient=patient_name,date=date,time=time,doctor=doctor_name)
    
    return render_template("booked_appointment.html",patient=patient_name,date=date,time=time,doctor=doctor_name)

@app.route("/doctor_schedule/")
def doctor_schedule():
    if "doctor" not in session:
        return redirect("/doctor/")
    
    db = sqlite3.connect("doctor_clients.db")
    completed=db.execute(f'''SELECT * FROM doctor_appointments WHERE Doctor_mob_num='{session["doctor"]}' and status= 1 ; ''').fetchall()
    incompleted =db.execute(f'''SELECT * FROM doctor_appointments WHERE Doctor_mob_num='{session["doctor"]}' and status= 0; ''').fetchall()
    db.close()
    # print("1completed", completed)
    # print("1incomplete", incompleted)
    return render_template("doctor_schedule.html",completed_data=completed,incomplete_data=incompleted)
    
@app.route("/updateDatabase/<phone>/<status>/<date>/",methods=["get","post"])
def updateDatabase (phone,status,date):
    if "doctor" not in session:
        return redirect("/doctor/")
    print(phone)
    print(status)
    db = sqlite3.connect("doctor_clients.db")
    db.execute(f'''UPDATE doctor_appointments
                    SET status = '{status}'
                    WHERE Patient_mob_num='{phone}'
                    and Doctor_mob_num='{session["doctor"]}' 
                    and Date='{date}';
                    ''')
    
    db.commit();
    completed=db.execute(f'''SELECT * FROM doctor_appointments
                         WHERE Doctor_mob_num='{session["doctor"]}' 
                         and status= 1 ''').fetchall()
    incompleted =db.execute(f'''SELECT * FROM doctor_appointments WHERE Doctor_mob_num='{session["doctor"]}' and status= 0; ''').fetchall()
    db.close()
    # print("completed", completed)
    # print("incomplete", incompleted)
    return render_template("doctor_schedule.html",completed_data=completed,incomplete_data=incompleted)
   

@app.route("/doctor_upload_file/<patient_numb>/<date>" ,methods=["get","post"])
def doctor_upload_file(patient_numb,date):
    
    if "doctor" not in session:
        return redirect("/doctor/")
   
    db = sqlite3.connect("doctor_clients.db")
    pat_details=db.execute(f'''SELECT First_Name,Last_Name,Email
                        FROM patients 
                        WHERE Mobile_number={patient_numb} 
                       ''').fetchone()
    print(pat_details)
    db.close()
    
    first_name=pat_details[0]
    last_name=pat_details[1]
    mail=pat_details[2]
    
    if request.method=="POST":
        file = request.files["filename"]
        filename = f"{patient_numb}"+file.filename
        file.save(f"user_files/{filename}")
        db = sqlite3.connect("doctor_clients.db")
        xyz=db.execute(f'''SELECT Filename FROM doctor_reports
                        WHERE Doctor_mob_num='{session["doctor"]}' 
                        and Patient_mob_num={patient_numb} 
                        and Date='{date}' and Filename='{filename}'; ''').fetchall()
        if len(xyz)==0:
            db.execute(f'''INSERT INTO doctor_reports 
                    (Patient_mob_num, Doctor_mob_num,Filename,Date)
                    VALUES ('{patient_numb}','{session["doctor"]}','{filename}', '{date}');''')
            db.commit()
            db.close()
        
    db = sqlite3.connect("doctor_clients.db")
    report_data=db.execute(f'''SELECT Filename FROM doctor_reports 
                            WHERE Doctor_mob_num='{session["doctor"]}' and Patient_mob_num={patient_numb}; ''').fetchall()
    print("report",report_data)
    
    return render_template("doctor_upload_file.html",first_name=first_name,last_name=last_name,mail=mail,pat_numb=patient_numb,report_data=report_data)
    
@app.route("/my_reports/")
def  client_reports():
    if "phone" not in session:
        return redirect ("/")
    db = sqlite3.connect("doctor_clients.db") 
    client_reports =  db.execute(f'''SELECT Filename,Doctor_mob_num,Date
                                 FROM doctor_reports 
                            WHERE Patient_mob_num={session["phone"]};''').fetchall()
    l=[]
    for i in client_reports:
        a=[]
        report=i[0]
        doc_num=i[1]
        date=i[2]
        a.append(report)
        a.append(doc_num)
        
        doc_details=db.execute(f'''SELECT Name,Specialization
                                 FROM doctor_table
                            WHERE Mobile_number={doc_num};''').fetchall()
        
        a.append(doc_details[0][0])
        a.append(doc_details[0][1])
        a.append(date)
        l.append(a)
        # print(a)   
    # print(l)
    db.close()
    return render_template("my_reports.html", l=l)

@app.route("/client_report_download/<file_name>/")
def client_download_file(file_name):
    if "phone" not in session:
        return redirect("/")
    
    db = sqlite3.connect("doctor_clients.db") 
    client_file_verify =  db.execute(f'''SELECT Filename,Patient_mob_num
                                FROM doctor_reports 
                            WHERE Patient_mob_num={session["phone"]} 
                            and Filename='{file_name}' ;''').fetchall()
    if len(client_file_verify)!=0:
        return send_file("user_files/"+file_name)
    return "File not found"

@app.route("/doctor_report_download/<file_name>/")
def doctor_download_file(file_name):
    if "doctor" not in session:
        return redirect("/doctor/")
    return send_file("user_files/"+file_name)
    
@app.route("/client_logout/")
def client_logout():
    if "phone" not in session:
        return redirect("/")
    session.pop("phone")
    return redirect("/") 

@app.route("/remedies/")
def remedies():
    return render_template("remedies.html")
app.run(debug=True)