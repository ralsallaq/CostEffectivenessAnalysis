#!/usr/bin/env python3
import sys, os, time
import numpy as np
import pandas as pd
import argparse


def RunCEA(Mat_Eff_Cost, IDColmnN=0, EffColmnN=6, CostColmnN=5):
    """ runs cost-effectiveness analysis on the given scenarios with IDs in the colmn with number
        IDColmnN according to specified effect in colmn with number EffColmnN and costs in the 
        colmn with number CostColmnN """
    import operator
    ## non-dominated by cost
    NumOfScen = Mat_Eff_Cost.shape[0] #define number of scenarios=number of rows
    # initialize some arrays
    NonDom_Cost=np.zeros(Mat_Eff_Cost.shape,dtype=float)
    NonDom_Cost = Mat_Eff_Cost[Mat_Eff_Cost[:,EffColmnN].argsort()] #sort rows according to sorted values in column no. EffColmnN
    # Here I detect rows of NonDom_Cost with equal effects (different or equal costs) and eliminate those with higher costs""" 
    Eff_Difs = np.diff(NonDom_Cost[:,EffColmnN]) #find difference between consecutive effect values
    Eff_Difs_ind = np.where(Eff_Difs==0.)[0]  # find the indices where diff is zero
    rows_todelete=[]
    for j, rown in enumerate(Eff_Difs_ind):
        if NonDom_Cost[rown+1,CostColmnN]<NonDom_Cost[rown,CostColmnN]:
            rows_todelete.append(rown)
        else:
            rows_todelete.append(rown+1)
    NonDom_Cost = np.delete(NonDom_Cost, rows_todelete,0)

    # Here I keep only scenarios with effects that increase when cost increase
    for k in range(len(NonDom_Cost[:,0])-1):
        upto_ind = (0 if k==0 else range(0,k+1)) # goes up to len(NonDom_Cost[:,0])-2
        x1=NonDom_Cost[upto_ind,CostColmnN]  # previous and index
        x2=NonDom_Cost[k+1,CostColmnN] # next element
        nan_index = np.where(x1>=x2)
        #nan_index = np.where(NonDom_Cost[upto_ind,CostColmnN]>NonDom_Cost[k+1,CostColmnN])
        NonDom_Cost[nan_index,CostColmnN]=np.nan
    # get the scenarios such that when effect increases cost increases ---> ICERs are +ve
    NonDom_Cost = NonDom_Cost[~np.isnan(NonDom_Cost[:,CostColmnN].astype(float)),:]
    
    ## non-dominated by ICER
    newsize=tuple(map(operator.add, NonDom_Cost.shape, (0,3))) #t=map(func,s) applies func to each element in s and returns a new list t
    NonDom_ICER = np.zeros(newsize,dtype=object)
    NonDom_ICER[:,range(NonDom_Cost.shape[1])]=NonDom_Cost
    incrEff_ind = newsize[1]-3
    incrCost_ind = newsize[1]-2
    ICER_ind = newsize[1]-1
    for k in range(1,len(NonDom_Cost[:,0])):
        stepback = 1
        # define the nearest previous ICER to compare againest
        prev_ind = k-stepback
        icer1 = NonDom_ICER[prev_ind,ICER_ind] 
        # calculate current ICER
        IncrEff = NonDom_Cost[k,EffColmnN] - NonDom_Cost[prev_ind,EffColmnN] 
        IncrCost = NonDom_Cost[k,CostColmnN] - NonDom_Cost[prev_ind,CostColmnN]
        NonDom_ICER[k,incrEff_ind] = IncrEff
        NonDom_ICER[k,incrCost_ind] = IncrCost
        if IncrCost==IncrEff==0.0:
            print ("Warning division by zero, looks like there are two identical scenarios with different IDs ---continuing--")
            NonDom_ICER[k,ICER_ind] = IncrCost/IncrEff
        elif IncrEff==0.0:
            print ("Looks like some scenarios add costs but have the same effect, some dominated scenarios should have been removed from the first step!---ignoring the more expensive/demoniated scenarios and continuing --- ")
            NonDom_ICER[k,ICER_ind] = IncrCost/IncrEff
        else:
            NonDom_ICER[k,ICER_ind] = IncrCost/IncrEff

        while IncrCost/IncrEff<icer1:  
             """ compare current icer with all previous ICERs 
                 and do something if they are larger """
             # put larger previous ICER nan
             NonDom_ICER[prev_ind,ICER_ind] = np.nan
             # move one step back
             stepback += 1
             if k-stepback>=0:
                 nearest_ind = range(k-stepback+1) # 0, 1, 2, ..,k-stepback
                 prev_ind=np.where(~np.isnan(NonDom_ICER[nearest_ind,ICER_ind].astype(float)))[0][-1]
             else:
                 break  # break out of while loop
             icer1 = NonDom_ICER[prev_ind,ICER_ind]
             IncrEff = NonDom_Cost[k,EffColmnN] - NonDom_Cost[prev_ind,EffColmnN]
             NonDom_ICER[k,incrEff_ind] = IncrEff
             IncrCost = NonDom_Cost[k,CostColmnN] - NonDom_Cost[prev_ind,CostColmnN]
             NonDom_ICER[k,incrCost_ind] = IncrCost
             NonDom_ICER[k,ICER_ind] = IncrCost/IncrEff
        
    return NonDom_ICER[~np.isnan(NonDom_ICER[:,ICER_ind].astype(float)),:] 


def main(args):
    """
       Invokes the driver function
    """
    input_tsv_file = args.input_tsv
    id_col_name = args.id_col
    effect_col_name = args.effectiveness_col
    cost_col_name = args.cost_col
    df = pd.read_csv(input_tsv_file, sep='\t')
    assert df.columns.isin([id_col_name, effect_col_name, cost_col_name]).sum() == 3, f"Some or all of supplied columns {[id_col_name, effect_col_name, cost_col_name]} do not exist in the input file {df.columns}"
    df.loc[:, effect_col_name] = df[effect_col_name].astype(float)
    df.loc[:, cost_col_name] = df[cost_col_name].astype(float)
    df_np_array = df[[id_col_name, effect_col_name, cost_col_name]].values
    economically_rational_alternatives = RunCEA(df_np_array, IDColmnN=0, EffColmnN=1, CostColmnN=2) 
    df = pd.DataFrame(economically_rational_alternatives, columns=[id_col_name, effect_col_name, cost_col_name, 'delta-effect', 'delta-cost','ICER'], index=range(economically_rational_alternatives.shape[0])) 
    print(f'The economically rational alternatives (efficient frontier) are\n:{df}')
    print('Saving results into Efficient_frontier.tsv')
    df.to_csv('Efficient_frontier.tsv', sep='\t', index=False)
    return 
 
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='get_efficient_frontier.py',
                    description='Conducts CEA and generates the efficient frontier')
                    
    parser.add_argument('-t', '--input_tsv', help='tab-delimited file with header', required=True) 
    parser.add_argument('-i', '--id_col', help='the column name in the TSV file that specifies alternative ids', required=True) 
    parser.add_argument('-e', '--effectiveness_col', help='the column name in the TSV file that specifies effectiveness of alternatives', required=True) 
    parser.add_argument('-c', '--cost_col', help='the column name in the TSV file that specifies costs of alternatives', required=True) 
    args = parser.parse_args()
    print(args)
    main(args)
