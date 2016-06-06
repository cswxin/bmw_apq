""" Make sure the filename is in the form of a abs path,
    or a relative path when the spreadsheet file or its sub dir is in the same location with easyExcel.py
    Row & Col index are 1 based for default
"""
import win32com.client

import os
import time
import string
import win32api

class ArguErr:pass

#Constants
"""I have no idea of how to use the original constants class in the gen_py package,
   so just create a mini one below :-(
"""
class constants:
    xlRed = win32api.RGB(255, 0, 0)
    xlGreen = win32api.RGB(0, 255, 0) 
    xlBlue = win32api.RGB(0, 0, 255)
    xlMagenta = win32api.RGB(255, 0, 255)
    xlHairline = 0x1        # from enum XlBorderWeight
    xlMedium = -4138      # from enum XlBorderWeight
    xlThick = 0x4        # from enum XlBorderWeight
    xlThin = 0x2        # from enum XlBorderWeight
    xlContinuous = 0x1        # from enum XlLineStyle
    xlDash = -4115      # from enum XlLineStyle
    xlDashDot = 0x4        # from enum XlLineStyle
    xlDashDotDot = 0x5        # from enum XlLineStyle
    xlDot = -4118      # from enum XlLineStyle
    xlDouble = -4119      # from enum XlLineStyle
    xlLineStyleNone = -4142      # from enum XlLineStyle
    xlSlantDashDot = 0xd        # from enum XlLineStyle
    xlDiagonalDown = 0x5        # from enum XlBordersIndex
    xlDiagonalUp = 0x6        # from enum XlBordersIndex
    xlEdgeBottom = 0x9        # from enum XlBordersIndex
    xlEdgeLeft = 0x7        # from enum XlBordersIndex
    xlEdgeRight = 0xa        # from enum XlBordersIndex
    xlEdgeTop = 0x8        # from enum XlBordersIndex
    xlInsideHorizontal = 0xc        # from enum XlBordersIndex
    xlInsideVertical = 0xb        # from enum XlBordersIndex
    xlPasteAll = -4104      # from enum XlPasteType
    xlPasteAllExceptBorders = 0x7        # from enum XlPasteType
    xlPasteColumnWidths = 0x8        # from enum XlPasteType
    xlPasteComments = -4144      # from enum XlPasteType
    xlPasteFormats = -4122      # from enum XlPasteType
    xlPasteFormulas = -4123      # from enum XlPasteType
    xlPasteFormulasAndNumberFormats = 0xb       # from enum XlPasteType
    xlPasteValidation = 0x6        # from enum XlPasteType
    xlPasteValues = -4163      # from enum XlPasteType
    xlPasteValuesAndNumberFormats = 0xc        # from enum XlPasteType
   
class easyExcel:
    """A utility to make it easier to get at Excel.  Remembering
    to save the data is your problem, as is  error handling.
    Operates on one workbook at a time."""
    
    def __init__(self, filename=None):
        import pythoncom
        pythoncom.CoInitialize()
        self.xlApp = win32com.client.Dispatch('Excel.Application')
        self.xlApp.DisplayAlerts = False
        if filename:
            if os.path.isabs(filename):
                self.filename = filename
            else:
                self.filename = os.path.abspath(filename)
            assert os.path.isfile(self.filename), "No such file exists in your located path!"
            self.xlBook = self.xlApp.Workbooks.Open(self.filename)
            
        else:
            self.xlBook = self.xlApp.Workbooks.Add()
            self.filename = ''
    
    def save(self, newfilename=None):
        if newfilename:
            self.filename = newfilename
            self.xlBook.SaveAs(newfilename)
        else:
            self.xlBook.Save()

    def close(self):
        self.xlBook.Close(SaveChanges=0)
        del self.xlApp
   
    def show(self):
        self.xlApp.Visible = 1
        
    def hide(self):
        self.xlApp.Visible = 0

