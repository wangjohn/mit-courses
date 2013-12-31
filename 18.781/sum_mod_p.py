
def getsum(k, p):
    sum = 0
    for i in xrange(1,p):
        sum += i**k
        sum = sum % p
    return sum

def factorial(k):
    if (k == 1):
        return 1
    else:
        return k*factorial(k-1)

def modpsq(p):
    return factorial(p-1) % p^2 

def getprimes(stop):
    output = []
    for i in xrange(2, stop):
        append = True 
        for j in xrange(2, i//2 + 1):
            if i % j == 0:
                append = False
        if append:
            output.append(i)
    return output

def a2n(a,n,p):
    return ((a**2)**n + 1) % p

def main1():
    for prime in [2,3,5,7,11,13,17,19,23,29,31]:
        print "Prime: ", prime
        for i in xrange(prime):
            print i, "Sum: ", getsum(i,prime)

def main2():
    for prime in getprimes(200):
        for n in xrange(p//2):
            if (prime % 2^(n+1) == 1):
                a2n(3,n,p)

if __name__ == '__main__':
    for prime in getprimes(50): 
        print "Prime: ", prime, "Factorial mod psquared: ", modpsq(prime)


