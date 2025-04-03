from icecube import icetray, dataio
from icecube.icetray import I3LogLevel
from PhotonFilter import FilterPhotonList
from argparse import ArgumentParser
import csv

icetray.I3Logger.global_logger.set_level(I3LogLevel.LOG_INFO)

usage = "usage: %prog [options]"
parser = ArgumentParser(usage)
parser.add_argument(
    "-i",
    "--infile",
    default="input.i3",
    help="read from infile (.i3{.gz} format)",
)
parser.add_argument(
    "-o",
    "--outfile",
    default="output.i3",
    help="Write output to outfile (.i3{.gz} format)",
)
parser.add_argument("-s", "--selectionfile",default="strings.csv",help="csv file with list of strings to keep in selection")

options = parser.parse_args()
outfile = options.outfile
infile = options.infile

allowed_strings = []
with open(options.selectionfile, 'r') as file:
	reader = csv.reader(file)
	for row in reader:
		allowed_strings=list(map(int,row))

icetray.logging.log_info(f"selected strings: {allowed_strings}")

tray = icetray.I3Tray()
# Load input file
tray.Add("I3Reader", Filename=infile)

# Filter photons, keeping only ModuleKeys with string IDs 1, 2, and 3
tray.Add(FilterPhotonList, 
         PhotonMapKey="I3Photons", 
         AllowedStrings=allowed_strings)

# Write to an output file
tray.Add("I3Writer", Filename=outfile)

tray.Execute()

