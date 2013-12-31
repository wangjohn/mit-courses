global d1 d2 a1 a2 b1 b2
d1 = 0.13;
d2 = 0.06;

a1 = 1;
a2 = 0.1;
b1 = 5;
b2 = 45;

numinitial = 1;
endtime = 500;

fh = findall(0,'type','figure');
for i=1:length(fh)
    clf(fh(i));
end

% cool shape
% d1 = 25/6 - .7;
% d2 = .002;
% 
% a1 = 100;
% a2 = 1.5;
% b1 = 2;
% b2 = 1;

% limit cycle
% d1 = 2;
% d2 = 0.002;
% 
% a1 = 25;
% a2 = .1;
% b1 = 5;
% b2 = 45; 

% semi-chaos
% d1 = .03;
% d2 = .014;
% 
% a1 = 1.3;
% a2 = .1;
% b1 = 3;
% b2 = 1;

xrange = [0 1];
yrange = [0 1];
zrange = [0 1];

initial = zeros(numinitial, 3);
for i = 1:numinitial
   initial(i,1) = rand*(xrange(2) - xrange(1)) + xrange(1);
   initial(i,2) = rand*(yrange(2) - yrange(1)) + yrange(1);
   initial(i,3) = 0; %rand*(zrange(2) - zrange(1)) + zrange(1);
end

for i = 1:numinitial
    [T,Y] = ode45(@sys,[0:.01:endtime],initial(i,:));  
    if (length(T) >= endtime/.01)
            figure(1)
            subplot(3,1,1)
            plot(T, Y(:,1))
            hold on
            
            subplot(3,1,2)
            plot(T,Y(:,2));
            hold on
            
            subplot(3,1,3)
            plot(T,Y(:,3))
            hold on
            
            figure(2)
            plot3(Y(:,1),Y(:,2),Y(:,3));
            hold on
    end
end

% Get minima and maxima
%[xn, xn1] = findmax(x, 5);

figure(1)
subplot(3,1,1)
xlabel('$$t$$','interpreter','latex','FontSize',16)
ylabel('$$x$$','interpreter','latex','FontSize',16)

subplot(3,1,2)
xlabel('$$t$$','interpreter','latex','FontSize',16)
ylabel('$$y$$','interpreter','latex','FontSize',16)

subplot(3,1,3)
xlabel('$$t$$','interpreter','latex','FontSize',16)
ylabel('$$z$$','interpreter','latex','FontSize',16)

figure(2)
%title('Attractor Inside $xy$ Plane Trapping Region','interpreter','latex')
xlabel('$$x$$','interpreter','latex','FontSize',16)
ylabel('$$y$$','interpreter','latex','FontSize',16)
zlabel('$$z$$','interpreter','latex','FontSize',16)

% [xn, xn1] = findmin(Y(100000:length(T),1));
% scatter(xn, xn1)
% 
% xnt = [];
% counter = 1;
% for i = 1:length(xn)
%     if xn(i)*1000 < 50
%         xnt(counter) = xn(i);
%         xn1t(counter) = xn1(i);
%         counter = counter + 1;
%     end
% end