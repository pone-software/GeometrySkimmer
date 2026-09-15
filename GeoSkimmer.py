import h5py
from icecube import icetray, dataio
from icecube.icetray import I3LogLevel
from FilterFrame import FilterFrame
from argparse import ArgumentParser
from NoiseGenerators.DarkNoise import DarkNoise
from NoiseGenerators.K40Noise import K40Noise
from icecube import phys_services
from DOM.PONEDOMLauncher import DOMSimulation
from Trigger.DOMTrigger import DOMTrigger
from Trigger.DetectorTrigger import DetectorTrigger
import csv
import sys

icetray.I3Logger.global_logger.set_level(I3LogLevel.LOG_INFO)

usage = "usage: %prog [options]"
parser = ArgumentParser(usage)
parser.add_argument("-i","--infile",nargs="+", default=None, help="read from one or more input files (.i3{.gz,.zst} format)")
parser.add_argument("-o","--outfile",default=None,help="Write output to outfile (.i3{.gz} format)")
parser.add_argument("-s","--selectionfile",default=None,help="csv file with list of strings to keep in selection")
parser.add_argument("-g","--gcdfile", default=None,help="read in gcdfile (.i3{.gz} format)")
parser.add_argument("-t","--outgcd", default=None,help="filtered gcdfile (.i3{.gz} format)")
parser.add_argument("-r","--randomseed",type=int, default="1", help="seed for random generator")


options = parser.parse_args()
outfile = options.outfile
outgcd = options.outgcd
infile = options.infile
ingcd = options.gcdfile

randomService = phys_services.I3SPRNGRandomService(
    seed=1234567, nstreams=10000, streamnum=options.randomseed
)

allowed_strings = []
allowed_oms = []
with open(options.selectionfile, 'r') as file:
	reader = csv.reader(file)
	rows = list(reader)
	if rows:
		allowed_strings = list(map(int, rows[0]))
	if len(rows) > 1:
		allowed_oms = list(map(int, rows[1]))

icetray.logging.log_info(f"selected strings: {allowed_strings}")
icetray.logging.log_info(f"selected oms: {allowed_oms}")

tray = icetray.I3Tray()

infiles = []
if infile: infiles.extend(infile)
if ingcd: infiles.append(ingcd)

if not infiles:
    print("No input")
    sys.exit(1) 

tray.Add("I3Reader", FilenameList=infiles)

tray.Add(FilterFrame, AllowedStrings=allowed_strings, AllowedOMs=allowed_oms)

tray.AddModule(DarkNoise,
               'AddDarkNoise',
               input_map      = 'Physics_MCPEMap',
               output_map     = 'Noise_Dark',
               random_service = randomService,
               gcd_file       = options.gcdfile
               )

tray.AddModule(K40Noise,
               'AddK40Noise',
               input_map             = 'Physics_MCPEMap',
               output_map            = 'Noise_K40',
               random_service        = randomService,
               gcd_file              = options.gcdfile
               )

tray.AddModule(DOMSimulation,
               'DOMLauncher',
               input_map      = 'Physics_MCPEMap',
               output_map     = 'PMT_Response',
               random_service = randomService,
               min_time_sep   = 0.2, #0.2 ns copied from example settings
               split_doms     = True,
               use_dark       = True,
               dark_map       = 'Noise_Dark',
               use_k40        = True,
               k40_map        = 'Noise_K40'
              )

tray.AddModule(
    DOMTrigger,
    "DOMTrigger",
    trigger_map="PMT_Response",
)

tray.AddModule(
    DetectorTrigger,
    "PONE_Trigger",
    output="_3PMT_2DOM",
    OMPMTCoinc=3,
    FullDetectorCoincidenceN=2,
    CutOnTrigger=False,
    EventLength=10000,
    TriggerTime=2000,
    PulseSeriesIn="PMT_Response",
    PulseSeriesOut="EventPulseSeries",
)

if outfile: tray.Add("I3Writer", Filename=outfile, Streams=[icetray.I3Frame.Simulation, icetray.I3Frame.DAQ])
if outgcd: tray.Add("I3Writer", Filename=outgcd, Streams=[icetray.I3Frame.Geometry, icetray.I3Frame.Calibration, icetray.I3Frame.DetectorStatus])


tray.Execute()
tray.Finish()
