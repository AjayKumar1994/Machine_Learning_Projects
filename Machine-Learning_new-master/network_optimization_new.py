# -*- coding: utf-8 -*-
"""
Spyder Editor
created by Joseph Roy
This is a temporary script file.
"""
def network():
    import pandas as pd
    import string
    import numpy as np
    import warnings
    
    A_in = pd.read_excel("Demo 2 - Open Solver.xlsx", sheet_name = "Inputs",\
                             header=[4])
    B_in = pd.read_excel("Demo 2 - Open Solver.xlsx", sheet_name = "As-Is")
    C_in = pd.read_excel("Demo 2 - Open Solver.xlsx", sheet_name = "To Be",\
                             header=[10])
    D_in =  pd.read_excel("Demo 2 - Open Solver.xlsx", sheet_name = "Results")
    
    C_in=C_in.drop(C_in.columns[0],axis=1)
    C_in=C_in.drop(C_in.columns[19:],axis=1) 
    C_in.rename(columns={'Dist Const':"Dist_Const"},inplace=True)
    #print(C_in)
    
    import pulp as p
    
        # Create a LP Minimization problem
    Lp_prob = p.LpProblem('Problem', p.LpMaximize)
    var_names = ['x' + str(i+1) for i in range(len(C_in))]
    var_names_series = pd.Series(var_names)
    
    #mapping variable in C_in
    C_in["variables"] = var_names_series 
   
    x_cont = [p.LpVariable(i, lowBound=0, cat="Continuous") for i in var_names]
    
        #print(type(x_cont[1]))
    for i in range(len(C_in)):
           
            exec('x'+ str(i+1)  + " = " + "p.LpVariable(" + '"' + var_names[i] + '"' +  "," +  "lowBound=0)")
            #print('x'+ str(i+1)  + " = " + "p.LpVariable(" + '"' + var_names[i] + '"' +  "," +  "lowBound=0)")
            #exec('x'+ str(i+1)  + " = " + "p.LpVariable(" + '"' + var_names[i] + '"' + ")")
            #print('x'+ str(i+1) + " = " + "p.LpVariable(" + '"' + var_names[i] + '"' + ")")
            
            
    #Objective Function
    obj = ""
    for i in range(len(C_in)):
        if(i==0):
            
    #        obj = "(" +"x" + str(i+1) + "*" + str(C_in['Cont / MT'][i])+")"
             obj = "(" +"x" + str(i+1) + "*" + str(C_in['Price'][i] - (C_in['Cost'][i] +  C_in['Load Hdl'][i]+C_in['Pri Fr'][i]+C_in['Sec Fr'][i]+C_in ['Handling'][i]))+")"
            
        else:
            obj = obj + "+" + "(" + "x" + str(i+1) + "*" + str(C_in['Price'][i] - (C_in['Cost'][i] +  C_in['Load Hdl'][i]+C_in['Pri Fr'][i]+C_in['Sec Fr'][i]+C_in ['Handling'][i]))+")"
                
            
        
    #for i in C_in.index:
        #obj = obj + C_in.loc[i,'variables'] + "*" + str(C_in.loc[i,'Cont / MT']) + '+'
        
        
    #obj = obj[:-1]
    #print(obj)
        # import the library pulp as p
    
    # Objective Function
    Lp_prob += eval(obj)
    
    
    #changed all constraints to point to specific variable

    k = C_in.loc[C_in.Source == 'P1']
    
    # Supply Constraints 1
    
    const1 = ""
   
    for i in k.index:
        
        
        const1 =    const1 + k.loc[i,'variables'] + '+'
        
    
    const1 = const1[:-1]
    #print(const1)
    #Lp_prob += '0'<= const1 <= '2000'          

    exec("Lp_prob += "'0''<=' + "(" + const1 + ")"+ '<=' '2000')
    #print(("Lp_prob += "'0''<=' + "(" + const1 + ")"+ '<=' '2000'))
    
    # Supply Constraints 2
    
    #C_in.loc[C_in.Source == 'P1']
    k1 = C_in.loc[C_in.Source == 'P2']
