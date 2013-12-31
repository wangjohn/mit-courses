SOLUTION TEMPLATE INSTRUCTIONS

We have prepared a template for you in writeup/ps5_answers.tex. Please modify it
to include all your answers, except for the Python source code, and then upload
it to Stellar.

To fill in the answer to a problem, e.g. Problem 2(c), search the document for
the answer start / end markers, which look like this:
    %%% PROBLEM 2(c) ANSWER START %%%
    %%% PROBLEM 2(c) ANSWER END %%%

You should then write your answer between the ANSWER START and ANSWER END
marker lines. Do NOT edit the marker lines.

Your homework will be automatically graded, and any changes to the marker lines 
or to the surrounding document may cause you to lose points. For additional
peace of mind, we recommend copying the original template to ps2_orig.tex, and
using a diff tool to compare your version to the original.
    Linux / MacOS:   diff ps2_sol.tex ps2_orig.tex
    Windows:         fc ps2_sol.tex ps2_orig.tex


MULTIPLE CHOICE QUESTIONS

The answer for multiple choice questions should be the number to the left of
your answer. For example, if Problem 1(a) has the answers:
    1. log n
    2. n
    3. 3n
    4. 4n

and you wish to answer "log n" (answer 1), your solution template should look
as follows:
    %%% PROBLEM 1(a) ANSWER START %%%
    1
    %%% PROBLEM 1(a) ANSWER END %%%


TRUE / FALSE QUESTIONS

The answer for True / False questions should be the numbers to the left of
the true answers separated by a space. For example, if Problem 1(b) has the
choices:
    1. Roses are red
    2. Roses are blue
    3. Violets are red
    4. Violets are blue

and you wish to answer that choices 1 and 3 are true and choices 2 and 4 are
false, your solution template should look as follows:
    %%% PROBLEM 1(b) ANSWER START %%%
    1 3
    %%% PROBLEM 1(b) ANSWER END %%%


PYTHON IDENTIFIER QUESTION

When answering questions that want the name of a Python variable, method or
class name, write the method name between the answer markers. Don't add any
fancy formatting, such as a \verbatim block. 
    %%% PROBLEM 2(c) ANSWER START %%%
    method_name
    %%% PROBLEM 2(c) ANSWER END %%%

You may use \_ instead of _, so that you can compile your solutions without
errors. Our grading tool will recognize the variation below as "method_name".
    %%% PROBLEM 2(c) ANSWER START %%%
    method\_name
    %%% PROBLEM 2(c) ANSWER END %%%


PROOF / PSEUDO-CODE QUESTION

Write your proof or pseudo-code, in LaTeX, between the answer markers. The LaTeX
that you learned for PS 1 and PS 2 should be sufficient for PS 5. If you want to
be fancy and use the CLRS pseudo-code format, read the documentation at

http://www.cs.dartmouth.edu/~thc/clrscode/clrscode3e.pdf


COLLABORATORS

Remember to list the full names of your collaborators, separated by commas,
between the answer markers.
    %%% COLLABORATORS START %%%
    John Doe, Jane Doe
    %%% COLLABORATORS END %%%