#
#    now for the helper methods
#
    def setRangeValBySheetIndex(self, sheet_index, rangeStr, Val):
        """supply a simply way to access the large indexed cells
        """
        sht = self.xlBook.Sheets(sheet_index)
        sht.Range(rangeStr).Value = Val

    def getRangeValBySheetIndex(self, sheet_index, rangeStr):
        """supply a simply way to access the large indexed cells
        """
        sht = self.xlBook.Sheets(sheet_index)
        return sht.Range(rangeStr).Value
    
    def setRangeVal(self, sheet, rangeStr, Val):
        """supply a simply way to access the large indexed cells
        """
        sht = self.xlBook.Worksheets(sheet)
        sht.Range(rangeStr).Value = Val

    def getRangeVal(self, sheet, rangeStr):
        """supply a simply way to access the large indexed cells
        """
        sht = self.xlBook.Worksheets(sheet)
        return sht.Range(rangeStr).Value

    def getSheetsCount(self):
        return self.xlBook.Worksheets.Count

    def setBorderStyle(self, sheet, range, style):
        """
        range can be any form of the legal Excel format!
        xlHairline                    =0x1        # from enum XlBorderWeight
	xlMedium                      =-4138      # from enum XlBorderWeight
	xlThick                       =0x4        # from enum XlBorderWeight
	xlThin                        =0x2        # from enum XlBorderWeight
	xlContinuous                  =0x1        # from enum XlLineStyle
	xlDash                        =-4115      # from enum XlLineStyle
	xlDashDot                     =0x4        # from enum XlLineStyle
	xlDashDotDot                  =0x5        # from enum XlLineStyle
	xlDot                         =-4118      # from enum XlLineStyle
	xlDouble                      =-4119      # from enum XlLineStyle
	xlLineStyleNone               =-4142      # from enum XlLineStyle
	xlSlantDashDot                =0xd        # from enum XlLineStyle
	xlDiagonalDown                =0x5        # from enum XlBordersIndex
	xlDiagonalUp                  =0x6        # from enum XlBordersIndex
	xlEdgeBottom                  =0x9        # from enum XlBordersIndex
	xlEdgeLeft                    =0x7        # from enum XlBordersIndex
	xlEdgeRight                   =0xa        # from enum XlBordersIndex
	xlEdgeTop                     =0x8        # from enum XlBordersIndex
	xlInsideHorizontal            =0xc        # from enum XlBordersIndex
	xlInsideVertical              =0xb        # from enum XlBordersIndex
        """
        if len(style) == 3:
            linestyle, color, weight = style
            sht = self.xlBook.Worksheets(sheet)
            sht.Range(range).Borders.LineStyle = linestyle
            sht.Range(range).Borders.Weight = weight
            sht.Range(range).Borders.Color = color
        else:
            borderindex, linestyle, color, weight = style
            sht = self.xlBook.Worksheets(sheet)
            sht.Range(range).Borders(borderindex).LineStyle = linestyle
            sht.Range(range).Borders(borderindex).Weight = weight
            sht.Range(range).Borders(borderindex).Color = color
        
    def setRowFont(self, sheet, row, font):
        fontname, size, bold, italic = font
        sht = self.xlBook.Worksheets(sheet)
        sht.Range("%s:%s" % (row, row)).Font.Name = fontname 
        sht.Range("%s:%s" % (row, row)).Font.Size = size 
        sht.Range("%s:%s" % (row, row)).Font.Bold = bold 
        sht.Range("%s:%s" % (row, row)).Font.Italic = italic 

    def pasteRow(self, sheet, row, pastevalues=1):
        """
        xlPasteAll                    =-4104      # from enum XlPasteType
	xlPasteAllExceptBorders       =0x7        # from enum XlPasteType
	xlPasteColumnWidths           =0x8        # from enum XlPasteType
	xlPasteComments               =-4144      # from enum XlPasteType
	xlPasteFormats                =-4122      # from enum XlPasteType
	xlPasteFormulas               =-4123      # from enum XlPasteType
	xlPasteFormulasAndNumberFormats=0xb       # from enum XlPasteType
	xlPasteValidation             =0x6        # from enum XlPasteType
	xlPasteValues                 =-4163      # from enum XlPasteType
	xlPasteValuesAndNumberFormats =0xc        # from enum XlPasteType
        """
        sht = self.xlBook.Worksheets(sheet)
	#sht.Range(sht.Cells(row,1), sht.Cells(row,256)).PasteSpecial()
        if pastevalues:
            sht.Range("%s:%s" % (row, row)).PasteSpecial(constants.xlPasteValues)
        else:
            sht.Range("%s:%s" % (row, row)).PasteSpecial()

    def copyRow(self, sheet, row):
        "row index based on 1"
        sht = self.xlBook.Worksheets(sheet)
        sht.Rows[row - 1].Copy()

    def addComments(self, sheet, row, col, comment, visible=0):
        self.xlBook.Worksheets(sheet).Cells(row, col).AddComment(comment)
        self.xlBook.Worksheets(sheet).Cells(row, col).Comment.Visible = visible

    def setRowColor(self, sheet, row, color=constants.xlMagenta):
        "row based on 1, color use RGB"
        self.xlBook.Worksheets(sheet).Rows[row - 1].Font.Color = color

    def setColumnColor(self, sheet, col, color=constants.xlBlue):
        "column based on 1, color use RGB"
        self.xlBook.Worksheets(sheet).Columns[col - 1].Font.Color = color

    def getCell(self, sheet, row, col):
        "Get value of one cell"
        sht = self.xlBook.Worksheets(sheet)
        return sht.Cells(row, col).Value

    def setCell(self, sheet, row, col, value):
        "set value of one cell"
        sht = self.xlBook.Worksheets(sheet)
        sht.Cells(row, col).Value = value
        
    def getRowCnt(self, sheet):
        "Get row count used in the selected sheet, incontiguous"
        sht = self.xlBook.Sheets(sheet)
        return sht.UsedRange.Rows.Count

    def getColCnt(self, sheet):
        "Get column count used in the selected sheet, incontiguous"
        sht = self.xlBook.Sheets(sheet)
        return sht.UsedRange.Columns.Count
    
    def getRangeObj(self, sheet, *fmt):
        """return the range object so as to deal with each cell in the for statement.
        Now you can use the A1 format of the range object or supply the 4 index of row1, col1, row2, col2
        >>> def test(a,*fmt):
        ... 	print len(fmt),fmt
        ... 
        >>> test(1,1,2,3,5)
        4 (1, 2, 3, 5)
        >>> test(1,"luhero")
        1 ('luhero',)"""
        sht = self.xlBook.Worksheets(sheet)
        if len(fmt) == 1:
            return sht.Range(fmt[0])
        elif len(fmt) == 4:
            row1, col1, row2, col2 = fmt
            return sht.Range(sht.Cells(row1, col1), sht.Cells(row2, col2))
        else: raise ArguErr

    def getRange(self, sheet, row1, col1, row2, col2):
        "return a 2d array (i.e. tuple of tuples)"
        sht = self.xlBook.Worksheets(sheet)
        return sht.Range(sht.Cells(row1, col1), sht.Cells(row2, col2)).Value
    
    def setRange(self, sheet, topRow, leftCol, data):
        """insert a 2d array starting at given location. 
        Works out the size needed for itself"""
        
        bottomRow = topRow + len(data) - 1
        rightCol = leftCol + len(data[0]) - 1
        sht = self.xlBook.Worksheets(sheet)
        sht.Range(
            sht.Cells(topRow, leftCol),
            sht.Cells(bottomRow, rightCol)
            ).Value = data

    def getContiguousRange(self, sheet, row, col):
        """Tracks down and across from top left cell until it
        encounters blank cells; returns the non-blank range.
        Looks at first row and column; blanks at bottom or right
        are OK and return None witin the array"""
        
        sht = self.xlBook.Worksheets(sheet)
        
        # find the bottom row
        bottom = row
        while sht.Cells(bottom + 1, col).Value not in [None, '']:
            bottom = bottom + 1
        
        # right column
        right = col
        while sht.Cells(row, right + 1).Value not in [None, '']:
            right = right + 1
        
        return sht.Range(sht.Cells(row, col), sht.Cells(bottom, right)).Value
 
    def fixStringsAndDates(self, aMatrix):
        # converts all unicode strings and times
        newmatrix = []
        for row in aMatrix:
            newrow = []
            for cell in row:
                if type(cell) is UnicodeType:
                    newrow.append(str(cell))
                elif type(cell) is TimeType:
                    newrow.append(int(cell))
                else:
                    newrow.append(cell)
            newmatrix.append(tuple(newrow))
        return newmatrix
    
    def deleteRow(self, sheet, row):
        sht = self.xlBook.Worksheets(sheet)
        sht.Rows(row).Delete()
    
    def setSheetName(self, sheet, newname):
        sht = self.xlBook.Worksheets(sheet)
        sht.Name = newname
    
