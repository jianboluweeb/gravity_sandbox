# Gravity Algorithm for AR Sandbox
# Fall 2016
# Jianbo Lu, Tyler Stercula, Sophie Deam

import numpy as np
from astropy.io import fits
from astropy.convolution import convolve, convolve_fft
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.mlab as mlab
import testing
# gdal (Geospatial Data Access Library) module allows DEM file manipulation
#import gdal
from time import time

start = time()

'''# Reading in DEM file
dem_file = gdal.Open('BathymetrySaverTool.dem')

# Converts dem_file to numpy array of shape (480, 639)
dem_array = np.array(dem_file.GetRasterBand(1).ReadAsArray())

# This is a temporary fix for an uncalibrated surface, i.e. we set a base level where any value is less than 3
for x in np.nditer(dem_array, op_flags=['readwrite']):
    if x[...] < 3.:
        x[...] = 0.

# Plot density field from dem, for testing purposes, if necessary
"""
fig = plt.figure()

cax = plt.imshow(myarray, cmap='hsv')
x_scale = 'log'
y_scale = 'log'
cbar = plt.colorbar(cax)
plt.title('Density Field')
#plt.set_axis_off()

plt.show()
"""



### Potential Calculation ###
plummer_kernel = fits.getdata('DiscPlumFITS.fits',0)              # Import Plummer Kernel
density_field = dem_array                                           # Import Density Field
print density_field.shape()
w = input()
potential =  -1 * convolve_fft(density_field, plummer_kernel)     # Calculation of potential field using discrete convolution

Poten = fits.PrimaryHDU(potential)                                # Assign HDU to potential calculation
Potenlist = fits.HDUList([Poten])
Potenlist.writeto('PotentialField.fits', clobber = True)          # Save potential field as .FITS file



'''
### Orbit Calculations ###
## Taking gradient of potential field to get acceleration field ##
'''h,w = np.asarray(potential).shape
x, y = np.mgrid[0:h, 0:w]
dy, dx = np.gradient(np.asarray(potential))
dy =  np.negative(dy) 
dx =  np.negative(dx)
p = np.asarray(potential)'''
dx,dy, potential = testing.make_acceleration_field(300,300,10)
dx, dy = np.gradient(potential)
dx = np.negative(dx)
dy = np.negative(dy)
# Sample values 
vel = np.array([0,0]) 
pos = np.array([250,250]) 

# NOTES: When the particle moves out of bounds of the density field, the calculation will stop and return an error. This will eventually be remedied so the particle either stops or reflects off of the boundary. 

# Calculate velocity from initial position
def acce(pos):
    return (dx[pos[0],pos[1]], dy[pos[0],pos[1]])

#needs exception handling

## Leapstep Definition ##
dtime = 0.1

acceleration = []
velocity_arr = []
def leap(pos,vel):
    posi = np.rint(pos)         # Interpolate between pixels using np.rint in x direction
    #print posi
    acc = acce(posi)
    acceleration.append(acc)
    #print acc
    vel = vel + 0.5*dtime*np.array(acc)
    velocity_arr.append(vel)
    pos = pos + 0.5*dtime*vel
    posv = np.rint(pos)         # Interpolate between pixels using np.rint in y direction
    #if pos[0]<460 and pos[1]<640:
    acc = acce(posv)
    acceleration.append(acc)
    vel = vel + 0.5*dtime*np.array(acc)
    velocity_arr.append(vel)
    pos = pos + 0.5*dtime*vel
    return pos,vel        

## Energy Conservation: K+U; K is 0.5v^2 and U is index on the potential.
def e(pos,vel):
    return (0.5*np.sum(np.square(vel)) + p[np.rint(pos[1]).astype(int)][np.rint(pos[0]).astype(int)])
# Needs further calibration: energy conservation violation becomes a problem as step size increases


## Orbit Calculation ##
posxtot = []
posytot = []

times = 50000                # Set the number of steps to be calculated
for n in xrange(1, times):
    if pos[0]<460 and pos[1]<640:
        pos,vel = leap(pos,vel)
        posxtot.append(pos[0])
        posytot.append(pos[1])

fig, (ax1,ax2) = plt.subplots(2)
ax1.plot(range(len(acceleration)), acceleration)
ax2.plot(range(len(velocity_arr)), velocity_arr)
plt.show()
plt.close()

# Plotting orbits for troubleshooting #
accel_im = np.zeros(dx.shape)
for i in range(dx.shape[0]):
    for j in range(dx.shape[1]):
        accel_im[i,j]=np.sqrt(dx[i,j]**2 + dy[i,j]**2)
fig = plt.figure()
plt.imshow(potential)
plt.plot(posxtot, posytot)
plt.suptitle('Orbit for DEM file')
plt.xlabel('X component of position')
plt.ylabel('Y component of position')
plt.savefig('test.png',bbinches='tight')


time = time() - start
print time                # Benchmark time

#### FINAL NOTES: There still needs to be code written to replace the "Sample Values" with an IMPORTED .txt file from the interface team to define intial positions and velocities. Also, there needs to be code written to OUTPUT a .txt file of x and y position and time for the interface team. 
