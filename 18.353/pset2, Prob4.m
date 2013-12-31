r = linspace(-5,5,500);
rneg = linspace(-5,0,250);
rpos = linspace(0,5,250);
rneg1 = linspace(-5,-2,150);
nans = NaN(1,200);
rpos1 = linspace(2,5,150);

stable = [(rneg1 + sqrt(rneg1.^2 - 4)) / 2, nans, (rpos1 + sqrt(rpos1.^2 - 4)) / 2];
unstable = [(rneg1 - sqrt(rneg1.^2 - 4)) / 2, nans, (rpos1 - sqrt(rpos1.^2 - 4)) / 2];

subplot(1,3,1)
plot(r, stable, '-b', r, unstable, '--r')
title('h < 0')
xlabel('r')
ylabel('x*')
legend('Stable', 'Unstable')

stable = [0*rneg, rpos];
unstable = [rneg, 0*rpos];

subplot(1,3,2)
plot(r, stable, '-b', r, unstable, '--r')
title('h = 0')
xlabel('r')
ylabel('x*')

stable = [(rneg + sqrt(rneg.^2 + 4)) / 2, (rpos + sqrt(rpos.^2 + 4)) / 2];
unstable = [(rneg - sqrt(rneg.^2 + 4)) / 2, (rpos - sqrt(rpos.^2 + 4)) / 2];

subplot(1,3,3)
plot(r, stable, '-b', r, unstable, '--r')
title('h > 0')
xlabel('r')
ylabel('x*')