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

% Initial conditions:
last = 2;
Initial = [6,3,3,50,10];

global r 
r = 60;

[T,Y] = ode45(@pecora_sys,[0:.005:2.5],Initial);

subplot(2,1,1)
plot(T,Y(:,2),'r-','LineWidth',2)
hold on 
plot(T,Y(:,4),'b--','LineWidth',2)

xlabel('$$t$$','FontSize',16,'interpreter','latex')
ylabel('$$y(t)$$ and $$y_r(t)$$','FontSize',16,'interpreter','latex')
title('Problem 3', 'FontSize', 16, 'interpreter', 'latex')

subplot(2,1,2)
b = 8/3;
dy = r*Y(:,1) - Y(:,1).*Y(:,3) - Y(:,2);
dz = Y(:,1).*Y(:,2) - b*Y(:,3);
U = Y(:,2) + dy;
V = Y(:,3) + dz;
quiver(Y(:,2), Y(:,3), U, V)
% plot(Y(:,2), Y(:,3),'k','LineWidth',2)

xlabel('$$y$$','FontSize',16,'interpreter','latex')
ylabel('$$z$$','FontSize',16,'interpreter','latex')