class easyWord:
    """A utility to make it easier to get at Excel.  Remembering
    to save the data is your problem, as is error handling.
    """ 
    def __init__(self, filename=None):
        self.docApp = win32com.client.Dispatch('Word.Application')
        if filename:
            if os.path.isabs(filename):
                self.filename = filename
            else:
                self.filename = os.path.abspath(filename)
            assert os.path.isfile(self.filename), "No such file exists in your located path!"
            self.docBook = self.docApp.Documents.Open(self.filename)
            
        else:
            self.docBook = self.docApp.Documents.Add()
            self.filename = ''  
    
    def save(self, newfilename=None):
        if newfilename:
            self.filename = newfilename
            self.docBook.SaveAs(newfilename)
        else:
            self.docBook.Save()

    def close(self):
        self.docBook.Close(SaveChanges=0)
        del self.docApp
   
    def show(self):
        self.docApp.Visible = 1
        
    def hide(self):
        self.docApp.Visible = 0
        
def HoneywellTask():
    cst = constants()
    spr = easyExcel('tmp.xls')
    spr.show()
    
    totalcnt = 0
    for i in range(1, 1030):
        tmp = spr.getRangeVal('sheet1', 'a%d' % i)
        if tmp not in [None, '']:totalcnt += 1

    print 'Total sb num is :', totalcnt

if __name__ == "__main__":
    HoneywellTask()
    
    
"""
The following table illustrates some A1-style references using the Range property.
Reference                Meaning 
Range("A1")              Cell A1 
Range("A1:B5")           Cells A1 through B5 
Range("C5:D9,G9:H16")    A multiple-area selection 
Range("A:A")             Column A 
Range("1:1")             Row 1 
Range("A:C")             Columns A through C 
Range("1:5")             Rows 1 through 5 
Range("1:1,3:3,8:8")     Rows 1, 3, and 8 
Range("A:A,C:C,F:F")     Columns A, C, and F 
"""    
