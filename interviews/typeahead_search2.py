import sys
import re

class Parser:
    def __init__(self, data):
        self.all_commands = data[1:]
        self.num_lines = int(data[0])
        self.data_store = DataStorage()
        for line in self.all_commands:
            self.get_command(line)

    def get_command(self, line):
        matching = re.match("(ADD|DEL|QUERY|WQUERY)", line)
        if matching:
            if matching.group(1) == "ADD":
                self.add_command(line)
            elif matching.group(1) == "DEL":
                self.del_command(line)
            elif matching.group(1) == "QUERY":
                self.query_command(line)
            elif matching.group(1) == "WQUERY":
                self.wquery_command(line)


    def add_command(self, line):
        matching = re.match("ADD (?P<type>user|topic|question|board) (?P<id>.*?) (?P<score>.*?) (?P<data_string>.*?)$", line)
        if matching:
            data_type = matching.group("type")
            data_id = matching.group("id")
            data_score = float(matching.group("score"))
            data_string = matching.group("data_string")
            self.data_store.add_data(Data(data_type, data_id, data_score, data_string))

    def del_command(self, line):
        matching = re.match("DEL (.*?)$", line)
        if matching:
            self.data_store.delete_data(matching.group(1))

    def query_command(self, line):
        matching = re.match("QUERY (?P<num_results>.*?) (?P<query>.*?)$", line)
        if matching:
            num_results = int(matching.group("num_results"))
            query = matching.group("query")
            self.data_store.query(num_results, query)

    def wquery_command(self, line):
        #matching = re.match("WQUERY (?P<num_results>.*?) (?P<num_boosts>.*?) (?P<type_boosts>(user|topic|question|board):.*?)* (?P<id_boosts>.*?:.*?)* (?P<query>.*?)$", line)
        matching = re.match("WQUERY (?P<num_results>[0-9]+) (?P<num_boosts>[0-9]+)", line)
        if matching:
            num_results = int(matching.group("num_results"))
            num_boosts = int(matching.group("num_boosts"))
        
            split_line = line.split(" ")[3:]
            boosts = split_line[:num_boosts]
            query = ' '.join(split_line[num_boosts:])

            type_boosts = []
            id_boosts = []
            # figure out the type and the id boosts
            boost_types = ["user", "topic", "question", "board"]
            for boost in boosts:
                split_boost = boost.split(":")
                if split_boost[0] in boost_types:
                    type_boosts.append((split_boost[0], float(split_boost[1])))
                else:
                    id_boosts.append((':'.join(split_boost[:-1]), float(split_boost[-1])))
            self.data_store.wquery(num_results, num_boosts, type_boosts, id_boosts, query)

class Data:
    def __init__(self, data_type, data_id, score, data_string):
        self.data_type = data_type
        self.data_id = data_id
        self.score = -score
        self.data_string = data_string.lower()
        self.boosted_score = None

    def get_boosted_score(self, weight):
        """Boosts the score, and temporarily stores the boosted score
            in the self.boosted_score variable. Make sure that the boosted
            score is cleared after you are finished with the
            calculations using the boosted scores"""
        # we could do reduce(mul, weights), but this is slower than 
        # the loop
        if self.boosted_score == None:
            self.boosted_score = self.score
        self.boosted_score *= weight
        return self.boosted_score

    def clear_boosted_score(self):
        self.boosted_score = None

class DataStorage:
    def __init__(self):
        self.data = [] 
        self.data_by_id = {}
        self.data_by_type = {}
    
    def add_data(self, new_data):
        index = self._get_insertion_index(new_data.score, self.data)
        self.data.insert(index, new_data)
        self.data_by_id[new_data.data_id] = new_data
        if new_data.data_type in self.data_by_type:
            type_index = self._get_insertion_index(new_data.score, self.data_by_type[new_data.data_type])
            self.data_by_type[new_data.data_type].insert(type_index, new_data)
        else:
            self.data_by_type[new_data.data_type] = [new_data]

    def _get_insertion_index(self, score, array):
        index = self._binary_search(score, 0, len(array)-1, array)
        if index == len(array) - 1:
            if array[-1].score < score:
                return len(array)
        while index > 0 and array[index-1].score == score:
            index -= 1
        return index

    def _binary_search(self, key, start, end, array):
        mid = start + ((end - start)//2)
        if end <= start:
            return start
        if array[mid].score > key:
            return self._binary_search(key, start, mid-1, array)
        if array[mid].score < key:
            return self._binary_search(key, mid+1, end, array)
        else:
            return mid

    def delete_data(self, data_id):
        data_obj = self.data_by_id[data_id]
        if not data_obj:
            return None
        
        del self.data_by_id[data_id]
        self._delete_from_list(self.data, data_id)
        self._delete_from_list(self.data_by_type[data_obj.data_type], data_id)
        return data_obj

    def _delete_from_list(self, array, data_id):
        for i in xrange(len(array)):
            if array[i].data_id == data_id:
                return array.pop(i)

    def query(self, num_results, prefix, forced_data={}):
        output = []
        if num_results == 0:
            return output
        prefixes = prefix.lower().split(" ")
        for data_obj in self.data:
            if data_obj.data_id not in forced_data and prefixes[0] in data_obj.data_string:
                all_matches = True
                for prefix in prefixes:
                    if prefix not in data_obj.data_string:
                        all_matches = False
                        break
                if all_matches:
                    output.append(data_obj)
                    if len(output) >= num_results:
                        break
        
        if forced_data:
            for data_obj in forced_data.itervalues():
                if prefixes[0] in data_obj.data_string:
                    all_matches = True
                    for prefix in prefixes:
                        if prefix not in data_obj.data_string:
                            all_matches = False
                            break
                    if all_matches:
                        output.append(data_obj)

        output = sorted(output, key = lambda data: get_score(data))
        result_ids = [x.data_id for x in output[:num_results]]
        print ' '.join(result_ids)
        return result_ids 
    
    def wquery(self, num_results, num_boosts, type_boosts, id_boosts, prefix):
        all_boosted = {}
        for data_type, weight in type_boosts:
            array = self.data_by_type[data_type]
            for data_obj in array:
                data_obj.get_boosted_score(weight)
                all_boosted[data_obj.data_id] = data_obj

        for data_id, weight in id_boosts:
            data_obj = self.data_by_id[data_id]
            data_obj.get_boosted_score(weight)
            all_boosted[data_obj.data_id] = data_obj

        output = self.query(num_results, prefix, all_boosted)
        
        for data_obj in all_boosted.itervalues():
            data_obj.clear_boosted_score()

        return output

def get_score(data):
    if data.boosted_score:
        return data.boosted_score
    else:
        return data.score

if __name__ == '__main__':
    data = sys.stdin.readlines()
    parser = Parser(data)
    print data
