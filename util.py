import numbers
from datetime import datetime
import json


def df_to_text(df, prefix, date_columns=None, include_time_in_dates=True):

    def convert_value(value):
        if isinstance(value, numbers.Number) or (isinstance(value, str) and 'new Date' in value) or value=='null':
            return str(value)
        elif isinstance(value, datetime):
            if include_time_in_dates:
                return json.dumps(value.strftime('%Y-%m-%d %H:%M'))
            else:
                return json.dumps(value.strftime('%Y-%m-%d'))
        elif isinstance(value, str) and value.startswith('{') and value.endswith('}'):
            return value
        else:
            return json.dumps(value)

    colnames = json.dumps(list(df.columns))
    rowdata = [list(row[1:]) for row in df.itertuples()]
    if date_columns is not None:
        for date_column in date_columns:
            for row in rowdata:
                if isinstance(row[date_column], str):
                    try:
                        d = datetime.strptime(row[date_column], '%Y-%m-%d')
                    except:
                        d = datetime.strptime(row[date_column], '%Y-%m')
                else:
                    d = row[date_column]
                row[date_column] = 'new Date({y},{m},{d},{H},{M})'.format(y=d.year, m=d.month-1, d=d.day, H=d.hour, M=d.minute)
    rowdata = ['[' +
               ', '.join(
                   [convert_value(val) for val in row]
               )
               + ']' for row in rowdata]
    rowdata = ',\n'.join(rowdata)
    return {prefix + '_columns': colnames,
            prefix + '_rows': rowdata.replace(' nan,', ' null,').replace(' nan]', ' null]')}