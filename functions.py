import datetime
import os.path


def logger(log_id, event, des):
    log_id = log_id.lower()
    log_file_name = log_id + "_log.txt"
    if not os.path.exists(log_file_name):
        # Initialising of log file for THIS entity
        with open(log_file_name, "w") as log_file:
            log = \
                '"file_name": "' + log_file_name + '", \n' + \
                '"creation": "' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '", \n' + \
                '"last update": "' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '",\n' + \
                '"logs":\n'
            log_file.write(log)
    # Now do the log
    with open(log_file_name, "r") as log_up_file:
        # read a list of lines into line variable
        line = log_up_file.readlines()
        line[2] = '"last update": "' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '",\n'
    with open(log_file_name, 'w') as log_up_file:
        # and write everything back
        log_up_file.writelines(line)
    with open(log_file_name, 'a') as log_up_file:
        # append log to file
        n_log = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '"    "' + event + '"    "' + des + '",\n'
        log_up_file.write(n_log)


def sort_and_clean(array_of_lists):
    final_list = []
    for list_str in array_of_lists:
        # Here I used my defined str_to_list function. Look at the next function.
        final_list = final_list + str_to_list(list_str)
    # sort by piece frequency from "RARE TO COMMON"
    sorted_list = sorted(final_list, key=final_list.count, reverse=False)
    # remove duplicates
    remove_duplicates = []
    for i in sorted_list:
        if i not in remove_duplicates:
            remove_duplicates.append(i)
    return remove_duplicates


def str_to_list(string, key_type = "int"):
    string = string[1:-1]  # remove first and last curly brackets =  removing {}
    if len(string) > 1:
        if key_type == "str":
            list_map_object = string.split(',')
        else:
            list_map_object = map(int, string.split(','))
            # # for list to list appending(Not list to array appending), we could use line below :
            # pieces_list = pieces_list.extend(list(pieces_map_object))
        return list(list_map_object)
    else:
        return []
