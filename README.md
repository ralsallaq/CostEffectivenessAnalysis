# CostEffectiveness
This repository encompasses code that conducts cost-effectiveness analyses on a list of alternative programs or interventions

# Getting started

Start with one of the examples say clinical_programs_single_disease.tsv

```
cat examples/clinical_programs_single_disease.tsv
Program Cost($) Lives-saved
A       100000  10
B       100000  12
C       200000  12
D       200000  15
```

To conduct cost-effectiveness analyses

```
./get_efficient_frontier.py -t examples/clinical_programs_single_disease.tsv -i Program -e Lives-saved -c 'Cost($)'
The economically rational alternatives are
:  Program Lives-saved Cost($) delta-effect delta-cost          ICER
0       B          12  100000            0          0             0
1       D          15  200000            3     100000  33333.333333
```

Note1 here that when the supplied column names contains spaces or special characters (e.g. ({\+>..etc)) use single quotation around them.
Note2 make sure that costs do not have commas that is use 5000 instead of 5,000 in the TSV file
The output of the code gives the economically rational alternatives and their incremental cost-effectiveness ratio (ICER) as well the delta-effect and delta-cost. 
