function out = lorenz_sys(t,in)

% This is the corresponding "system" file for solverPS3.m. 
% This code is called by the "solver" and is provided with some
% information.  It is given the current location of the system (x,dxdt)
% which comes in as a column vector and the current time.  It will return
% the derivative vector for this point, dy.


%  You will need to modify this code in order to do the problem.  Modify 
% the following parameter of 'r' in order to see how the parameter modifies 
% the position of the stable fixed points.

out = zeros(size(in));

% The following is the ODE that you will need to program in.  A different
% system is currently in place and will need to be updated to the system in
% Problem 4.
global r;

% Normal parameters:
sigma = 10;
b = (8/3);

x = in(1);
y = in(2);
z = in(3);

out(1) = sigma*(y - x);
out(2) = r*x - x*z - y;
out(3) = x*y - b*z;