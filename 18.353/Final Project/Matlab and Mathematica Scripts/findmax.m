function [mn, mn1] = findmax(x, transient)

size = length(x);
if x(2) > x(1)
    current = 1;
else
    current = 0;
end
max = [];
msize = 1;

for i = 2:size
    if (x(i) > x(i-1)) && (current == 1)
        current = 1;
    elseif (x(i) < x(i - 1)) && (current == 1)
        current = 0;
        msize = msize + 1;
        max(msize) = x(i - 1);
    elseif (x(i) < x(i - 1)) && (current == 0)
        current = 0;
    elseif (x(i) > x(i - 1)) && (current == 0)
        current = 1;
    end

end

mn = max((1 + transient):(length(max) - 1));
mn1 = max((2 + transient):length(max));

end