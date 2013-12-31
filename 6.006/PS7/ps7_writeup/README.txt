SOLUTION TEMPLATE INSTRUCTIONS

We have prepared a template for you in the file ps7_answers.tex.  Please modify
it to include all your answers, except for the Python source code, and then
upload the modified files to Stellar under the assignment "Problem Set 7 --
LaTeX Template."

To fill in the answer to a problem, e.g. Problem 2(d), search the document for
the answer start / end markers, which look like this:

    %%% PROBLEM 2(d) ANSWER START %%%
    %%% PROBLEM 2(d) ANSWER END %%%

You should then write your answer between the ANSWER START and ANSWER END
marker lines. Do NOT edit the marker lines.

Note that Problems 2(a), 2(b), 2(c), 2(r), and 2(s) on this problem set have
their answers divided into four locations.  The four marker lines associated
with each of these problems begin with the same text (e.g. "%%% PROBLEM 2(c)"),
but are then followed by the name of a company (e.g. "DALE" or "MACROWARE").
See the instructions under "STOCK PURCHASING QUESTIONS" for details on how to
fill this out.
 
Your homework will be automatically graded, and any changes to the marker lines 
or to the surrounding document may cause you to lose points. For additional
peace of mind, we recommend copying the original template to ps7_orig.tex, and
using a diff tool to compare your version to the original.

    Linux / MacOS:   diff ps7_answers.tex ps7_orig.tex
    Windows:         fc ps7_answers.tex ps7_orig.tex


STOCK PURCHASING QUESTIONS

Problems 2(a), 2(b), 2(c), 2(r), and 2(s) on this problem set ask you to give
the optimal number of shares to buy in each company to maximize your profits.
There are four companies: Dale, JCN, Macroware, and Pear.  As a result, there
are four slots.  For instance, suppose that you decide that the optimal
strategy for Problem 2(a) involves buying 1 share in Dale, 5 in JCN, and 3 in
Macroware.  Then you would fill out the four slots as follows:

	%%% PROBLEM 2(a) DALE ANSWER START %%%
	1
	%%% PROBLEM 2(a) DALE ANSWER END %%%
	[ ... other parts of the document here ... ]
	%%% PROBLEM 2(a) JCN ANSWER START %%%
	5
	%%% PROBLEM 2(a) JCN ANSWER END %%%
	[ ... other parts of the document here ... ]
	%%% PROBLEM 2(a) MACROWARE ANSWER START %%%
	3
	%%% PROBLEM 2(a) MACROWARE ANSWER END %%%
	[ ... other parts of the document here ... ]
	%%% PROBLEM 2(a) PEAR ANSWER START %%%
	0
	%%% PROBLEM 2(a) PEAR ANSWER END %%%

You do not need to give the amount of money that you leave as cash, or the
profit that you would make.  These amounts are calculable from the answers you
give.


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


PROOF / PSEUDO-CODE QUESTION

Write your proof or pseudo-code, in LaTeX, between the answer markers. If you
want to be fancy and use the CLRS pseudo-code format, read the documentation at

http://www.cs.dartmouth.edu/~thc/clrscode/clrscode3e.pdf


COLLABORATORS

Remember to list the full names of your collaborators, separated by commas,
between the answer markers.
    %%% COLLABORATORS START %%%
    John Doe, Jane Doe
    %%% COLLABORATORS END %%%
