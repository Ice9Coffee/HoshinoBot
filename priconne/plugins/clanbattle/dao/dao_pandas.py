import pandas as pd
import os


class DaoPandas(object):
    def __init__(self, filepath, fields):
        super().__init__()
        self.filepath = filepath
        self.fields = fields
        if os.path.exists(filepath):
            if os.path.isfile(filepath):
                self._table = pd.read_csv(filepath)
            else:
                raise IOError('%s is not a file' % filepath)
        else:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            self._table = pd.DataFrame(columns=fields)

    def __del__(self):
        #self.save()
        pass

    def save(self):
        self._table.to_csv(self.filepath, index=False)

    def add(self, item):
        self._table = self._table.append(item, ignore_index=True)

    def modify(self, item):
        pass

    def delete(self, id):
        pass

    def select(self, like):
        def _mask(df, key, value):
            return df[df[key] == value]
        

    def sort(self):
        pass

    def print_table(self):
        print(self._table)


    