import numpy as np # for numerical calculations such as histogramming
import matplotlib.pyplot as plt # for plotting
from matplotlib.ticker import AutoMinorLocator # for minor ticks
import uproot # for reading .root files
import awkward as ak # to represent nested data in columnar format
import vector # for 4-momentum calculations
import time
import os
import requests
from tqdm import tqdm

from data_loader import *
from selection import *

weight_variables = ['xsec', 'mcWeight', 'ScaleFactor_PILEUP', 'ScaleFactor_FTAG', 'ScaleFactor_JVT', 'filteff', 'kfac', 'sum_of_weights']

fraction = 1
# Define empty dictionary to hold awkward arrays
all_data = {}

# Ensure cache directory exists
os.makedirs('./cache', exist_ok=True)

# Loop over samples
for s in samples:
    # Print which sample is being processed
    print('Processing '+s+' samples')

    # Define empty list to hold data for each sample
    frames = []

    # Loop over each file
    for val in samples[s]['list'][0:2]:

        url = val # file name / URL to open
        filename = url.split('/')[-1]
        local_path = f'./cache/{filename}'
        temp_path = f'./cache/{filename}.tmp'
        
        # Download logic from read_data.py
        if not os.path.exists(local_path):
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                with open(temp_path, 'wb') as f:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"  Downloading: {filename}", leave=False) as pbar:
                        for chunk in r.iter_content(chunk_size=8*1024*1024):
                            f.write(chunk)
                            pbar.update(len(chunk))
                os.replace(temp_path, local_path)

        # start the clock
        start = time.time()

        # Open local cached file instead of the URL
        tree = uproot.open(local_path + ":analysis")
        
        sample_data = []

        # Loop over data in the tree
        for data in tree.iterate(variables + weight_variables,
                                 library="ak",
                                 entry_stop=tree.num_entries*fraction): # process up to numevents*fraction
                                 #step_size = 1000000):

            padded_array = ak.pad_none(data['jet_pt'], 2)
            data['leading_jet_pt'] = padded_array[:, 0]
            data['subleading_jet_pt'] = padded_array[:, 1]
            padded_array = ak.pad_none(data['jet_eta'], 2)
            data['leading_jet_eta'] = padded_array[:, 0]
            data['subleading_jet_eta'] = padded_array[:, 1]

            # Event Selection (reference: https://arxiv.org/pdf/1409.6212)

            # Generate btag identifier
            data['btag_ID'] = (data['jet_btag_quantile'] >= 4)

            data = data[data['trigMET']] # Apply MET trigger 
            data = data[data['met'] > 150 * GeV] # MET>30 GeV 
            
            data = data[selectJets(data)]
            data = data[selectZeroLeptons(data)]
            
            data = data[select_HT(data)]
            data = data[select_2b_phi(data)]
            data = data[select_metbb_phi(data)]
            data = data[select_min_metjets_phi(data)]

            # Invariant Mass
            data['mass'] = calc_mass(data)

            # Store Monte Carlo weights in the data
            if 'Data' not in s: # Only calculates weights if the data is MC
                #print(f'weight: {sumweights}')
                if s=='Signal':
                    data['totalWeight'] = calc_weight(data)
                else:
                    data['totalWeight'] = calc_weight(data)
                print(data['totalWeight'])  
            elapsed = time.time() - start # time taken to process
            print("\t"+str(len(data)) + " events in "+str(round(elapsed,1))+"s") # events before and after

            # Append data to the whole sample data list
            sample_data.append(data)

        frames.append(ak.concatenate(sample_data))

    all_data[s] = ak.concatenate(frames) # dictionary entry is concatenated awkward arrays

# Variable to plot. 
# Set to either "mass" (for invariant mass of two b-jets) or 
# "met" for the missing transverse energy
variable_to_plot = 'mass'
# x-axis range of the plot
if variable_to_plot == "met":
    step_size = 25* GeV
    xmin = 150 * GeV
    xmax = 500 * GeV
else:
    step_size = 20* GeV
    xmin = 20 * GeV
    xmax = 500 * GeV


bin_edges = np.arange(start=xmin, # The interval includes this value
                    stop=xmax+step_size, # The interval doesn't include this value
                    step=step_size ) # Spacing between values
