%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% function out = extract_raw_data (in)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Copyright (c) 2014-2017, Infineon Technologies AG
% All rights reserved.
%
% Redistribution and use in source and binary forms, with or without modification,are permitted provided that the
% following conditions are met:
%
% Redistributions of source code must retain the above copyright notice, this list of conditions and the following
% disclaimer.
%
% Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
% disclaimer in the documentation and/or other materials provided with the distribution.
%
% Neither the name of the copyright holders nor the names of its contributors may be used to endorse or promote
% products derived from this software without specific prior written permission.
%
% THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
% INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
% DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE  FOR ANY DIRECT, INDIRECT, INCIDENTAL,
% SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
% SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
% WHETHER IN CONTRACT, STRICT LIABILITY,OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
% OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% DESCRIPTION:
% This simple example demos the acquisition of data.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% cleanup and init
% Before starting any kind of device the workspace must be cleared and the
% MATLAB Interface must be included into the code. 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clc
disp('******************************************************************');
addpath('..\..\RadarSystemImplementation'); % add Matlab API
clear all %#ok<CLSCR>
close all
resetRS; % close and delete ports

% 1. Create radar system object
szPort = findRSPort; % scan all available ports
oRS = RadarSystem(szPort); % setup object and connect to board

disp('Connected RadarSystem:');
oRS %#ok<*NOPTS>

% 2. Enable automatic trigger with frame time 1s
%oRS.oEPRadarBase.set_automatic_frame_trigger(1000000);  % in microsec?
oRS.oEPRadarBase.set_automatic_frame_trigger(250000);
%oRS.oEPRadarBase.set_automatic_frame_trigger(500000);
min_frame_interval = oRS.oEPRadarBase.min_frame_interval_us 

% Graden's additional settings below
%oRS.oEPRadarBase.set.num_samples_per_chirp(obj, val)
chirps_per_frame = 48;
samples_per_chirp = 32; 
%rawData = zeros(sample_per_chirp, ??, chirps_per_frame);
oRS.oEPRadarBase.stop_automatic_frame_trigger; % stop it to change values 
oRS.oEPRadarBase.num_chirps_per_frame = chirps_per_frame;   
oRS.oEPRadarBase.num_samples_per_chirp = samples_per_chirp; % can be [32, 64, 128, 256] 
Tc_nano = double(oRS.oEPRadarBase.chirp_duration_ns);                  %chirp time in nanosecs
Tc = Tc_nano*(1e-9);
Fs = double(oRS.oEPRadarADCXMC.samplerate_Hz);          %sample rate (Hz)
lower_freq = oRS.oEPRadarFMCW.lower_frequency_kHz;   % lower FMCW frequency   
upper_freq = oRS.oEPRadarFMCW.upper_frequency_kHz;   % upper FMCW frequency 
BW = double(upper_freq - lower_freq)*1000;             %bandwidth in Hz
chirps_data = zeros(chirps_per_frame, samples_per_chirp);    %each row is chirp
rangeFFT_length = 512; 
auto_range = 0;     %  if 0, will use below range_select. if 1, will auto-detect range
range_select = 20;  %which 'bin' to collect phase.if zero, then will autodetect
Ta = 0.25;          %aquisition time (time per frame)
plot_buffer_size = 2000;    %how many points to display on plot
plot_buffer = zeros(1,plot_buffer_size);   %circular buffer??, init with zeros
time_buffer = zeros(1,plot_buffer_size);   %circular buffer??
curr_time = 0.00        %assumes that each plot point is aqcuired linearly according to aquistion time
%buffer time = buffer_size*(Ta/chirps_per_frame);
%e.g. 1000 is 10.42 secs, 1500 is 15.63 secs , 2000 is 20.833 secs,  2500 is 26.04 secs


%signal analyis
data_buffer_size = 2500; 
data_buffer = zeros(1, data_buffer_size);
data_time_buffer = zeros(1, data_buffer_size);
%phaseFFT_length = 2048; %make sure this is > data_buffer_size and is a power of 2
phaseFFT_length = 4096;
polynum = 6;            %polynomial degree for detrending
min_distance = 1;     %rangeFFT will be truncated below this (to ignore low freq spikes)
lower_bandstop = 0.1;	%in Hz. phase-FFT will be "truncated" (by setting magnitude to 0) AT THIS FREQ and below (rounded to FFT bin)
c = 3e8;
plot_timer = 0; 
plot_toggle = 0;
loop_time = 0; 

