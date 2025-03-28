from certifi import contents
import requests
import logging
import json
from singleton import singleton

class AIPInfo:
    aip_id = ''
    jira_issue_key = ''
    car_id = ''
    cyberrt_version = ''
    datetime = ''
    remark = ''
    jira_link = ''
    dv_link = ''

@singleton
class NDPApi:
    base_url = 'http://ndp.data.neolix.cn'
    token = ''

    def __init__(self) -> None:
        pass

    def login(self,username:str,passwd:str)->bool:
        url = self.base_url+"/service/pro/ndp/user/login"
        params = {
            'username':username,
            'password':passwd
                  }
        res = requests.get(url,params=params)
        if res.status_code == 200:
            obj = json.loads(res.text)
            self.token = obj['data']['access_token']
            logging.debug("get token:{}".format(self.token))
            return True
        else:
            logging.error("login has err,code={}".format(res.status_code))
        return False     

    def search_api(self,aip:str,s_type=''):
        if not self.token:
            logging.warning("don't have token")
            return None

        url = self.base_url+'/service/pro/ndp/aicar/faultReport/page'
        params = {
            'pageIndex':1,
            'pageSize':10,
            'jiraIssueKey':aip,
            'access_token':self.token,
        }
        if s_type:
            params['type'] = s_type
        if s_type=='SC':
            params['subTypes'] = 'TBD'

        headers = {
            'Authorization':self.token
        }
        res = requests.get(url,params=params,headers=headers)
        if res.status_code ==200:
            obj = json.loads(res.text)
            print(obj)
            # total = obj["data"]["total"]
            # if total <=0:
            #     logging.error("no found aip:{}".format(aip))
            #     return None
            # elif total>1:
            #     logging.error("found multi aip:{}".format(aip))
            #     return None
                
            contents = obj["data"]["contents"]
            aip_info = contents[0]
            logging.info("aip:{},aip id:{}".format(aip,aip_info['id']))
            caip_info = AIPInfo()
            caip_info.aip_id = aip_info['id']
            caip_info.jira_issue_key = aip_info['jiraIssueKey']
            caip_info.car_id = aip_info['carId']
            caip_info.cyberrt_version = aip_info['carCyberRtVersion']
            caip_info.datetime = aip_info['dateTime']
            caip_info.remark = aip_info['remark']
            caip_info.jira_link = aip_info['jiraIssueLink']
            # caip_info.dv_link = 'http://ndp.data.neolix.cn/neodata/#/dvPlay?recordPath='+aip_info['dvObjName']+ \
            #     '&mapName='+aip_info['carMapVersion']+'&carId='+aip_info['carId']+'&version='+aip_info['carCyberRtVersion']
            return caip_info
        else:
            logging.error("search aip {},code={}".format(aip,res.status_code))
        return None

    # @return: list[{filesize,name,objName,updateTime}],list[record_download_url]
    def aip_info(self,aip_id:str):
        if not self.token:
            logging.warning("don't have token")
            return None,None
        url = self.base_url+"/service/pro/ndp/aicar/faultReport/task/file"
        params = {
            'id':aip_id,
            'access_token':self.token
        }
        headers = {
            'Authorization':self.token
        }
        res = requests.get(url,params=params,headers=headers)
        if res.status_code ==200:
            # logging.debug(res.text)
            obj = json.loads(res.text)
            if 'logFiles' in obj['data'] and 'record3dayLinks' in obj['data']: 
                return obj['data']['logFiles'],obj['data']['record3dayLinks']
            elif 'logFiles' in obj['data']:
                return obj['data']['logFiles'],[]
            elif 'record3dayLinks' in obj['data']:
                return [],obj['data']['record3dayLinks']

        else:
            logging.error("find aip info,aip_id:{},code={}".format(aip_id,res.status_code))
        return None,None

    def get_file_download_url(self,obj_name)->str:
        if not self.token:
            logging.warning("don't have token")
            return ''
        ret_url = ''
        url = self.base_url+"/service/pro/ndp/aicar/obs/signedUrl"
        params = {
            'objName':obj_name,
            'access_token':self.token
        }
        headers = {
            'Authorization':self.token
        }
        res = requests.get(url,params=params,headers=headers)
        if res.status_code ==200:
            logging.debug(res.text)
            obj = json.loads(res.text)
            ret_url = obj['data']
        else:
            logging.error("obj name:{},code={}".format(obj_name,res.status_code))
        return ret_url

    def download_url(self,url,local_path):
        if not url:
            logging.error('download url is null')
            return
        req = requests.get(url,stream=True)
        with open(local_path,'wb') as f:
            for chunk in req.iter_content(chunk_size=1024):
                f.write(chunk)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    ndp_api = NDPApi()
    ndp_api.login('maxinyuan','xxxxxxxx')
    aip_id,_,_ = ndp_api.search_api('AIP-23709')
    if aip_id:
        log_files,record = ndp_api.aip_info(aip_id)
        download_url = ndp_api.get_file_download_url(log_files[0]['objName'])
        ndp_api.download_url(download_url,log_files[0]['name'])
