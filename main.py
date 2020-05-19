from auto_enroller import *
import time, config, sys, vlc, threading, select, os, login_credentials_DO_NOT_PUSH, traceback
from tqdm.auto import tqdm

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

## dont forget to add support for linux and windoww chrome drivers, get python to detect the OS for this and download appropriate drivers.


def get_academic_timetable_url_input() -> str:

    # Gets input from user for which timetable they want to use. Loops until 1 or 2 is selected as they are the
    # only valid answers
    while True:

        timetable = input('\nSelect which academic timetable you would like to set the alert in. (ENTER 1 or 2) \n\n'
                          'Available options: \n'
                          '1. Summer\n'
                          '2. Fall/Winter\n\n'
                          'Input: ')
        print('')

        if timetable not in ['1', '2']:
            print('ERROR: Incorrect entry. Make sure you inputted the number and not the text')
            continue
        else:
            if timetable == '1':
                timetable_url = config.urls_dict['Summer']
                return timetable_url
            elif timetable == '2':
                timetable_url = config.urls_dict['Fall/Winter']
                return timetable_url


def get_courses_list_input() -> list:

    try:

        while True:

            # gets course names input from user
            course_names = input(
                'Enter the course name, course code, and class nbr, seperated by commas for multiple courses. Each portion of the course must be seperated by a space. (Example: COMPSCI 1026A 1625, PSYCHOL 2035A 1210)\n\n'
                'Input: ')
            print('')

            # if strong is empty, it asks the user to re-enter it.
            if course_names == '':
                print('ERROR: Empty course name. Try again.\n')
                continue

            # splits courses by the commas in the string, storing split values in a list
            courses = course_names.split(',')

            #empty list to store valid course inputs, course must have 3 components to be stored. course name,
            # course number, and class_nbr

            courses_list = []

            # iterates through courses list (course names inputted by user)
            for course in courses:

                # seperates each course name entry into its course name, course number, and class nbr components
                # if it's a valid enbtry
                course = course.strip().split(' ')

                # if course has 3 components (course_name, course_number, and class_nbr), we add the course (which is
                # a list of 3 elements to the course_list, creating a list of lists

                if len(course) == 3:
                    courses_list.append(course)

                elif len(course) < 3:
                    print(
                        'ERROR: COURSE COMPONENTS MISSING IN {0}. Make sure each course has 3 components. A course name, course number, and a class nbr (can be found in timetable).\n'.format(
                            course))
                else:
                    print(
                        'ERROR: TOO MANY COURSE COMPONENTS IN {0}. Make sure each course has 3 components. A course name, course number, and a class nbr (can be found in timetable).\n'.format(
                            course))

                # if the number of entries in courses_list is the same as the number of entries in courses (the
                # original user input, then all of the user's input for courses hae been added to the courses_list and
                # therefore have 3 components as required

                if len(courses_list) == len(courses):
                    return courses_list

    except Exception as e:
        print(e)


def get_chrome_path_input() -> str:

    while True:

        chrome_version = input('\nSelect the version of your Google Chrome browser. This can be found in Help -> About Google Chrome. (ENTER 1,2, or 3)\n\n'
                          'Available options: \n'
                          '1. 80.0.3987.106\n'
                          '2. 81.0.4044.138\n'
                          '3. 83.0.4103.39\n\n'
                          'Input: ')
        print('')

        my_path = os.path.dirname(__file__)

        if chrome_version not in ['1', '2', '3']:
            print('ERROR: Incorrect entry. Make sure you inputted the number and not the text')
            continue

        elif chrome_version == '1':
            chrome_path = os.path.join(my_path, "chromedriver_mac_80.0.3987.106")

        elif chrome_version == '2':
            chrome_path = os.path.join(my_path, "chromedriver_mac_81.0.4044.138")

        elif chrome_version == '3':
            chrome_path = os.path.join(my_path, "chromedriver_mac_83.0.4103.39")

        return chrome_path


