from flask import Flask, render_template, Response, jsonify, request,send_file,stream_with_context
import requests
import json
import os
import time
from datetime import datetime
import time
import threading

import mysql.connector
from mysql.connector import Error

from flask_cors import CORS

connection = None

app = Flask(__name__)
CORS(app)
# global varible
status_pesent_detect = {"qrdata":0,"hight":0}
@app.route("/setting", methods=["POST"])
def set_value():
    data = request.get_json()  # Get the JSON data sent in the request
    # load json file -------------------------------------
    file_path = os.path.join(os.path.dirname(__file__), 'settingbuf.json')
    with open(file_path, 'r') as file:
        data_load = json.load(file)
    # add json file to databese --------------------------
    data_load[data['time_save']] = {
        "name": data['tube_name_setting_str'],
        "tube_hight": float(data['tube_hight_str']),
        "tube_diameter": float(data['tube_diameter_str']),
        "px":int(data['tube_px_str']),
        "mm":int(data['tube_mm_str'])
    }
    with open(file_path, 'w') as file:
        json.dump(data_load, file)
    #----------------------------------------------------
    # upload data to data base
    response = {
        "stsave": True,
    }

    # status_res = requests.get('http://210.246.215.145:5000/save_setting_from_database')

    return jsonify(response), 200

@app.route("/loadsetting", methods=["GET"])
def loadsetting():
    file_path = os.path.join(os.path.dirname(__file__), 'settingbuf.json')
    with open(file_path, 'r') as file:
        data_load = json.load(file)
    response = {
        "data": data_load,
    }
    return jsonify(response), 200

@app.route("/usesettingthis", methods=["POST"])
def usesettingthis():
    data_from_app = request.get_json()
    #load json
    file_path = os.path.join(os.path.dirname(__file__), 'settingbuf.json')
    with open(file_path, 'r') as file:
        data_load = json.load(file)
    buf_data_json = data_load[data_from_app['old_id']]
    #sort json
    del data_load[data_from_app['old_id']]
    data_load[data_from_app['new_id']] = buf_data_json
    #dump json
    with open(file_path, 'w') as file:
        json.dump(data_load, file)
    response = {
        "data": "data_load",
    }
    return jsonify(response), 200

@app.route("/deletesettingthis", methods=["POST"])
def deletesettingthis():
    data_from_app = request.get_json()
    #load json
    file_path = os.path.join(os.path.dirname(__file__), 'settingbuf.json')
    with open(file_path, 'r') as file:
        data_load = json.load(file)
    buf_data_json = data_load[data_from_app['old_id']]
    #sort json
    del data_load[data_from_app['old_id']]
    # data_load[data_from_app['new_id']] = buf_data_json
    #dump json
    with open(file_path, 'w') as file:
        json.dump(data_load, file)
    # -----------------------
    res = requests.get('http://127.0.0.1:5000/sync_setting_from_database')
    #-----------------------
    response = {
        "data": "data_load",
    }
    return jsonify(response), 200


@app.route("/status_chacking", methods=["GET"])
def status_chacking():
    global status_pesent_detect
    response = {
        "status_detect": status_pesent_detect,
    }
    return jsonify(response), 200


@app.route("/get_model_from_internet", methods=["GET"])
def get_model_from_internet():
    url = "http://210.246.215.145:1234/get_model_from_internet"
    response = requests.get(url)
    response = response.json()

    file_path = os.path.join(os.path.dirname(__file__), 'modellist/listmode.json')
    with open(file_path, 'w') as json_file:
        json.dump(response, json_file)

    # print(response)
    return jsonify(response), 200

# load use now model in mypc ---------------
version_model_usenow = ''
file_path = os.path.join(os.path.dirname(__file__), 'modellist/nowusemodel.json')
with open(file_path, 'r') as json_file:
    data_load_from_now_model = json.load(json_file)
    version_model_usenow = data_load_from_now_model['use_now_model']
# print(data_load_from_now_model)


