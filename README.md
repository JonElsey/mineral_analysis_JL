Simple script to analyse and plot chemical composition of olivine and pyroxene minerals based on SEM measurements.
Developed by Jon Elsey for Johan Lissenberg. 

Download the .py files and `requirements.txt` to a folder.

Then, install the required modules (Numpy, Pandas and Matplotlib - see `requirements.txt`). I recommend using a new Conda environment if using Anaconda.

`mineral_analysis.py` runs the main code. You will need all the other `.py` files in order to run the code.  

Note: If you are getting a permission denied error when running the code, ensure that the name of your output data
(default 'output_data.xlsx') is not open in Excel. Excel "hogs" the file, meaning that other programs can't change it
while it is open in Excel.