def get_all_dfs_for_courses(courses_list: list, auto_enroller: AutoEnroller) -> dict:

    all_dfs_for_courses = {}

    for course in tqdm(courses_list):

        course_name = course[0]
        course_number = course[1]
        class_nbr = course[2]

        auto_enroller.set_all_course_sections_df(course_name, course_number)
        time.sleep(10)

        all_dfs_for_courses[(course_name, course_number, class_nbr)] = auto_enroller.all_course_sections_df

    # returns dictionary of pandas Dataframe where each key is the class_nbr. Can have empty pandas Dataframe
    # if the course name and course number don't exist
    return all_dfs_for_courses


def all_inputted_courses_exist(all_dfs_for_courses: dict, auto_enroller: AutoEnroller) -> bool:

    try:
        # empty list to store booleans of whether the course exists or not
        course_sections_exists = {}

        print('Checking if course sections inputted exist in the timetable...')

        for course, df in all_dfs_for_courses.items():
            auto_enroller.all_course_sections_df = df
            # course[2] is class_nbr, check get_all_dfs_for_courses method for reference
            course_sections_exists[course] = auto_enroller.course_section_exists(course[2])

        # If all values in list are True then they all exist and it returns the courses list containing all of them
        if all(bool == True for course, bool in course_sections_exists.items()):
            print('SUCCESS: ALL COURSES INPUTTED FOUND IN THE TIMETABLE\n')
            return True

        # Atleast 1 of the course names inputted doesn't exists and asks the user to re-enter the course names.
        # First notifies the user which course was incorrect though.
        else:
            for course, bool in course_sections_exists.items():
                if bool == False:
                    print(
                        'ERROR: {0} {1} {2} NOT FOUND IN TIMETABLE. Make sure you have spelled the course name, course code, and class nbr correctly and you have selected the right timetable.\n'.format(
                            course[0].upper().strip(), course[1].upper().strip(),
                            course[2].upper().strip()))
            return False

    except:
        print('ERROR:')
        print(traceback.format_exc())


def auto_enroll() -> bool:

    while True:

        auto_enroll = input('Would you like to AUTO ENROLL in these courses as soon as they are available? (Enter Y or N)\n\n'
                            'Input: ').lower()
        print('')

        if auto_enroll not in ['y','n']:
            print('ERROR: Incorrect entry. Make sure you inputted Y or N.')
            continue
        elif auto_enroll == 'y':
            return True
        #auto_enroll == 'n'
        else:
            return False


