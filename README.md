# GeometrySkimmer
From an input i3 file and a csv file specifying a subset of string IDs:
  * Produces a reduced GCD file
  * Removes I3Photons from Q frames that are on 'missing' strings
  * Deletes now empty Q frames

The notebook and identical python script in the examples/ show a way to visualize the subselection and produce the input csv file

## Usage

```python GeoSkimmer.py -i inputData.i3 -g inputGCD.i3 -o outputData.i3 -t outputGCD.i3 -s stringSelection.csv```

Only the -s option is required. -i -o and -g -t (as pairs), can be used together or independently.
