function [mn, mn1] = findmin(x, transient)

size = length(x);
if x(2) > x(1)
    current = 1;
else
    current = 0;
end
min = [];
msize = 1;

for i = 2:size
    if (x(i) > x(i-1)) && (current == 1)
        current = 1;
    elseif (x(i) < x(i - 1)) && (current == 1)
        current = 0;
    elseif (x(i) < x(i - 1)) && (current == 0)
        current = 0;
    elseif (x(i) > x(i - 1)) && (current == 0)
        if (x(i - 1) < 0.9)
            current = 1;
            msize = msize + 1;
            min(msize) = x(i - 1);
        end
    end
end

mn = min((1 + transient):(length(min) - 1));
mn1 = min((2 + transient):length(min));

end