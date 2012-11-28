import os
import re
from dateutil import parser

class FileCommit:
    def __init__(self, filename, datetime, files_changed, insertions, deletions):
        self.filename = filename
        self.datetime = datetime
        self.files_changed = files_changed
        self.insertions = insertions
        self.deletions = deletions



def get_all_commits(begin_date, end_date):
    git_command = "cd ~/panjiva_web_branches/web; git rev-list --after='%s' --before='%s' --all" % (begin_date, end_date)    
    result = os.popen(git_command).read()
    return result.split("\n")

def get_commit_shortstats(result):
    amount_changed_match = re.search("([0-9]+) files? changed, ([0-9]+) insertions?\\(\\+\\), ([0-9]+) deletions?\\(\\-\\)", result)
    if amount_changed_match:
        files_changed = amount_changed_match.group(1)
        insertions = amount_changed_match.group(2)
        deletions = amount_changed_match.group(3)
    else:
        match2 = re.search("([0-9]+) files? changed, ([0-9]+) insertions?\\(\\+\\)", result)
        if match2:
            files_changed = match2.group(1)
            insertions = match2.group(2)
            deletions = 0
        else:
            match3 = re.search("([0-9]+) files? changed, ([0-9]+) deletions?\\(\\-\\)", result)
            if match3:
                files_changed = match3.group(1)
                insertions = 0
                deletions = match3.group(2)
            else:
                files_changed = 0
                insertions = 0
                deletions = 0

    return (files_changed, insertions, deletions)


def get_controller_commits(controller_name, before, after):
    git_command = "cd ~/panjiva_web_branches/web; git log --format=' %ad' --shortstat --before='" + before + "' --after='" + after + "' --follow app/controllers/" + controller_name  
    result = os.popen(git_command).read()
    split_result = result.split("\n")

    all_commits = []
    for i in xrange(len(split_result)/3):
        time = parser.parse(split_result[i*3])
        files_changed, insertions, deletions = get_commit_shortstats(split_result[i*3+2])
        commit = FileCommit(controller_name, time, files_changed, insertions, deletions)
        all_commits.append(commit)
    return all_commits


if __name__ == '__main__':
    get_controller_commits("my_panjiva_controller.rb", "11/15/2012", "11/15/2011")
