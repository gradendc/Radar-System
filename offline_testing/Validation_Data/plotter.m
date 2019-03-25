%plot(output_time_buffer, output_buffer); 
%ylim([0 1]);
output_matrix = [timeStore' phasePointStore' freqStore.' magStore.'];
%output_matrix = [data_buffer.'];

csvwrite('output.csv' ,output_matrix); 
%plot(output_matrix);

%plot(data_buffer)