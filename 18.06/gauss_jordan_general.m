% Define a function to give I and X
function [I,X] = gauss_jordan_general(A,B)
    X = A\B;
    [n,~] = size(A);
    I = eye(n);
end

