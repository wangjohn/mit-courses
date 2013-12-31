global d1 d2 a1 a2 b1 b2
d1 = .03;
d2 = .014;

a1 = 1.3;
a2 = .1;
b1 = 3;
b2 = 1;

numinitial = 2;
endtime = 5000;
step = 0.01;

dist = @(vec1, vec2) ((vec1(1) - vec2(1))^2 + (vec1(2) - vec2(2))^2 + (vec1(3) - vec2(3))^2)^(1/2);

xrange = [0 2];
yrange = [0 2];
zrange = [0 2];

initial = zeros(numinitial, 3);
for i = 1:numinitial
   initial(i,1) = rand*(xrange(2) - xrange(1)) + xrange(1);
   initial(i,2) = rand*(yrange(2) - yrange(1)) + yrange(1);
   initial(i,3) = rand*(zrange(2) - zrange(1)) + zrange(1);
end

for i = 1:numinitial
    [T,Y] = ode45(@sys,[0:step:endtime],initial(i,:));
    if (i == 1)
        Y1 = Y;
    end
end

Distance = zeros(endtime,1);
for i = 1:endtime
   Distance(i) = dist(Y(i*(1/step),:),Y1(i*(1/step),:)); 
end


