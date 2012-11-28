import csv
import datetime

class ActivityLog:
    def __init__(self, input_lines):
        self.id = int(input_lines[0])
        self.user_account_id = int(input_lines[1])
        self.controller = input_lines[2]
        self.action = input_lines[3]
        self.model_id = input_lines[4]
        self.status = input_lines[5]
        self.created_at = datetime.datetime.strptime(input_lines[6], "%Y-%m-%d %H:%M:%S.%f")
        self.query_params = input_lines[7]
        self.ip_address = input_lines[8]
        self.next_profile_activity_log_id = input_lines[9]
        self.session_id = input_lines[10]
        self.impersonated = input_lines[11]

    def get_day(self):
        return self.created_at.strftime("%Y-%m-%d")

# id,user_account_id,controller,action,model_id,status,created_at,query_params,ip_address,next_profile_activity_log_id,session_id,impersonated
def read_in_data(filename):
    all_logs = []
    with open(filename, 'rb') as f:
        reader = csv.reader(f, delimiter=",")
        first = True
        for row in reader:
            if first:
                first = False
            else:
                all_logs.append(ActivityLog(row))
    all_logs = sorted(all_logs, key = lambda k : k.created_at)
    return all_logs


# find all the users who saw a controller/action pair k days before a commit and after the commit
def find_users(controller, action, commit_datetime, k):
    approx_commit_index = binary_search_on_created_at(activity_logs, commit_datetime, 0, len(activity_logs)-1)
    lower_datetime = commit_datetime - datetime.timedelta(days=k)
    upper_datetime = commit_datetime + datetime.timedelta(days=k)
    lower_index = binary_search_on_created_at(activity_logs, lower_datetime, 0, len(activity_logs)-1)
    upper_index = binary_search_on_created_at(activity_logs, upper_datetime, 0, len(activity_logs)-1)
    before_users = {}
    for i in xrange(lower_index, approx_commit_index, 1):
        current_activity_log = activity_logs[i]
        if current_activity_log.user_account_id in before_users:
            before_users[current_activity_log.user_account_id].append(current_activity_log)
        else:
            before_users[current_activity_log.user_account_id] = [current_activity_log]
    both_ba = {}
    for i in xrange(approx_commit_index, upper_index, 1):
        current_activity_log = activity_logs[i]
        # this must be true in order for them to be be in both before and after
        if current_activity_log.user_account_id in before_users:
            if current_activity_log.user_account_id in both_ba:
                both_ba[current_activity_log.user_account_id][1].append(current_activity_log)
            else:
                both_ba[current_activity_log.user_account_id] = [before_users[current_activity_log.user_account_id], [current_activity_log]]
    return both_ba

def binary_search_on_created_at(activity_logs, datetime, start, end):
    if end <= start:
        return start
    mid = (start + end)/2
    if activity_logs[mid].created_at > datetime:
        return binary_search_on_created_at(activity_logs, datetime, start, mid-1)
    elif activity_logs[mid].created_at < datetime:
        return binary_search_on_created_at(activity_logs, datetime, start+1, mid)
    else:
        return mid


