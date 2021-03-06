# -*- coding: UTF-8 -*-
from budget_app.models import *
from budget_app.loaders import SimpleBudgetLoader
from decimal import *
import csv
import os
import re

class ArroyomolinosBudgetLoader(SimpleBudgetLoader):

    def parse_item(self, filename, line):
        # Programme codes have changed in 2015, due to new laws. Since the application expects a code-programme
        # mapping to be constant over time, we are forced to amend budget data prior to 2015.
        programme_mapping = {
            # old programme: new programme
            '1340': '1350',     # Protección Civil
            '1350': '1360',     # Extinción de incendios
            '1600': '9201',     # Servicios generales
            '2300': '2310',     # Servicios sociales > Asistencia social primaria
            '2310': '2210',     # Acción social > Otras prestaciones económicas a favor de empleados
            '2340': '3341',     # Infancia y juventud
            '2350': '3342',     # Tercera edad
            '2360': '3343',     # Mujer
            '4310': '4320',     # Turismo
            '9200': '9202',     # Administración general

        }
        programme_mapping_2015 = {
            # old programme: new programme
            '1651': '1650',
            '2450': '2440',
            '3110': '3130',
        }

        # Some dirty lines in input data
        if line[2]=='':
            return None

        is_expense = (filename.find('gastos.csv')!=-1)
        is_actual = (filename.find('/ejecucion_')!=-1)
        if is_expense:
            # We got 3- or 4- digit functional codes as input, so add a trailing zero
            fc_code = line[1].ljust(4, '0')
            ec_code = line[2]

            # For years before 2015 we check whether we need to amend the programme code
            year = re.search('municipio/(\d+)/', filename).group(1)
            if int(year) < 2015:
                fc_code = programme_mapping.get(fc_code, fc_code)
            else:
                fc_code = programme_mapping_2015.get(fc_code, fc_code)

            return {
                'is_expense': True,
                'is_actual': is_actual,
                'fc_code': fc_code,
                'ec_code': ec_code[:-2],        # First three digits (everything but last two)
                'ic_code': '000',
                'item_number': ec_code[-2:],    # Last two digits
                'description': line[4],
                'amount': self._parse_amount(line[11 if is_actual else 8])
            }

        else:
            description = line[3]
            # Fix typo in input data
            if description=='Trnasferencias I.A.E.' or description=='Trnasferencias del I.A.E.':
                description = 'Transferencias I.A.E.';

            ec_code = line[2]
            return {
                'is_expense': False,
                'is_actual': is_actual,
                'ec_code': ec_code[:-2],        # First three digits
                'ic_code': '000',               # All income goes to the root node
                'item_number': ec_code[-2:],    # Fourth and fifth digit
                'description': description,
                'amount': self._parse_amount(line[7 if is_actual else 4])
            }
