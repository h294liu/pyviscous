import numpy as np
import pandas as pd
from   scipy.stats       import multivariate_normal
import matplotlib        as mpl
import matplotlib.pyplot as     plt
import matplotlib.colors as     colors  
from   matplotlib        import gridspec

import sys
sys.path.append('./')
import pyviscous         as vs

def plot_rosenbrock_3d(ofile):
    # Generate gridded sample data
    N = 1000  # number of meshgrid points
    x1 = np.linspace(-2, 2, N)
    x2 = np.linspace(-2, 2, N)

    # Generate meshgrids
    X1, X2 = np.meshgrid(x1, x2)
    Y = 100 * (X2 - X1**2)**2 + (1 - X1)**2  

    # Plot data in 3D mode 
    fig = plt.figure(figsize=(5,4.5))
    ax = fig.add_subplot(1, 1, 1, projection='3d')

    surf = ax.plot_surface(X1, X2, Y, cmap='viridis', edgecolor='none',alpha=0.7) # plot 3D surface.
    fig.colorbar(surf, ax=ax, shrink=0.6, pad=0.01) # Add a color bar which maps values to colors.

    # Other settings
    ax.set_xlabel(r"$X_1$",rotation=80,fontweight='bold',fontsize='small')
    ax.set_ylabel(r"$X_2$",rotation=80,fontweight='bold',fontsize='small')
    ax.set_zlabel(r"$Y$",fontweight='bold',fontsize='small')

    plt.xticks(rotation=80)
    plt.yticks(rotation=80)
    ax.tick_params(axis='x', which='major', pad=-5)
    ax.tick_params(axis='y', which='major', pad=-5)

    ax.view_init(20, 50) 
    ax.scatter(1, 1, 0, s=100, c='k', marker="o", alpha=0.9)
    ax.text(0.5, -0.5, 100, "Global minimum", color='k')
    ax.text(0.5, -0.5, -200, "$(x_1,x_2,y)=(1,1,0)$", color='k')

    fig.canvas.draw()
    fig.tight_layout()

    # # Save figure
    plt.show()
    fig.savefig(ofile)
    plt.close(fig)  
    return 

def plot_data_conversion(x,y,x_norm,y_norm,ux,uy,xIndex,ofile):
    
    ### PLOT ###
    # set figure columns and rows
    ndata   = 3        # three sets of data
    ncols   = ndata*2  # number of columns 
    nrows   = 2        # number of rows

    # set figure width and heigh ratios
    fig = plt.figure(figsize=(8,2.5),constrained_layout=True)
    widths = [4,1,4,1,4,1]
    heights = [1,4]
    spec = fig.add_gridspec(nrows, ncols, width_ratios=widths, height_ratios=heights,
                            left=0.05, right=0.99, bottom=0.05, top=0.95, wspace=0.0, hspace=0.0)
    # plot
    for i in range(ndata):
        if i == 0:
            data_x,data_y = x[:,xIndex],y
            xlabel,ylabel = '${X_1}$','$Y$'
            title = '(a) Input-output data $(x_1, y)$'  
        elif i == 1:
            data_x,data_y = x_norm[:,xIndex],y_norm
            xlabel,ylabel = "${X'_1}$","$Y'$"  
            title = "(b) Normalized data $(x'_1, y')$"  
        elif i == 2:
            data_x,data_y = ux[:,xIndex],uy
            xlabel,ylabel = '${U_{X_1}}$','${U_{Y}}$'
            title = '(c) Marginal CDF data $(u_{x_1}, u_y)$'

        # Create the Axes.  
        ax = fig.add_subplot(spec[1, i*2])
        ax_histx = fig.add_subplot(spec[0, i*2], sharex=ax)
        ax_histy = fig.add_subplot(spec[1, i*2+1], sharey=ax)

        # the scatter plot and histogram plots:
        ax.scatter(data_x, data_y, c="darkblue",s=0.3,alpha=0.8)
        ax_histx.hist(data_x, bins=50, edgecolor = "black", color = 'gray')
        ax_histy.hist(data_y, bins=50, orientation='horizontal', edgecolor = "black", color = 'gray') 

        # labels
        ax_histx.set_axis_off()
        ax_histy.set_axis_off() 
        ax.spines[['right', 'top']].set_visible(False) # Hide the right and top spines

        # title
        ax_histx.set_title(title, fontsize='medium')

        ax.set_xlabel(xlabel, fontsize='small', fontweight='bold',labelpad=0)
        ax.set_ylabel(ylabel, fontsize='small', fontweight='bold',labelpad=0) 
        if i == 3:
            ax.set_ylabel(ylabel, fontsize='small', fontweight='bold',labelpad=-1) 
        ax.tick_params(axis='both', labelsize='small')

    # plt.savefig(os.path.join(outputDir,'data.png'), dpi=150)
    # plt.savefig(os.path.join(outputDir,'data.pdf'))
    plt.show()
    return