j=0; 
total_time = 0;
while true
	tic;
	
    % 3. Trigger radar chirp and get the raw data
    [mxRawData, sInfo] = oRS.oEPRadarBase.get_frame_data;
    
    %ydata = mxRawData; % get raw data
    
    %rawData = [rawData, mxRawData];
    
    %disp(ydata); %used to be disp(ydata');
    
    %TODO: mxRawData in form eg 64x1x4, so samples x frames? x chirps
    %eg mxRawData(:,:,1) is first chirp, in a column of 64 values
    for i = 1:chirps_per_frame
        chirps_data(i, :) = mxRawData(:, 1, i).';
        %plot(chirps_data(i,:)); 
        %drawnow
    end  
    %chirps_data = mxRawData(:, 1, :);   %replace four_frames with above formatted data
    %chirps_data = mxRawData.'; 
    for i = 1:chirps_per_frame
        rangeFFT = fft(chirps_data(i,:),rangeFFT_length,2);   %take FFT of single chirp
        rangeFFT = rangeFFT(1:(rangeFFT_length/2));
        if auto_range == 1
            %range_min = round(min_distance/((Fs/rangeFFT_length)*((c*Tc)/(4*BW))));
            range_min = 2;
            [max_val, range_select] = max(abs(rangeFFT(range_min:end))); 
        end
        detected_distance = range_select*((Fs/rangeFFT_length)*((c*Tc)/(4*BW)));
        
        phase = angle(rangeFFT);
        phase_point = phase(range_select); 
        curr_time = curr_time + (Ta/chirps_per_frame);
        plot_buffer = [plot_buffer(2:end) phase_point];
        time_buffer = [time_buffer(2:end) curr_time];  

		%signal analyis
        data_buffer = [data_buffer(2:end) phase_point];
        data_time_buffer = [data_time_buffer(2:end) curr_time]; 		
    end
	
	%signal analyis
    %code that calculates dominant frquency
    [p,s,mu] = polyfit(data_time_buffer,data_buffer,polynum);
    f_y = polyval(p,data_time_buffer,[],mu);
    detrended_data = data_buffer - f_y;
	% %windowing
    % window = hann(data_buffer_size);
    % detrended_data = detrended_data.*(window.');
	
    phaseFFT = abs(fft(detrended_data,phaseFFT_length));
    phaseFFT = phaseFFT(1:(phaseFFT_length/2));     %truncate last half
	trunc_phase_bin = round(lower_bandstop/((chirps_per_frame/Ta)/phaseFFT_length)); 
	if(trunc_phase_bin ~= 0)
		for i = 1:trunc_phase_bin
		phaseFFT(i) = 0;     %"truncate" low freq spikes by setting to 0
		end
	end
    %TODO am i losing info by truncating? should i be recombining somehow?
    [max_mag, max_freq] = max(phaseFFT);
    signal_freq = max_freq*((chirps_per_frame/Ta)/phaseFFT_length);
    
	plot_timer = plot_timer+toc; 
    if plot_timer >= 4
        if plot_toggle == 2
            plot_toggle = 0;
        else
            plot_toggle = plot_toggle +1; 
        end
        plot_timer= 0;
    end
    %plot_toggle = 1; 
    figure(1); 
    if plot_toggle == 0
        %subplot(2,1,1);
        plot(time_buffer, plot_buffer); 
        title(['Phase vs Time, Detected frequency = ',num2str(signal_freq)], 'FontSize',18);
        xlim([(curr_time - plot_buffer_size*(Ta/chirps_per_frame))  curr_time]);
        %ylim( [-1  1]); 
        %xticks(((curr_time - plot_buffer_size*(Ta/chirps_per_frame)):5:curr_time)); 
        drawnow
    elseif plot_toggle == 1  
        %subplot(2,1,2);
        axis_phaseFFT = (0:1:((phaseFFT_length/2)-1))*((chirps_per_frame/Ta)/phaseFFT_length); 
        plot(axis_phaseFFT, phaseFFT); 
        title(['Phase FFT, freq = ',num2str(signal_freq)], 'FontSize',18);
        xlim([0  3.5]);
        drawnow
    elseif plot_toggle == 2
        %subplot(2,1,2);
        axis_rangeFFT = (0:1:((rangeFFT_length/2)-1))*(Fs/rangeFFT_length)*((c*Tc)/(4*BW));
        plot(axis_rangeFFT, abs(rangeFFT)); 
        %plot(abs(rangeFFT)); 
        title(['Range FFT, dist = ',num2str(detected_distance)], 'FontSize',18);
        %xlim([0  10]);
        drawnow
    end
    %annotation('textbox',[0 0 .1 .2],'String',['Looptime', num2str(loop_time)],'EdgeColor','none');  

    j = j+1;
    loop_time = toc;
    %toc
    total_time = total_time + loop_time;
    av_runtime = total_time/j
    loop_time
	
end;