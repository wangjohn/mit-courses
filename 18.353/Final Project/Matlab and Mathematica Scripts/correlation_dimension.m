function avg_points = correlation_dimension(epsilon_range, numpoints)

stepsize = 0.01;
endtime = 5000;
transient = 100000;
avg_points = zeros(1, length(epsilon_range));
for i = 1:length(epsilon_range)
    avg_points(i) = pointwise_dimension(stepsize, endtime, epsilon_range(i), numpoints, transient);
end

end