bin_centres = np.arange(start=xmin+step_size/2, # The interval includes this value
                        stop=xmax+step_size/2, # The interval doesn't include this value
                        step=step_size ) # Spacing between values

bin_left = np.arange(start=xmin, # The interval includes this value
                        stop=xmax+step_size, # The interval doesn't include this value
                        step=step_size ) # Spacing between values

data_x,_ = np.histogram(np.clip(ak.to_numpy(all_data['Data'][variable_to_plot]),bin_edges[0],bin_edges[-2]),
                        bins=bin_edges ) # histogram the data
data_x_errors = np.sqrt( data_x ) # statistical error on the data

signal_x = np.clip(ak.to_numpy(all_data['Signal'][variable_to_plot]),bin_edges[0],bin_edges[-2]) # histogram the signal
signal_weights = ak.to_numpy(all_data['Signal'].totalWeight) # get the weights of the signal events
signal_color = samples['Signal']['color'] # get the colour for the signal bar

mc_x = [] # define list to hold the Monte Carlo histogram entries
mc_weights = [] # define list to hold the Monte Carlo weights
mc_colors = [] # define list to hold the colors of the Monte Carlo bars
mc_labels = [] # define list to hold the legend labels of the Monte Carlo bars

for s in samples: # loop over samples
    if s not in ['Data', 'Signal']: # if not data nor signal
        # if 'V' in s or 'bar' in s:
        #     print(f'skip {s}')
        #     break
        mc_x.append( np.clip(ak.to_numpy(all_data[s][variable_to_plot]),bin_edges[0],bin_edges[-2]) ) # append to the list of Monte Carlo histogram entries
        mc_weights.append( ak.to_numpy(all_data[s].totalWeight) ) # append to the list of Monte Carlo weights
        mc_colors.append( samples[s]['color'] ) # append to the list of Monte Carlo bar colors
        mc_labels.append( s ) # append to the list of Monte Carlo legend labels

# *************
# Main plot
# *************
fig = plt.gcf()
fig.set_size_inches(18.5, 10.5)

# Create a 2-row grid layout
fig, (main_axes, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(8, 6),
                               gridspec_kw={'height_ratios': [3, 1]})
fig.set_size_inches(13.5, 13.5)
#main_axes = plt.gca() # get current axes

# plot the data points
main_axes.errorbar(x=bin_centres, y=data_x, yerr=data_x_errors,
                   fmt='ko', # 'k' means black and 'o' is for circles
                   markersize=4, # Adjust the size of the circles
                   label='Data')

# # plot the Monte Carlo bars
mc_heights = main_axes.hist(mc_x, bins=bin_edges,
                            weights=mc_weights, stacked=True,
                            color=mc_colors,
                            label=mc_labels )

mc_x_tot = mc_heights[0][-1] # stacked background MC y-axis value

# calculate MC statistical uncertainty: sqrt(sum w^2)
mc_x_err = np.sqrt(np.histogram(np.hstack(mc_x), bins=bin_edges, weights=np.hstack(mc_weights)**2)[0])

# plot the signal bar
signal_heights = main_axes.hist(signal_x, bins=bin_edges, bottom=mc_x_tot,
                    weights=signal_weights, color=signal_color,
                    label=r'Signal ($m_H$ = 125 GeV)')

signal_x_tot = signal_heights[0]# stacked background MC y-axis value

# plot the statistical uncertainty
main_axes.bar(bin_centres, # x
                2*mc_x_err, # heights
                alpha=0.5, # half transparency
                bottom=mc_x_tot-mc_x_err, color='none',
                hatch="////", width=step_size, label='Stat. Unc.' )

# plot the signal bar
main_axes.hist(signal_x, bins=bin_edges, #bottom=mc_x_tot,
                weights=signal_weights*(10 if variable_to_plot == "met" else 5), color=signal_color, histtype='step', linewidth=1.5, 
                label=r'Signal ($m_H$ = 125 GeV) x %i'%(10 if variable_to_plot == "met" else 5))

