import calendar

def restcalend(year, month):
   
    cal = calendar.monthcalendar(year, month)

    
    table_header = ".. table:: {} {}\n\n".format(calendar.month_name[month], year)
    table_header += "\n    == == == == == == ==\n"
    table_header += "    Mo Tu We Th Fr Sa Su\n"
    table_header += "    == == == == == == ==\n"

    
    table_rows = ""
    for week in cal:
        row = "    "
        for day in week:
            if day == 0:
                row += "   "
            else:
                row += "{:2d} ".format(day)
        row += "\n"
        table_rows += row

  
    table_footer = "    == == == == == == ==\n"

   
    return table_header + table_rows + table_footer

print(restcalend(2024, 4))