def plot_gmm_pdf_cluster(gmm, data, ofile):
    
    '''Plot the GMM (Gaussian mixture model) inverse CDF, PDFs and clusters for given data.
    
    Parameters
    -------
    gmm:     input object. The best fitted Gaussian mixture model (GMM) used by a specific variable group.
    data:    input array. Inverse CDF data (nSample,n_variables).
    ofile:   output figure file path. 
    
    Note
    -------
    This function is valid for the first-order sensitivity estimate. 
    Please adjust for the total-order sensitivity because more dimensions need included in the plot. '''
    
    # Get the GMM information based on the GMCM parameters    
    gmmWeights         = gmm.params.prob          # shape (n_components,)
    gmmMeans           = gmm.params.means         # shape (n_components, n_variables). n_variables = n_feature in sklearn.mixture.GaussianMixture reference.
    gmmCovariances     = gmm.params.covs          # (n_components, n_variables, n_variables) if covariance_type = ‘full’ (by default).    
    gmmNComponents     = gmm.params.n_clusters    # number of components

    pdf_all_cpnts = np.zeros((len(data),gmmNComponents))
    for n_component in range(gmmNComponents):
        mean, cov = gmmMeans[n_component,:],gmmCovariances[n_component,:,:]
        pdf_all_cpnts[:,n_component] = multivariate_normal.pdf(data, mean, cov)
    labels = np.argmax(pdf_all_cpnts, axis=1)
    
    # Calculate the joint pdf value of data
    pdf = gmm.pdf(data)

    # Construct a dataframe with four pieces of information
    frame            = pd.DataFrame()
    frame['zx']      = data[:,0]
    frame['zy']      = data[:,-1]
    frame['cluster'] = labels+1 # cluster starts from one, not zero.
    frame['pdf']     = pdf #pdf_gmcm 

    # Plot 
    ncols   = 3
    nrows   = 1
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols,figsize=(4*ncols,3*nrows))

    for icol in range(ncols):
        if icol == 0:
            title = '(a) ($z_{x_1}$, $z_y$) data in GMM'
            counts, xedges, yedges, im = ax[icol].hist2d(frame["zx"], frame["zy"],cmin=1,
                                                    bins=100,cmap='viridis',density=False)
            cbar = fig.colorbar(im, ax=ax[icol])
            cbar.ax.set_title('Count',fontsize='medium',style='italic')    

        elif icol == 1:
            title = '(b) ($z_{x_1}$, $z_y$) PDF in GMM' 
            scatter = ax[icol].scatter(frame["zx"], frame["zy"], c=frame["pdf"], 
                                       s=1,cmap="viridis",alpha=0.8)

            cbar = plt.colorbar(scatter, ax=ax[icol])
            cbar.ax.set_title('PDF',fontsize='medium',style='italic')

        if icol == 2:
            title = '(c) ($z_{x_1}$, $z_y$) cluster in GMM' 
            scatter = ax[icol].scatter(frame["zx"], frame["zy"], c=frame["cluster"], s=1,cmap="jet",alpha=0.8)
            
            if gmmNComponents<=4:
                legend = ax[icol].legend(*scatter.legend_elements(),ncol=1,loc="best", title="Cluster",fontsize='small')
            else:
                ticks = np.arange(1.5,gmmNComponents+1.5,1) 
                boundaries = np.arange(1,gmmNComponents+1+1,1) 
                cbar = plt.colorbar(scatter, ax=ax[icol], spacing='proportional', 
                                    ticks=ticks, boundaries=boundaries, format='%1i')
                cbar.ax.set_yticklabels(np.arange(1,gmmNComponents+1,1))
                cbar.ax.set_title('Cluster',fontsize='medium',style='italic')    

        ax[icol].set_title(title)#,fontsize='small')
        ax[icol].set_xlabel('$Z_{X_1}$',labelpad=0)
        ax[icol].set_ylabel('$Z_Y$',labelpad=0)

    # Apply the same xlim and ylim for all subplots.
    plt.setp(ax, xlim=ax[0].get_xlim())
    plt.setp(ax, ylim=ax[0].get_ylim())

    plt.tight_layout()
    plt.savefig(ofile, dpi=150)
    plt.show()
    
    return


