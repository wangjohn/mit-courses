diary('PS5')
%%%%%% PART A %%%%%%

b = randn(3,1);
A = randn(3,2);

[R, pivcol] = rref(A);
C = A(:, pivcol);
Pc = C*inv(C'*C)*C';
Pa = A*inv(A'*A)*A';

proj = Pc*b;
new_proj = Pa*proj;

proj
new_proj

%%%%%% PART B %%%%%%%

A = randn(3,1);
A = [A, 2*A];
Pb = A * inv(A' * A) * A';

Pb
%%%%%% PART C %%%%%%%

P = Pa;
Z = 0;
for i = 1:100
    Z = Z + P^i;
end

Pa
P

diary off