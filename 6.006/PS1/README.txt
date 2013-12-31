********************************************************************************
***************************** FORMATTING INSTRUCTIONS **************************
********************************************************************************

Your answers to the problem set should ALL be written in the file ps1_sol.tex.
To fill in the answer to a particular problem, e.g. Problem 3(a), you should
look through the document for a pair of lines that look like this:

    %%% PROBLEM 3(a) SOLUTION START %%%
    1
    %%% PROBLEM 3(a) SOLUTION END %%%

You should then edit the line between the START and END lines to indicate what
your answer is.  Do NOT edit the marker lines.  Your homework will be
automatically graded, and any changes to the marker lines or to the
surrounding document may cause you to lose points.  In addition, your solutions
should follow several strict formatting requirements:

Ordering Problem

    Your answer should take the form of an ordering of the numbers 1, 2, 3, 4.
    The numbers should be separated by commas; whitespace is optional.  The
    ordering of the numbers should correspond to the ordering of the functions:
    for instance, if you think that the correct ordering of the functions
    should be f_4(n), f_2(n), f_3(n), f_1(n), then you should write those
    numbers in that order: 4, 2, 3, 1.

Multiple Choice

    Your answer should take the form of a single number.  The number should be
    the number assigned to the answer you wish to choose.  For instance, if
    you are trying to answer a question with the answers 1. A and 2. B,
    you would write the number 2 to indicate that your answer is B.

Proof

    Your answer should take the form of a series of lines.  These lines will
    be formatted using LaTeX, but you don't need to learn all of LaTeX to
    write up your proof --- all you need to learn is the basics of the math
    mode.  See the website for resources on this topic.  The source of the
    proof given in the homework should give you an idea of what we're looking
    for.

Counterexamples

    Your answer should be copy-and-pasted from the Python documents containing
    your counterexamples.  An example of this is shown in the existing document,
    with a very simple matrix.  The extra LaTeX code in there, \begin{verbatim}
    and \end{verbatim}, is used to make the formatting of your solution look
    nice, but is not necessary.

Collaborators

    Place the list of your collaborators in the marked location:

        %%% COLLABORATORS START %%%
        None.
        %%% COLLABORATORS END %%%

    The name of each collaborator should be listed separated by commas.  If
    you did not have any collaborators, you do not need to update the list.

Once your solutions have been formatted in this way, upload the file
ps1_sol.tex to the Stellar website, for Problem Set 1.

********************************************************************************
******************************* CODING INSTRUCTIONS ****************************
********************************************************************************

The steps that you should take to solve this problem set are as follows:

1) First, read through the problem set in ps1.pdf.  Solve the asymptotic
ordering problems and the recurrence relation problems, and place the answers
in the file ps1_sol.tex according to the instructions given above.

2) Read through the four algorithms in the file algorithms.py.

3) Try to understand how each of the four algorithms works.  To improve your
understanding of the algorithms, we have provided a visualizer in the file
visualizer.html.  To run the visualizer on a particular matrix, enter the
matrix into the file problem.py, then run the Python script main.py, and
then open the file visualizer.html in a browser.  (Chrome and Chromium are the
only browsers guaranteed to work with the visualizer, but other modern browsers
are also likely to work.)

4) Analyze the runtime of each of the four algorithms.  You may find it useful
to look at the comments of some of the functions in peak.py and trace.py, in
which the runtimes are given.

5) Try to figure out which algorithms are correct.  You can try to do this by
running the algorithms on random matrices (generated using the Python script
generate.py), but keep in mind that random matrices have a large number of
peaks, and do not usually have a very interesting peak structure.  You may
have better luck examining the algorithms in detail, and constructing
counterexamples by hand.

6) Fill out the multiple-choice answers concerning correctness and runtime.

7) Construct one counterexample (a matrix where the algorithm returns an
incorrect answer) for each incorrect algorithm.

8) Figure out which of the correct algorithms is most efficient, and write a
proof of correctness for it.

9) Place ALL of your answers in the file ps1_sol.tex, and submit the problem
set through the Stellar website.

********************************************************************************
******************************** DIRECTORY CONTENTS ****************************
********************************************************************************

ps1.pdf

    The file containing the assignment. 

ps1_sol.tex

    The file that you should fill in with your responses.  Your answers should
    be entered ONLY in the locations indicated, and you should NEVER change
    anything outside of those locations.  Your answers WILL be automatically
    graded --- if you do not put them in the correct locations, you may not
    get proper credit for them!

ps1_critique.tex

    This is the file where you will fill in your critique of your own proof,
    AFTER the assignment is due and the solutions have been released.  You
    should then copy and paste your proof into the designated location, and
    then provide a critique of your own proof afterwards.  The critique will
    be due AFTER the rest of the assignment is due.

algorithms.py

    The Python file containing the four algorithms algorithm1, algorithm2,
    algorithm3, and algorithm4.  This is the file that you should spend most of
    your time looking at, to examine the four algorithms for correctness and
    efficiency.  You may assume that any bugs that might occur will occur in
    this file --- there is no need to examine any other files for correctness.

generate.py

    This Python file can be run to generate a random matrix.  With no
    arguments (such as when running the file in IDLE), the code generates a
    random matrix of size 10 x 10, with numbers between 0 and 200, and prompts
    the user for a place to save the result.  It also takes the following
    command-line arguments:

        python generate.py [<filename> [<rows> <columns> [<maximum>]]]

    The first command-line argument, <filename>, specifies the output file.
    The next two command-line arguments, <rows> and <columns>, must both be
    specified for either one to be read.  The fourth and final command-line
    argument, <maximum>, specifies the maximum number that can be generated
    in any cell of the matrix.

main.py

    When this Python file is run, it loads a peak problem from a file that
    the user specifies, and does the following:

        (1) Tests all four algorithms on the desired peak problem, and
            outputs the results.

        (2) Generates a record of the execution of all four algorithms, and
            outputs both the peak problem and the execution traces to the file
            trace.jsonp.  These traces can be examined by displaying the file
            visualizer.html in a browser.

    When run with no arguments (such as when run in IDLE), main.py prompts
    the user for a file name to read the matrix from, defaulting to problem.py.
    It also takes a single optional argument (the filename to read the matrix
    from):

        python main.py [<filename>]

peak.py

    This file contains the code for constructing a PeakProblem object, and a
    number of methods that can be called on such a problem.  These methods are
    used by the algorithms in algorithms.py.  Each of these functions has been
    labeled with its worst-case runtime, to simplify your analysis of the
    four algorithms.

problem.py

    Thie file contains a template for entering in a matrix.  This is also the
    default name for files read by main.py and written by generate.py.  The
    counterexamples that you submit should look like this, but instead of the
    matrix we have given you, you should find a matrix that causes at least one
    of the four algorithms to fail.

trace.py

    This file contains the code for recording information about the sequence of
    steps performed by an algorithm.  Just like peak.py, it has been annotated
    with runtimes to make it easier to analyze the four algorithms.

utils.py

    This file contains some methods used for getting file names from the user.
    None of the functions in this file are used by any of the algorithms, so
    you are not responsible for reading and understanding this code.

trace.jsonp

    This file contains an object representing the history of the execution of
    the four algorithms.  You need not read it yourself --- it will be written
    by main.py, and read by visualizer.html.

visualizer.html

    An HTML visualizer for the algorithm traces generated by main.py.  The
    visualizer is a tool for improving your understanding of how the algorithms
    work.  The included legend explains what each of the symbols mean.

********************************************************************************
****************************** COMPATIBILITY ***********************************
********************************************************************************

This code has been verified to work with Python 2.7.  It will not work with
Python 3.x.
