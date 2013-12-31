% This is the first code that you will need to complete Problem 4 for P-Set
% 3.  This code and the code systemPS3.m will be used to simulate the
% system presented in the problem statement.  In its original state it will
% solve the ode x_dot = r-x.  You will need to tweak various portions of
% the code to complete the problem.

% This code is the "solver"  it takes in the initial condition and uses the
% function ode45 to numerically solve the system of equations which are in
% the "system" file which in this case is systemPS3.m.

% After you input modify the parameter and the system, select the initial
% condition and run the code.  Within the work environment you will have a
% couple new variables T and Y which are the time and system values as a
% function of time.  You will be responsible for creating a couple of
% plots.  You can either write the codes in the Command Window or you can
% add your lines of code to the bottom of this code.

theta = 0:pi/15:4*pi;
a = 2;

xInitial = a*cos(theta);
yInitial = a*sin(theta);

b = 1;
x2 = b*cos(theta);
y2 = b*sin(theta);

c = 3;
x3 = c*cos(theta);
y3 = c*sin(theta);

xInitial = [xInitial, x2, x3];
yInitial = [yInitial, y2, y3];

subplot(3,1,3)
for i = 1:length(xInitial)

        [T,Y] = ode45(@systemTH4,[0:0.1:0.1],[xInitial(i), yInitial(i)]); % This is the solving command line.  
                    % It has a couple inputs that you should understand.  These
                    % are discussed in the MATLAB Primer.

        %  If you want the code to create the plot after it solves the system you
        %  should input your lines of code here.
        if i == 1
            vector = [Y(length(Y),1), Y(length(Y),2)];
        else 
            vector = [vector; Y(length(Y),1), Y(length(Y),2)];
        end
end

quiver(xInitial', yInitial', vector(:,1) - xInitial', vector(:,2) - yInitial');

xlabel('$$x$$','FontSize',16,'interpreter','latex')
ylabel('$$y$$','FontSize',16,'interpreter','latex')
title('Stable Spiral: $$\alpha = 3 \pi / 4$$','FontSize',16,'interpreter','latex')
set(gca,'FontSize',14)