def plot_gmm_counter(gmm, z, xIndex, ofile):
    ###############################################################################
    #  Compute GMM PDF and each component PDF at mesh grid points

    # Get GMM weights, means, and covariances.
    gmmWeights         = gmm.params.prob          # shape (n_components,)
    gmmMeans           = gmm.params.means         # shape (n_components, n_variables). n_variables = n_feature in sklearn.mixture.GaussianMixture reference.
    gmmCovariances     = gmm.params.covs          # (n_components, n_variables, n_variables) if covariance_type = ‘full’ (by default).    
    gmmNComponents     = gmm.params.n_clusters    # number of components

    # (1) Create mesh grid on (zx1,zy) dimensions for contour plot
    N                  = 1000   # meshgrid points used in uniform sampling to create mesh grid
    zx_2cpnt,zy_2cpnt  = z[:,xIndex], z[:,-1]
    zx_min, zx_max     = np.min(zx_2cpnt),np.max(zx_2cpnt)
    zy_min, zy_max     = np.min(zy_2cpnt),np.max(zy_2cpnt)
    zx_uniform_samples = np.linspace(zx_min, zx_max, N)  # uniform samples in zx space [-3, 3] given the range of the standard normal distribution.
    zy_uniform_samples = np.linspace(zy_min, zy_max, N)  # uniform samples in zy space [-3, 3]. 

    zx_uniform_samples = zx_uniform_samples.reshape(-1,1) # reshape into (N,1)
    zy_uniform_samples = zy_uniform_samples.reshape(-1,1) # reshape into (N,1)

    X, Y = np.meshgrid(zx_uniform_samples, zy_uniform_samples)  # create mesh over N-N grids

    # (2) Loop to calculate GMM PDF and invidivual component PDF per mesh grid point
    jointPDF = np.zeros((N,N))                    # GMM PDF, dimension is (x,y).
    jointPDFCpnt = np.zeros((N,N,gmmNComponents)) # Individual component PDF, dimension is (x,y,component).

    # Loop zx 
    for i in range(N):  
        xx, yy = zx_uniform_samples[i],zy_uniform_samples

        # Given xx, handle all the N samples of zy using vector operations   
        # Combine x and y into a multi-variate data array. Shape (N, n_variables).
        multivariateData = np.concatenate((np.ones((N,1))*xx,yy), axis=1)  
        # Calculate its joint probability in GMM.  
        jointPDF[:,i]    = gmm.pdf(multivariateData)  # pdf, taking z as input.

        # Calculate its individual component's PDF.
        for iComponent in range(gmmNComponents):
            jointPDFCpnt[:,i,iComponent] = multivariate_normal.pdf(multivariateData, 
                                                                   mean=gmmMeans[iComponent,:],
                                                                   cov=gmmCovariances[iComponent,:,:]) 

    ###############################################################################
    # Plot GMM PDF and invidivual componnet PDF in contours
    fs        = 'medium'  # plot font size
    ncols     = 3         # three subplots per row
    nrows     = int(np.ceil((gmmNComponents+1)/ncols)) # number of rows given ncols and gmmNComponents
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols,figsize=(4*ncols,3*nrows))

    # If the plot has only one row.
    if nrows==1: 
        for icol in range(ncols):
            count = icol

            if count <= (gmmNComponents):
                if count == gmmNComponents:
                    im = axes[icol].contour(X, Y, jointPDF, alpha=0.8,levels=100,cmap='viridis')
                    axes[icol].set_title('Gaussian mixture model\n(GMM)')
                else:
                    iComponent = count
                    im = axes[icol].contour(X, Y, jointPDFCpnt[:,:,iComponent], alpha=0.8,levels=100,cmap='viridis')                
                    axes[icol].set_title('Gaussian component %d\n(weight = %.2f)'%(iComponent+1, gmmWeights[iComponent]))

                # Set colorbar and tick label
                kwargs = {'format': '%.1f'}
                cbar = plt.colorbar(im, ax=axes[icol], **kwargs)
                cbar.ax.set_title('PDF',fontsize=fs, style='italic')    

                axes[icol].set_xlabel(r"$Z_{x_1}$")
                axes[icol].set_ylabel(r"$Z_y$")
            else:
                axes[icol].axis('off')

    # If the plot has more than one rows.
    elif nrows>1: 
        for irow in range(nrows):
            for icol in range(ncols):
                count = irow*ncols + icol 

                if count <= (gmmNComponents):
                    if count == gmmNComponents:
                        im = axes[irow,icol].contour(X, Y, jointPDF, alpha=0.8,levels=100,cmap='viridis')
                        axes[irow,icol].set_title('Gaussian mixture model\n(GMM)')
                    else:
                        iComponent = count
                        im = axes[irow,icol].contour(X, Y, jointPDFCpnt[:,:,iComponent], alpha=0.8,levels=100,cmap='viridis')                
                        axes[irow,icol].set_title('Gaussian component %d\n(weight = %.2f)'%(iComponent+1, gmmWeights[iComponent]))

                    # Set colorbar and tick label
                    kwargs = {'format': '%.1f'}
                    cbar = plt.colorbar(im, ax=axes[irow,icol], **kwargs)
                    cbar.ax.set_title('PDF',fontsize=fs, style='italic')

                    axes[irow,icol].set_xlabel(r"$z_{X_%d}$"%(xIndex+1),fontsize=fs)
                    axes[irow,icol].set_ylabel(r"$z_Y$",fontsize=fs)
                else:
                    axes[irow,icol].axis('off')

    plt.tight_layout()
    # plt.savefig(os.path.join(outputDir,'gmm_2cpnt_contour.png'), dpi=150)
    plt.show() 
    return

