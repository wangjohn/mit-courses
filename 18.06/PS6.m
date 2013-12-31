%%%%% Problem 7 %%%%%

n = 500;

x = linspace(0, 2*pi, 2*n); 
x = x( 1:(length(x) - 1));
x = x';

q1 = 1/sqrt(n) * cos(x);
q2 = 1/sqrt(n) * cos(3*x);

Q = [q1, q2]; 

b1 = cos(x).^3;
v1 = Q*Q'*b1;

b2 = cos(x).^5;
v2 = Q*Q'*b2;

dif1 = v1 - b1;
dif2 = v2 - b2;