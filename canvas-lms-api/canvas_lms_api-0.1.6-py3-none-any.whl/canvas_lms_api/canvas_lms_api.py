################################################################################
# grader.py - Originally coded by: Carmine T. Guida
# Updated by Tyson Bailey Renamed canvas_lms_api
################################################################################

import os
import sys
import requests
import csv
import urllib
import time

################################################################################
class Canvas:
    def __init__(self, base, token, course=None):
        self.base = base
        self.course = course
        self.token = token

    def GetCourseUsers(self, include_email=False):
        params = {}

        if (include_email):
            params["include[]"] = "email"

        self.canvasCourseUsers = self.CanvasAPIGet("/api/v1/courses/" + self.course + "/users", params)
        
        return self.canvasCourseUsers
################################################################################

    def CanvasAPIGet(self, url, extra_params={}):

        pageNum = 1

        headers = {"Authorization": "Bearer " + self.token}

        current = url
        if (current.startswith(self.base) == False):
            current = self.base + url
        responseList = []

        while True:
            params = {"page":str(pageNum), "per_page":"100"}
            params.update(extra_params)
            response = requests.get(current, headers=headers, params=params)
            if (response.status_code != requests.codes.ok):
                if (response.status_code == 401):
                    if (url.endswith("group_categories")):
                        return []
                print("ERROR HTTP STATUS CODE: " + str(response.status_code))
                print("URL: " + url)
                quit()
            else:
                result = response.json()

                # Quiz submissions are a list inside of a dict
                if ("quizzes" in url and "submissions" in url):
                    if ("quiz_submissions" in result):
                        result = result["quiz_submissions"]

                if (isinstance(result, dict)):
                    return result
                responseList.extend(result)

                linkCurrent = response.links["current"]
                linkLast = response.links["last"]

                if (linkCurrent["url"] == linkLast["url"]):
                    return responseList
                pageNum += 1


    def CanvasAPIPut(self, url, params):

        headers = {"Authorization": "Bearer " + self.token}

        response = requests.put(self.base + url, headers=headers, data=params)

        if (response.status_code != requests.codes.ok):
            print("ERROR HTTP STATUS CODE: " + str(response.status_code))
        else:
            #print (response.text)
            return response.json()

    def CanvasAPIPost(self, url, params):

        headers = {"Authorization": "Bearer " + self.token}

        response = requests.post(self.base + url, headers=headers, data=params)

        if (response.status_code != requests.codes.ok):
            print("ERROR HTTP STATUS CODE: " + str(response.status_code))
        else:
            #print (response.text)
            return response.json()

