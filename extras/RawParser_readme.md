* rawparser.py is a python utility to extract Depth, AB, Confidence and XYZ from the frames captured via Data collect or from ADI ToF Viewer.

Command Usage: 
	
	usage: rawparser.py [-h] [--no_xyz] filename

	Script to parse a raw file and extract different frame data

	options:
	  -h, --help           show this help message and exit
	  --no_xyz             Use no_xyz option when passing input file without XYZ

Example:

	rawparser.py <input bin file path>
	
	- The above command will extract Depth, AB, Confidence and XYZ from the outfile and save to outfile_parsed directory.