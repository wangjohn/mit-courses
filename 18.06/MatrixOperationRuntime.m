%%%%%%%%%%%%%%%%%%%%%
%%%% Problem 9.A %%%%
%%%%%%%%%%%%%%%%%%%%%

nset = [100, 200, 800];
runtimes = zeros(3,3);

for npointer = 1:3
    n = nset(npointer);
    t = 50;
    addition = zeros(t,1);
    multiplication = zeros(t,1);
    solvesys = zeros(t,1);
    for i = 1:t
        a = rand(n); 
        b = rand(n);
        c = b(:,1);
        % Addition
        tic, a+b; addition(i) = toc;
        % Multiplication
        tic, a*b; multiplication(i) = toc;
        % Solving a System
        tic, linsolve(a,c); solvesys(i) = toc;
    end
    runtimes(npointer,1) = mean(addition);
    runtimes(npointer,2) = mean(multiplication);
    runtimes(npointer,3) = mean(solvesys);
end

%%%%%%%%%%%%%%%%%%%%%
%%%% Problem 9.B %%%%
%%%%%%%%%%%%%%%%%%%%%

rate = zeros(3,3);
% Rate of computation
for i = 1:3
   % Rate of addition
   rate(i,1) = runtimes(i,1) / nset(i)^2;  
   % Rate of multiplication
   rate(i,2) = runtimes(i,2) / (2*nset(i)^3);
   % Rate of solving a system
   rate(i,3) = runtimes(i,3) / ((2/3)*(n^3));
end

disptable(runtimes,'Addition|Multiplication|Solve System','n=100|n=200|n=800', 3, 4)
disptable(mean(rate),'Addition|Multiplcation|Solve System','Rate of Computation', 3, 4)

