from kivy.uix.modalview import ModalView 

from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.lang import Builder
Builder.load_file('screens/widgets/static_graph.kv')

from collections import OrderedDict

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.ticker as ticker


from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas # pylint:disable=unresolved-import

'''Formatter function for X Axis'''
def min_sec(x, pos):
    'The two args are the value and tick position'
    minutes, seconds = divmod(x, 60)

    if minutes < 10:
        if seconds == 0:
            return '0{}'.format(int(minutes))
        else:
            return '0{}:{}'.format(int(minutes), int(seconds))
    else:
        if seconds == 0:
            return '{}'.format(int(minutes))
        else:
            return '{}:{}'.format(int(minutes), int(seconds))

class MyFigureCanvas(FigureCanvas):

    def on_touch_down(self, touch):
        Window.release_all_keyboards()

class StaticGraph(ModalView):
    bl_static = ObjectProperty()

    def __init__(self, buff_large, dt, marker_list, y_lim, met2compute, **kwargs):

        super(StaticGraph, self).__init__(**kwargs)

        self.metrics = met2compute

        ax = OrderedDict()

        time = np.linspace(1, buff_large[list(self.metrics.keys())[0]].__len__(), buff_large[list(self.metrics.keys())[0]].__len__()) * dt
        plt.rcParams.update({'figure.autolayout': True})
        fig = plt.figure()
        fig.patch.set_facecolor((float(25) / 255, float(63) / 255, float(90) / 255))

        subplot_ndx = 1
        for met in self.metrics.keys():
            ax[met] = fig.add_subplot(self.metrics.keys().__len__(), 1, subplot_ndx)
            subplot_ndx += 1

        '''Plot Customization'''
        formatter = FuncFormatter(min_sec)

        for axes in ax:
            ax[axes].set_facecolor((float(189) / 255, float(218) / 255, float(237) / 255))
            for child in ax[axes].get_children():
                if isinstance(child, matplotlib.spines.Spine):
                    child.set_color('white')
            ax[axes].tick_params(axis='x', colors='white')
            ax[axes].tick_params(axis='y', colors='white')

            ax[axes].grid()
            ax[axes].yaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))
            ax[axes].xaxis.set_major_formatter(formatter)

            ax[axes].tick_params(axis='x',  # changes apply to the x-axis
                                 which='both',  # both major and minor ticks are affected
                                 bottom=False,  # ticks along the bottom edge are off
                                 top=False,  # ticks along the top edge are off
                                 labelbottom=False)  # labels along the bottom edge are off)
            ax[axes].tick_params(axis='y', labelsize=15)

            ax[axes].set_title(axes, fontsize=20, color='white')
            
            ax[axes].set_ylim(y_lim[axes])

            ax[axes].plot(time, buff_large[axes], lw=3, color=[float(25) / 255, float(63) / 255, float(90) / 255])
            #         ax.plot(time,self.wl_buff_large,lw=2,color = [float(25)/255,float(63)/255,float(90)/255])
            #         ax_gsr.plot(time,gsr_buff_large,lw=2,color = [float(132)/255, float(60)/255, float(12)/255])

            for marker in marker_list:
                ax[axes].axvline(x=marker * dt, color=[float(233) / 255, float(147) / 255, float(34) / 255])
        #         ax.axhline(y=self.th_wl, xmin=0, xmax=1,c = 'r',lw=2)
        #         ax.plot(time,self.wl_buff_art_large,'o',color = [float(233)/255, float(147)/255, float(34)/255] ,ms = 9,alpha = 1)
        
        ax[list(ax.keys())[-1]].set_xlabel('Time[min]', fontsize=15, color='white')
        ax[list(ax.keys())[-1]].tick_params(axis='x', bottom=True)

        canvas = MyFigureCanvas(fig)
        self.bl_static.add_widget(canvas)