################################################################################

    def GetProfile(self):
        self.canvasProfile = self.CanvasAPIGet("/api/v1/users/self/profile")
        return self.canvasProfile

    def GetUserProfile(user_id):
        return self.CanvasAPIGet("/api/v1/users/" + user_id + "/profile")

    def GetCourses(self):
        self.canvasCourses = self.CanvasAPIGet("/api/v1/courses")
        return self.canvasCourses

    def GetCourseEnrollments(self, students_only=False):
        params = {}

        if (students_only):
            params["type[]"] = "StudentEnrollment"


        self.canvasCourseEnrollments = self.CanvasAPIGet("/api/v1/courses/" + self.course + "/enrollments", params)
        return self.canvasCourseEnrollments

    def GetCourseGroupCategories(self):
        self.courseGroupCategories = self.CanvasAPIGet("/api/v1/courses/" + self.course + "/group_categories")
        return self.courseGroupCategories

    def GetCourseGroups(self):
        self.courseGroups = self.CanvasAPIGet("/api/v1/courses/" + self.course + "/groups")
        return self.courseGroups

    def GetCourseGroupUsers(self):
        if (self.courseGroup == "all"):
            self.courseGroupUsers = self.canvasCourseUsers
            return
        self.courseGroupUsers = self.CanvasAPIGet("/api/v1/groups/" + self.courseGroup + "/users")
        return self.courseGroupUsers

    def GetCourseAssignments(self):
        self.canvasCourseAssignments = self.CanvasAPIGet("/api/v1/courses/" + self.course + "/assignments")
        return self.canvasCourseAssignments

    def GetCourseQuizes(self):
        canvasCourseQuizes = self.CanvasAPIGet("/api/v1/courses/" + course + "/quizzes")

    def GetCourseQuizSubmissions(self):
        canvasCourseQuizSubmissions = self.CanvasAPIGet("/api/v1/courses/" + course + "/quizzes/" + quiz + "/submissions")


    def GetCourseAssignmentSubmissions(self):
        courseAssignmentSubmissions = self.CanvasAPIGet("/api/v1/courses/" + course + "/assignments/" + assignment + "/submissions")

    def SubmitGrade(self, course_id, assignment_id, user_id, score, comment):
        params = {
            "include[visibility]":"true",
            "submission[posted_grade]":score,
            "comment[text_comment]":comment,
            "comment[group_comment]":"true"
        }

        self.CanvasAPIPut("/api/v1/courses/" + course_id + "/assignments/" + assignment_id + "/submissions/" + user_id, params)

    def GetCourseModules(self):
        canvasCourseModules = self.CanvasAPIGet("/api/v1/courses/" + course + "/modules")

    def ModuleCreateItemSubHeader(self, course_id, module_id, position, indent, title):
        params = {
            "module_item[title]":title,
            "module_item[type]":"SubHeader",
            "module_item[position]":position,
            "module_item[indent]":indent
        }

        self.CanvasAPIPost("/api/v1/courses/" + course_id + "/modules/" + module_id + "/items", params)


    def ModuleCreateItemExternalURL(self, course_id, module_id, position, indent, title, external_url):
        params = {
            "module_item[title]":title,
            "module_item[type]":"ExternalUrl",
            "module_item[position]":position,
            "module_item[indent]":indent,
            "module_item[external_url]":external_url,
            "module_item[new_tab]":"true"
        }

        self.CanvasAPIPost("/api/v1/courses/" + course_id + "/modules/" + module_id + "/items", params)

    def GetName(self, entry):
        if ("name" in entry):
            return entry["name"]
        return ""

    def GetAssignments(self):
        params = {}
        self.CourseAssignments = self.CanvasAPIGet("/api/v1/courses/" + self.course + "/assignments", params)
        return self.CourseAssignments

    def CreateAssignment(self, assignment_details):
        params = {
            "assignment[name]" : assignment_details["name"],
            "assignment[allowed_extensions][]" : assignment_details["allowed_extensions"],
            "assignment[points_possible]" : assignment_details["points_possible"],
            "assignment[due_at]" : assignment_details["due_at"],
            "assignment[lock_at]" : assignment_details["lock_at"],
            "assignment[unlock_at]" : assignment_details["unlock_at"],
            "assignment[description]" : assignment_details["description"],
            "assignment[published]" : assignment_details["published"],
            "assignment[submission_types][]" : "online_upload",
            "assignment[allowed_attempts]" : -1,
        }

        self.CanvasAPIPost("/api/v1/courses/" + self.course + "/assignments", params)
        


    ################################################################################

    def FindSubmissionByUser(self, user):
        user_id = user["id"]
        for entry in self.courseAssignmentSubmissions:
            if (entry["user_id"] == user_id):
                return entry
        return None

    def FindUser(self, user_id):
        for entry in self.canvasCourseUsers:
            if (int(entry["id"]) == int(user_id)):
                return entry
        return None

    def FindQuiz(self, quiz_id):
        for entry in self.canvasCourseQuizes:
            if (int(entry["id"]) == int(quiz_id)):
                return entry
        return None

    def GetEmails(self):
        '''
        Returns a dictionary containing emails as keys and Names as values, 
        this may be worthwhile changing but works for now
        '''
        if self.course != None:
            emails = {}
            if not hasattr(self, 'canvasCourseUsers'):
                self.GetCourseUsers()
            for i in self.canvasCourseUsers:
                #print (i)
                emails[i["email"]] = i["name"]
            return emails
        return None

################################################################################
def PromptCourse():
    global canvasCourses
    global course
    print("Which Course?")
    for entry in canvasCourses:
        print(str(entry["id"]) + " " + GetName(entry))

    while len(course) <= 0:
        course = str(input(":")).strip()

def PromptAssignment():
    global canvasCourseAssignments
    global assignment
    print("Which Assignment?")
    for entry in canvasCourseAssignments:
        print(str(entry["id"]) + " " + GetName(entry))

    while len(assignment) <= 0:
        assignment = str(input(":")).strip()

def PromptQuiz():
    global canvasCourseQuizes
    global quiz
    print("Which Quiz?")
    for entry in canvasCourseQuizes:
        print(str(entry["id"]) + " " + entry["title"])

    while len(quiz) <= 0:
        quiz = str(input(":")).strip()

def PromptGroup():
    global courseGroups
    global courseGroup

    if (courseGroups is None):
        print ("Course does not have groups. Using all students.")
        courseGroup = "all"
        return

    if (len(courseGroups) <= 0):
        print ("Course does not have groups. Using all students.")
        courseGroup = "all"
        return

    print("Which Group?")
    for entry in courseGroups:
        print(str(entry["id"]) + " " + GetName(entry))

    while len(courseGroup) <= 0:
        courseGroup = str(input(":")).strip()

