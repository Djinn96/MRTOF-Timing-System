import matplotlib.pyplot as plt
import numpy as np
import cv2

def plotTimingSignal(ax:plt.Axes,period,pulses,invert:bool,n):
    '''
    Plots a single timing signal onto the given Axes ax.
    '''
    x = np.arange(0,period,1)
    y = np.zeros(len(x))
    for pulse in pulses:
        if pulse[1] < pulse[0]: # cyclic data may produce reversed timings
            y += [1 if (i >= 0        and i <= pulse[1]) else 0 for i in x]
            y += [1 if (i >= pulse[0] and i <= period  ) else 0 for i in x]
        y += [1 if (i >= pulse[0] and i <= pulse[1]) else 0 for i in x]
    y = np.where(y>0,1,0) # constrain such that multiple overlapping pulses maintains a pulse height = 1
    if invert: y = -y + 1
    ax.step(x,y+n)

def bpaChart(period,timingList,bpaNames,xorMask):
    '''
    Creates a chart of all timing signals as defined in the BitPatternArray (bpa)
    returns a png encoded byte image so that it could be sent via REST API to the front end
    '''
    fig,ax = plt.subplots(1,1,figsize=(25,5))

    for i,timings in enumerate(timingList):
        invert = False
        if (xorMask & 2**i) > 0: invert = True
        plotTimingSignal(ax,period,timings,invert,-i*2)
        plt.text(0,0.2-i*2,bpaNames[i])

    ax.set_xlim(0,period)
    ax.set_xlabel('period = {} us'.format(period))
    fig.tight_layout()
    canvas = fig.canvas
    canvas.draw()

    image_flat = np.frombuffer(canvas.tostring_argb(), dtype='uint8')  # (H * W * 3,)
    # NOTE: reversed converts (W, H) from get_width_height to (H, W)
    image = image_flat.reshape(*reversed(canvas.get_width_height()), 4)  # (H, W, 3)
    image = image[:,:,::-1]

    success, encoded_image = cv2.imencode('.png', image)

    return encoded_image.tobytes()