fx = @(x) (x^2 + 9) / (2*x);

start = 1;
iterations = 10;
output = zeros(iterations, 1);
for (i = 1:iterations)
    iterations(i,1) = start;
    start = fx(start);
end
iterations