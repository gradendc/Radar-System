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
min_frame_interval = oRS.oEPRadarBase.min_frame_interval_us 

% Graden's additional settings below
%oRS.oEPRadarBase.set.num_samples_per_chirp(obj, val)
rawData = [];
chirps_per_frame = 48;
samples_per_chirp = 32; 
oRS.oEPRadarBase.stop_automatic_frame_trigger; % stop it to change values 
oRS.oEPRadarBase.num_chirps_per_frame = chirps_per_frame;   
oRS.oEPRadarBase.num_samples_per_chirp = samples_per_chirp; % can be [32, 64, 128, 256] 
chirps_data = zeros(chirps_per_frame, samples_per_chirp);    %each row is chirp
rangeFFT_length = 512; 
range_select = 20;  %which 'bin' to collect phase 
Ta = 0.25;          %aquisition time (time per frame)
plot_buffer_size = 2000;    %how many points to display on plot
figure(1);hold all
plot_buffer = zeros(1,plot_buffer_size);   %circular buffer??, init with zeros
time_buffer = zeros(1,plot_buffer_size);   %circular buffer??
curr_time = 0.00        %assumes that each plot point is aqcuired linearly according to aquistion time

while true
    % 3. Trigger radar chirp and get the raw data
    [mxRawData, sInfo] = oRS.oEPRadarBase.get_frame_data;
    
    ydata = mxRawData; % get raw data
    
    rawData = [rawData, mxRawData];
    
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
        %TODO display FFT here??
        %TODO auto-detect range_select here?
        phase = angle(rangeFFT);
        phase_point = phase(range_select);
        fprintf(1, "%f \n", phase_point);
        curr_time = curr_time + (Ta/chirps_per_frame);
        %plot_buffer = [plot_buffer(2:end) phase_point];
        %time_buffer = [time_buffer(2:end) curr_time];    
    end
    
    %plot(time_buffer, plot_buffer); 
    %xlim([(curr_time - plot_buffer_size*(Ta/chirps_per_frame))  curr_time]);
    %ylim( [-1  1]); 
    %xticks(((curr_time - plot_buffer_size*(Ta/chirps_per_frame)):5:curr_time)); 
    %TODO may need to also define y axis range with ylim[]
    drawnow
    
end;