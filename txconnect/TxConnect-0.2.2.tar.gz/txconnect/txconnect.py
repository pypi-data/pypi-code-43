import json
import copy
import requests
from bs4 import BeautifulSoup

BS4_PARSER = 'html5lib'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
}

BASE_URL = 'https://txconnpa.esc13.net/PACB'

login_data = {
    'ctl00$Contentplaceholder$lgnUserLogin$LoginButton': 'Log In',
    'ctl00$Contentplaceholder$hfMobileDevice': 'false',
}

switch_data = {
    '__ASYNCPOST': 'true'
}

open_grade_data = {
    '__ASYNCPOST': 'true'
}   

class TxConnect:

### PUBLIC METHODS ###

    def login(self, username, password):
        self.session = requests.Session()
        self.resp = self.session.get('{}/Login.aspx'.format(BASE_URL), headers = HEADERS)
        self.soup = BeautifulSoup(self.resp.content, BS4_PARSER)
        login_data['__VIEWSTATE'] = self.soup.find('input', attrs={'id': '__VIEWSTATE'})['value']
        login_data['__VIEWSTATEGENERATOR'] = self.soup.find('input', attrs={'id': '__VIEWSTATEGENERATOR'})['value']
        login_data['ctl00$Contentplaceholder$lgnUserLogin$UserName'] = username
        login_data['ctl00$Contentplaceholder$lgnUserLogin$Password'] = password
        self.resp = self.session.post('{}/Login.aspx?ReturnUrl=%2fPACB%2fParentAccess%2fGrades%2fGrades.aspx'.format(BASE_URL), data=login_data, headers=HEADERS)        
        self.soup = BeautifulSoup(self.resp.content, BS4_PARSER)
        return True if 'Grades' in self.resp.text else False

    def get_student_list(self):
        self.student_list = dict()
        names = self.soup.select('div[id$=ctiveStudent]')
        student_ids = self.soup.select('input[id$=StudentID]')
        for i in range(len(names)):
            student_id = student_ids[i]['id']
            self.student_list[student_ids[i]['value']] = dict(name=names[i].text.strip(), web_id = student_id[21:student_id.rfind('_')])
        return json.dumps(self.student_list)

    def get_classes(self, student_id):
        self.__switch_student(student_id)
        class_list = []
        self.resp = self.session.get('{}/ParentAccess/Grades/Grades.aspx'.format(BASE_URL), headers=HEADERS)
        self.soup = BeautifulSoup(self.resp.content, BS4_PARSER)

        periods = self.soup.select('span[id$=ucScheduleInfo_lblSimplePeriod]')
        classes = self.soup.select('span[id$=_ucScheduleInfo_lblCourse]')
        teachers = self.soup.select('span[style="white-space: nowrap"]')

        averages = self.soup.select('a[id$=lnbActiveCycleGrade]')

        for i in range(len(periods)):
            class_info = dict(period = periods[i].text.strip(), name = classes[i].text.strip(), teacher = teachers[i].text.strip().replace(u'\xa0', ' '), email = teachers[i].find('a')['href'][7:-21] if teachers[i].find('a') != None else None, average = averages[i].text.strip())
            self.__get_grades(class_info, i)
            class_list.append(class_info)
        
        return json.dumps(class_list)

### PRIVATE METHODS ###

    def __switch_student(self, student_id, semester=1):
        web_id = self.student_list[student_id]['web_id']

        switch_data['ctl00$MainContent$ctl02$ctl01$ucScheduleSelector$ddlSemester'] = semester
        switch_data['ctl00$Scriptmanager1'] = 'ctl00$UpdatePanel2|ctl00$rptStudents$ctl{}$lnbStudentName'.format(web_id)

        switch_data['__VIEWSTATE'] = self.soup.find('input', attrs={'id': '__VIEWSTATE'})['value']
        switch_data['__VIEWSTATEGENERATOR'] = self.soup.find('input', attrs={'id': '__VIEWSTATEGENERATOR'})['value']
        switch_data['__EVENTTARGET'] = 'ctl00$rptStudents$ctl{}$lnbStudentName'.format(web_id)
        for key in self.student_list:
            switch_data['ctl00$rptStudents$ctl{}$hdnStudentID'.format(self.student_list[key]['web_id'])] = key
        
        self.resp = self.session.post('{}/ParentAccess/Grades/Grades.aspx'.format(BASE_URL), data=switch_data, headers=HEADERS)
    
    def __get_grades(self, class_info, n, semester = 1):
        self.resp = self.session.get('{}/ParentAccess/Grades/Grades.aspx'.format(BASE_URL), headers=HEADERS)
        self.soup = BeautifulSoup(self.resp.content, BS4_PARSER)
        
        web_id = str(n).zfill(2)
        open_grade_data['ctl00$Scriptmanager1'] = 'ctl00$UpdatePanel1|ctl00$MainContent$ctl02$ctl01$rptSchedule$ctl{}$rptCycles$ctl00$lnbActiveCycleGrade'.format(web_id)
        open_grade_data['ctl00$rptStudents$ctl00$hdnStudentID'] = '061780'
        open_grade_data['ctl00$rptStudents$ctl01$hdnStudentID'] = '061698'
        open_grade_data['ctl00$MainContent$ctl02$ctl01$ucScheduleSelector$ddlSemester'] = 1
        open_grade_data['__EVENTTARGET'] = 'ctl00$MainContent$ctl02$ctl01$rptSchedule$ctl{}$rptCycles$ctl00$lnbActiveCycleGrade'.format(web_id)
        open_grade_data['__VIEWSTATE'] = self.soup.find('input', attrs={'id': '__VIEWSTATE'})['value']
        open_grade_data['__VIEWSTATEGENERATOR'] = self.soup.find('input', attrs={'id': '__VIEWSTATEGENERATOR'})['value']

        self.resp = self.session.post('{}/ParentAccess/Grades/Grades.aspx'.format(BASE_URL), data=open_grade_data, headers=HEADERS)
        self.soup = BeautifulSoup(self.resp.content, BS4_PARSER)

        rows = self.soup.select('table[summary="Assignment details"]')[0].find('tbody').find_all('tr')

        is_formative = True
        formative = dict()
        summative = dict()

        for row in rows:
            cols = row.find_all('td')

            if 'SUMMATIVE' in row.text.strip():
                is_formative = False
                continue

            if len(row.select('td[class="text assignment"]')) == 0:
                continue

            grades = formative if is_formative else summative

            name = cols[0].text
            name = name[0: -name.rfind('Assignment Note')].strip()
            grades[name] = dict(date = cols[1].text.strip(), grade = cols[2].text.strip())

        try:
            class_info['formative_average'] = self.soup.select('td[class="value"]')[0].text.strip()
            class_info['summative_average'] = self.soup.select('td[class="value"]')[1].text.strip()
        except:
            class_info['formative_average'] = None
            class_info['summative_average'] = None
        class_info['formative'] = formative
        class_info['summative'] = summative


    