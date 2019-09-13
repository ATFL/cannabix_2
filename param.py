import numpy as np
param_array = []
test_file_name = 'test1'
length_of_test = 200
exposure_time = 10
recovery_time = 20
Analyte ='THC'
concentration = '100 ug'
sensor_max1 = 1.5
sensor_max2 = 2
sensor_max3 = 3
sensor_max4 = 4
print(param_array)

param_array.append('Filename: ' + test_file_name)
param_array.append('Test Length: ' + str(length_of_test))
param_array.append('Exposure Time: ' + str(exposure_time))
param_array.append('Recovery Time: ' + str(recovery_time))
param_array.append('Analyte: ' + Analyte)
param_array.append('Concentration: ' + str(concentration))
param_array.append('Sensor max Val: ' + str(sensor_max1))

print(param_array)
filename = test_file_name + '.param'
np.savetxt(filename,param_array, fmt="%s")