def plot_gmm_marginal_dists(u, gmm, xIndex, ofile):
    '''
    u: CDF data
    gmm: fitted GMM
    ofile: output file'''
    
    # Approximates the inverse cdf of the input given the GMM parameters
    z = vs.gmm_marginal_ppf(u, gmm.params)  

    # Get GMM weights, means, and covariances.
    gmmWeights         = gmm.params.prob        # shape (n_components,)
    gmmMeans           = gmm.params.means       # shape (n_components, n_variables). n_variables = n_feature in sklearn.mixture.GaussianMixture reference.
    gmmCovariances     = gmm.params.covs        # (n_components, n_variables, n_variables) if covariance_type = ‘full’ (by default).    
    gmmNComponents     = gmm.params.n_clusters  # number of components

    # Get each z data point's GMM clustering (label). 
    # Which cluster a data point belongs to depends on which component it has the highest PDF.
    pdf_all_cpnts = np.zeros((len(z),gmmNComponents))
    for n_component in range(gmmNComponents):
        mean, cov = gmmMeans[n_component,:],gmmCovariances[n_component,:,:]
        pdf_all_cpnts[:,n_component] = multivariate_normal.pdf(z[:,[0,-1]], mean, cov)
    labels = np.argmax(pdf_all_cpnts, axis=1)
    # print(np.unique(labels, return_counts=True))
    
    # Plot 
    ncols   = 2
    nrows   = 1
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols)#,figsize=(4*ncols,3gmmNComponents*nrows))

    col = (np.arange(gmmNComponents))/(gmmNComponents)
    cmap = mpl.colormaps['jet'] # 'viridis'

    for icol in range(ncols):
        if icol == 0:
            title = '(a) $z_{x_%d}$ in GMCM marginal distributions'%(xIndex+1)
            xlabel,ylabel='$z_{x_%d}$'%(xIndex+1),'Count'
            # loop each component and plot
            for iComponent in range(gmmNComponents):
                ax[icol].hist(z[labels==iComponent,0], bins=20, color=cmap(col[iComponent]),
                              edgecolor = 'black', alpha=0.5,
                              label='Cpnt%d (mean=%.2f,var=%.2f,weight=%.2f)'%(iComponent+1, gmmMeans[iComponent,0],
                                                                            gmmCovariances[iComponent,0,0], gmmWeights[iComponent]))

        elif icol == 1:
            title = '(b) $z_{y}$ in GMCM marginal distributions'
            xlabel,ylabel='$z_{y}$','Count'
            # loop each component and plot
            for iComponent in range(gmmNComponents):
                ax[icol].hist(z[labels==iComponent,-1], bins=20, color=cmap(col[iComponent]),
                              edgecolor = 'black', alpha=0.5,
                              label='Cpnt%d (mean=%.2f,var=%.2f,weight=%.2f)'%(iComponent+1, gmmMeans[iComponent,-1],
                                                                            gmmCovariances[iComponent,-1,-1], gmmWeights[iComponent]))

        ax[icol].set_title(title,fontsize='small')
        ax[icol].set_xlabel(xlabel,fontsize='small')#,labelpad=0)
        ax[icol].set_ylabel(ylabel,fontsize='small')#,labelpad=-5)
        ax[icol].tick_params(axis='both', labelsize='small')

        # Put a legend below current axis
        ax[icol].legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), fancybox=False, shadow=False, ncol=1,fontsize='small')

    plt.tight_layout()
    plt.savefig(ofile, dpi=150)
    plt.show()
    return

