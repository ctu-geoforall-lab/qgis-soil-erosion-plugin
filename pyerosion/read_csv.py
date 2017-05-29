import codecs

class ReadCSV():
    def __init__(self, csv_file):
        """Read CSV file into table
        """
        with codecs.open(csv_file, 'rb', 'utf-8') as f:
            # assuming that first line contains column names
            # csv is not used here because it do not support unicode (in Python 2)
            self._data = {}
            for line in f.readlines():
                c1, c2 = line.split(',', 1)
                self._data[c1] = c2
        
    def value(self, key):
        """Get value from table.

        :param key: row of key
        """
        return self._data.get(key, None)

    def list(self):
        """Make list of keys from dictionary
        """
        return self._data.keys()
