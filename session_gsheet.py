import time
from collections import defaultdict
from datetime import date


class Session:

    def __init__(self,sheet):
        self.worksheet = sheet
        self.date_offset = 13
        self.report_offset = 50

    @staticmethod
    def show_logs(filepath):
        with open(filepath) as f:
            for i in f.readlines():
                print(i, end='')


    def write_logs(self, data: dict, filepath='session_logs.txt'):
        def get_current_time():
            return time.strftime("%Y-%m-%d  %H:%M:%S", time.localtime(time.time()))

        with open(filepath, 'a') as file:
            file.write(self.date_offset*'-'+ get_current_time()+ self.date_offset*'-'+'\n')
            file.write(str(data))
            file.write('\n' +  self.report_offset * '-' + '\n')

    @staticmethod
    def find_duplicates_indices(data:list):
        tally = defaultdict(list)
        for i, item in enumerate(data):
            tally[item].append(i)
        return ((key, locs) for key, locs in tally.items()
                if len(locs) > 1)

    def check_for_duplicates(self, cols: list):
        redundant_locs = {}
        flag = False
        for col in cols:
            data = self.worksheet.col_values(col)
            if (len(set(data)) != len(data)):
                flag = True
                duplicates = self.find_duplicates_indices(data)
                for (item, locs) in duplicates:
                    redundant_locs[item]=(locs[1:], col)
        if flag:
            self.write_logs(data=redundant_locs)
            self.rewrite_column([list(set(self.worksheet.col_values(col))) for col in cols], cols)
        return redundant_locs

    def rewrite_column(self, data: list, cols):
        for col in cols:
            self.worksheet.delete_columns(col, col)
            row = 1
            for val in data[0]:
                self.worksheet.update_cell(row,col,val)
                row+=1