def get_dependant_components_for_courses_input(courses_list: list, all_dfs_for_courses: dict, auto_enroller: AutoEnroller):

    dependant_components_for_courses_input = {}

    for course in courses_list:
        course_name = course[0]
        course_number = course[1]
        class_nbr = course[2]

        auto_enroller.all_course_sections_df = all_dfs_for_courses[(course_name, course_number, class_nbr)]

        dependant_components_for_course_input = list()

        if auto_enroller.has_dependant_course_components():


            course_section_location = auto_enroller.get_course_location_for_course_section(class_nbr)

            dependant_components_df = auto_enroller.get_dependant_course_components_df(class_nbr)

            dependant_lab_components_df = dependant_components_df.loc[(dependant_components_df['course_component'] == 'LAB') & (dependant_components_df['course_location'] == course_section_location)]
            dependant_tut_components_df = dependant_components_df.loc[(dependant_components_df['course_component'] == 'TUT') & (dependant_components_df['course_location'] == course_section_location)]
            dependant_lec_components_df = dependant_components_df.loc[(dependant_components_df['course_component'] == 'LEC') & (dependant_components_df['course_location'] == course_section_location)]

            # one of these is expected to be empty because whatever componenet I choose will only have 2 dependant course
            # components at its maximum. This is because a course can only have 3 course components in total.

            ## add feature later to add multiple of the same components for a variety of options for enrolling. User
            # sections based on preference and if none of the preferences are available then it picks the first open slot
            for dependant_component_df in [dependant_lab_components_df, dependant_lec_components_df, dependant_tut_components_df]:
                if not dependant_component_df.empty:
                    while True:

                        print("This {0} {1} {2} has a required '{3}' component.\n".format(course_name.upper(), course_number.upper(), class_nbr, dependant_component_df.iloc[0]['course_component']))
                        print("""
                        Please enter the index values (numbers of the leftmost coloumn) for the desired '{0}' 
                        component you would like to enroll in. Enter values based on order of preference (most preferred
                        to least preferred). Any values not entered will be considered as possible options if all other
                        sections entered are full.
                        
                        Note: Only sections that have the same course location as the course inputted originally are
                        shown as possible options because it is assumed that students cannot enroll in a course with 
                        course components scattered across MAIN and other affiliate colleges. For example, a student
                        cannot enroll in a LEC on MAIN campus and a LAB on KINGS campus.
                        """.format(dependant_component_df.iloc[0]['course_component']))

                        print(dependant_component_df)

                        print('')
                        input_index_list = input('Input: ')
                        print('')

                        try:
                            # splits user inputs into seperate index strings
                            input_index_list = input_index_list.strip().split(',')

                            cleaned_input_index_list = []
                            for input_index in input_index_list:
                                cleaned_input_index = input_index.strip()
                                cleaned_input_index_list.append(cleaned_input_index)

                            input_index_list = cleaned_input_index_list

                            # converts all index strings in list to integers and adds them to a new list
                            int_input_index_list = [int(val) for val in input_index_list]

                            # adds remaining course sections not inputted by user (least preferred) to the end of the
                            # inputted index list
                            all_indexes = dependant_component_df.index.values.tolist()
                            remaining_indexes = [i for i in all_indexes if i not in int_input_index_list]
                            int_input_index_list.extend(remaining_indexes)

                        except:
                            print('ERROR: Index must be a number. Please re-try')
                            continue

                        # if all inputted indexes are in the df.index (entries are valid) and the inputted list is
                        # not empty
                        if all(1 <= index <= len(dependant_component_df.index) for index in int_input_index_list) and int_input_index_list:

                            # 2d list containing all the sections for the component (ie. all LAB components)
                            dependant_component_list = list()

                            for index in int_input_index_list:

                                # 1d list
                                dependant_component = list()

                                dependant_comp = dependant_component_df.iloc[index-1] #actual index is index - 1
                                dependant_comp_class_nbr = dependant_comp['class_nbr']
                                dependant_comp_course_component = dependant_comp['course_component']

                                dependant_component.append(dependant_comp_class_nbr)
                                dependant_component.append(dependant_comp_course_component)

                                dependant_component_list.append(dependant_component)

                            # adds 2d list to list, eventually returns 3d list
                            dependant_components_for_course_input.append(dependant_component_list)

                            #break out while loop for this dependant_component_df and moves on to next
                            break

                        else:
                            not_found_indexes = [index for index in int_input_index_list if index > len(dependant_component_df.index) or index < 1]
                            print('ERROR: Index {0} not found. Please re-try.'.format(not_found_indexes))
                            continue

        # values are 3d lists, if course has no dependants, value is a 1d empty list
        dependant_components_for_courses_input[(course_name, course_number, class_nbr)] = dependant_components_for_course_input

    # returns dict, some values of keys can be empty lists if course section has no dependant components
    return dependant_components_for_courses_input


def alert(course: list):

    try:

        course_name = course[0]
        course_number = course[1]
        class_nbr = course[2]

        print('{0} {1} with class number {2} is now available!'.format(course_name.upper(), course_number.upper(), class_nbr))

        # plays sound, once ended, system talks
        p = vlc.MediaPlayer("Red Alert-SoundBible.com-108009997.mp3")
        p.play()
        time.sleep(3)

        os.system('say "the course {0} {1} with class number {2} is now available!"'.format(course_name.upper(), course_number.upper(), class_nbr))

    except:
        print('ERROR:')
        print(traceback.format_exc())


