import unittest
import pandas as pd
from converttodate import render
import numpy as np

date_input_map = 'AUTO|Date (U.S.) MM/DD/YYYY|Date (E.U.) DD/MM/YYYY'.lower().split('|')
reference_date = np.datetime64('2018-08-07T00:00:00.000000000')

class TestConvertDate(unittest.TestCase):

    def setUp(self):
        # Very simple test cases for now to deliver MVP, auto-detection does not catch most cases
        self.table = pd.DataFrame([
            ['08/07/2018', '07/08/2018', '2018-08-07', '08.07.2018', '08/07/2018', 99, 'August 7, 2018'],
            [' 08/07/2018T00:00:00 ', ' 07/08/2018T00:00:00 ', ' 2018.08.07T00:00:00 ', '08.07.2018', 99, 99, 'August 07, 2018'],
            ['..08/07/2018T00:00:00:00..', '..07/08/2018T00:00:00..', '..2018.08.07T00:00:00..', '08.07.2018', 99, 99, 'August 07, 2018']],
            columns=['us', 'eu', 'yearfirst', 'catcol', 'null', 'number', 'written'])

        self.table['catcol'] = self.table['catcol'].astype('category')
        self.table['null'] = self.table['null'].astype('category')

    def test_NOP(self):
        params = {'colnames': ''}
        out = render(self.table, params)
        self.assertTrue(out.equals(self.table))  # should NOP when first applied

    def test_us(self):
        # All cells should have the same date
        params = {'colnames': 'us', 'type_null': True, 'type_date': date_input_map.index('date (u.s.) mm/dd/yyyy')}
        out = render(self.table.copy(), params)
        for y in out['us']:
            self.assertTrue(y.to_datetime64() == reference_date)

    def test_eu(self):
        # All cells should have the same date
        params = {'colnames': 'eu', 'type_null': True, 'type_date': date_input_map.index('date (e.u.) dd/mm/yyyy')}
        out = render(self.table.copy(), params)
        for y in out['eu']:
            self.assertTrue(y.to_datetime64() == reference_date)

    def test_numbers(self):
        # Should throw type error
        params = {'colnames': 'eu,number', 'type_null': True, 'type_date': date_input_map.index('date (e.u.) dd/mm/yyyy')}
        self.assertTrue(render(self.table.copy(), params) == 'Cannot convert numerical columns.')

    def test_auto(self):
        # All cells should have the same date
        params = {'colnames': 'catcol,written,yearfirst', 'type_null': True, 'type_date': date_input_map.index('auto')}
        out = render(self.table.copy(), params)
        for y in out[['catcol', 'yearfirst', 'written']].values:
            for x in y:
                self.assertTrue(x == reference_date)

    def test_error(self):
        # Error should indicate there are 2 cells that have formatting issues
        params = {'colnames': 'null', 'type_null': False, 'type_date': date_input_map.index('auto')}

        # Test exact error message
        self.assertTrue(render(self.table.copy(), params) == "Format error in row 2 of 'null'. Overall, there are 2 errors in 1 columns. Select 'non-dates to null' to set these cells to null")


if __name__ == '__main__':
    unittest.main()
