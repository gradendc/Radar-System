plot(output_time_buffer, output_buffer); 
ylim([0 0.75]);
output_matrix = [output_time_buffer.' output_buffer.'];

csvwrite('output.csv' ,output_matrix); 