def main():

    timetable_url = get_academic_timetable_url_input()
    chrome_path = get_chrome_path_input()
    courses_list = get_courses_list_input()

    auto_enroller = AutoEnroller(chrome_path, timetable_url, config.urls_dict['Student_Center_Login_Page'], login_credentials_DO_NOT_PUSH.login_creds['username'], login_credentials_DO_NOT_PUSH.login_creds['password'])

    print('Retrieving all sections for each course from the selected timetable...')
    all_dfs_for_courses = get_all_dfs_for_courses(courses_list, auto_enroller)
    print('')

    # if courses inputted by user exists, it continues, otherwise, asks again for input
    while True:
        if all_inputted_courses_exist(all_dfs_for_courses, auto_enroller):
            break
        else:
            courses_list = get_courses_list_input()

    # asks whether they would like to auto enroll in the courses
    bool_auto_enroll = auto_enroll()

    # Initiates dict()mt0o store depedant course components inputted for all courses inputted
    dependant_components_for_courses_input = dict()

    # if auto enrolling is selected
    if bool_auto_enroll:
        dependant_components_for_courses_input = get_dependant_components_for_courses_input(courses_list, all_dfs_for_courses, auto_enroller)

    # while there are still courses that have not become available yet, script continues
    while len(courses_list) > 0:

        print('Reloading timetable and updating section information for remaining courses...')
        all_dfs_for_courses = get_all_dfs_for_courses(courses_list, auto_enroller)
        print('')

        for index, course in enumerate(courses_list):

            course_name = course[0]
            course_number = course[1]
            class_nbr = course[2]

            auto_enroller.all_course_sections_df = all_dfs_for_courses[(course_name, course_number, class_nbr)]

            # seperates the dependant components of a course into a dict comprising of its LAB, TUT, or LEC as keys

            dependant_course_components_dict = {}

            # if dict has elements in it
            if dependant_components_for_courses_input:
                # if value (which is a list) for the key is not empty, it means this course section has at least one
                # dependant course component
                if dependant_components_for_courses_input[(course_name, course_number, class_nbr)]:

                    dependant_course_components = dependant_components_for_courses_input[(course_name, course_number, class_nbr)]

                    for dependant_course_component in dependant_course_components:
                        # gets first list and second val for course component name as key, ex: ['1210','LAB]
                        course_component_name = dependant_course_component[0][1]
                        dependant_course_components_dict[course_component_name] = dependant_course_component

            # if course section is not full
            if not auto_enroller.course_section_is_full(class_nbr):

                # if auto enroll selected
                if bool_auto_enroll:

                    # 2d list, will convert to dict after for passing to function
                    selected_components_to_enroll_in = []

                    for key, component in dependant_course_components_dict.items():
                        for indiv_component in component:
                            # select class of the individual component and check if its full, if not full, then add it
                            # for enrollment and then stop since they are added in order most preferred to least preferred to list.
                            if not auto_enroller.course_section_is_full(indiv_component[0]):
                                selected_components_to_enroll_in.append(indiv_component)
                                break

                    args ={}

                    for index, selected_component in enumerate(selected_components_to_enroll_in):
                        key = 'dependant_class_nbr_with_course_component_list_' + str(index+1)
                        args[key] = selected_component

                    # alert and enroll
                    alert(course)
                    if args:
                        auto_enroller.enroll(course_name, course_number, class_nbr, **args)
                    else:
                        auto_enroller.enroll(course_name, course_number, class_nbr)

                # if auto enroll not selected alert goes on loop instead until key is pressed
                else:
                    while True:
                        print("Press <Enter> to stop the alert!")
                        alert(course)

                        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                            line = input()
                            break

                # delete the course from the courses_list because don;t need to search for it anymore
                del courses_list[index]

                # atleast another course must be in queue for searching after the found one is dropped
                # for this if statment to be triggered

                if len(courses_list) > 0:
                    print('Moving onto the next course...\n')

            # course section is full
            else:
                print('{0} {1} {2} is full. Will re-try in 5 seconds.'.format(course_name.upper(), course_number.upper(),class_nbr))


if __name__ == '__main__':
    main()