def plot_gmm_mean_cov(gmm, sensType, xIndex, ofile):
    
    '''Plot the mean and covariance estiamtes for each GMM component.
    
    Parameters
    -------
    gmm:         input, object. The Gaussian mixture model (GMM).
    sensType:    input, str. Type of Sensitivity index calculation. Two options: 'first', 'total'.
    xIndex:      input, int. The evaluated input variable index, starting from zero.   
    ofile:       output, figure file path. '''

    # Get the GMM information based on the GMCM parameters    
    gmmWeights         = gmm.params.prob          # shape (n_components,)
    gmmMeans           = gmm.params.means         # shape (n_components, n_variables). n_variables = n_feature in sklearn.mixture.GaussianMixture reference.
    gmmCovariances     = gmm.params.covs          # (n_components, n_variables, n_variables) if covariance_type = ‘full’ (by default).    
    gmmNComponents     = gmm.params.n_clusters    # number of components
    
    (n_components, n_variables) = np.shape(gmmMeans) # number of GMM components and included variables (including x and x).
    cov_max = np.max(np.abs(gmmCovariances))      # max of the absolute covariance values, use for plot only.

    # Define xticklabels depending on xIndex and sensType    
    if sensType == 'first':       
        xticklabels = [r'${Z_{x_{%d}}}$'%(xIndex+1)] # Create Zx ticks
        xticklabels.append(r'${Z_{y}}$')             # Append Zy tick

    elif sensType == 'total': 
        xticklabels = [r'${Z_{x_{%d}}}$'%(ii+1) for ii in np.arange(n_variables)]  # Create a list of all Zx variable names        
        xticklabels.pop(xIndex)           # Drop xIndex corresponding variable
        xticklabels.append(r'${Z_{y}}$')  # Append Zy tick

    # Plot
    fs      ='small'                                                                # text fontsize
    markers = ['o', 'v', 's', '*', '^', 'D', 'p', '>', 'h', 'H', '<', 'd', 'P', 'X'] # a list of markers for Gaussian mean plot
    axes    = []                                                                     # collect a list of axes to insert the colorbar

    # Create a figure
    ncol = 3
    nrow = 1+int(np.ceil(gmmNComponents/ncol))
    fig  = plt.figure(figsize=(2*ncol,2*nrow), constrained_layout=True) 

    # Divide figure into grids
    heights = [1]
    for i in np.arange(1,nrow):
        heights.append(1.1)
    gs = gridspec.GridSpec(nrows=nrow, ncols=ncol, figure=fig, height_ratios=heights)

    # Plot Gaussian mean
    iRow = 0            
    ax = fig.add_subplot(gs[iRow, :])
    for i in range(gmmNComponents):
        ax.scatter(range(1,1+n_variables),gmmMeans[i,:],label='Cpnt '+str(i+1), alpha=0.7, marker=markers[i%len(markers)])

    ax.set_xticks(range(1,1+n_variables))
    ax.set_xticklabels(xticklabels, fontsize=fs)
    ax.set_ylabel('Mean', fontsize=fs)

    ax.tick_params(axis='x', labelsize=fs)
    ax.tick_params(axis='y', labelsize=fs)
    ax.legend(loc='best', ncol=3, fontsize='small',framealpha=0.5)  
    ax.set_title('(a) Means of all Cpnts', fontsize=fs)

    # Plot Gaussian covariance
    for i in range(gmmNComponents):
        iRow      = i//ncol + 1
        iCol      = i%ncol
        ax        = fig.add_subplot(gs[iRow, iCol])

        vmin,vmax = (-1)*cov_max, cov_max
        norm      = colors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
        aa        = ax.imshow(gmmCovariances[i,:,:],cmap='bwr', norm=norm)

        ax.set_xticks(range(n_variables))
        ax.set_xticklabels(xticklabels, fontsize=fs)

        ax.set_yticks(range(n_variables))
        ax.set_yticklabels(xticklabels, fontsize=fs)
        ax.set_title('(%s) Covariance of Cpnt %d'%(chr(ord('b')+i), (i+1)), fontsize=fs)

        # Colorbar setup
        axes.append(ax)
        if (i) == (gmmNComponents-1):
            cbar = fig.colorbar(aa, ax=axes, pad=0.0, shrink=0.5, location='bottom') 
            cbar.ax.set_title('Covariance',fontsize=fs,style='italic')
            cbar.ax.tick_params(labelsize=fs)    

    plt.savefig(ofile,dpi=150)
    plt.show()    
    return