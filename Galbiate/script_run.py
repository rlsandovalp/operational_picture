# %%
import pandas as pd
import numpy as np
import os
import re

# %%
def create_rain_file(i, atr, duration):
    r = 0.5
    dt = 5
    n = 0.5
    tp = duration[i]*r/60

    chicago_space = np.zeros((int(duration[i]/dt)+1, 3))
    chicago_space[:,0]= np.linspace(0,duration[i],int(duration[i]/dt)+1)

    for j in range(chicago_space.shape[0]):
        if chicago_space[j,0]>=r*duration[i]:
            chicago_space[j,1] = atr[i]*(r*(tp/r)**n+(1-r)*((chicago_space[j,0]/60-tp)/(1-r))**n)
        else:
            chicago_space[j,1] = r*atr[i]*((tp/r)**n-((tp-chicago_space[j,0]/60)/r)**n)

    for j in range(1, chicago_space.shape[0]):
        chicago_space[j,2] = chicago_space[j,1]-chicago_space[j-1,1]

    chicago_final = np.zeros((chicago_space.shape[0],2))
    chicago_final[:,0] = chicago_space[:,0]
    chicago_final[:,1] = chicago_space[:,2]

    veces = chicago_final.shape[0]
    dates = ['07/09/2020']*veces

    time_list, hour, minute = [], 1, 0
    for vez in range(veces):
        time_list.append(f"{hour:02d}:{minute:02d}")
        minute = minute + dt
        if minute == 60:
            hour = hour + 1
            minute = 0

    df = pd.DataFrame(np.transpose([dates, time_list, chicago_final[:,1]]))
    df.to_csv('input/RG_Chicago_10.dat', sep=' ', header=False, index=False)

def read_volume():
    start_string = '  Node Flooding Summary'
    end_string = '  Outfall Loading Summary'
    no_flooding = '  No nodes were flooded.'

    table_data = []
    no_floods = False
    with open('output/Report_stochastic.rpt', 'r') as file:
        line_count = 0

        for line in file:
            line_count += 1
            # Check if we've found the key string
            if start_string in line:
                start_line = line_count
            # Check if we've found the end string
            if no_flooding in line:
                no_floods = True
            if end_string in line:
                end_line = line_count

    if no_floods:
        return 0
    else:
        with open('output/Report_stochastic.rpt', 'r') as file:
            # Iterate through the lines, keeping track of line numbers
            for line_number, line in enumerate(file, start=1):
                if start_line + 10 <= line_number <= end_line - 4:
                    # print(line)
                    input_string = line.strip()
                    row_data = re.split(r'\s+', input_string)
                    table_data.append(row_data)


        table = np.array(table_data)
        volume = np.sum(np.array(table[:, 5], dtype=float))
        return volume

