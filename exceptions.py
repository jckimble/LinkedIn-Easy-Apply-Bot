
class RequiredException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class BlacklistedException(Exception):
    def __init__(self, fieldName, fieldValue, job_id):
        self.value = fieldValue
        self.name = fieldName
        self.job_id = job_id
        super().__init__(fieldName + " Blacklisted: "+fieldValue)

    def __str__(self):
        return self.name + " Blacklisted: " + self.value


class ApplyException(Exception):
    def __init__(self, job_id, message):
        self.job_id = job_id
        self.msg = message
        self.questions = []
        super().__init__(message)

    def __str__(self):
        return self.msg

    def addQuestion(self, question):
        if question not in self.questions:
            self.questions.append(question)

    def getQuestions(self):
        return self.questions


class FinishException(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(msg)

    def __str__(self):
        return self.msg
