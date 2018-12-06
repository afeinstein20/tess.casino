from astropy.table import Table
from astroquery.mast import Observations
from astropy.io import fits
import numpy as np
import pandas as pd
from bokeh.plotting import ColumnDataSource, figure, output_file, save

point_color = '#006600' # darkened casino green

def download_lightcurve(obsid):
    """Return a pandas dataframe of lightcurve data for one source."""
    dl = Observations.download_products(obsid, productSubGroupDescription='LC')
    fn = dl['Local Path'][0]
    hdul = fits.open(fn)
    lc = Table(hdul[1].data)
    lc['NORM_PDCSAP_FLUX'] = lc['PDCSAP_FLUX']/np.nanmedian(lc['PDCSAP_FLUX'])
    data = lc.to_pandas()
    return data

def generate_figure(data):
    fig = figure(tools="pan,wheel_zoom,box_zoom,reset,save", 
                active_scroll="wheel_zoom", plot_width=800, plot_height=300)
    render = fig.circle('TIME','NORM_PDCSAP_FLUX', source=data, 
                    size=3, line_color=point_color, fill_color=point_color)
    fig.xaxis.axis_label = 'Time (BJD - 2457000)'
    fig.yaxis.axis_label = 'Normalized Flux'
    fig.xaxis.axis_label_text_font_size = '14pt'
    fig.xaxis.major_label_text_font_size = '10pt'
    fig.yaxis.axis_label_text_font_size = '12pt'   
    fig.yaxis.major_label_text_font_size = '10pt'
    return fig

if __name__ == '__main__':
    t = Table.read('../data/tess-timeseries-mast.csv')
    t = t[t['sequence_number'] == 1] # HACK - just do sector 1
    N = len(t)
    n = 0
    for i,o in zip(t['target_name'], t['obsid']): # TIC ID, MAST obsid
        print("TIC {0} ({1} of {2})".format(o,n,N))
        obsid = str(o)
        data = download_lightcurve(obsid)
        fig = generate_figure(data)
        output_file('fig/TIC{0:.0f}.html'.format(i))
        save(fig)
        n += 1