def PromptModule():
    global canvasModules
    global module
    print("Which Module?")
    for entry in canvasCourseModules:
        print(str(entry["id"]) + " " + GetName(entry))

    while len(module) <= 0:
        module = str(input(":")).strip()

################################################################################

def GetAttachmentsLink(attachments):
    if (attachments == None):
        return ""
    link = ""
    for attachment in attachments:
        if (link != ""):
            link += "\n"
        link += attachment["url"]
    return link

def GetCourseAndAssignment(excludeSubmissions = False):
    GetCourses()
    PromptCourse()

    GetCourseUsers()

    GetCourseGroupCategories()
    GetCourseGroups()

    GetCourseAssignments()
    PromptAssignment()

    if not excludeSubmissions:
        GetCourseAssignmentSubmissions()

def GetCourseAndQuiz():
    GetCourses()
    PromptCourse()

    GetCourseUsers()

    GetCourseGroupCategories()
    GetCourseGroups()

    GetCourseQuizes()
    PromptQuiz()


    def CommandMentor(self):

        GetCourses()
        PromptCourse()

        GetCourseUsers()

        GetCourseGroupCategories()
        GetCourseGroups()

        PromptGroup()
        GetCourseGroupUsers()

        mentorName = self.canvasProfile["name"]

        for user in courseGroupUsers:
            print(mentorName + " - " + user["name"] + " - Mentor Discussion thread")

        print("Done!")

    def CommandExportEmail(filename):
        global canvasCourseUsers
        global course

        GetCourses()
        PromptCourse()

        GetCourseUsers(True)

        print("Exporting: " + filename)
        headerList = ["user_id", "name", "email", "email_alias"];

        with open(filename, "w")  as csvfile:
            writer = csv.writer(csvfile, dialect="excel")
            writer.writerow(headerList)
            for user in canvasCourseUsers:
                login_id = ""
                if ("login_id" in user):
                    login_id = user["login_id"]
                    if (login_id is None):
                        login_id = ""
                    else:
                        login_id = login_id + "@gatech.edu"

                row = [user["id"], user["sortable_name"], login_id, user["email"]]
                writer.writerow(row)

        print("Done!")


    def GetExtension(filename):
        pos = filename.rfind(".")
        if (pos < 0):
            return ""
        return filename[pos:].lower().strip()

    def DownloadSubmissionByUser(foldername, user):
        link = ""

        submission = FindSubmissionByUser(user)
        if (submission != None):
            if ("attachments" in submission):
                attachments = submission["attachments"]
                if (attachments is None):
                    return

                attachmentCount = 0
                for attachment in attachments:
                    link = attachment["url"]
                    if (link == ""):
                        return

                    ext = GetExtension(attachment["filename"])
                    filename = user["sortable_name"]
                    filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                    if (attachmentCount > 0):
                        filename = filename + "_" + str(attachmentCount)

                    filename = foldername + filename + ext

                    print("Downloading: " + link + " [to] " + filename)

                    DownloadURLToFile(link, filename)

                    attachmentCount = attachmentCount + 1


    def CommandDownload(foldername, otherfile):
        global canvasCourseUsers
        global course
        global assignment

        GetCourseAndAssignment()

        if (foldername.endswith("/") == False):
            foldername = foldername + "/"

        if (os.path.exists(foldername) == False):
            print("Creating folder: " + foldername)
            os.makedirs(foldername)

        print ("Downloading to: " + foldername)

        if (otherfile == ""):
            PromptGroup()
            GetCourseGroupUsers()
            for user in courseGroupUsers:
                DownloadSubmissionByUser(foldername, user)
        else:
            if (os.path.exists(otherfile) == False):
                print("ERROR: " + otherfile + " does not exist.")
                return

            lines = []
            with open(otherfile) as f:
                lines = f.readlines()

            for line in lines:
                user_id = line.strip()
                if (len(user_id) <= 0):
                    continue
                user = FindUser(user_id)
                DownloadSubmissionByUser(foldername, user)

        print("Done!")

    def CommandModuleImport(foldername):
        global course
        global module
        global canvasCourseModules

        GetCourses()
        PromptCourse()

        GetCourseModules()
        PromptModule()

        if (foldername.endswith("/") == False):
            foldername = foldername + "/"

        directories = os.listdir(foldername)
        directories.sort()
        position = 1
        for dir in directories:
            if (dir == ".DS_Store"):
                continue
            indent = 0
            print("Creating SubHeader: " + dir)
            ModuleCreateItemSubHeader(course, module, position, indent, dir)
            position += 1
            files = os.listdir(foldername + dir)
            files.sort()
            for file in files:
                if (file.endswith(".srt") == True):
                    file = file[:-4]
                indent = 1
                print("Creating ExternalURL: " + file)
                ModuleCreateItemExternalURL(course, module, position, indent, file, "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
                position += 1


        print("Done!")




    def CommandExport(filename):
        global canvasCourseUsers
        global course
        global assignment

        GetCourseAndAssignment()

        print ("Exporting: " + filename)
        headerList =  ["course_id", "assignment_id", "user_id", "name", "link", "score", "comment"];

        with open(filename, "w")  as csvfile:

            writer = csv.writer(csvfile, dialect="excel")
            writer.writerow(headerList)
            for user in canvasCourseUsers:
                link = ""
                score = ""
                comment = ""

                submission = FindSubmissionByUser(user)
                if (submission != None):
                    if ("score" in submission):
                        if (submission["score"] != None):
                            score = submission["score"]
                    if ("attachments" in submission):
                        link = GetAttachmentsLink(submission["attachments"])

                row = [course, assignment, user["id"], user["sortable_name"], link, score, comment]
                writer.writerow(row)

        print("Done!")

    def ExtractAnswers(events):
        answers = {}
        eventlist = events["quiz_submission_events"]

        for event in eventlist:
            event_type = event["event_type"]
            if (event_type != "question_answered"):
                continue
            event_data = event["event_data"]
            for subevent in event_data:
                quiz_question_id = str(subevent["quiz_question_id"])
                answer = subevent["answer"]
                if (answer == None):
                    answer = ""
                else:
                    answer = str(answer)

            answers[quiz_question_id] = answer

        return answers


    def CommandExportQuiz(filename):
        global canvasCourseQuizes
        global course
        global quiz

        GetCourseAndQuiz()
        GetCourseQuizSubmissions()

        submissionList = canvasCourseQuizSubmissions
        print ("submissionList: " + str(len(submissionList)) + " entries.")

        questionCount = 0
        quizData = FindQuiz(quiz)

        if (quizData != None):
            questionCount = quizData["question_count"]

        print ("Exporting: " + filename + " (" + str(questionCount) + " questions in quiz)")

        #params = {
        #    "quiz_report[report_type]":"student_analysis" #
        #}

        #print ("Telling canvas to generate the report.")
        #report = CanvasAPIPost("/api/v1/courses/" + str(course) + "/quizzes/" + str(quiz)+ "/reports", params)
        #reportURL = report["url"]

        #print ("Sleeping for 10 second to give it time to do that.")
        #time.sleep(10)



        headerList =  ["course_id", "quiz_id", "user_id", "name", "score"];

        for i in range(0, questionCount):
            headerList.append("Q" + str(i + 1) + "Score")

        for i in range(0, questionCount):
            headerList.append("Q" + str(i + 1) + "Answer")

        with open(filename, "w")  as csvfile:
            writer = csv.writer(csvfile, dialect="excel")
            writer.writerow(headerList)

            for submission in submissionList:
                id = submission["id"]
                user_id = submission["user_id"]
                score = submission["score"]

                name = ""
                user = FindUser(user_id)
                if (user != None):
                    name = user["sortable_name"]

                correctList = []
                for i in range(0, questionCount):
                    correctList.append(0)

                events = self.CanvasAPIGet("/api/v1/courses/" + str(course) + "/quizzes/" + str(quiz) + "/submissions/" + str(id) + "/events")
                answerdict = ExtractAnswers(events)

                submissionData = self.CanvasAPIGet("/api/v1/quiz_submissions/" + str(id)+ "/questions")

                answerList = []
                for i in range(0, questionCount):
                    answerList.append("")

                submissionQuestions = submissionData["quiz_submission_questions"]
                for entry in submissionQuestions:
                    if ("position" not in entry):
                        continue

                    position = (entry["position"] - 1)

                    if ("correct" in entry):
                        correct = entry["correct"]
                        if (correct == True):
                            correctList[position] = 1

                    entry_id = str(entry["id"])
                    answer = ""
                    if (entry_id in answerdict):
                        answer = answerdict[entry_id]

                    #Multiple choice answers are id numbers NOT A, B, C, D so we need to match them up
                    if (answer != "" and ("answers" in entry)):
                        answers = entry["answers"]

                        for a in range(0, len(answers)):
                            ans = answers[a]
                            if (str(ans["id"]) == answer):
                                answer = chr(65 + a)
                                break

                    answerList[position] = answer

                row = [course, quiz, user_id, name, score]
                for i in range(0, questionCount):
                    row.append(correctList[i])

                for i in range(0, questionCount):
                    row.append(answerList[i])

                writer.writerow(row)

        print("Done!")

    def CommandGetRubric(filename):
        global canvasCourseUsers
        global course
        global assignment

        GetCourseAndAssignment(True)

        global course
        global assignment
        courseAssignnment = self.CanvasAPIGet("/api/v1/courses/" + course + "/assignments/" + assignment)
        rubric = courseAssignnment["rubric"]


        print ("Exporting: " + filename)
        headerList =  ["course_id", "assignment_id", "rubric_id", "description", "long_description", "points"];

        with open(filename, "w")  as csvfile:

            writer = csv.writer(csvfile, dialect="excel")
            writer.writerow(headerList)
            for item in rubric:
                row = [course, assignment, item["id"], item["description"], item["long_description"], item["points"]]
                writer.writerow(row)

        print("Done!")

    def DownloadURLToFile(url, filename):
        with open(filename, "wb") as file:
            response = requests.get(url)
            file.write(response.content)

    def IndexRequired(list, id, errorIfMissing=True):
        try:
            return list.index(id)
        except ValueError:
            if (errorIfMissing):
                print("ERROR Could not find column: " + id)
                quit()
            return -1


    def CommandImport(filename):
        print ("Importing: " + filename)
        with open(filename, "r")  as csvfile:
            reader = csv.reader(csvfile)
            headerList = next(reader)

            course_id_index = IndexRequired(headerList, "course_id")
            assignment_id_index = IndexRequired(headerList, "assignment_id")
            user_id_index = IndexRequired(headerList, "user_id")
            score_index = IndexRequired(headerList, "score")
            comment_index = IndexRequired(headerList, "comment")

            name_index = IndexRequired(headerList, "name", False)
            if (name_index < 0):
                name_index = IndexRequired(headerList, "Name", False)

            rowCount = 1
            for row in reader:
                course_id = row[course_id_index]
                assignment_id = row[assignment_id_index]
                user_id = row[user_id_index]
                score = row[score_index]
                comment = row[comment_index]
                name = ""

                if (name_index >= 0):
                    name = row[name_index]

                print("Processing Row " + str(rowCount) + " " + user_id + " " + name + ": ", end="")

                if (len(score) <= 0):
                    print("Skipped (score was blank)")
                else:
                    SubmitGrade(course_id, assignment_id, user_id, score, comment)
                    print("Grade posted")
                rowCount += 1

        print("Done!")

    # follows the standard import headers, but link column must exist (and is not used)
    # rubric item ID goes in header cell, starting in the cell AFTER link
    # put points scored for that item under the rubric item ID and put the comments in the next column
    # must have a pair of these columns for every rubric item you wish to populate
    # and they must be the LAST columns in the sheet starting AFTER link column
    # you can get the rubric item IDs from the exportrubric command
    # SAMPLE HEADERS: course_id	assignment_id, user_id, name, link, _5573, comment, _5397, comment
    def CommandImportRubric(filename):
        print ("Importing: " + filename)
        with open(filename, "r")  as csvfile:
            reader = csv.reader(csvfile)
            headerList = next(reader)

            course_id_index = IndexRequired(headerList, "course_id")
            assignment_id_index = IndexRequired(headerList, "assignment_id")
            user_id_index = IndexRequired(headerList, "user_id")
            link_index = IndexRequired(headerList, "link")
            rubric_item_start = link_index + 1

            name_index = IndexRequired(headerList, "name", False)
            if (name_index < 0):
                name_index = IndexRequired(headerList, "Name", False)

            rowCount = 1
            for row in reader:
                course_id = row[course_id_index]
                assignment_id = row[assignment_id_index]
                user_id = row[user_id_index]
                name = ""

                if (name_index >= 0):
                    name = row[name_index]

                print("Processing Row " + str(rowCount) + " " + user_id + " " + name + ": ", end="")

                params = {
                    "include[visibility]":"true"
                }
                i = rubric_item_start
                while i < len(headerList):
                    params["rubric_assessment[" + headerList[i] + "][points]"] = row[i]
                    params["rubric_assessment[" + headerList[i] + "][comments]"] = row[i + 1]
                    i += 2

                CanvasAPIPut("/api/v1/courses/" + course_id + "/assignments/" + assignment_id + "/submissions/" + user_id, params)
                print("Grade posted")
                rowCount += 1

        print("Done!")