def create_inp_file(subareas, infiltration, conduits, xsections):
    
    with open('input/swmm_stochastic.inp', 'w') as the_file:
        the_file.write('''[TITLE]
;;Project Title/Notes
Galviate

[OPTIONS]
;;Option             Value
FLOW_UNITS           CMS
INFILTRATION         CURVE_NUMBER
FLOW_ROUTING         DYNWAVE
LINK_OFFSETS         DEPTH
MIN_SLOPE            0
ALLOW_PONDING        NO
SKIP_STEADY_STATE    NO

START_DATE           07/09/2020
START_TIME           00:00:00
REPORT_START_DATE    07/09/2020
REPORT_START_TIME    00:00:00
END_DATE             07/09/2020
END_TIME             04:00:00
SWEEP_START          01/01
SWEEP_END            12/31
DRY_DAYS             15
REPORT_STEP          00:01:00
WET_STEP             00:00:05
DRY_STEP             01:00:00
ROUTING_STEP         0:00:10 
RULE_STEP            00:00:00

INERTIAL_DAMPING     PARTIAL
NORMAL_FLOW_LIMITED  FROUDE
FORCE_MAIN_EQUATION  D-W
VARIABLE_STEP        0.75
LENGTHENING_STEP     0
MIN_SURFAREA         1.167
MAX_TRIALS           8
HEAD_TOLERANCE       0.0015
SYS_FLOW_TOL         5
LAT_FLOW_TOL         5
MINIMUM_STEP         0.5
THREADS              1

[FILES]
;;Interfacing Files
SAVE OUTFLOWS ".\output\outflow_stochastic.txt"
SAVE RUNOFF ".\output\\runoffs_stochastic.rof"

[EVAPORATION]
;;Data Source    Parameters
;;-------------- ----------------
CONSTANT         0.0
DRY_ONLY         NO

[RAINGAGES]
;;Name           Format    Interval SCF      Source    
;;-------------- --------- ------ ------ ----------
RG1              VOLUME    0:05     1.0      TIMESERIES Chicago10       
                       
[SUBCATCHMENTS]
;;Name           Rain Gage        Outlet           Area     %Imperv  Width    %Slope   CurbLen  SnowPack        
;;-------------- ---------------- ---------------- -------- -------- -------- -------- -------- ----------------
6287             RG1              1287             0.42     0        77       15.78947368 0                        
6296             RG1              1296             0.23     0        40       56.4516129 0                        
25107            RG1              20107            0.28     0        39       26.31578947 0                        
25108            RG1              20108            0.24     0        27       32.60869565 0                        
25109            RG1              20109            0.48     0        47       30.76923077 0                        
25110            RG1              20110            0.33     0        41       26.31578947 0                        
25117            RG1              20117            0.53     0        56       8.695652174 0                        
25119            RG1              20119            0.19     0        33       36.36363636 0                        
25120            RG1              20120            0.34     0        55       32.25806452 0                        
25121            RG1              20121            0.16     0        41       26.31578947 0                        
25122            RG1              20122            0.39     0        56       27.77777778 0                        
25123            RG1              20123            0.71     0        59       16.66666667 0                        
25124            RG1              20124            0.37     0        45       24.69135802 0                        
25125            RG1              20125            0.28     0        69       35.71428571 0                        
25126            RG1              20126            0.05     0        31       29.41176471 0                        
25127            RG1              20127            0.02     0        30       50       0                        
25129            RG1              20129            0.41     0        76       48.07692308 0                        
25130            RG1              20130            0.19     0        35       49.01960784 0                        
25131            RG1              20131            0.15     0        31       40       0                        
25132            RG1              20132            0.18     0        39       39.53488372 0                        
25133            RG1              20133            0.06     0        14       45.45454545 0                        
25135            RG1              20135            0.18     0        41       25.86206897 0                        
25136            RG1              20136            0.27     0        47       36.17021277 0                        
25977            RG1              20977            0.45     0        107      40.47619048 0                        
27169            RG1              22169            0.49     0        71       26.5625  0                        
28233            RG1              23233            0.89     0        125      9.722222222 0                        

[SUBAREAS]
;;Subcatchment   N-Imperv   N-Perv     S-Imperv   S-Perv     PctZero    RouteTo    PctRouted 
;;-------------- ---------- ---------- ---------- ---------- ---------- ---------- ----------
''')
        the_file.write(subareas.to_string(header=False, index=False))
        the_file.write('''  

[INFILTRATION]
;;Subcatchment   Param1     Param2     Param3     Param4     Param5    
;;-------------- ---------- ---------- ---------- ---------- ----------
''')
        the_file.write(infiltration.to_string(header=False, index=False))
        the_file.write('''

[JUNCTIONS]
;;Name           Elevation  MaxDepth   InitDepth  SurDepth   Aponded   
;;-------------- ---------- ---------- ---------- ---------- ----------
1287             414.91     0.9        0          0          0         
1296             434.21     1.13       0          0          0         
20107            398.75     1.28       0          0          0         
20108            397.59     1.65       0          0          0         
20109            396.72     1.26       0          0          0         
20110            393.96     0.92       0          0          0         
20111            393.42     1.35       0          0          0         
20119            409.9      0.96       0          0          0         
20120            407.8      1.27       0          0          0         
20121            399.87     1.47       0          0          0         
20122            394.5      1.18       0          0          0         
20123            397.63     1.47       0          0          0         
20124            417.42     1.12       0          0          0         
20125            421.37     1.12       0          0          0         
20126            425.9      1.22       0          0          0         
20127            428.01     0.95       0          0          0         
20128            429.21     1.57       0          0          0         
20129            430.41     1.05       0          0          0         
20130            431.71     0.87       0          0          0         
20131            434.15     0.95       0          0          0         
20132            436.01     1.12       0          0          0         
20133            439.03     1.05       0          0          0         
20135            431.05     1.48       0          0          0         
20136            421.76     1.26       0          0          0         
20138            414.37     1.44       0          0          0         
20977            440.4      0.52       0          0          0         
22169            408.29     1.1        0          0          0         
20117            380.85     1.3        0          0          0         
20116            384.44     1.42       0          0          0         
23233            385        0.6        0          0          0         

[OUTFALLS]
;;Name           Elevation  Type       Stage Data       Gated    Route To        
;;-------------- ---------- ---------- ---------------- -------- ----------------
1                377.71     FREE                        NO                       

[CONDUITS]
;;Name           From Node        To Node          Length     Roughness  InOffset   OutOffset  InitFlow   MaxFlow   
;;-------------- ---------------- ---------------- ---------- ---------- ---------- ---------- ---------- ----------''')
        the_file.write(conduits.to_string(header=False, index=False))
        the_file.write('''   

[XSECTIONS]
;;Link           Shape        Geom1            Geom2      Geom3      Geom4      Barrels    Culvert   
;;-------------- ------------ ---------------- ---------- ---------- ---------- ---------- ----------''')
        the_file.write(xsections.to_string(header=False, index=False))
        the_file.write('''

[TIMESERIES]
;;Name           Date       Time       Value     
;;-------------- ---------- ---------- ----------
Chicago10        FILE "input/RG_Chicago_10.dat"

[REPORT]
;;Reporting Options
SUBCATCHMENTS ALL
NODES ALL
LINKS ALL

[TAGS]

[MAP]
DIMENSIONS 527029.454 5070546.248 530427.344 5075351.248
Units      Meters

[COORDINATES]
;;Node           X-Coord            Y-Coord           
;;-------------- ------------------ ------------------
1287             529522.700         5074170.140       
1296             529559.127         5074300.041       
20107            529149.297         5074137.685       
20108            529201.088         5074135.826       
20109            529247.141         5074129.313       
20110            529298.851         5074100.919       
20111            529320.310         5074092.799       
20119            529283.621         5074181.036       
20120            529331.979         5074166.626       
20121            529310.837         5074131.953       
20122            529319.554         5074098.901       
20123            529388.926         5074092.470       
20124            529465.193         5074192.323       
20125            529413.216         5074217.911       
20126            529348.614         5074228.368       
20127            529315.880         5074234.620       
20128            529285.262         5074233.806       
20129            529284.590         5074240.893       
20130            529301.996         5074243.456       
20131            529338.234         5074249.626       
20132            529365.610         5074259.350       
20133            529406.102         5074266.258       
20135            529528.696         5074257.537       
20136            529536.239         5074208.786       
20138            529521.103         5074163.710       
20977            529419.348         5074268.994       
22169            529367.183         5074157.436       
20117            529272.011         5073993.445       
20116            529307.414         5074023.627       
23233            529313.498         5074026.497       
1                529231.834         5073951.164       

[VERTICES]
;;Link           X-Coord            Y-Coord           
;;-------------- ------------------ ------------------

[Polygons]
;;Subcatchment   X-Coord            Y-Coord           
;;-------------- ------------------ ------------------
6287             529512.850         5074231.782       
6287             529534.085         5074238.559       
6287             529541.992         5074211.677       
6287             529527.986         5074165.367       
6287             529491.354         5074175.000       
6287             529462.248         5074187.731       
6287             529471.058         5074207.611       
6287             529472.865         5074242.400       
6287             529481.902         5074241.722       
6287             529492.971         5074232.912       
6296             529552.635         5074295.223       
6296             529548.533         5074297.859       
6296             529494.051         5074332.961       
6296             529499.178         5074339.873       
6296             529514.991         5074346.876       
6296             529531.256         5074353.201       
6296             529536.678         5074355.686       
6296             529545.714         5074365.626       
6296             529553.395         5074345.069       
6296             529558.365         5074319.542       
6296             529560.704         5074303.517       
25107            529162.166         5074131.980       
25107            529153.356         5074129.269       
25107            529147.708         5074138.531       
25107            529131.443         5074192.748       
25107            529178.209         5074221.000       
25107            529175.494         5074132.884       
25108            529206.443         5074226.860       
25108            529200.344         5074131.302       
25108            529175.494         5074132.658       
25108            529178.209         5074221.000       
25109            529252.979         5074236.348       
25109            529247.332         5074128.592       
25109            529200.344         5074131.302       
25109            529206.217         5074226.634       
25109            529212.543         5074232.056       
25110            529319.168         5074098.735       
25110            529306.495         5074098.470       
25110            529296.352         5074098.058       
25110            529278.947         5074109.308       
25110            529247.105         5074129.232       
25110            529250.493         5074182.998       
25110            529283.249         5074180.739       
25110            529280.527         5074141.598       
25110            529311.035         5074131.717       
25117            529227.418         5074102.520       
25117            529307.388         5074023.680       
25117            529271.921         5073992.731       
25117            529193.758         5074067.505       
25119            529285.284         5074213.983       
25119            529283.476         5074181.001       
25119            529250.269         5074183.034       
25119            529252.753         5074236.122       
25119            529284.606         5074240.640       
25119            529285.284         5074234.089       
25120            529332.046         5074166.769       
25120            529283.476         5074180.775       
25120            529285.735         5074233.185       
25120            529315.781         5074234.541       
25120            529347.859         5074227.989       
25121            529310.792         5074131.753       
25121            529280.521         5074141.692       
25121            529283.458         5074180.548       
25121            529331.801         5074166.316       
25122            529379.015         5074114.358       
25122            529354.139         5074099.599       
25122            529319.828         5074098.319       
25122            529311.470         5074131.301       
25122            529332.253         5074166.090       
25122            529396.184         5074150.051       
25123            529509.136         5074169.763       
25123            529514.332         5074168.577       
25123            529529.467         5074165.019       
25123            529524.046         5074148.980       
25123            529501.907         5074146.721       
25123            529470.507         5074150.562       
25123            529439.106         5074115.547       
25123            529389.181         5074092.504       
25123            529378.790         5074114.417       
25123            529416.064         5074190.321       
25123            529431.425         5074183.770       
25123            529436.847         5074200.035       
25124            529471.962         5074227.264       
25124            529471.284         5074208.514       
25124            529462.248         5074187.731       
25124            529412.187         5074212.460       
25124            529418.286         5074242.054       
25124            529414.220         5074267.129       
25124            529453.753         5074277.295       
25124            529458.723         5074243.861       
25124            529472.640         5074241.948       
25125            529414.329         5074267.260       
25125            529418.380         5074241.854       
25125            529412.057         5074212.613       
25125            529396.204         5074218.503       
25125            529347.861         5074224.603       
25125            529347.861         5074253.292       
25125            529365.082         5074258.901       
25126            529348.365         5074227.953       
25126            529315.835         5074234.730       
25126            529314.253         5074244.895       
25126            529336.618         5074248.510       
25126            529347.235         5074253.028       
25127            529316.061         5074234.504       
25127            529285.338         5074234.278       
25127            529284.886         5074240.377       
25127            529314.027         5074244.670       
25129            529253.318         5074236.322       
25129            529212.787         5074232.032       
25129            529231.294         5074287.630       
25129            529292.246         5074296.601       
25129            529302.228         5074243.127       
25130            529327.245         5074302.133       
25130            529337.695         5074250.130       
25130            529302.228         5074243.127       
25130            529292.133         5074296.827       
25130            529308.843         5074297.392       
25131            529337.695         5074250.356       
25131            529327.471         5074302.472       
25131            529339.890         5074305.069       
25131            529358.293         5074302.811       
25131            529366.159         5074259.392       
25132            529365.933         5074258.940       
25132            529358.180         5074302.924       
25132            529363.938         5074302.811       
25132            529394.986         5074310.601       
25132            529406.596         5074265.943       
25133            529406.502         5074266.231       
25133            529394.986         5074310.375       
25133            529407.292         5074312.746       
25133            529419.924         5074268.654       
25135            529513.683         5074296.463       
25135            529515.490         5074303.463       
25135            529517.296         5074310.463       
25135            529520.118         5074316.221       
25135            529552.521         5074295.221       
25135            529561.666         5074304.479       
25135            529562.231         5074295.560       
25135            529529.113         5074256.634       
25135            529500.474         5074276.818       
25135            529509.619         5074284.496       
25136            529528.678         5074256.885       
25136            529531.474         5074247.481       
25136            529533.874         5074238.361       
25136            529512.865         5074231.358       
25136            529493.437         5074233.165       
25136            529482.142         5074241.749       
25136            529458.648         5074243.331       
25136            529454.130         5074277.216       
25136            529478.302         5074279.927       
25136            529500.440         5074276.538       
25977            529461.711         5074320.875       
25977            529481.807         5074317.149       
25977            529493.210         5074332.955       
25977            529520.532         5074316.246       
25977            529509.807         5074284.521       
25977            529501.250         5074276.335       
25977            529476.400         5074280.175       
25977            529454.262         5074276.560       
25977            529419.924         5074268.428       
25977            529407.292         5074312.633       
25977            529436.760         5074318.843       
27169            529436.865         5074199.977       
27169            529431.218         5074183.712       
27169            529415.856         5074190.715       
27169            529395.977         5074150.278       
27169            529332.272         5074166.543       
27169            529347.181         5074225.278       
27169            529395.525         5074218.727       
27169            529411.790         5074212.628       
28233            529378.762         5074114.871       
28233            529383.957         5074103.689       
28233            529389.153         5074092.507       
28233            529378.244         5074049.024       
28233            529307.614         5074023.906       
28233            529227.321         5074102.899       
28233            529247.662         5074128.212       
28233            529276.314         5074111.031       
28233            529296.081         5074098.380       
28233            529319.349         5074098.606       
28233            529354.138         5074099.510       

[SYMBOLS]
;;Gage           X-Coord            Y-Coord           
;;-------------- ------------------ ------------------
RG1              529142.990         5074325.402       


[BACKDROP]
FILE       "G:\My Drive\07 - Operational_Picture\basemap_a.jpeg"
DIMENSIONS 528879.163 5073636.387 529679.162 5074436.386
''')

