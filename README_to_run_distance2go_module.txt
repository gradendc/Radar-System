Quickstart Instructions

These instructions show how to run to run distance2go module with the software developed by the 2018/2019 capstone team:
-Make sure you have python installed and that the dataLogger2.py file is in the same folder as extract_raw-data_integration.m. 
-(For your info: dataLogger2.py contains a function that is called by the matlab script to communicate with the integrated system)
-Open matlab
-Open extract_raw_data_integration.m
-Plug in distance2go module via the usb connection (connection on main module (bigger square), not on debugger side)
-Start script
-Script should start plotting live data/results from radar
-Note if integrated system is not running/set-up, or if there is a connection error, the script should output an error in the console. But the radar should still run. 

Troubleshooting:
-If the script freezes/get stuck/ doesn't start running, try 
1) unplugging the module and plugging it back in. 
2)open the infineon distance2go GUI program provided by infineon, and make sure that the program is connecting to the radar and showing data from it
3)close the GUI and open Matlab, then re-run the script