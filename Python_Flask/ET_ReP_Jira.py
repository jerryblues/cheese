# coding=utf-8
"""
@file: ET_ReP_Jira.py.py
@time: 2023/4/26 11:01
@author: h4zhang
"""
from flask import Flask, render_template, request
import requests
import json
from jira import JIRA


def get_token():
    # 定义请求的URL
    url = 'https://rep-portal.wroclaw.nsn-rdnet.net/jwt/obtain/'

    # 定义POST请求的数据（字典形式）
    data = {
        "username": "h4zhang",
        "password": "Holmes-09"
    }

    # 发送POST请求
    response = requests.post(url, json=data)

    # 打印响应结果
    # print(response.text)

    # 找到第一个双引号的索引位置
    first_quote_index = response.text.find('"')

    # 找到第二个双引号的索引位置，从第一个双引号索引位置开始搜索
    second_quote_index = response.text.find('"', first_quote_index + 1)

    # 再次使用 find() 方法找到第三个双引号的索引位置，从第二个双引号索引位置开始搜索
    third_quote_index = response.text.find('"', second_quote_index + 1)

    # 再次使用 find() 方法找到第四个双引号的索引位置，从第三个双引号索引位置开始搜索
    fourth_quote_index = response.text.find('"', third_quote_index + 1)

    # 利用切片获取第三个和第四个双引号之间的内容
    token = response.text[third_quote_index + 1:fourth_quote_index]

    # 输出 'token'
    print("token:", token)
    return token


def validate_token(t):
    # 定义请求的URL
    url = 'https://rep-portal.wroclaw.nsn-rdnet.net/jwt/verify/ '

    # 定义POST请求的数据（字典形式）
    data = {
        "pk": 1606902367,
        "token": t}

    # 发送POST请求
    res = requests.post(url, json=data)
    # If the token is invalid, the server will respond with status 400 and JSON object that contains further details of the error.
    print("response:", res)
    return res


def query_rep(feature):
    query_link = url + feature
    # print(query_link)
    response = requests.get(query_link, headers=headers)
    # print("status:", response.status_code)
    # print("headers:", response.headers)
    # print("text:", response.text)
    return json.loads(response.text)


def query_jira(link):
    end_fb_string = 0
    label_string = 0
    issues = jira.search_issues(link, maxResults=1000)
    for issue in issues:
        end_fb_string = issue.fields.customfield_38693
        label_string = issue.fields.labels
    # print("end_fb:", end_fb_string)
    return end_fb_string, label_string


# token = get_token()
# validate_token(token)

url = "https://rep-portal.ext.net.nokia.com/api/qc-beta/instances/report/?fields=id,m_path,test_set__name,backlog_id,name,url,status,status_color,fault_report_id_link,comment,sw_build,res_tester,test_entity,function_area,ca,organization,release,feature,requirement,last_testrun__timestamp&limit=200&m_path__pos_neg=s\RAN_L3_SW_CN_1&ordering=name&test_set__name__pos_neg_empty_str="
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6Img0emhhbmciLCJpYXQiOjE2ODI0MDY1NzksImV4cCI6MTY4MjY2NTc3OSwianRpIjoiNzk4Y2EwZDgtMTA2YS00YjE2LWExNDQtYmUyMGFlMzlmMmE0IiwidXNlcl9pZCI6MTM0OTgsInVzZXJfcHJvZmlsZV9pZCI6WzEzNDk4XSwib3JpZ19pYXQiOjE2ODI0MDY1NzksImlzX2FkbWluIjpmYWxzZX0.Qm7v87_ZDOP1JzJYpvOIBt4zjc2aV7SVdUqS84OU0NQ"
# query_url = url + feature

# headers format is "JWT token" in type of string
headers = {
    "Authorization": "JWT " + token
}

# Jira configuration
jira_server = 'https://jiradc.ext.net.nokia.com'  # jira地址
jira_username = 'h4zhang'  # 用户名，本地调试时，可用明文代替
jira_password = 'Holmes-09'  # 密码，本地调试时，可用明文代替
jira = JIRA(basic_auth=(jira_username, jira_password), options={'server': jira_server})


def get_result(feature):
    i = 0
    backlog_id = []
    case_name = []
    qc_status = []
    end_fb = []
    label = []
    # query backlog ID and case name
    query_rep_result = query_rep(feature)
    '''
    data format
    print(data)
    print(data['results'][0]['backlog_id'])  # list
    print(data['results'][0]['backlog_id'][0])  # dic
    print(data['results'][0]['backlog_id'][0]['id'])  # value
    print(type(data), type(data['results']), type(data['results'][1]))
    print(len(data['results']))
    '''
    while i < len(query_rep_result['results']):
        backlog_id.append(query_rep_result['results'][i]['backlog_id'][0]['id'])
        case_name.append(query_rep_result['results'][i]['name'][:19])
        qc_status.append(query_rep_result['results'][i]['status'])
        # query end FB and label
        query_jira_result = query_jira("key = " + backlog_id[i])
        end_fb.append(query_jira_result[0])
        tc_tag = [s for s in query_jira_result[1] if s.startswith('TC')]
        label.append(tc_tag)
        i += 1
        # print(backlog_id[k], end_fb[k], case_name[k], label[k], qc_status[k])
    return backlog_id, end_fb, case_name, label, qc_status


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("case_status_form.html")


@app.route("/feature_case_status", methods=["POST"])
def process_input():
    feature = request.form.get("feature_id")
    data = get_result(feature)
    return render_template('case_status_table.html',
                           len=len(data[0]),
                           list1=data[0], list2=data[1], list3=data[2], list4=data[3], list5=data[4])


if __name__ == "__main__":
    app.run()
