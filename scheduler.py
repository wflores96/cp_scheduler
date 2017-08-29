'''
gets 4 weekends off
goes by who submitted first
up to 8 execs and 4 directors off
whoever asks off gets priority
'''
import csv
import sys

################### GLOBALS #######################

# EDIT THIS
filename = 'Responses.csv'
member_max_nights_off = 4
max_execs_off = 8
max_dires_off = 4
# DONT EDIT THE REST OF THESE
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

nights_table = {}
members = []
needs_another_night = set()
# End Globals

if len(sys.argv) == 2:
    filename = sys.argv[1]
elif len(sys.argv) > 2:
    print('USAGE: python|python3 scheduler.py [filename]')

# Class Defs

class Date:

    @classmethod
    def get_int_from_month(cls, month):
        if month == 'Jan':
            return 1
        elif month == 'Feb':
            return 2
        elif month == 'Mar':
            return 3
        elif month == 'Apr':
            return 4
        elif month == 'May':
            return 5
        elif month == 'Jun':
            return 6
        elif month == 'Jul':
            return 7
        elif month == 'Aug':
            return 8
        elif month == 'Sep':
            return 9
        elif month == 'Oct':
            return 10
        elif month == 'Nov':
            return 11
        elif month == 'Dec':
            return 12
        else:
            return -1

    @classmethod
    def get_month_from_int(cls, month_int):
        if month_int == 1:
            return 'Jan'
        elif month_int == 2:
            return 'Feb'
        elif month_int == 3:
            return 'Mar'
        elif month_int == 4:
            return 'Apr'
        elif month_int == 5:
            return 'May'
        elif month_int == 6:
            return 'Jun'
        elif month_int == 7:
            return 'Jul'
        elif month_int == 8:
            return 'Aug'
        elif month_int == 9:
            return 'Sep'
        elif month_int == 10:
            return 'Oct'
        elif month_int == 11:
            return 'Nov'
        elif month_int == 12:
            return 'Dec'
        else:
            return -1

    def __init__(self, date_string):
        date_arr = date_string.split(' ')
        self.month = int(self.get_int_from_month(date_arr[0]))
        self.day = int(date_arr[1].split('-')[0])

    def __lt__(self, other):
        if self.month < other.month:
            return True
        return self.day < other.day

    def __gt__(self, other):
        if self.month > other.month:
            return True
        return self.day > other.day

    def __str__(self):
        return self.get_month_from_int(self.month) + " " + str(self.day)


class Person:
    def __init__(self, name, pos):
        self.name = name
        self.requested_nights = []
        self.position = pos
        self.assigned = []

    def __str__(self):
        return self.name + ", " + self.position


class Night:
    def __init__(self, _id):
        self.date = _id
        self.exec_count = 0
        self.dir_count = 0
        self.members_on = []


# Function Defs


def convert_directors(filename):
    with open(filename, 'rU') as inputFile:
        data = list(csv.reader(inputFile))
        # separate data into packets and update packets
        for packet in data:
            if packet[1][:3] == 'Dir':
                packet[1] = 'Direc'

    # open same file in write mode, and write updated data
    with open(filename, 'w') as outputFile:
        writer = csv.writer(outputFile)
        for packet in data:
            writer.writerow(packet)


def load_members():
    with open(filename) as inputFile:
        data = list(csv.reader(inputFile))
        for person in data:
            members.append(create_person_from_csv(person))


def create_person_from_csv(person_data):
    person = Person(person_data[0], person_data[1])
    nights_off = person_data[2:]
    for request in nights_off:
        person.requested_nights.append(request)
    return person


# returns true if the person was given a night, otherwise false
def validEntry(person, date):
    # case: first person to request this night
    if date not in nights_table:
        temp_night = Night(date)  # Night object
        if person.position == "Direc":
            temp_night.dir_count += 1
        elif person.position == "Exec":
            temp_night.exec_count += 1
        temp_night.members_on.append(person)  # add person to night
        person.assigned.append(Date(date))
        nights_table[date] = temp_night
        return True
    else:
        night_obj = nights_table[date]
        # case: director and they have a spot available
        if person.position == "Direc" and night_obj.dir_count < max_dires_off:
            person.assigned.append(Date(date))
            night_obj.dir_count += 1
            night_obj.members_on.append(person)
            return True
        # case: exec and they have a spot available
        elif person.position == "Exec" and night_obj.exec_count < max_execs_off:
            person.assigned.append(Date(date))
            night_obj.exec_count += 1
            night_obj.members_on.append(person)
            return True
        # case: night full
        else:
            return False


if __name__ == '__main__':
    convert_directors(filename)
    load_members()
    with open('Assignments.csv', 'w') as output_file:
        done_list = [False] * len(members)
        while False in done_list:
            for (i, member) in enumerate(members):
                if len(member.assigned) < member_max_nights_off:
                    # give this person a night
                    inserted = False
                    while not inserted:
                        if len(member.requested_nights) < 1:
                            print('ran out of choices')
                            needs_another_night.add(member.name)
                            while len(member.assigned) < 4:
                                member.assigned.append(None)
                            break
                        date = member.requested_nights.pop(0)
                        if date.split(' ')[0] not in months:
                            # this member has elected to pick random which we can do later
                            # need to tell us who did this
                            needs_another_night.add(member.name)
                            member.assigned.append(None)
                            break

                        inserted = validEntry(member, date)
                else:
                    # set them as finished
                    done_list[i] = True

        writer = csv.writer(output_file)
        for member in members:
            dates = list(filter(lambda x: x is not None, member.assigned))
            dates = sorted(dates, key=lambda x: x.month*30 + x.day)
            while len(dates) < 4:
                dates.append('NONE')
            line = [member.name]
            for date in dates:
                line.append(str(date))
            writer.writerow(line)

print('THESE PEOPLE NEED NIGHTS ADDED MANUALLY')
print(needs_another_night)
