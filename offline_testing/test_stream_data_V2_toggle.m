%the following should replace the while loop in extract_raw_data.m
clear all;clc
%%%%%%%%%%%%for testing purposes, delete later....%%%%%%%%%%%%%%%%%%%
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

chirps_per_frame = 4;
samples_per_chirp = 64; 
rangeFFT_length = 512; 
range_select = 0;  %which 'bin' to collect phase. if zero, then will autodetect
Ta = 0.25;          %aquisition time (time per frame)
plot_buffer_size = 2000;    %how many points to display on plot
plot_buffer = zeros(1,plot_buffer_size);   %circular buffer??, init with zeros
time_buffer = zeros(1,plot_buffer_size);   %circular buffer??
curr_time = 0.00        %assumes that each plot point is aqcuired linearly according to aquistion time

%signal analyis
data_buffer_size = 2000; 
data_buffer = zeros(1, data_buffer_size);
data_time_buffer = zeros(1, data_buffer_size);
phaseFFT_length = 2048; %make sure this is > data_buffer_size and is a power of 2
polynum = 6;            %polynomial degree for detrending
min_distance = 0.5;     %rangeFFT will be truncated below this (to ignore low freq spikes)
Fs = 42666.0;           %sample rate (Hz)
Tc = 1500e-6;                   %chirp time in secs
c = 3e8;
BW = 200e6;             %bandwidth in Hz
lower_bandstop = 0.05;	%in Hz
plot_timer = 0; 
plot_toggle = false;
loop_time = 0; 

%Averaging Constants
fftFrame = 1;
NumAverageFrames = 8;
SummedPhaseFFTData = zeros(1,phaseFFT_length/2);
PhaseFFTDataArray = zeros(NumAverageFrames,phaseFFT_length/2);

%storage for testing
phasePointStore= [];
freqStore=[];
magStore = [];
timeStore=[];
signal_freq =0;
norm_max_mag =0;


j=0; 
total_time = 0;
%fileID = fopen('data_log.csv','w');
while true
    tic;
    %for testing purposes%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    pause(0.005);
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
        rangeFFT = rangeFFT(1:(rangeFFT_length/2));
        phase = angle(rangeFFT);
        if range_select == 0
            range_min = round(min_distance/((Fs/(rangeFFT_length/2))*((c*Tc)/(4*BW))));
            [max_val, range_select] = max(rangeFFT(range_min:end)); 
            detected_distance = range_select*((Fs/(rangeFFT_length/2))*((c*Tc)/(4*BW)))
        end
        phase_point = phase(range_select); 
        %fileID = fopen('data_log.csv','a');
        %formatSpec = '%4.2f \n';
        %fprintf(fileID, formatSpec, phase_point);
        %fclose(fileID);
        curr_time = curr_time + (Ta/chirps_per_frame);
        plot_buffer = [plot_buffer(2:end) phase_point];
        time_buffer = [time_buffer(2:end) curr_time]; 
        
        %signal analyis
        data_buffer = [data_buffer(2:end) phase_point];
        data_time_buffer = [data_time_buffer(2:end) curr_time]; 
        
        %store data
        phasePointStore= [phasePointStore phase_point];
        freqStore=[freqStore signal_freq];
        magStore = [magStore norm_max_mag];
        timeStore=[timeStore curr_time];
    end
    
    figure(1); %hold on
    subplot(2,1,1);
    plot(time_buffer, plot_buffer); 
    title('Phase vs Time');
    xlim([(curr_time - plot_buffer_size*(Ta/chirps_per_frame))  curr_time]);
    %xticks(((curr_time - plot_buffer_size*(Ta/chirps_per_frame)):5:curr_time)); 
    %TODO may need to also define y axis range with ylim[]
    drawnow
    
    %signal analyis
    %code that calculates dominant frquency
    [p,s,mu] = polyfit(data_time_buffer,data_buffer,polynum);
    f_y = polyval(p,data_time_buffer,[],mu);
    detrended_data = data_buffer - f_y;
    phaseFFT = abs(fft(detrended_data,phaseFFT_length));
    phaseFFT = phaseFFT(1:(phaseFFT_length/2));     %truncate last half
	trunc_phase_bin = round(lower_bandstop/((chirps_per_frame/Ta)/phaseFFT_length)); 
	if(trunc_phase_bin ~= 0)
		for i = 1:trunc_phase_bin
		phaseFFT(i) = 0;     %"truncate" low freq spikes by setting to 0
		end
	end
    %TODO am i losing info by truncating? should i be recombining somehow?
    
    %Averaging Phase FFT over multiple frames
    if fftFrame == NumAverageFrames
        fftFrame = 1;
    else
        fftFrame = fftFrame + 1;
    end
    
    PhaseFFTDataArray(fftFrame,:) = phaseFFT;
    SummedPhaseFFTData = zeros(1,phaseFFT_length/2);
    
    for f = 1:NumAverageFrames
        SummedPhaseFFTData = SummedPhaseFFTData + PhaseFFTDataArray(f,:);
    end
    
    % Adding averaging max [max_mag, max_freq] = max(phaseFFT);
    [max_mag, max_freq] = max(SummedPhaseFFTData);
    signal_freq = max_freq*((chirps_per_frame/Ta)/phaseFFT_length);
    %calculate normalized magnitude
    phase_mean = mean(SummedPhaseFFTData);
    phase_sd = std(SummedPhaseFFTData);
    norm_max_mag = (max_mag - phase_mean)/phase_sd;
    
    plot_timer = plot_timer+toc; 
    if plot_timer >= 4
        plot_toggle = ~plot_toggle;
        plot_timer= 0;
    end
    plot_toggle = true;
    if plot_toggle == true  
        subplot(2,1,2);
        axis_phaseFFT = (0:1:((phaseFFT_length/2)-1))*((chirps_per_frame/Ta)/(phaseFFT_length/2)); 
        plot(axis_phaseFFT, SummedPhaseFFTData); 
        title(['Phase FFT, freq = ',num2str(signal_freq)]);
        xlim([0  3.5]);
    else
        subplot(2,1,2);
        axis_rangeFFT = (0:1:((rangeFFT_length/2)-1))*(Fs/(rangeFFT_length/2))*((c*Tc)/(4*BW));
        plot(axis_rangeFFT, rangeFFT); 
        title(['Range FFT, dist = ',num2str(detected_distance)]);
        xlim([0  5]);
    end
    %annotation('textbox',[0 0 .1 .2],'String',['Looptime', num2str(loop_time)],'EdgeColor','none');  

    j = j+1;
    loop_time = toc
    %toc
    total_time = total_time + loop_time;
    av_runtime = total_time/j
   
    
end