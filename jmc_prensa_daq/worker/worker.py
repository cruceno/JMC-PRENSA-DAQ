'''
Created on 1 mar. 2018

@author: javier
'''
from PyQt4.QtCore import QThread, SIGNAL
from jmc_prensa_daq.instrument.N1540 import N1540
import time


class WorkerClass (QThread):

    def __init__(self):
        QThread.__init__(self)
        self.exiting = False

    def dotest(self,
               outfile,
               dps,
               presure_port,
               displacement_port,
               cylinder_area,
               work_area,
               zero_fix):

        try:
            self.presure_sensor = N1540(presure_port)
        except Exception as err:
            self.emit(SIGNAL("msgsignal(PyQt_PyObject)"), err)
            return False
        try:
            self.displacement_sensor = N1540(displacement_port)
        except Exception as err:
            self.emit(SIGNAL("msgsignal(PyQt_PyObject)"), err)
            return False

        self.zero_fix = zero_fix
        self.cylinder_area = cylinder_area
        self.work_area = work_area
        self.delay = 1 / dps
        self.outfile = outfile
        self.start()

    def run(self):

        zero_time = time.time()

        p_spa1 = self.presure_sensor.getAlarmsPoints()['Spa1']
        d_spa1 = self.displacement_sensor.getAlarmsPoints()['Spa1']
        d_spa2 = self.displacement_sensor.getAlarmsPoints()['Spa2']

        while not self.exiting:

            fsock = open(self.outfile, 'a')
            time_stamp = time.time() - zero_time

            last_values = fsock.readlines()
            if len(last_values) > 16:
                t, p, d, f, pm, v = last_values[-1].split('\t')

            try:
                presure = self.presure_sensor.getPV()
                displacement = self.displacement_sensor.getPV()
                if presure < p_spa1 and (d_spa1 < displacement < d_spa2):
                    data = [time_stamp,
                            format(presure, '.3f'),
                            format(displacement - self.zero_fix, '.1f'),
                            format(presure * self.cylinder_area / 100, '.3f'),
                            format(presure * self.cylinder_area * 10 / self.work_area, '.3f'),
                            format((displacement - d) / (time_stamp - t), '.2f')
                            ]

                    fsock.write('\t'.join(str(x) for x in data) + '\n')
                    fsock.close()

                    self.emit(SIGNAL("readsignal(PyQt_PyObject)"), data)
                else:
                    self.emit(SIGNAL("stopbylimit()"))

            except Exception as err:
                self.emit(SIGNAL("msgsignal(PyQt_PyObject)"), '{}'.format(err))
                continue

            time.sleep(self.delay)
