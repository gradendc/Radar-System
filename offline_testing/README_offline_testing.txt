Scripts for development without the radar module streaming live data (offline testing)

test_stream_data_V2_toggle.m:
Run the test_stream_data_V2_toggle.m file to stream in pre-recorded data from the radar module and process/display it in pseudo-live time. 
You will need to edit the line "[raw, label]=xlsread('test1b.csv');" (line 4 currently)  by changing the .csv file to whatever .csv file you want to stream. 
You can pre-record radar data using the Infineon radar GUI program. Go into the GUI settings and choose it to output time domain FMCW data to a directory of your choice. 
The GUI will output a file with a .tdd extention. Change the extension to .csv and it will be compatible the the matlab scripts. 

ICA and jade python scripts:
Code expirementing with using the the jade ICA algorithm for signal processing. 

python_scripts folder:
has scripts for "faking" matlab/radar data stream for the integrated system (see folder's readme for more detail)