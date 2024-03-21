from singleton import singleton
import json

@singleton
class Config:
    config_path = './conf/config.json'
    def __init__(self) -> None:
        with open(self.config_path,'r') as file:
            self.config_data = json.load(file)

    def get_tmp_dict(self)->str:
        return self.config_data['tmp_path']
    
    def set_login_user(self,user:str):
        self.config_data['user'] = user
        self.update_to_file()

    def set_login_pwd(self,pwd:str):
        # TODO add crypto
        self.config_data['pwd'] = pwd
        self.update_to_file()

    def set_auto_login(self,enable:bool):
        self.config_data['auto_login'] = enable
        self.update_to_file()

    def set_remember_pwd(self,enbale:bool):
        self.config_data['remember_pwd'] = enbale
        self.update_to_file()

    def get_login_user(self)->str:
        return self.config_data['user']

    def get_login_pwd(self)->str:
        return self.config_data['pwd']

    def get_auto_login(self)->bool:
        return self.config_data['auto_login']

    def get_remember_pwd(self)->bool:
        return self.config_data['remember_pwd']

    def update_to_file(self):
        with open(self.config_path,'w') as file:
            json.dump(self.config_data,file,indent=4)

