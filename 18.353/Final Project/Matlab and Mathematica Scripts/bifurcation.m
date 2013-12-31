global d1 d2 a1 a2 b1 b2

d2 = 0.05;
a1 = 1;
a2 = 0.1;
b1 = 5;
b2 = 45;

%parameter ranges:
d1range = 0.004:0.002:0.1;

numinitial = length(d1range);

%ode45 parameters
stepsize = 0.01;
endtime = 300;
transient = round(0.99*endtime/stepsize);
xrange = [0 10];
yrange = [0 10];
zrange = [0 10];

initial = zeros(numinitial, 3);
for i = 1:numinitial
   initial(i,1) = rand*(xrange(2) - xrange(1)) + xrange(1);
   initial(i,2) = rand*(yrange(2) - yrange(1)) + yrange(1);
   initial(i,3) = rand*(zrange(2) - zrange(1)) + zrange(1);
end


for i = 1:length(d1range)
    d1 = d1range(i);
    [~,Y] = ode45(@sys,[0:stepsize:endtime],[0.3 0.3 0.3]);
    [xmax,~,xmin,~] = extrema(Y(:,1));
    if length(xmax) >= 5
        minimum = xmin(5);
    else
        minimum = xmin(1);
    end
    if length(xmin) >= 5
        maximum = xmax(5);
    else
        maximum = xmax(1);
    end
    vec = minimum:0.001:maximum;
    if length(Y) >= stepsize / endtime
        transient = round(0.99*length(Y));
        plot(d1range(i), Y(transient:length(Y),1), 'MarkerSize',2)
        hold on
    end
end