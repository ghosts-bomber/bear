from certifi import contents
import requests
import logging
import json
from singleton import singleton

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
        none = (None,None,None)
        if not self.token:
            logging.warning("don't have token")
            return none

        url = self.base_url+'/service/pro/ndp/aicar/faultReport/page'
        params = {
            'pageIndex':1,
            'pageSize':10,
            'jiraIssueKey':aip,
            'access_token':self.token
        }
        if s_type:
            params['type'] = s_type

        headers = {
            'Authorization':self.token
        }
        res = requests.get(url,params=params,headers=headers)
        if res.status_code ==200:
            obj = json.loads(res.text)
            total = obj["data"]["total"]
            if total <=0:
                logging.error("no found aip:{}".format(aip))
                return none
            elif total>1:
                logging.error("found multi aip:{}".format(aip))
                return none 
                
            contents = obj["data"]["contents"]
            aip_info = contents[0]
            logging.info("aip:{},aip id:{}".format(aip,aip_info['id']))
            return aip_info['id'],aip_info['dateTime'],aip_info['remark'] 
        else:
            logging.error("search aip {},code={}".format(aip,res.status_code))
        return none

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
            return obj['data']['logFiles'],obj['data']['record3dayLinks']
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
