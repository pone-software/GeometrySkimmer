from icecube import icetray, dataio
from icecube.icetray import I3LogLevel
from FilterFrame import FilterFrame
from argparse import ArgumentParser
import csv

icetray.I3Logger.global_logger.set_level(I3LogLevel.LOG_INFO)

usage = "usage: %prog [options]"
parser = ArgumentParser(usage)
parser.add_argument("-i","--infile",default="input.i3",  help="read from infile (.i3{.gz} format)")
parser.add_argument("-o","--outfile",default="output.i3",help="Write output to outfile (.i3{.gz} format)")
parser.add_argument("-s","--selectionfile",default="strings.csv",help="csv file with list of strings to keep in selection")
parser.add_argument("-g","--gcdfile", default=None,help="read in gcdfile (.i3{.gz} format)")
parser.add_argument("-t","--outgcd", default=None,help="filtered gcdfile (.i3{.gz} format)")


options = parser.parse_args()
outfile = options.outfile
outgcd = options.outgcd
infile = options.infile
ingcd = options.gcdfile

allowed_strings = []
with open(options.selectionfile, 'r') as file:
	reader = csv.reader(file)
	for row in reader:
		allowed_strings=list(map(int,row))

icetray.logging.log_info(f"selected strings: {allowed_strings}")

tray = icetray.I3Tray()

infiles=[infile]
if ingcd: infiles.append(ingcd)

tray.Add("I3Reader", FilenameList=infiles)

tray.Add(FilterFrame, AllowedStrings=allowed_strings)

tray.Add("I3Writer", Filename=outfile, Streams=[icetray.I3Frame.DAQ])
if outgcd: tray.Add("I3Writer", Filename=outgcd, Streams=[icetray.I3Frame.Geometry, icetray.I3Frame.Calibration, icetray.I3Frame.DetectorStatus])


tray.Execute()
tray.Finish()
