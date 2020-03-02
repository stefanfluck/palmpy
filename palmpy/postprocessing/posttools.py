import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

#%%set plotting style
cmap = 'bwr'
plt.style.use('seaborn')
plt.rcParams['xtick.labelsize']='small'
plt.rcParams['xtick.major.size']= 3
plt.rcParams['ytick.labelsize']='small'
plt.rcParams['ytick.major.size']= 3
plt.rcParams['axes.labelsize']='small'
plt.rcParams['figure.figsize'] = 7.2,4.45
plt.rcParams['axes.titlesize'] = 'medium'
plt.rcParams['legend.fontsize'] = 'small'



#%% XZ QUIVER

def plotxz_quiv(filein, fileout, seltime, originz, y, 
                xslice, zslice, plotsize=(7.2,4), cbarspan=[0,5],
                title='Title', cbarlabel='Magnitude', quivdens=10, saveflag=0,
                dpi=300, qual=100, closeafter=False):
    '''
    

    Parameters
    ----------
    filein : TYPE
        DESCRIPTION.
    fileout : TYPE
        DESCRIPTION.
    seltime : TYPE
        DESCRIPTION.
    originz : TYPE
        DESCRIPTION.
    y : TYPE
        DESCRIPTION.
    xslice : TYPE
        DESCRIPTION.
    zslice : TYPE
        DESCRIPTION.
    plotsize : TYPE, optional
        DESCRIPTION. The default is (7.2,4).
    cbarspan : TYPE, optional
        DESCRIPTION. The default is [0,5].
    title : TYPE, optional
        DESCRIPTION. The default is 'Title'.
    cbarlabel : TYPE, optional
        DESCRIPTION. The default is 'Magnitude'.
    quivdens : TYPE, optional
        DESCRIPTION. The default is 10.
    saveflag : TYPE, optional
        DESCRIPTION. The default is 0.
    dpi : TYPE, optional
        DESCRIPTION. The default is 300.
    qual : TYPE, optional
        DESCRIPTION. The default is 100.
    closeafter : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    None.

    '''
    
    cmap='bwr'
    data = xr.open_dataset(filein)
    dz=data.zw.values[1]-data.zw.values[0]
    data.zw.values = data.zw.values+originz
    data.zu.values = data.zu.values+originz
    
    dataw = data.w_xz.sel(y_xz=y, zw=slice(zslice[0], zslice[1]-dz/2)).sel(time=seltime, method='nearest')
    datau = data.u_xz.sel(y_xz=y, zu=slice(zslice[0], zslice[1])).sel(time=seltime, method='nearest')
    
    fig = plt.figure(figsize=plotsize)
    ax=fig.gca(); ax.set_aspect('equal')
    dataw.plot(ax=ax, cmap=cmap, center=cbarspan[0], vmax=cbarspan[1], 
               cbar_kwargs={'shrink':0.7, 'label':cbarlabel})
    ax.quiver(dataw.x.values[1::quivdens], dataw.zw.values[1::quivdens],
              datau.values[1::quivdens, 1::quivdens], dataw.values[1::quivdens, 1::quivdens],
              headlength=3, headaxislength=3, minshaft=2, width=0.002, scale_units='x')
    
    ax.set_title(title)
    ax.set_ylabel('z [m]')
    ax.set_xlabel('x [m]')
    
    if saveflag==1:
        plt.savefig(fileout, dpi=dpi, quality=qual)
        
    plt.show()
    if closeafter==True:
        plt.close()





















