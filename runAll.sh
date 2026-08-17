#Example of a job to be run in a container
TASKID=$1
TMPDIR=$2

if [ "$TASKID" -ge 1000 ]; then
    ZPAD=$(printf "%04d" "$TASKID")
else
    ZPAD=$(printf "%03d" "$TASKID")
fi

BASEDIR='/usr/local/icetray'
MCDIR='/project/6008051/pone_simulation/MC10-000002-nu_mu-2_7-LeptonInjector-PROPOSAL-clsim/'
OUTDIR='/project/6008051/pone_simulation/geometry_subselections/70String_default_geometry/000002/'

export PATH=$BASEDIR/build/bin:$PATH
export LD_LIBRARY_PATH=$BASEDIR/build/lib:$BASEDIR/build/lib/tools:/usr/local/OpenBLAS/:$LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH=$BASEDIR/build/lib:$BASEDIR/build/lib/tools:$DYLD_LIBRARY_PATH
export PYTHONPATH=$BASEDIR/build/lib:/cvmfs/software.pacific-neutrino.org/pone_offline/v1.0/:$PYTHONPATH
export I3_SRC=$BASEDIR
export I3_BUILD=$BASEDIR/build
export I3_TESTDATA=$BASEDIR/build/test-data
export I3_PRODDATA=$BASEDIR/build/prod-data
export PONESRCDIR=/project/6008051/pone_simulation/pone_offline

cp $MCDIR/Photon/cls_${ZPAD}.i3 $TMPDIR/.
python3 GeoSkimmer.py -i $TMPDIR/cls_${ZPAD}.i3 -o $TMPDIR/filt_${ZPAD}.i3.zst -s 70string_default.csv
cp $TMPDIR/filt_${ZPAD}.i3.zst ${OUTDIR}/filtered_data/. 
