# USTclient.py
# 6.857 spring 2013
# staff: Rivest, Wilson, Popa
# Note: this code is ``naive'' and not commercial-grade or bullet-proof...

import hashlib
import random
import requests

SERVER_URL = "http://kagu.csail.mit.edu:6857"


# HASHING

def exponentiate(base, exponent, modulo):
    value = base
    current_exponent = 1
    while current_exponent*2 <= exponent:
        current_exponent *= 2
        value = value**2 % modulo

    # finish off the calculation
    for i in xrange(current_exponent, exponent):
        value = value*base % modulo
    return value

def inverse(value, modulo):
    x, y = extended_gcd(value, modulo)
    return x % modulo

def extended_gcd(a, b):
    x = 0
    y = 1
    last_x = 1
    last_y = 0
    while b != 0:
        quotient = a / b
        a, b = b, a % b
        x, last_x = last_x - quotient*x, x
        y, last_y = last_y - quotient*y, y
    return (last_x, last_y)

def H(m):
    """ 
    return hash (256-bit integer) of string m, as long integer.
    If the input is an integer, treat it as a string.
    """
    m = str(m)
    return int(hashlib.sha256(m).hexdigest(),16)

def blind(value, r, modulo, e):
    return exponentiate(r, e, modulo)*value % modulo


def main():

    # This is the server's public key
    (n,e) = (93715031694904665096888055002697470198252335679677901252409323176141222036432351101554951123733435495725006414347083088768193707960233779092919096492766147696692504661585300430366015573333244992219235624452140405877359765323303762553750772802856716366564360322106221631390511413624945975038695313305553516297, 65537)

    # Replace this with the values you got from the course staff.  
    # This is the nonce and sig(hash(nonce)) that would be received 
    # through "subscription".
    (nonce, sig) = (14525312887284414684388591974928593263214248826992664611224146316873720363326728566317583846189885797927132916578443031606377715231220554792595783616559571529486311569212621203288600053453774894374964494337729146790963210405909284647728510723928140418309695818748660382823273269779895077682482411650520211000, 39837591143969814388264448483337333794893547861606290669380163503059569415553806850074654908386059398232956667120539816039574249791973738918530740595416445533187756988218749130629618509396906391854791428988589541985133687499789393504661404207320462081883023661395118220988595992996808778169998877034912502242)

    # Number of iterations.  Please don't make this very large.
    num_iterations = 10

    for i in xrange(0,num_iterations):
        #generate a new nonce (new_nonce) and blinded object (blinded_new_hash) to sign
        random_r = random.randint(0, n-1)
        inverse_random_r = inverse(random_r, n)

        new_nonce = random.randint(0, n-1)
        blinded_new_hash = blind(H(new_nonce), random_r, n, e)

        #make a request to the server
        (text_string, new_blinded_sig) = send_request(sig, nonce, blinded_new_hash)
        new_blinded_sig = long(new_blinded_sig)

        #unblind the new sig (yielding new_sig)
        new_sig = (new_blinded_sig * inverse_random_r % n)

        # If you feel like printing out any other information, here's 
        # a good place to do it...
        print "RANDOM R: ", random_r
        print "INVERSE RANDOM R: ", inverse_random_r
        print "NEW NONCE: ", new_nonce
        print "BLINDED NEW HASH: ", blinded_new_hash
        print "NEW BLINDED SIG: ", new_blinded_sig
        print "NEW SIG: ", new_sig

        try:
            print "RESULT: "
            print text_string
            print ""
        except:
            print "RESULT: ILL FORMATTED"

        #change to next nonce/signature for next iteration
        (nonce, sig) = (new_nonce, new_sig)

# Send a request of the form sig(hash(nonce)), nonce, blind(hash(new_nonce))
def send_request(signed_hash, nonce, blinded_new_hash):
    payload = {'sig': signed_hash, 'nonce': nonce, 'blinded': blinded_new_hash}
    r = requests.get(SERVER_URL, params=payload)
    if(r.status_code != 200):
        raise Exception(r.text)
    return r.text.splitlines()

main()
