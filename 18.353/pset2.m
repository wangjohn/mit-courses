fun = inline('r*x - x/(x+1)','r','x');
rangexy = [-3,3,-3,3];
ngrid = 400;

% Implicit plot function
% function implot(fun,rangexy,ngrid)
% fun is 'inline' function f(x,y)=0 (Note function written as equal to zero)
% rangexy =[xmin,xmax,ymin,ymax] range over which x and y is ploted default(-2*pi,2*pi)
% ngrid is the number of grid points used to calculate the plot,
% Start with course grid (ngrid =20) and then use finer grid if necessary
% default ngrid=50
%
% Example 
% Plot y^3+exp(y)-tanh(x)=0
%
% write function f as an 'inline' function of x and y-- right hand side 
% equal to zero
%
% f=inline('y^3+exp(y)-tanh(x)','x','y')
% implot(f,[-3 3 -2 1])


%       A.Jutan UWO 2-2-98  ajutan@julian.uwo.ca



if nargin == 1  ;% grid value and ranges not specified calculate default
        rangexy=[-2*pi,2*pi,-2*pi,2*pi];
   ngrid=50;
end


if nargin == 2;  % grid value not specified
   ngrid=50;
end


% get 2-D grid for x and y


xm=linspace(rangexy(1),rangexy(2),ngrid);
ym=linspace(rangexy(3),rangexy(4),ngrid);
[x,y]=meshgrid(xm,ym);
fvector=vectorize(fun);% vectorize the inline function to handle vectors of x y
fvalues=feval(fvector,x,y); %calculate with feval-this works if fvector is an m file too
%fvalues=fvector(x,y); % can also calculate directly from the vectorized inline function
fprime = inline('r - 1/(x+1)^2', 'r','x');
fprime = vectorize(fprime);
fprvalues = feval(fprime,x,y);

[r1, c1] = size(x);
for i = 1:r1
    for j = 1:c1
        if fprvalues(i,j) < 0;
            stable(i,j) = fvalues(i,j);
            unstable(i,j) = -50;
        else
            unstable(i,j) = fvalues(i,j);
            stable(i,j) = -50;
        end
    end
end

for i = 1:c1
    unstable(134,i) = 0;
    stable(134,i) = NaN;
end
    
contour(x,y,stable,[0,0],'b');
hold on
contour(x,y,unstable,[0,0],'r');
xlabel('r');ylabel('x*');
grid off
title('Problem Set 2, Problem 2: Bifurcation Diagram')
legend('Stable','Unstable')