#    print(k1)
    
    
    const2 = ""
    
    for i in k1.index:
        const2 =    const2 + k1.loc[i,'variables'] + '+'
        
        
            
            
    
    const2 = const2[:-1]
    #print(const2)
    #exec("Lp_prob += " + "(" + const2 + ")"+ '>=' '0')    
    exec("Lp_prob += "'0''<=' + "(" + const2 + ")"+ '<=' '2000')
    
    
    # Supply Constraints 2
    
    #used destination column instead of godown

    #C_in.loc[C_in.Source == 'P1']
    k2 = C_in.loc[C_in.Destination == 'C1']
  
        
    
    # Demand Constraints
    const11 = ""
    
    for i in k2.index:
        const11 =    const11 + k2.loc[i,'variables'] + '+'
        
            
            
    
    
    const11 = const11[:-1]
   
    #exec("Lp_prob += " + "(" + const11 + ")"+ '>=' '0')    
    exec("Lp_prob += "'0''<=' + "(" + const11 + ")"+ '<=' '200')
    
    
    k3 = C_in.loc[C_in.Destination == 'C2']
    #print(k2)
    
    
    # Demand Constraints
    const22 = ""
    
    for i in k3.index:
        const22 =    const22 + k3.loc[i,'variables'] + '+'
        
        
            
            
    
    
    const22=const22[:-1]
    #exec("Lp_prob += " + "(" + const22 + ")"+ '>=' '0')    
    exec("Lp_prob += "'0''<=' + "(" + const22 + ")"+ '<=' '150')
    
    k4 = C_in.loc[C_in.Destination == 'C3']
    #print(k2)
    
    const33 = ""
    
    for i in k4.index:
        const33 =    const33 + k4.loc[i,'variables'] + '+'
        
        
            
            
    
    
    const33=const33[:-1]
    #exec("Lp_prob += " + "(" + const33 + ")"+ '>=' '0')    
    exec("Lp_prob += "'0''<=' + "(" + const33 + ")"+ '<=' '200')
    
    k5 = C_in.loc[C_in.Destination == 'C4']
    
    const44 = ""
    
    for i in k5.index:
        const44 =    const44 + k5.loc[i,'variables'] + '+'
        
        
            
            
    
    
    const44 = const44[:-1]
    #exec("Lp_prob += " + "(" + const44 + ")"+ '>=' '0')    
    exec("Lp_prob += "'0''<=' + "(" + const44 + ")"+ '<=' '300')
    
    k6 = C_in.loc[C_in.Destination == 'C5']
    
    const55 = ""
    
    for i in k6.index:
        const55 =    const55 + k6.loc[i,'variables'] + '+'
        
        
            
            
    
    
    const55 = const55[:-1]
    #exec("Lp_prob += " + "(" + const55 + ")"+ '>=' '0')    
    exec("Lp_prob += "'0''<=' + "(" + const55 + ")"+ '<=' '450')
    
    k7 = C_in.loc[C_in.Destination == 'C6']
    
    const77 = ""
    
    for i in k7.index:
        const77 =    const77 + k7.loc[i,'variables'] + '+'
        
        
            
            
    
    
    const77 = const77[:-1]
    #exec("Lp_prob += " + "(" + const77 + ")"+ '>=' '0')    
    exec("Lp_prob += "'0''<=' + "(" + const77 + ")"+ '<=' '200')
    
    k8 = C_in.loc[C_in.Destination == 'C7']
    
    const88 = ""
    
    for i in k8.index:
        const88 =    const88 + k8.loc[i,'variables'] + '+'
        
        
            
            
    
    
    const88 = const88[:-1]
    
    #exec("Lp_prob += " + "(" + const88 + ")"+ '>=' '0')    
    exec("Lp_prob += "'0''<=' + "(" + const88 + ")"+ '<=' '350')
    
    k9 = C_in.loc[C_in.Destination == 'C8']
    
    const99 = ""
    
    for i in k9.index:
        const99 =    const99 + k9.loc[i,'variables'] + '+'
        
        
            
            
    
    
    const99 = const99[:-1]
    #exec("Lp_prob += " + "(" + const99 + ")"+ '>=' '0')    
    exec("Lp_prob += "'0''<=' + "(" + const99 + ")"+ '<=' '550')
    
    k10 = C_in.loc[C_in.Destination == 'C9']
    
    const100 = ""
    
    for i in k10.index:
        const100 =    const100 + k10.loc[i,'variables'] + '+'
        
        
            
            
    
    
    const100 = const100[:-1]
    
    
    #exec("Lp_prob += " + "(" + const100 + ")"+ '>=' '0')    
    exec("Lp_prob += "'0''<=' + "(" + const100 + ")"+ '<=' '500')
    
    k11 = C_in.loc[C_in.Destination == 'C10']
    
    const110 = ""
    
    for i in k11.index:
        const110 =    const110 + k11.loc[i,'variables'] + '+'
        
        
            
            
    
    
    const110 = const110[:-1]
    #exec("Lp_prob += " + "(" + const110 + ")"+ '>=' '0')    
    exec("Lp_prob += "'0''<=' + "(" + const110 + ")"+ '<=' '200')


    #adding distance const

    k12 = C_in.loc[C_in.Dist_Const == 1]
    
    const120 = ""
    
    for i in k12.index:
        const120 =    const120 + k12.loc[i,'variables'] + '+'
        
        
            
            
    
    
    const120 = const120[:-1]
    #exec("Lp_prob += " + "(" + const110 + ")"+ '>=' '0')    
    exec("Lp_prob += ""(" + const120 + ")"+ '==' '0')
    
    #print(Lp_prob)
    status = Lp_prob.solve()  # Solver
    #print(p.LpStatus[status])  # The solution status
    
    # Printing the final solution
    dfresult = pd.DataFrame(np.zeros([1, len(C_in)]))
    #print(dfresult)
    
    for i in range(len(C_in)):
        dfresult.iloc[0, i] = p.value(eval(var_names[i]))
    
    
    #print(dfresult)
    #dfresult.to_csv('pulp2.csv')
#    print(Lp_prob.objective)
    
    df_var = pd.DataFrame(var_names)
    #print(df_var)
    w = dfresult.T
    df_new = pd.concat([df_var, w,C_in["Destination"]],axis=1)

    df_new.columns=[["Variables","Allocation","Destination"]]
    #df_new["Destination"] = df_new["Destination"].astype('category')

    #print(df_new["Destination"].unique())
    
    #print(p.value(Lp_prob.objective))

    #added godown cost value to be subtracted from final result
    
    print("The optimized cost is predicted as" ,"₹",round((p.value(Lp_prob.objective)/100000)-0.93,2))
    #print(p.value(i) for i in var_names)
    #df_new.set_index('Destination',inplace=True)
    #print(df_new.dtypes)
    #print(df_new.dtypes)
    return df_new

network()
    
    






