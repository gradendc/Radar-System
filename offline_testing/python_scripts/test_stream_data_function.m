%the following should replace the while loop in extract_raw_data.m
clear all;clc
%%%%%%%%%%%%for testing purposes, delete later....%%%%%%%%%%%%%%%%%%%
a = 0;
b = 1;
[raw, label]=xlsread('test1b.csv');
Q = raw(2:2:end,:);                         
I = raw(1:2:end,:);
phasor_matrix = complex(I,Q);             %matrix of Q and I data combined into complex time domain data
num_of_frames = length(phasor_matrix(:,1));     %column length = number of frames
combined = []; 
samples_per_chirp = 64; 
num_of_chirps = 24; 
for frame_num = 1:num_of_frames 
    %frame = zeros(24, 63);
    %frame(1,:) = phasor_matrix(frame_num, 1:63); 
    %for i=2:num_of_chirps
    %frame = zeros(num_of_chirps-2, samples_per_chirp);   %don't include first and last chirp because for some they have only 63 samples, also first chirp is corrupted
    frame = zeros(num_of_chirps, samples_per_chirp-1);     %only add 63 data points for now until can fix data input
    frame(1,:) = phasor_matrix(frame_num, (samples_per_chirp:(samples_per_chirp*2-2)) );      
    for i=2:num_of_chirps                                                                    
        frame(i,:) = phasor_matrix( frame_num, ((i-1)*samples_per_chirp):((i-1)*samples_per_chirp + samples_per_chirp-2 ));
    end
    combined = [combined; frame]; 
    frame_index = 1; 
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

rawData = [];

figure(1); hold on
chirps_per_frame = 4;
samples_per_chirp = 64; 
rangeFFT_length = 512; 
range_select = 20;  %which 'bin' to collect phase 
Ta = 0.25;          %aquisition time (time per frame)
plot_buffer_size = 2000;    %how many points to display on plot
plot_buffer = zeros(1,plot_buffer_size);   %circular buffer??, init with zeros
time_buffer = zeros(1,plot_buffer_size);   %circular buffer??
curr_time = 0.00        %assumes that each plot point is aqcuired linearly according to aquistion time

