fx = @(x) (x^2 + 9) / (2*x);

start = 1;
iterations = 10;
for (i = 1:iterations)
    start = fx(start);
end
start