def sum_static_history(start_date,end_date,mode):
    sum_his_lost = {}
    sum_his_true = {}
    souse_data = {}
    data_all = {}
    try:
        start_timestamp = int(start_date)
        end_timestamp = int(end_date)
        date1 = datetime.fromtimestamp(start_timestamp).date().strftime("%Y-%m-%d")
        date2 = datetime.fromtimestamp(end_timestamp).date().strftime("%Y-%m-%d")
        db = mysql.connector.connect(
                host="210.246.215.145",
                user="root",
                password="OKOEUdI1886*",
                database="plasma"
            )
        cursor = db.cursor()
        # query = """SELECT * FROM `graph`WHERE `time` BETWEEN %s AND %s;"""
        query = """SELECT * FROM `graph` WHERE `time` BETWEEN %s AND %s ORDER BY `time` ASC;"""
        cursor.execute(query, (date1, date2))
        results = cursor.fetchall()
        
        if(mode == "Day"):
            count = 0
            for data in results:
                sum_his_lost[f"{data[0]}"] = data[2]
                sum_his_true[f"{data[0]}"] = data[1]
                souse_data[count] = count
                count+=1
                # print(data[0])

        if(mode == "Week"):
            count = 0
            T_sum = 0
            F_sum = 0
            c_sou = 0
            for data in results:
                count += 1
                F_sum = F_sum + data[2]
                T_sum = T_sum + data[1]
                if count % 7 == 0 or results[-1][0] == data[0]:
                    sum_his_lost[f"{data[0]}"] = F_sum
                    sum_his_true[f"{data[0]}"] = T_sum
                    T_sum = 0
                    F_sum = 0
                    souse_data[c_sou] = c_sou
                    c_sou+=1

    
        if(mode == "Month"):
            m_now = results[0][0].month #0
            T_sum = 0
            F_sum = 0
            for data in results:
                if(data[0].month != m_now or results[-1][0] == data[0]):
                    m_now = data[0].month
                    sum_his_lost[f"{data[0]}"] = F_sum
                    sum_his_true[f"{data[0]}"] = T_sum
                    T_sum = 0
                    F_sum = 0
                else:
                    F_sum = F_sum + data[2]
                    T_sum = T_sum + data[1]
# #  'Day', 'Week', 'Month', 'Year'
        if(mode == "Year"):
            m_now = results[0][0].year #0
            T_sum = 0
            F_sum = 0
            for data in results:
                if(data[0].year != m_now or results[-1][0] == data[0]):
                    m_now = data[0].year
                    sum_his_lost[f"{data[0]}"] = F_sum
                    sum_his_true[f"{data[0]}"] = T_sum
                    T_sum = 0
                    F_sum = 0
                else:
                    F_sum = F_sum + data[2]
                    T_sum = T_sum + data[1]
        
        cursor.close()
        db.close()
    except (ValueError, TypeError, KeyError) as e:
        pass

    # print(mode)
    data_all["false_tube"] = sum_his_lost
    data_all["true_tube"] = sum_his_true
    data_all["souse"] = souse_data

    return data_all


@app.route("/get_history_for_graph", methods=["POST"])
def get_history_for_graph():
    data_from_app = request.get_json()
    
    # print(data_from_app['mode'])
    
    res_data = sum_static_history(data_from_app["start"],data_from_app['end'],data_from_app['mode'])
    # print(res_data)
    response = {
        "hisreturn": res_data,
    }
    
    # response = {
    #     "hisreturn": {"false_tube":{"1/2":50},"true_tube":{"1/2":13}},
    # }
    return jsonify(response), 200


@app.route("/sync_setting_from_database", methods=["GET"])
def sync_setting_from_database():
    file_path = os.path.join(os.path.dirname(__file__), 'settingbuf.json')
    with open(file_path, 'r') as file:
        data_load = json.load(file)
    data_for_save = {
        "data_sync":data_load
    }
    url = 'http://210.246.215.145:1234/sync_setting_from_database'
    response = requests.post(url, json=data_for_save)
    response = {
        "st_sync": True,
    }
    return jsonify(response), 200


@app.route("/save_setting_from_database", methods=["GET"])
def save_setting_from_database():
    url = 'http://210.246.215.145:1234/save_setting_from_database'
    response = requests.get(url)
    response = response.json()
    file_path = os.path.join(os.path.dirname(__file__), 'settingbuf.json')
    with open(file_path, 'w') as file:
        json.dump(response["data_sync"], file)
    response = {
        "st_sync": True,
    }

    # status_res = requests.get('http://210.246.215.145:5000/sync_setting_from_database')
    
    return jsonify(response), 200


@app.route("/get_log", methods=["GET"])
def get_log():
    global connection,json
    
    try:
        connection = mysql.connector.connect(
            host='210.246.215.145',
            database='plasma',
            user='root',
            password='OKOEUdI1886*',
            connection_timeout=3
        )
        # print("testStatus ",connection.is_connected())
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version", db_Info)
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            cursor.execute("SELECT * FROM log ORDER BY timestamp DESC LIMIT 5")
            rows = cursor.fetchall()
            # print("from log server : ",rows)
            return jsonify(rows),200

    except Error as e:
        return jsonify([["no internet","False","no internet",0,0,0,0.0,"\rno internet"]]), 200

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    #         print("MySQL connection is closed")


