function out = gn(n)
    out = fft(eye(n))/sqrt(n);
end