import csv
import datetime
from dateutil import parser

class ActivityLog:
    def __init__(self, input_lines):
        self.id = int(input_lines[0])
        self.user_account_id = int(input_lines[1])
        self.controller = input_lines[2]
        self.action = input_lines[3]
        self.model_id = input_lines[4]
        self.status = input_lines[5]
        self.created_at = parser.parse(input_lines[6]) #datetime.datetime.strptime(input_lines[6], "%Y-%m-%d %H:%M:%S.%f")
        self.query_params = input_lines[7]
        self.ip_address = input_lines[8]
        self.next_profile_activity_log_id = input_lines[9]
        self.session_id = input_lines[10]
        self.impersonated = input_lines[11]
        self.time_from_event = None

    def convert_to_row(self):
        return [self.id, self.user_account_id, self.controller, self.action, self.model_id, self.status, self.created_at, self.query_params, self.ip_address, self.next_profile_activity_log_id, self.session_id, self.impersonated, self.time_from_event]

    def get_day(self):
        return self.created_at.strftime("%Y-%m-%d")

# id,user_account_id,controller,action,model_id,status,created_at,query_params,ip_address,next_profile_activity_log_id,session_id,impersonated
def read_in_data(filename):
    all_logs = []
    counter = 0
    with open(filename, 'rb') as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            if counter == 0:
                first = False
            else:
                all_logs.append(ActivityLog(row))
            counter += 1
            if counter % 100000 == 0:
                print counter
    all_logs = sorted(all_logs, key = lambda k : k.created_at)
    return all_logs


class FindUserSets:
    def __init__(self, activity_logs):
        self.activity_logs = activity_logs

    # find all the users who saw a controller/action pair k days before a commit and after the commit
    # outputs: hash of user_account_id : [[before_activity_logs], [after_activity_logs]] 
    def find_users(activity_logs, controller, action, commit_datetime, k):
        approx_commit_index = binary_search_on_created_at(activity_logs, commit_datetime, 0, len(activity_logs)-1)
        lower_datetime = commit_datetime - datetime.timedelta(days=k)
        upper_datetime = commit_datetime + datetime.timedelta(days=k)
        lower_index = binary_search_on_created_at(activity_logs, lower_datetime, 0, len(activity_logs)-1)
        upper_index = binary_search_on_created_at(activity_logs, upper_datetime, 0, len(activity_logs)-1)
        before_users = {}
        for i in xrange(lower_index, approx_commit_index, 1):
            current_activity_log = activity_logs[i]
            current_activity_log.time_from_event = commit_datetime - current_activity_log.created_at
            if current_activity_log.user_account_id in before_users:
                before_users[current_activity_log.user_account_id].append(current_activity_log)
            else:
                before_users[current_activity_log.user_account_id] = [current_activity_log]
        both_ba = {}
        for i in xrange(approx_commit_index, upper_index, 1):
            current_activity_log = activity_logs[i]
            # this must be true in order for them to be be in both before and after
            if current_activity_log.user_account_id in before_users:
                current_activity_log.time_from_event = commit_datetime - current_activity_log.created_at
                if current_activity_log.user_account_id in both_ba:
                    both_ba[current_activity_log.user_account_id][1].append(current_activity_log)
                else:
                    both_ba[current_activity_log.user_account_id] = [before_users[current_activity_log.user_account_id], [current_activity_log]]
        return both_ba

    def format_both_ba_into_rows_aggregated(both_ba, output_rows, extra_data, extra_data_names):
        column_names = extra_data_names
        column_names.extend(['user_account_id', 'num_before', 'num_after', 'total'])
        for user_account_id, activity_logs_list in both_ba.iteritems():
            num_before = len(activity_logs_list[0])
            num_after = len(activity_logs_list[1])
            output_rows.append(extra_data + [user_account_id, num_before, num_after, num_before + num_after])
        return output_rows

    def format_both_ba_into_rows_meancentered(both_ba, output_rows):
        column_names = ['id', 'user_account_id', 'controller', 'action', 'model_id', 'status', 'created_at', 'query_params', 'ip_address', 'next_profile_activity_log_id', 'session_id', 'impersonated', 'time_from_event']
        column_names.append('after_commit')
        for user_account_id, activity_logs_list in both_ba.iteritems():
            for activity_log_before in activity_logs_list[0]:
                output_rows.append(activity_log_before.convert_to_row() + [0])
            for activity_log_after in activity_logs_list[1]:
                output_rows.append(activity_log_after.convert_to_row() + [1])
        return output_rows



def binary_search_on_created_at(self, activity_logs, datetime, start, end):
    if end <= start:
        return start
    mid = (start + end)/2
    if activity_logs[mid].created_at > datetime:
        return binary_search_on_created_at(activity_logs, datetime, start, mid-1)
    elif activity_logs[mid].created_at < datetime:
        return binary_search_on_created_at(activity_logs, datetime, start+1, mid)
    else:
        return mid

if __name__ == '__main__':
    all_logs = read_in_data("data/activity_log_out.csv")
    print 'all loaded'
    test_datetime = datetime.datetime(2012, 7, 14)
    fus = FindUserSets(all_logs)
    b = fus.find_users(all_logs, "my_panjiva", "async_activity_feed", test_datetime, 10)
    print "Length of the results"
    for key, value in b.iteritems():
        print key, len(b[0]), len(b[1])
