import xmlrpclib
import traceback
import sys
import os
import tarfile

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from key import USERNAME as username, PASSWORD as password, XMLRPC_URL as server_url
except ImportError:
    print "Error: Can't find your 'key.py' file!  Please go download one from"
    print "<https://6.034.scripts.mit.edu:444/fall10/tester/key.py>"
    sys.exit(1)
    
# This is a skeleton for what the tester should do. Ideally, this module
# would be imported in the pset and run as its main function. 

# We need the following rpc functions. (They generally take username and
# password, but you could adjust this for whatever security system.)
#
# tester.submit_code(username, password, pset, studentcode)
#   'pset' is a string such as 'ps0'. studentcode is a string containing
#   the contents of the corresponding file, ps0.py. This stores the code on
#   the server so we can check it later for cheating, and is a prerequisite
#   to the tester returning a grade.
#
# tester.get_tests(pset)
#   returns a list of tuples of the form (INDEX, TYPE, NAME, ARGS):
#     INDEX is a unique integer that identifies the test.
#     TYPE should be one of either 'VALUE' or 'FUNCTION'.
#     If TYPE is 'VALUE', ARGS is ignored, and NAME is the name of a
#     variable to return for this test.  The variable must be an attribute
#     of the lab module.
#     If TYPE is 'FUNCTION', NAME is the name of a function in the lab module
#     whose return value should be the answer to this test, and ARGS is a
#     tuple containing arguments for the function.
#
# tester.send_answer(username, password, pset, index, answer)
#   Sends <answer> as the answer to test case <index> (0-numbered) in the pset
#   named <pset>. Returns whether the answer was correct, and an expected
#   value.
#
# tester.status(username, password, pset)
#   A string that includes the official score for this user on this pset.
#   If a part is missing (like the code), it should say so.

# Because I haven't written anything on the server side, test_online has never
# been tested.

def test_summary(dispindex, ntests):
    return "Test %d/%d" % (dispindex, ntests)

def show_result(testsummary, testcode, correct, got, expected, verbosity):
    if correct:
        if verbosity > 0:
            print "%s: Correct." % testsummary
        if verbosity > 1:
            print '\t', testcode
            print
    else:
        print "%s: Incorrect." % testsummary
        print '\t', testcode
        print "Got:     ", got
        print "Expected:", expected

def show_exception(testsummary, testcode):
    print "%s: Error." % testsummary
    print "While running the following test case:"
    print '\t', testcode
    print "Your code encountered the following error:"
    traceback.print_exc()
    print


def get_lab_module():
    lab = None

    # Try the easy way first
    try:
        from tests import lab_number
        lab = __import__('lab%s' % lab_number)
    except ImportError:
        pass

    for labnum in xrange(6):
        try:
            lab = __import__('lab%s' % labnum)
        except ImportError:
            pass

    if lab == None:
        raise ImportError, "Cannot find your lab; or, error importing it.  Try loading it by running 'python labN.py' (for the appropriate value of 'N')."

    if not hasattr(lab, "LAB_NUMBER"):
        lab.LAB_NUMBER = labnum
    
    return lab

    
def run_test(test, lab):
    id, type, attr_name, args = test
    attr = getattr(lab, attr_name)

    if type == 'VALUE':
        return attr
    elif type == 'FUNCTION':
        return apply(attr, args)
    else:
        raise Exception, "Test Error: Unknown TYPE '%s'.  Please make sure you have downloaded the latest version of the tester script.  If you continue to see this error, contact a TA."