if variable_to_plot == "met":
    ax2.tick_params(axis='y', labelsize=20)
    main_axes.set_xticks(list(np.arange(0, 550, step=25)), list(np.arange(0, 550, step=25)))  # Set text labels and properties.
    ax2.set_xticks(list(np.arange(0, 550, step=25)), list(np.arange(0, 550, step=25)),fontsize=20)  # Set text labels and properties.
else:
    main_axes.set_xticks(list(np.arange(0, 520, step=20)), list(np.arange(0, 520, step=20)))  # Set text labels and properties.
    ax2.set_xticks(list(np.arange(0, 520, step=20)), list(np.arange(0, 520, step=20)),fontsize=16)  # Set text labels and properties.
    ax2.tick_params(axis='y', labelsize=20)
main_axes.tick_params(axis='y', labelsize=20)

# set the x-limit of the main axes
main_axes.set_xlim( left=xmin, right=xmax )

# separation of x axis minor ticks
main_axes.xaxis.set_minor_locator( AutoMinorLocator() )

# set the axis tick parameters for the main axes
main_axes.tick_params(which='both', # ticks on both x and y axes
                        direction='in', # Put ticks inside and outside the axes
                        top=True, # draw ticks on the top axis
                        right=True ) # draw ticks on right axis


# write y-axis label for main axes
main_axes.set_ylabel('Events / '+str(step_size)+' GeV',
                        y=1, horizontalalignment='right',fontsize=40)



# add minor ticks on y-axis for main axes
main_axes.yaxis.set_minor_locator( AutoMinorLocator() )

if variable_to_plot == "met":
    xtit = r'$E_{T}^{miss}$ [GeV]'
    main_axes.set_yscale('log')
    # set y-axis limits for main axes
    main_axes.set_ylim( bottom=0.4, top=350000)#np.amax(data_x)*1.6 )
else:
    xtit = r'$m_{bb}$ [GeV]'
    #main_axes.set_yscale('log')
    main_axes.set_ylim( bottom=0.1, top=1120)#np.amax(data_x)*1.6 )
    ax2.set_ylim( bottom=0.45, top=4.5)#np.amax(data_x)*1.6 )
# draw the legend
main_axes.legend( frameon=False, fontsize=20 ); # no box around the legend


# Calculate the ratio where counts2 is not zero
this_data_x = data_x.astype('float64')
ratio = np.divide(this_data_x , (mc_x_tot + signal_x_tot), out=np.zeros_like(this_data_x), where=(mc_x_tot != 0))


# Calculate uncertainty in the ratio using propagation of uncertainty
ratio_uncertainty = ratio * np.sqrt((data_x_errors/this_data_x)**2 + (mc_x_err/(mc_x_tot + signal_x_tot))**2)


ratio_uncertainty[ratio_uncertainty < 0] = 0      # Replace negative numbers with 0
ratio_uncertainty[np.isnan(ratio_uncertainty)] = 0  # Replace NaN with 0

# Plot the ratio with markers in the bottom subplot
mid_bins = 0.5 * (bin_edges[:-1] + bin_edges[1:])  # Midpoints of bins for plotting
bin_widths = np.diff(bin_edges) / 2  # Half bin width for each midpoint

# To get the edges right need to add an additional point to the right of the axis limits
mc_x_err = np.append(mc_x_err,mc_x_err[-1])
mc_x_tot = np.append(mc_x_tot,mc_x_tot[-1])

uncertainty = 0.1
# Add a shaded area representing the error around ratio = 1
ax2.fill_between(bin_left, 1 - mc_x_err/mc_x_tot, 1 + mc_x_err/mc_x_tot, 
                 hatch="////",color='gray', alpha=0.5, label='Error Band', step = 'pre')

ax2.errorbar(mid_bins, ratio, xerr=bin_widths ,yerr=ratio_uncertainty,fmt="o", color='black')
ax2.set_xlabel(xtit ,fontsize=40,loc='right')
ax2.set_ylabel('Data/Pred.',fontsize=20)
ax2.set_ylim( bottom=0.4, top=1.6)#np.amax(data_x)*1.6 )
ax2.grid(True)  # Enable gridlines for the bottom subplot

# add minor ticks on y-axis for main axes
ax2.yaxis.set_minor_locator( AutoMinorLocator() )

# Adjust layout
plt.tight_layout()

plt.savefig('mbb.png')
print("Plot saved as mbb.png")

