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
        self.num_views_day_later = None

    def convert_to_row(self):
        return [self.id, self.user_account_id, self.controller, self.action, self.model_id, self.status, self.created_at, self.ip_address, self.next_profile_activity_log_id, self.session_id, self.impersonated, self.time_from_event.seconds + 86400*self.time_from_event.days]

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

    def find_controllers(self):
        pairs = {}
        for log in self.activity_logs:
            current_pair = log.controller 
            pairs[current_pair] = True
        return pairs.keys()

    # find all the users who saw a controller/action pair k days before a commit and after the commit
    # outputs: hash of user_account_id : [[before_activity_logs], [after_activity_logs]] 
    def find_users(self, activity_logs, controller, commit_datetime, k):
        approx_commit_index = binary_search_on_created_at(activity_logs, commit_datetime, 0, len(activity_logs)-1)
        lower_datetime = commit_datetime - datetime.timedelta(days=k)
        upper_datetime = commit_datetime + datetime.timedelta(days=k)
        lower_index = binary_search_on_created_at(activity_logs, lower_datetime, 0, len(activity_logs)-1)
        upper_index = binary_search_on_created_at(activity_logs, upper_datetime, 0, len(activity_logs)-1)
        before_users = {}
        for i in xrange(lower_index, approx_commit_index, 1):
            current_activity_log = activity_logs[i]
            if current_activity_log.controller == controller:
                current_activity_log.time_from_event = current_activity_log.created_at.replace(tzinfo=None) - commit_datetime.replace(tzinfo=None) 
                # get the number of views 1 day later
                if current_activity_log.user_account_id in before_users:
                    before_users[current_activity_log.user_account_id].append(current_activity_log)
                else:
                    before_users[current_activity_log.user_account_id] = [current_activity_log]
        both_ba = {}
        for i in xrange(approx_commit_index, upper_index, 1):
            current_activity_log = activity_logs[i]
            # this must be true in order for them to be be in both before and after
            if current_activity_log.controller == controller and current_activity_log.user_account_id in before_users:
                current_activity_log.time_from_event = current_activity_log.created_at.replace(tzinfo=None) - commit_datetime.replace(tzinfo=None) 
                if current_activity_log.user_account_id in both_ba:
                    both_ba[current_activity_log.user_account_id][1].append(current_activity_log)
                else:
                    both_ba[current_activity_log.user_account_id] = [before_users[current_activity_log.user_account_id], [current_activity_log]]
        return both_ba

    def format_both_ba_into_rows_aggregated(self, both_ba, output_rows, extra_data, extra_data_names):
        column_names = extra_data_names
        column_names.extend(['user_account_id', 'num_before', 'num_after', 'total'])
        for user_account_id, activity_logs_list in both_ba.iteritems():
            activity_logs_list[0][0].convert_to_row()
            num_before = len(activity_logs_list[0])
            num_after = len(activity_logs_list[1])
            output_rows.append(extra_data + [user_account_id, num_before, num_after, num_before + num_after])
        return output_rows

    def format_both_ba_into_rows_meancentered(self, both_ba, output_rows, commit_datetime):
        #column_names = ['id', 'user_account_id', 'controller', 'action', 'model_id', 'status', 'created_at', 'query_params', 'ip_address', 'next_profile_activity_log_id', 'session_id', 'impersonated', 'time_from_event', 'after_commit', 'num_views_day_later']
        
        for user_account_id, activity_logs_list in both_ba.iteritems():
            combined_list = activity_logs_list[0] + activity_logs_list[1]
            for i in xrange(len(activity_logs_list[0])):
                activity_log_before = activity_logs_list[0][i]
                if abs(activity_log_before.created_at.replace(tzinfo=None) - commit_datetime.replace(tzinfo=None)) < datetime.timedelta(days=2):
                    j = binary_search_on_created_at(combined_list, activity_log_before.created_at + datetime.timedelta(days=1), 0, len(combined_list)-1)
                    output_rows.append(activity_log_before.convert_to_row() + [0, j-i])
            for i in xrange(len(activity_logs_list[1])):
                activity_log_after = activity_logs_list[1][i]
                if abs(activity_log_after.created_at.replace(tzinfo=None) - commit_datetime.replace(tzinfo=None)) < datetime.timedelta(days=2):
                    j = binary_search_on_created_at(combined_list, activity_log_after.created_at + datetime.timedelta(days=1), 0, len(combined_list)-1)
                    output_rows.append(activity_log_after.convert_to_row() + [1, j-(i+len(activity_logs_list[0])-1)])
        return output_rows

def binary_search_on_created_at(activity_logs, datetime, start, end):
    if end <= start:
        return start
    mid = (start + end)/2
    created_at = activity_logs[mid].created_at.replace(tzinfo=None)
    datetime = datetime.replace(tzinfo=None)
    if created_at > datetime:
        return binary_search_on_created_at(activity_logs, datetime, start, mid-1)
    elif created_at < datetime:
        return binary_search_on_created_at(activity_logs, datetime, mid+1, end)
    else:
        return mid

if __name__ == '__main__':
    all_logs = read_in_data("data/activity_log_out.csv")
    print 'all loaded'
    test_datetime = datetime.datetime(2012, 8, 14)
    fus = FindUserSets(all_logs)
    print cap
    print len(cap)
    #b = fus.find_users(all_logs, "my_panjiva", "async_activity_feed", test_datetime, 10)
    #print "Length of the results"
    #for key, value in b.iteritems():
    #    print key, len(value[0]), len(value[1])
