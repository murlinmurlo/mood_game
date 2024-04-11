import sys
import calendar


def restcalend(Y, M):
    '''ReSTify calendar().

:param Y: Year
:param M: Month
:return: ReSTified calendar'''

    print('.. table:: ', end ='')
    title, days, *nums = calendar.month(yr, mth).split('\n')

    print(title.replace('  ', ''))
    print()
    print('    == == == == == == ==')
    print('   ', days)
    print('    == == == == == == ==')
    for num in nums[:-1]:
        print('   ', num)
    print('    == == == == == == ==')

if '__name__' == '__main__':
    yr = int(sys.argv[1])
    mth = int(sys.argv[2])
    restcalend(yr, mth)