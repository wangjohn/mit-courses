class BigNum(object):

    def __init__(self, number):
        self.d = []
        number = str(number)
        for i in number:
            self.d.append(int(i))

def slow_mul(self, other):
    '''
    Slow method for multiplying two numbers w/ good constant factors.
    '''
    result = [0 for x in range(124)]
    self_len = len(self.d)
    other_len = len(other.d)
    for i in range(self_len):
        for j in range(other_len):
            newDigit = self.d[self_len - 1 - i] * other.d[other_len - 1 - j]
            result[123 - j - i] += newDigit % 10
            if newDigit > 9 and newDigit <= 99:
                result[122 - j - i] += newDigit // 10
            
    for k in range(124):
        i = 123 - k
        remain = result[i]
        base = 0
        while remain > 9:
            result[i - base] = remain % 10
            remain = remain // 10
            if remain > 0:
                result[i - base - 1] += remain  
            base += 1

    return result

class QueueObject(object):
    """ Object for creating a Queue. """
    def __init__(self, value, left = None, right = None):
        self.right = right
        self.left = left
        self.value = value
        
    def disconnect(self):
        self.right = None
        self.left = None

class PushQueue(object):
    """ Queue for pushing and popping items. """
    def __init__(self, first_obj = 'None'):
        self.first = QueueObject(first_obj)
        self.last = self.first

    def __len__(self):
        index = 0
        obj = self.first
        while obj != self.last:
            index += 1
            obj = obj.right
        return index + 1

    def add(self, obj):
        if  self.first.value == 'None' and self.last == self.first:
            self.first.disconnect()
            self.first = QueueObject(value = obj, left = self.last)
            self.last = self.first
        else:
            self.last.right = QueueObject(value = obj, left = self.last)
            self.last = self.last.right

    def push(self, obj):
        self.add(obj)
        old_first = self.first
        new_first = self.first.right
        
        self.first = new_first
        new_first.left = None
        old_first.disconnect()

        return old_first.value

    def get_all(self):
        output = []
        obj = self.first
        while obj != self.last:
            output.append(obj.value)
            obj = obj.right
        output.append(self.last.value)
        return ''.join(output)


a0 = 234234
b0 = 2293211

a = BigNum(234234)
b = BigNum(2293211)
slow_mul(a,b)
