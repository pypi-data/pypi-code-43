import requests

class apigitlab:
    adr=''
    token_i=''

    def __init__(self,adr2,token):
        self.adr=adr2
        self.token_i=token
        
    def get_projects(self):
        r = requests.get(self.adr, params=self.token_i)
        t=tuple(r.json())
        array={}
        for i in t:
          array[i['name']]={'id':i['id'],'merge_requests':i['_links']['merge_requests'],'repo_branches':i['_links']['repo_branches'],'labels':i['_links']['labels'],'issues':i['_links']['issues']}
        return array
    
    def get_project_id(self,project):
        r = requests.get(self.adr, params=self.token_i)
        t=tuple(r.json())
        array={}
        for i in t:
          array[i['name']]={'id':i['id'],'merge_requests':i['_links']['merge_requests'],'repo_branches':i['_links']['repo_branches'],'labels':i['_links']['labels'],'issues':i['_links']['issues']}
        array=array[project]
        return array.get('id')
    
    def merge_requests_project(self,id):  
        r = requests.get(self.adr + str(id) +'/merge_requests?state=opened', params=self.token_i)
        return r.json()
    
    def get_pipelines(self,id,iid):
        t={}
        self.token_i['per_page']=20
        r = requests.get(self.adr + str(id) +'/merge_requests/'+ str(iid) +'/pipelines', params=self.token_i)
        t=r.json()
        while True:
            self.token_i['page']=r.headers.get('X-Next-Page')
            r = requests.get(self.adr + str(id) +'/merge_requests/'+ str(iid) +'/pipelines', params=self.token_i)
            for i in r.json():
                t.append(i)
            if r.headers.get('X-Page')==r.headers.get('X-Total-Pages'):
               break
        return t
    
    def cancel_pipelines(self,id,pid):
        r = requests.post(self.adr + str(id) +'/pipelines/'+ str(pid) +'/cancel', params=self.token_i)
        print(r.url)
        return r.json()
    
    def get_pipelines_project(self,id):
        t={}
        self.token_i['per_page']=20
        r = requests.get(self.adr + str(id) +'/pipelines', params=self.token_i)
        t=r.json()
        while True:
            self.token_i['page']=r.headers.get('X-Next-Page')
            r = requests.get(self.adr + str(id) +'/pipelines', params=self.token_i)
            for i in r.json():
                t.append(i)
            if r.headers.get('X-Page')==r.headers.get('X-Total-Pages'):
               break
        return t
    
    def get_commit(self,id):
      r = requests.get(self.adr + str(id) +'/repository/commits', params=self.token_i)
      print(tuple(r.json()))
      print("_______")
    
    def get_branch(self,id,branch):
       self.token_i['per_page']=100
       r = requests.get(self.adr+ str(id) +'/repository/branches/' , params=self.token_i)
       ret=r.json()
       for i in ret:
           
           if branch==i.get('name'):
             temp=i.get('commit')
             return temp.get('id')  
       message={'message':'404 Branch Not Found'}
       return message  
      
    def get_reg_con(self,id):
      self.token_i['per_page']=20
      self.token_i['tags']=1
      r = requests.get(self.adr+ str(id) +'/registry/repositories', params=self.token_i)
      t=r.json()
      while True:
            self.token_i['page']=r.headers.get('X-Next-Page')
            r = requests.get(self.adr+ str(id) +'/registry/repositories', params=self.token_i)
            for i in r.json():
                t.append(i)
            if r.headers.get('X-Page')==r.headers.get('X-Total-Pages'):
               break

      return t
    
    def get_registry_repositories(self,id):
        #GET /projects/:id/registry/repositories
        r=requests.get(self.adr + str(id) +'/registry/repositories', params=self.token_i)
        return r.json()
    
    # Delete repository tags in bulk
    # Delete repository tags in bulk based on given criteria.
    # DELETE /projects/:id/registry/repositories/:repository_id/tags
    #   id	integer/string	yes	The ID or URL-encoded path of the project owned by the authenticated user.
    #   repository_id	integer	yes	The ID of registry repository.
    #   name_regex	string	yes	The regex of the name to delete. To delete all tags specify .*.
    #   keep_n	    integer no	The amount of latest tags of given name to keep.
    #   older_than	string	no	Tags to delete that are older than the given time, written in human readable form 1h, 1d, 1month.
    #   https://docs.gitlab.com/ee/api/container_registry.html
    
    def delete_registry_repositories(self,id,r_id,**data):
        for v,k in data.items():
            self.token_i[v]=k
        print(self.token_i)
        r=requests.delete(self.adr + str(id) +'/registry/repositories/'+ str(r_id) + "/tags" , params=self.token_i)
        return r.json()
    
    def get_info_registry_tag(self,id,r_id):
        self.token_i['page']=1
        r=requests.get(self.adr + str(id) +'/registry/repositories/'+ str(r_id) + "/tags" , params=self.token_i)
        return r.json()
    def delete_registry_repositories_tag(self,id,r_id,tag):
        r=requests.delete(self.adr + str(id) +'/registry/repositories/'+ str(r_id) + "/tags/" + tag , params=self.token_i)
        
    
    
    
     
        

#         payload = {'some':'data'}
#         headers = {'content-type': 'application/json'}
# url = "https://www.toggl.com/api/v6/" + data_description + ".json"
# response = requests.delete(url, data=json.dumps(payload), headers=headers,auth=HTTPBasicAuth(toggl_token, 'api_token'))
     




    # Within a group
    # Get a list of registry repositories in a group.
    # GET /groups/:id/registry/repositories

    # Delete registry repository
    # Delete a repository in registry.
    # This operation is executed asynchronously and might take some time to get executed.
    # DELETE /projects/:id/registry/repositories/:repository_id

    # Within a project
    # Get a list of tags for given registry repository.
    # GET /projects/:id/registry/repositories/:repository_id/tags
 
    # Get details of a repository tag
    # Get details of a registry repository tag.
    # GET /projects/:id/registry/repositories/:repository_id/tags/:tag_name

    # Delete a repository tag
    # Delete a registry repository tag.
    # DELETE /projects/:id/registry/repositories/:repository_id/tags/:tag_name

   
   





    
