#!/usr/bin/python
"""
"""

import csv
import sys

ZIPS_CSV_PATH = "slcsp/zips.csv"

PLANS_CSV_PATH = "slcsp/plans.csv"

SLCSP_CSV_PATH = "slcsp/slcsp.csv"

METAL_LEVEL = "Silver"

HEADINGS = ["zipcode", "rate"]

ZIP_CODE_LENGTH = 5

MSG_BAD_ZIP_CODE = f"""ZIP code must be a sequence of {ZIP_CODE_LENGTH} digits.
You are trying to use ZIP code:"""

MSG_OSERROR_READ = "Check ZIPS_CSV_PATH, PLANS_CSV_PATH, and SLCSP_CSV_PATH"

MSG_OSERROR_WRITE = "Check/close file:"

TESTING_MODE = False

SOLUTION_CSV_PATH = "testing/solution.csv"


def read_data(data_csv_path):
    try:
        with open(data_csv_path) as data_csv:
            data = list(csv.reader(data_csv))[1:]
    except OSError as e:
        print(e)
        print(MSG_OSERROR_READ)
        sys.exit(1)
    return data


def filter_zips(zips):
    #            ZIP code     state        rate_area
    zips = set([(zip_code[0], zip_code[1], zip_code[4]) for zip_code in zips])
    seen = set()
    unique_zips = dict()
    duplicate_zips = set()
    for zip_code in zips:
        if zip_code[0] in seen:
            duplicate_zips.add(zip_code[0])
        else:
            seen.add(zip_code[0])
            #           ZIP code        state        rate_area
            unique_zips[zip_code[0]] = [zip_code[1], zip_code[2]]
    return unique_zips, duplicate_zips


def filter_plans(plans):

    #            state    rate     rate_area
    return set([(plan[1], plan[3], plan[4])
                for plan in plans
                if plan[2] == METAL_LEVEL])


def get_slcsp_rate(zip_code, unique_zips, duplicate_zips, plans):

    rate = ""
    if zip_code not in duplicate_zips:
        zip_code_info = unique_zips[zip_code]
        rates = [float(plan[1]) for plan in plans  # rate
                 if plan[0] == zip_code_info[0]    # state
                 and plan[2] == zip_code_info[1]]  # rate_area
        if len(rates) > 1:
            rate = format(round(sorted(rates)[1], 2), ".2f")
    return [zip_code, rate]


def write_data(slcsp_rates):

    try:
        with open(SLCSP_CSV_PATH, 'w', newline='') as data_csv:
            csv_writer = csv.writer(data_csv, delimiter=',')
            csv_writer.writerow(HEADINGS)
            for row in slcsp_rates:
                csv_writer.writerow(row)
    except OSError as e:
        print(e)
        print(MSG_OSERROR_WRITE, SLCSP_CSV_PATH)
        sys.exit(3)


def emit_answers(slcsp_rates):

    print(f"{HEADINGS[0]},{HEADINGS[1]}")
    for row in slcsp_rates:
        print(f"{row[0]},{row[1]}")


def test_result():

    with open(SLCSP_CSV_PATH) as result_csv:
        result = list(csv.reader(result_csv))
    with open(SOLUTION_CSV_PATH) as solution_csv:
        solution = list(csv.reader(solution_csv))
    if result == solution:
        print("\nTESTING_MODE: Test passed")
    else:
        print("\nTESTING_MODE: Test failed")
        [print("Result: ", row[0], "Solution: ", row[1])
         for row in zip(result, solution)
         if row[0] != row[1]]


def determine_slcsp(arguments):

    zips = read_data(ZIPS_CSV_PATH)
    available_zips = set([zip_code[0] for zip_code in zips])
    unique_zips, duplicate_zips = filter_zips(zips)
    plans = read_data(PLANS_CSV_PATH)
    plans = filter_plans(plans)
    if len(arguments) > 1:
        slcsp = [[arguments[1], ""]]
    else:
        slcsp = read_data(SLCSP_CSV_PATH)
    slcsp_rates = []
    for zip_rate in slcsp:
        if len(zip_rate[0]) != ZIP_CODE_LENGTH or not zip_rate[0].isdigit():
            print(MSG_BAD_ZIP_CODE, zip_rate[0])
            sys.exit(2)
        if zip_rate[0] in available_zips:
            answer = get_slcsp_rate(zip_rate[0], unique_zips, duplicate_zips,
                                    plans)
        else:
            answer = [zip_rate[0], ""]
        slcsp_rates.append(answer)
    emit_answers(slcsp_rates)
    if len(sys.argv) == 1:
        write_data(slcsp_rates)
    if TESTING_MODE:
        test_result()


if __name__ == "__main__":
    determine_slcsp(sys.argv)