def test_offline(verbosity=1):
    import tests as tests_module
    test_names = list(tests_module.__dict__.keys())
    test_names.sort()

    tests = [ (x[:-8],
               getattr(tests_module, x),
               getattr(tests_module, "%s_testanswer" % x[:-8]),
               getattr(tests_module, "%s_expected" % x[:-8]),
               "_".join(x[:-8].split('_')[:-1]))
              for x in test_names if x[-8:] == "_getargs" ]
    
    ntests = len(tests)
    ncorrect = 0
    
    for index, (testname, getargs, testanswer, expected, fn_name) in enumerate(tests):
        dispindex = index+1
        summary = test_summary(dispindex, ntests)

        if getargs == 'VALUE':
            type = 'VALUE'
            getargs = lambda: getattr(get_lab_module(), testname)
            fn_name = testname
        else:
            type = 'FUNCTION'
            
        try:
            answer = run_test((0, type, fn_name, getargs()), get_lab_module())
            correct = testanswer(answer)
        except Exception:
            show_exception(summary, testname)
            continue
        
        show_result(summary, testname, correct, answer, expected, verbosity)
        if correct: ncorrect += 1
    
    print "Passed %d of %d tests." % (ncorrect, ntests)
    return ncorrect == ntests

def get_target_upload_filedir():
    cwd = os.getcwd() # Get current directory.  Play nice with Unicode pathnames, just in case.
        
    print "Please specify the directory containing your lab."
    print "Note that all files from this directory will be uploaded!"
    print "Labs should not contain large amounts of data; very-large"
    print "files will fail to upload."
    print
    print "The default path is '%s'" % cwd
    target_dir = raw_input("[%s] >>> " % cwd)

    target_dir = target_dir.strip()
    if target_dir == '':
        target_dir = cwd

    print "Ok, using '%s'." % target_dir

    return target_dir

def get_tarball_data(target_dir, filename):
    data = StringIO()
    file = tarfile.open(filename, "w|bz2", data)

    print "Preparing the lab directory for transmission..."
            
    file.add(target_dir)
    
    print "Done."
    print
    print "The following files have been added:"
    
    for f in file.getmembers():
        print f.name
            
    file.close()

    return data.getvalue()
    

def test_online(verbosity=1):
    lab = get_lab_module()

    try:
        server = xmlrpclib.Server(server_url, allow_none=True)
        tests = server.get_tests(username, password, lab.__name__)
    except NotImplementedError:
        print "Your version of Python doesn't seem to support HTTPS, for"
        print "secure test submission.  Would you like to downgrade to HTTP?"
        print "(note that this could theoretically allow a hacker with access"
        print "to your local network to find your 6.034 password)"
        answer = raw_input("(Y/n) >>> ")
        if len(answer) == 0 or answer[0] in "Yy":
            server = xmlrpclib.Server(server_url.replace("https", "http"))
            tests = server.get_tests(username, password, lab.__name__)
        else:
            print "Ok, not running your tests."
            print "Please try again on another computer."
            print "Linux Athena computers are known to support HTTPS,"
            print "if you use the version of Python in the 'python' locker."
            sys.exit(0)
            
    ntests = len(tests)
    ncorrect = 0

    lab = get_lab_module()
    
    target_dir = get_target_upload_filedir()

    tarball_data = get_tarball_data(target_dir, "lab%s.tar.bz2" % lab.LAB_NUMBER)
            
    print "Submitting to the 6.034 Webserver..."

    server.submit_code(username, password, lab.__name__, xmlrpclib.Binary(tarball_data))

    print "Done submitting code."
    print "Running test cases..."
    
    for index, testcode in enumerate(tests):
        dispindex = index+1
        summary = test_summary(dispindex, ntests)

        try:
            answer = run_test(testcode, get_lab_module())
        except Exception:
            show_exception(summary, testcode)
            continue

        correct, expected = server.send_answer(username, password, lab.__name__, testcode[0], answer)
        show_result(summary, testcode, correct, answer, expected, verbosity)
        if correct: ncorrect += 1
    
    response = server.status(username, password, lab.__name__)
    print response



if __name__ == '__main__':
    if 'submit' in sys.argv:
        test_online()
    elif test_offline():
        if "IDLE" in sys.executable:
            print "submitting and testing online..."
            test_online()
        else:
            print "Local tests passed! Run 'python %s submit' to submit your code and have it graded." % sys.argv[0]
