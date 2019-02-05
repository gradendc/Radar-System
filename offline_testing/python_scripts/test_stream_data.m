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


while true
    tic;
    %for testing purposes%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    pause(0.1);
    four_frames = combined(frame_index:(frame_index+3) , :);
    frame_index = frame_index+4; 
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
%     % From infineon code - 3. Trigger radar chirp and get the raw data
%     [mxRawData, sInfo] = oRS.oEPRadarBase.get_frame_data;
%     ydata = mxRawData; % get raw data
%     rawData = [rawData, mxRawData];     %TODO note, make sure that the rawData is incrementing correctly (dimensions)
%     disp(ydata); %used to be disp(ydata');
    
    %TODO: format ydata into matrix, which each row is 1 chirp 
    %eg 4 chirps = 4 rows, 64 columns (64 samples_per_chirp)
    chirps_data = four_frames;   %replace four_frames with above formatted data
    for i = 1:chirps_per_frame
        rangeFFT = fft(chirps_data(i,:),rangeFFT_length,2);   %take FFT of single chirp
        %TODO display FFT here??
        %TODO auto-detect range_select here?
        phase = angle(rangeFFT);
        phase_point = phase(range_select)
        curr_time = curr_time + (Ta/chirps_per_frame);
        plot_buffer = [plot_buffer(2:end) phase_point];
        time_buffer = [time_buffer(2:end) curr_time];

    end
    
    plot(time_buffer, plot_buffer); 
    xlim([(curr_time - plot_buffer_size*(Ta/chirps_per_frame))  curr_time]);
    %xticks(((curr_time - plot_buffer_size*(Ta/chirps_per_frame)):5:curr_time)); 
    %TODO may need to also define y axis range with ylim[]
    drawnow;
    
    toc; 
end