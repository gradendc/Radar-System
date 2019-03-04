plot(output_time_buffer, output_buffer); 
ylim([0 1]);
output_matrix = [output_time_buffer.' output_buffer.'];

csvwrite('output.csv' ,output_matrix); 