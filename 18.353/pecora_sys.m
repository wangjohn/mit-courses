function out = pecora_sys(t, in)

out = zeros(size(in));
global r
b = 8/3;
sigma = 10;

x = in(1);
y = in(2);
z = in(3);
yr = in(4);
zr = in(5);

out(1) = sigma*(y - x);
out(2) = r*x - x*z - y;
out(3) = x*y - b*z;
out(4) = r*x - yr - x*zr;
out(5) = x*yr - b*zr;