@app.route("/test_log_status_true", methods=["GET"])
def test_log_status_true():
    try:
        now_time = int(time.time())
        db = mysql.connector.connect(
            host="210.246.215.145",
            user="root",
            password="OKOEUdI1886*",
            database="plasma"
        )

        cursor = db.cursor()
        rr = {}
        rr[str(now_time)] = {"Tube": "True", "Datetime": now_time}
        for key, value in rr.items():
            timestamp_value = int(key)
            data = value["Tube"]
            datetime_value = value["Datetime"]
            cursor.execute("""
            INSERT INTO log (timestamp, data, datetime)
            VALUES (FROM_UNIXTIME(%s), %s, FROM_UNIXTIME(%s))
            """, (timestamp_value, data, datetime_value))
        db.commit()
        cursor.close()
        db.close()
        return jsonify(rr), 200
    
    except:
        data_list = []
        file_path = os.path.join(os.path.dirname(__file__), 'offline_log\\offline_log.json')
        with open(file_path, 'r') as file:
            data_load = json.load(file)

        dt_object = datetime.fromtimestamp(now_time)
        formatted_date = dt_object.strftime('%a, %d %b %Y %H:%M:%S GMT')
        data_load.insert(0,[f"{formatted_date}","True",f"{formatted_date}"])

        with open(file_path, 'w') as file:
            json.dump(data_load, file)

        return jsonify([f"{formatted_date}","True",f"{formatted_date}"]),200


@app.route("/test_log_status_false", methods=["GET"])
def test_log_status_false():
    try:
        now_time = int(time.time())
        db = mysql.connector.connect(
            host="210.246.215.145",
            user="root",
            password="OKOEUdI1886*",
            database="plasma"
        )
        cursor = db.cursor()
        rr = {}
        rr[str(now_time)] = {"Tube": "False", "Datetime": now_time}
        for key, value in rr.items():
            timestamp_value = int(key)
            data = value["Tube"]
            datetime_value = value["Datetime"]
            cursor.execute("""
            INSERT INTO log (timestamp, data, datetime)
            VALUES (FROM_UNIXTIME(%s), %s, FROM_UNIXTIME(%s))
            """, (timestamp_value, data, datetime_value))
        db.commit()
        cursor.close()
        db.close()
        return jsonify(rr), 200
    except:
        data_list = []
        file_path = os.path.join(os.path.dirname(__file__), 'offline_log\\offline_log.json')
        with open(file_path, 'r') as file:
            data_load = json.load(file)

        dt_object = datetime.fromtimestamp(now_time)
        formatted_date = dt_object.strftime('%a, %d %b %Y %H:%M:%S GMT')
        data_load.insert(0,[f"{formatted_date}","False",f"{formatted_date}"])

        with open(file_path, 'w') as file:
            json.dump(data_load, file)

        return jsonify([f"{formatted_date}","False",f"{formatted_date}"]),200


def server_run2():
    app.run(host='0.0.0.0',port=5000,debug=False)

# zone run ai pre -------------------------------
app_4 = Flask(__name__)
CORS(app_4)
keep_data_setting = [True,True,True]

def send_login(u,p):
    try:
        db = mysql.connector.connect(
                host="210.246.215.145",
                user="root",
                password="OKOEUdI1886*",
                database="plasma"
            )
        cursor = db.cursor()
        print(cursor)
        query = """SELECT * FROM account WHERE user = %s AND password = %s;"""
        cursor.execute(query, (u, p))
        results = cursor.fetchall()
        print(results)
        cursor.close()
        db.close()
        if(results[0][0] == u and results[0][1] == p):
            return jsonify({"st":True})
        else:
            return jsonify({"st":False})
    except:
        return jsonify({"st":False})

@app_4.route("/login", methods=["POST"])
def get_data_from():
    data_from_app = request.get_json()
    print(data_from_app)
    # status_res = requests.get('http://210.246.215.145:5000/sync_setting_from_database')
    return(send_login(data_from_app['t'],data_from_app['a'])),200

@app_4.route("/upload_All_to_pool", methods=["GET"])
def upload_All_to_pool():
    folder_path = os.path.join(os.path.dirname(__file__), 'image_pr\\good')
    url = 'http://210.246.215.145:1234/save_dataset_to_pool'
    json_data = {
        "pool": "good",
    }
    for image_name in os.listdir(folder_path):
        image_path = os.path.join(folder_path, image_name)
        if image_name.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            with open(image_path, 'rb') as img_file:
                files = {'file': img_file}
                data = {'json_data': json.dumps(json_data)}
                response = requests.post(url, files=files, data=data)
                # if response.status_code == 200:
                #     os.remove(image_path)

    folder_path = os.path.join(os.path.dirname(__file__), 'image_pr\\bad')
    url = 'http://210.246.215.145:1234/save_dataset_to_pool'
    json_data = {
        "pool": "bad",
    }
    for image_name in os.listdir(folder_path):
        image_path = os.path.join(folder_path, image_name)
        if image_name.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            with open(image_path, 'rb') as img_file:
                files = {'file': img_file}
                data = {'json_data': json.dumps(json_data)}
                response = requests.post(url, files=files, data=data)
    return jsonify({"ok":"ok"}), 200

def run_ai_pre():
    app_4.run(host='0.0.0.0',port=3500, debug=False)

if __name__ == '__main__':
    c3 = threading.Thread(target=server_run2)
    c3.daemon = True
    c3.start()
    c6 = threading.Thread(target=run_ai_pre)
    c6.daemon = True
    c6.start()
    while True:
        time.sleep(1)