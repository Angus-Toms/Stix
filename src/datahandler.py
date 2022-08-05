from typing import List
import csv
import xlsxwriter

class DataHandler():
    def __init__(self):
        return
        
    """
    FILE WRITING AND READING        
    """
    def list_to_csv(self, data: List[List], fname: str) -> None:
        """ Write contents of 2D list to .csv file  

        Args:
            data (List[List]): 2D list being written
            fname (str): File being written to
        """
        with open((fname), 'w') as csv_file:
            writer = csv.writer(csv_file)
            for row in data:
                clean_row = []
                for i in range(len(row)):
                    try:
                        clean_row.append(round(row[i], 4))
                    except:
                        clean_row.append(row[i])

                writer.writerow(clean_row)
                
    def list_to_xlsx(self, data: List[List], fname: str) -> None:
        """ Write contents of 2D list to .xlsx file  

        Args:
            data (List[List]): 2D list being written
            fname (str): File being written to
        """
        workbook = xlsxwriter.Workbook(fname)
        worksheet = workbook.add_worksheet()

        for i in range(len(data)):
            for j in range(len(data[0])):
                try:
                    worksheet.write(i, j, round(data[i][j], 4))
                except:
                    worksheet.write(i, j, data[i][j])

        workbook.close()
