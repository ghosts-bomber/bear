from jira import JIRA
from config import Config
import time
from io import BytesIO, BufferedReader
class JiraApi:
    def __init__(self) -> None:
        self.config = Config()
        self.jira = JIRA('https://jira.neolix.net/', auth=(self.config.get_jira_user(), self.config.get_jira_pwd()))
    def get_issue(self,aip:str):
        return self.jira.issue(aip)
    def get_issue_info(self,aip:str):
        issue = self.get_issue(aip)

        # print (issue)  #JiraID
        # print (issue.id)  #internalID
        # print (issue.fields.project)  #所属项目
        #  
        # print (issue.fields.issuetype)  #问题类型
        # print (issue.fields.status)  #问题状态
        # # print (issue.fields.subtasks)  #关联的sub-task
        # # print (issue.fields.issuelinks)  #关联的blockissues
        #  
        # print (issue.fields.creator)  #创建人
        # print (issue.fields.reporter)  #报告人
        # print (issue.fields.assignee)  #指派人
        # print (issue.fields.customfield_10508)  # 版本号
        # print (issue.fields.customfield_11306)  # 其它版本号
        # print (issue.fields.customfield_10510)  # 问题时间
        # print (issue.fields.customfield_10512)  # 车号
        # print (issue.fields.created)  #创建日期
        # print (issue.fields.updated)  #修改日期
        # print (issue.fields.lastViewed)  #最后查看时间
        # print (issue.fields.summary)  #主题
        # print (issue.fields.description)  #描述
        # print (issue.fields.attachment)  #附件信息
        # print (issue.fields.comment.comments[0].body)  #评论
        #  
        # print (issue.fields.issuetype.avatarId)  #类型ID
        # print (issue.fields.priority)  #优先级

    def add_issue_comment(self,aip:str,comment:str):
        issue = self.get_issue(aip)
        self.jira.add_comment(issue,comment)

    def add_issue_attachment_use_file(self,aip:str,attachment_path:str,attachment_name:str):
        issue = self.get_issue(aip)
        with open(attachment_path,'rb') as f:
            self.jira.add_attachment(issue=issue,attachment=f,filename=attachment_name)

    def add_issue_attachment_use_bytes(self,aip:str,data:bytes,attachment_name:str):
        issue = self.get_issue(aip)
        reader = BytesIO(data)        
        self.jira.add_attachment(issue=issue,attachment=reader,filename=attachment_name)

    def add_issue_attachment_use_data(self,aip:str,data:str,attachment_name:str):
        issue = self.get_issue(aip)
        self.jira.add_attachment(issue=issue,attachment=data,filename=attachment_name)

    def get_image_attachment_comment(self,attachment_name:str)->str:
        return f'!{attachment_name}|thumbnail!'

        # with open('./cyber_shm.vpd-Page-3.png','rb') as f:
        #     self.jira.add_attachment(issue=issue,attachment=f,filename='11122.png')
        # for item in issue.fields.attachment:
        #     print(item)
        # self.jira.add_comment(issue, "Comment text:\n !11122.png|thumbnail!")

if __name__ == "__main__":
    jira_api = JiraApi()
