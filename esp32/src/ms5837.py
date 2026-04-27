from machine import Pin, I2C 
import time

class Sensor():
    """
    float's sensor. comm's over i2c.
    
    custom 02ba driver based on code from [bluerobotics ms5837 driver.](https://github.com/bluerobotics/ms5837-python). chatgpt was used
    """
    _ADDR = 0x76
      
    # densities (kg m^-3)
    DENSITY_FRESHWATER = 997
    DENSITY_SALTWATER = 1029

    # pressure units
    UNIT_PRESSURE_Pa     = 100.0
    UNIT_PRESSURE_hPa    = 1.0
    UNIT_PRESSURE_kPa    = 0.1
    UNIT_PRESSURE_mbar   = 1.0
    UNIT_PRESSURE_bar    = 0.001
    UNIT_PRESSURE_atm    = 0.000986923
    UNIT_PRESSURE_Torr   = 0.750062
    UNIT_PRESSURE_psi    = 0.014503773773022

    # commands
    _CMD_RESET            = 0x1E
    _CMD_ADC_READ         = 0x00
    _CMD_PROM_READ_ORIGIN = 0xA0
    _CMD_READ_RAW_PRES    = 0x48
    _CMD_READ_RAW_TEMP    = 0x58

    def __init__(self) -> None:
        self._bus = I2C(0)

        self._pressure = 0
        self._temperature = 0

        self._raw_pres = 0
        self._raw_temp = 0
        self._calibration = []
        self._calibrate()

    def temperature(self):
        return self._temperature / 100.0
    
    def pressure(self, unit: float = UNIT_PRESSURE_mbar):
        return self._pressure * unit
    
    def depth(self, fluid_density: float = DENSITY_FRESHWATER):
        return (self.pressure(Sensor.UNIT_PRESSURE_Pa)-101300)/(fluid_density*9.80665)
    

    def _calibrate(self):
        self._w(Sensor._CMD_RESET)
        _sleep_ms(10)

        self._calibration = []
        for i in range(7):
            self._w(Sensor._CMD_PROM_READ_ORIGIN + (i * 2))
            data = self._r(2)
            value = data[0] << 8 | data[1]
            self._calibration.append(value)

    def _read_adc(self) -> int:
        self._w(Sensor._CMD_ADC_READ)
        data = self._r(3)

        return data[0] << 16 | data[1] << 8 | data[2]

    def _read_raw_pressure(self):
        self._w(Sensor._CMD_READ_RAW_PRES)
        _sleep_ms(20)
        self._raw_pres = self._read_adc()

    def _read_raw_temperature(self):
        self._w(Sensor._CMD_READ_RAW_TEMP)
        _sleep_ms(20)
        self._raw_temp = self._read_adc()

    def read(self):
        self._read_raw_pressure()
        self._read_raw_temperature()

        # apply calibration and compensation
        OFFi = 0
        SENSi = 0
        Ti = 0

        dT = self._raw_temp-self._calibration[5]*256
        SENS = self._calibration[1]*65536+(self._calibration[3]*dT)/128
        OFF = self._calibration[2]*131072+(self._calibration[4]*dT)/64
        self._pressure = (self._raw_pres*SENS/(2097152)-OFF)/(32768)
        
        self._temperature = 2000+dT*self._calibration[6]/8388608

        # Second order compensation
        if (self._temperature/100) < 20: # Low temp
            Ti = (11*dT*dT)/(34359738368)
            OFFi = (31*(self._temperature-2000)*(self._temperature-2000))/8
            SENSi = (63*(self._temperature-2000)*(self._temperature-2000))/32
        
        OFF2 = OFF-OFFi
        SENS2 = SENS-SENSi
    
        self._temperature = (self._temperature-Ti)
        self._pressure = (((self._raw_pres*SENS2)/2097152-OFF2)/32768)/100.0  

    # read/write helpers
    def _w(self, data: int):
        self._bus.writeto(Sensor._ADDR, bytes([data]))

    def _r(self, size: int) -> bytes:
        return bytes(self._bus.readfrom(Sensor._ADDR, size))
    

def _sleep_ms(ms: int):
    time.sleep(ms/1e3)