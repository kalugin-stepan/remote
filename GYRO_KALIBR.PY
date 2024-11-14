import time
from i2c_itg3205 import i2c_itg3205

gyro = i2c_itg3205(1)  # порт может быть различным в зависимости от вашей конфигурации Raspberry Pi
z_sum = 0

try:
    for _ in range(1000):  # для 1000 итераций, измените это число для изменения числа итераций
        _, _, z = gyro.getDegPerSecAxes()
        z_sum += z
        time.sleep(0.01)  # задержка между измерениями
except KeyboardInterrupt:
    pass
    
print(f"Average Z: {z_sum/1000} degrees/sec")