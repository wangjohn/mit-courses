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
Initial = zeros(3, last);
for i = 1:last
    Initial(:,i) = [round(20*rand), round(20*rand), round(20*rand)];
end

global r 
r = 24.5;
scrsz = get(0, 'ScreenSize');

for i = 1:last
    s = figure('Position', [1 -scrsz(4)/2 scrsz(3)/2 scrsz(4)/1.2]);
    [T,Y] = ode45(@lorenz_sys,[0:.1:(30*i)],Initial(:,i));
                % This is the solving command line.  
                % It has a couple inputs that you should understand.  These
                % are discussed in the MATLAB Primer.

    subplot(3,1,1)
    plot(T,Y(:,1),'k','LineWidth',2)
    xlabel('$$t$$','FontSize',16,'interpreter','latex')
    ylabel('$$x$$','FontSize',16,'interpreter','latex')
    
    tit = sprintf('r = 24.5, x(0) = %d, y(0) = %d, z(0) = %d', ...
        Initial(1,i), Initial(2,i), Initial(3,i));
    title(tit, 'FontSize', 16, 'interpreter', 'latex')
    hold on

    subplot(3,1,2)
    plot(T,Y(:,2), 'k', 'LineWidth',2)
    xlabel('$$t$$','FontSize',16,'interpreter','latex')
    ylabel('$$y$$','FontSize',16,'interpreter','latex')
    hold on

    subplot(3,1,3)
    plot(Y(:,1),Y(:,3), 'k','LineWidth',2)
    xlabel('$$x$$','FontSize',16,'interpreter','latex')
    ylabel('$$z$$','FontSize',16,'interpreter','latex')
    hold on
    
    print(s, '-dpdf',sprintf('Lorenz24F%d.pdf', i))
end