# %%
conduits_to_modify =   [3117, 3118, 3119, 3120, 3132, 3734]
subareas_to_modify = [25107, 25108, 25109, 25110, 25121, 25122, 28233]

# %%
roughnesses_pipes = [0.09091, 0.014286]
diameters = [0.3, 0.4, 0.5, 0.6]
CN_decreases = [5, 10, 15]


atr_min, atr_max = 30, 55
duration_min, duration_max = 15, 60
roughness_min, roughness_max = 0.01, 0.25
depression_min, depression_max = 0, 10

# %%
n_realizations = 100

atr = np.random.uniform(atr_min, atr_max, n_realizations)
duration = np.random.uniform(duration_min, duration_max, n_realizations)
roughness_soil = np.random.uniform(roughness_min, roughness_max, n_realizations)
depression = np.random.uniform(depression_min, depression_max, n_realizations)

# %%
results = np.zeros((n_realizations, 28))
results[:, 0] = atr
results[:, 1] = duration
results[:, 2] = roughness_soil
results[:, 3] = depression

subareas = pd.read_csv('input/info/subareas.csv', sep =r'\s+', engine='python', header=None).set_index(0)
infiltration = pd.read_csv('input/info/infiltration.csv', sep =r'\s+', engine='python', header=None).set_index(0)
conduits = pd.read_csv('input/info/conduits.csv', sep =r'\s+', engine='python', header=None).set_index(0)
xsections = pd.read_csv('input/info/xsections.csv', sep =r'\s+', engine='python', header=None).set_index(0)

