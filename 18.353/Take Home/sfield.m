function [dx, dy] = sfield(fn, rm, Np)

xx = linspace(rm(1), rm(2),Np);
yy = linspace(rm(3), rm(4), Np);
[x,y] = meshgrid(xx,yy);

eval(['f = ', fn,'(x,y);'])

angle = atan(f);
dx = cos(angle);
dy = sin(angle);

dx(imag(dx)~=0) = NaN;
dy(imag(dy)~=0) = NaN;

quiver(x,y,dx,dy);