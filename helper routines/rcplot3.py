#%% plotter run_control file
import matplotlib.pyplot as plt
import pandas as pd
import sys


#%%
#rcfile = str(input('insert relative path to the tmp/<casename>.XXXX/RUN_CONTROL file you want to plot: '))
rcfile = str(sys.argv[1])
#%%


with open(rcfile) as f:
    f = f.readlines()

outstart = 0

i = 0
for line in f:
    if "RUN" in line:
        outstart=i
    else:
        i += 1

f = f[outstart+2:] #outstart+10

colnames = ['run','iter','time','dt','umax','vmax','wmax',
            'us','ws','thetas','zi','energ','distenerg','divold',
            'divnew','umaxk','umaxj','umaxi','vmaxk','vmaxj','vmaxi',
            'wmaxk','wmaxj','wmaxi','advecx','advexj','mgcyc']
i = 0
list = []
while i < len(f)-1:
    for line in f:
        list.append(line.split())
        i+=1


df = pd.DataFrame(list)
df.columns = colnames
df = df.set_index(['iter'])

#df.dt = df.dt.str.rstrip('A')
df_obj = df.select_dtypes(['object'])
df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip('AD'))


df[['run','dt','umax','vmax','wmax',
    'us','ws','thetas','zi','energ','distenerg','divold',
    'divnew','umaxk','umaxj','umaxi','vmaxk','vmaxj','vmaxi',
    'wmaxk','wmaxj','wmaxi','advecx','advexj','mgcyc']] = df[['run','dt','umax','vmax','wmax',
    'us','ws','thetas','zi','energ','distenerg','divold',
    'divnew','umaxk','umaxj','umaxi','vmaxk','vmaxj','vmaxi',
    'wmaxk','wmaxj','wmaxi','advecx','advexj','mgcyc']].astype(float)
df['time'] = pd.to_timedelta(df.time)

plt.style.use('default')
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(12,6))
df.dt.plot(ax=axes[0,0], color='red'); axes[0,0].set_title('dt', weight='bold'); axes[0,0].grid()
df[['divold','divnew']].plot(ax=axes[0,1], color=['red','blue']); axes[0,1].set_title('divold/new', weight='bold'); axes[0,1].grid(); axes[0,1].set_ylim([0,1e-3])
df[['umax','vmax']].plot(ax=axes[1,0], color=['red','blue']); axes[1,0].set_title('umax, vmax', weight='bold'); axes[1,0].grid()
df.wmax.plot(ax=axes[1,1], color='red'); axes[1,1].set_title('wmax', weight='bold'); axes[1,1].grid()
df[['energ','distenerg']].plot(ax=axes[0,2], color=['red','blue']); axes[0,2].set_title('E', weight='bold'); axes[0,2].grid()
df.us.plot(ax=axes[1,2], color='red'); axes[1,2].set_title('us', weight='bold'); axes[1,2].grid()

plt.tight_layout()
plt.show()
