%clear all;clc
% x=[0:.1:16]
% y=sin(3*x)
% figure(1);hold all
% Dx=50;y1=-1.2;y2=1.2;
% for n=1:1:numel(x)
%       plot(x,y);
%       axis([x(n) x(n+Dx) y1 y2]);
%       drawnow
%       pause(0.1);
% end




clear all;clc
figure(1);hold all
plot_buffer = [];   %circular buffer??
time_buffer = [];   %circular buffer??
for %blah blah
    
    %code that gets the radar data
    %code that stores all data from 1 chip into a chirp_buffer
    %if data from 1 chirp collected:
        %process chirp data by running FFT
        %get phase of FFT at the range of the object
    %optional: store phase into csv log?
    %store phase into a plot_buffer (oldest point deleted)
    %store aquisition time into time_buffer (oldest point deleted)
    
    plot(plot_buffer,time_buffer); 
    %may need to also define x and y axis range (as above) depending on code 
    drawnow
end