# %%
for i in range(n_realizations):
    print(i)
    create_rain_file(i, atr, duration)
    subareas[2] = roughness_soil[i]
    subareas[4] = depression[i]
    
    runs = 0
    for roughness in roughnesses_pipes:
        for diameter in diameters:
            for CN_decrease in CN_decreases:

                conduits.loc[conduits_to_modify,4] = roughness
                xsections.loc[conduits_to_modify,2] = diameter
                infiltration.loc[subareas_to_modify,1] = infiltration[1][subareas_to_modify]-CN_decrease
                os.remove('input/swmm_stochastic.inp')

                subareas['New_index'] = np.arange(1, len(subareas)+1)
                subareas[0] = subareas.index.values
                subareas = subareas[[0] + [col for col in subareas.columns if col != 0]]
                aa = subareas.set_index('New_index')

                infiltration['New_index'] = np.arange(1, len(infiltration)+1)
                infiltration[0] = infiltration.index.values
                infiltration = infiltration[[0] + [col for col in infiltration.columns if col != 0]]
                bb = infiltration.set_index('New_index')

                conduits['New_index'] = np.arange(1, len(conduits)+1)
                conduits[0] = conduits.index.values
                conduits = conduits[[0] + [col for col in conduits.columns if col != 0]]
                cc = conduits.set_index('New_index')

                xsections['New_index'] = np.arange(1, len(xsections)+1)
                xsections[0] = xsections.index.values
                xsections = xsections[[0] + [col for col in xsections.columns if col != 0]]
                dd = xsections.set_index('New_index')
                create_inp_file(aa, bb, cc, dd)
                os.system('swmm5 input/swmm_stochastic.inp output/Report_stochastic.rpt output/outfile_stochastic.out >> output/verbose.txt')
                volume = read_volume()
                results[i, 4 + runs] = volume
                runs += 1
                # print(volume)

# %%
pd.DataFrame(results).to_csv('output/results_stochastic.csv', index=False, header=False)


