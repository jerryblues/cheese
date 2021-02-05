# coding=utf-8
from jira import JIRA

# pip3 install jira

account = input('>>>>>:').strip()    # 本地调试时注释掉
password = input('>>>>>:').strip()   # 本地调试时注释掉

jira_server = 'https://jiradc.ext.net.nokia.com'  # jira地址
jira_username = account   # 用户名，本地调试时，可用明文代替
jira_password = password  # 密码，本地调试时，可用明文代替

jira = JIRA(basic_auth=(jira_username, jira_password), options={'server': jira_server})

def searchIssues(jql, max_results=1000):
    ''' Search issues
    @param jql: JQL, str
    @param max_results: max results, int, default 100
    @return issues: result, list
    '''
    try:
        issues = jira.search_issues(jql, maxResults=max_results)
        return issues
    except Exception as e:
        print(e)


jql = '''
    project = FCA_5G_L2L3 AND issuetype in (epic) AND resolution = Unresolved AND status not in (Done, obsolete) AND cf[29790] in (5253, 5254, 5351) ORDER BY createdDate DESC
'''
issues = searchIssues(jql)
summary = []
team = []
start_FB = []
original_estimate = []
data = {}

for issue in issues:
    # summary.append(issue.fields.summary)
    team.append(issue.fields.customfield_29790)
    start_FB.append(issue.fields.customfield_38694)
    original_estimate.append(issue.fields.customfield_39191)

print(start_FB, original_estimate, team)

# for t in team:
#     if t == 5254:
#


# target output:
# team  FB
#       FB2101  FB2101 FB2103
# A     100     200    300
# B
# R
