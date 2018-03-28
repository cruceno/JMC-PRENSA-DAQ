from minimalmodbus import Instrument
from minimalmodbus import MODE_RTU
from jmc_prensa_daq.instrument.serialutil import scan_serial_ports

TYPES = [('tc j', 0),
         ('tc k', 1),
         ('tc t', 2),
         ('tc n', 3),
         ('tc r', 4),
         ('tc s', 5),
         ('tc b', 6),
         ('tc e', 7),
         ('Pt100', 8),
         ('0-20 mA', 9),
         ('4-20 mA', 10),
         ('0-50 mV', 11),
         ('0-5 Vcc', 12),
         ('0-10 Vcc', 13),
         ('4-20mA Ln j', 14),
         ('4-20mA Ln k', 15),
         ('4-20mA Ln t', 16),
         ('4-20mA Ln n', 17),
         ('4-20mA Ln r', 18),
         ('4-20mA Ln s', 19),
         ('4-20mA Ln b', 20),
         ('4-20mA Ln e', 21),
         ('4-20mA LnPt', 22)
         ]

DPPO = [('xx.xxx', 2),
        ('xxx.xx', 3),
        ('xxxx.x', 4),
        ('xxxxx', 5),
        ]


def get_n1540_list(ports=scan_serial_ports(20, verbose=False)):

    n1540_list = []
    for port in ports:
        try:
            n = N1540(port[1])
            n1540_list.append((n.getSerialNumber(), port[1]))

        except:
            continue
    return n1540_list

class N1540(Instrument):

    def __init__(self, port, slaveaddress=1, mode=MODE_RTU):

        Instrument.__init__(self, port, slaveaddress, mode)

        self.REGISTERS = {'AlarmsPoints': {'Spa1': 18,
                                           'Spa2': 19,
                                           },
                          'AlarmsFunctions': {'fvA1': 22,
                                              'fvA2': 23,
                                              },
                          'InputConfig': {'type': 50,
                                          'dppo': 52,
                                          'fltr': 53,
                                          'offs': 56,
                                          'inll': 57,
                                          'inxl': 58,
                                          }
                          }

    def getSerialNumber(self):

        '''
        Reuturn the serial number of the N1540,
        request and joining the 0012 and 0013 registers
        '''

        return "".join(str(x) for x in self.read_registers(12, 2))

    def getDecimalNumbers(self):
        return 5 - self.read_register(52)

    def getPV(self):
            return self.read_register(0, self.getDecimalNumbers())

    def getAlarmsPoints(self):
        registers = self.REGISTERS['AlarmsPoints']
        values = {}
        for key, value in registers.items():
            values[key] = self.read_register(value, self.getDecimalNumbers())
        return values

    def getAlarmsFunctions(self):
        registers = self.REGISTERS['AlarmsFunctions']
        values = {}
        for key, value in registers.items():
            values[key] = self.read_register(value)
        return values

    def getInputConfig(self):
        registers = self.REGISTERS['InputConfig']
        values = {}
        for key, value in registers.items():
            if key == 'inll' or key == 'inxl':
                numberOfDecimals = self.getDecimalNumbers()
            else:
                numberOfDecimals = 0
            values[key] = self.read_register(value, numberOfDecimals)
        return values

    def setAlarmPoints(self, ap):
        '''
        SPA1
        HR_SPA1

        Name: Setpoint de alarme 1

        Description: Value that defines the alarm activation point. For the alarms set up with \
        the functions of the type Differential, these parameters define the maximum differences \
        accepted between PV and a reference value defined in the parameter ALrF. For the alarm function ierr, \
        this parameter is not used.

        Allows write: yes

        Lower limit: 
         IF -(HR_SPHL - HR_SPLL) >= -2000
             THEN VALUE >= -(HR_SPHL - HR_SPLL)
             ELSE VALUE >= -2000

        Upper limit: 
         IF (HR_SPHL - HR_SPLL) <= 30000
             THEN VALUE <= (HR_SPHL - HR_SPLL)
             ELSE VALUE <= 30000

        '''

        for key, value in ap.items():
            try:
                self.write_register(self.REGISTERS['AlarmsPoints'][key], value, self.getDecimalNumbers())
            except Exception as err:
                print('Error al insertar el regstro {}:{}'.format(key, err))
                return False
        return True

    def setAlarmsFunctions(self, functions):
        for key, value in functions.items():
            try:
                self.write_register(self.REGISTERS['AlarmsFunctions'][key], value)
            except Exception as err:
                print('Error al insertar el regstro {}:{}'.format(key, err))
                return False
        return True

    def setInputConfig(self, config):
        for key, value in config.items():
            try:
                if key == 'inll' or key == 'inxl' or key =='offs':
                    numberOfDecimals = self.getDecimalNumbers()
                else:
                    numberOfDecimals = 0

                self.write_register(self.REGISTERS['InputConfig'][key], value, numberOfDecimals)
            except Exception as err:
                raise err
        return True


# n = N1540('/dev/ttyACM0')
#
# alarmspoints = {'Spa3': 0.00, 'Spa4': 0.00, 'Spa1': 5.0, 'Spa2': 0.00}
# n.setAlarmPoints(alarmspoints)
# print(n.getAlarmsPoints())
#
# functions = {'fvA3': 0, 'fvA4': 0, 'fvA1': 2, 'fvA2': 0}
# n.setAlarmsFunctions(functions)
# print(n.getAlarmsFunctions())
#
# config = {'type': 13, 'inxl': 10.000, 'inll': 0.000, 'dppo': 2, 'offs': 0, 'fltr': 5}
# n.setInputConfig(config)
# print(n.getInputConfig())




