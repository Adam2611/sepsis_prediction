#main driver code

import copy
import pandas as pd
import numpy as np
import multiprocessing
import ray

import call_model
import postprocessing
import preprocessing
import rules
import const

def single_work(input = None, frontend = None, input_csv = None):               #monitors a single patient
    # df_raw = pd.DataFrame
    #for list of list implementation
    pt_identifier = []
    time = [] 
    Bp1 = [] 
    Bp2 = []
    Pulse = [] 
    Temp = []
    Rr = [] 
    O2Sat = [] 
    Age_Number = [] 
    Gender = []
    Lactate_value = [] 
    Lactate_ref_range = []  
    WBC_value = [] 
    WBC_ref_range = []
    Male = []
    Female = []
    Lactate_adjusted = []
    WBC_adjusted = []

    main_dict = {}

    main_dict["pt_identifier"] = pt_identifier
    main_dict["time"] = time
    main_dict["bp1"] = Bp1
    main_dict["bp2"] = Bp2
    main_dict["pulse"] = Pulse
    main_dict["temp"] = Temp
    main_dict["rr"] = Rr
    main_dict["o2sat"] = O2Sat
    main_dict["age_number"] = Age_Number
    main_dict["gender"] = Gender
    main_dict["lactate_value"] = Lactate_value
    main_dict["lactate_ref_range"] = Lactate_ref_range
    main_dict["wbc_value"] = WBC_value
    main_dict["wbc_ref_range"] = WBC_ref_range
    main_dict["male"] = Male
    main_dict["female"] = Female
    main_dict["lactate_adjusted"] = Lactate_adjusted
    main_dict["wbc_adjusted"] = WBC_adjusted


    if frontend and input:
        #incoming from the frontend 
        to_frontend = frontend_single(main_dict, input)
        return to_frontend
    
    elif input_csv:
        #incoming from a csv
        csv_single(input_csv)

    else:
        #live data inputted one at a time in console; not cleaned, for real medical data stream
        live_single(main_dict)
    

def frontend_single(main_dict, input):
    fe = copy.deepcopy(main_dict)
        #print ("TYPE: ",type(input))
        # raw_input1 = "A1B2C3, 0, 100, 80, 65, 37, 20, 100, 13, Male, 3, 2-5, 5, 4-11"
        # raw_input2 = "A1B2C3, 5, 100, 80, 65, 37, 20, 100, 13, Male, 3, 2-5, 5, 4-11"
        # raw_input3 = "A1B2C3, 15, 100, 80, 65, 37, 20, 100, 13, Male, 3, 2-5, 5, 4-11"
        # raw_input4 = "A1B2C3, 25, 100, 80, 65, 37, 20, 100, 13, Male, 3, 2-5, 5, 4-11"
    try:
        input = input.split(", ")
        rows = int(len(input)/14)
        raw_input_list = []
        
        for row in range(rows):
            first = row*14
            second = row*14 + 14
            raw_input_list.append(input[first:second])

        new_str_list = []
        for row2 in range(rows):
            new_str_list.append("")

        for row3 in range(rows):
            for x in range(14):
                if x != 13:
                    new_str_list[row3] = new_str_list[row3]+raw_input_list[row3][x] + ", "
                else:
                    new_str_list[row3] = new_str_list[row3]+raw_input_list[row3][x]

    except:
        return "Please Enter 3+ Rows of Data"

#A1B2C3, 0, 100, 80, 65, 37, 20, 100, 13, Male, 3, 2-5, 5, 4-11, A1B2C3, 0, 100, 80, 65, 37, 20, 100, 13, Male, 3, 2-5, 5, 4-11, A1B2C3, 0, 100, 80, 65, 37, 20, 100, 13, Male, 3, 2-5, 5, 4-11, A1B2C3, 0, 100, 80, 65, 37, 20, 100, 13, Male, 3, 2-5, 5, 4-11
#A1B2C3, 0, 100, 80, 65, 37, 20, 100, 19, Male, 32, 2-5, 5, 4-11, A1B2C3, 0, 100, 80, 65, 37, 20, 100, 19, Male, 13, 2-5, 5, 4-11, A1B2C3, 0, 100, 80, 65, 37, 20, 100, 19, Male, 0, 2-5, 5, 4-11, A1B2C3, 0, 100, 80, 65, 37, 20, 100, 19, Male, 3, 2-5, 5, 4-11
    # fe = preprocessing.insert_into_dict(new_1, fe)
    # fe = preprocessing.insert_into_dict(new_2, fe)
    # fe = preprocessing.insert_into_dict(new_3, fe)
    # fe = preprocessing.insert_into_dict(new_4, fe) 

    print("rows: ", rows)
    print("Raw input list", raw_input_list)
    print("new str list ", new_str_list)
    for row4 in range(rows):
        fe = preprocessing.insert_into_dict(new_str_list[row4], fe)

    print("ROWS: ", rows)
    result1 = rules.master_rules(fe, rows-1)

    if result1==True:
        print("Sepsis!")
        frontend_result = "Sepsis was detected or is imminent in the patient."
        return frontend_result

    else:
        return "No Sepsis Detected. Inputs are normal."

def csv_single(input_csv):
    preprocessed = pd.read_csv(input_csv)
    row_length = len(preprocessed)
    count = 3

    while count<row_length:
        result1 = rules.master_rules(preprocessed, count)
        if result1 == True:
                print("Sepsis found with rules!")
                break
        else:
            #continue with model
            model_result = call_model.call(preprocessed, count)
            if model_result>const.ML_THRESHOLD:
                print("Sepsis found with model!")
                break
            else:
                print("not done")
        count+=1
    pass

def live_single(main_dict):
    count = 0
    preprocessed = copy.deepcopy(main_dict)

        
    while count<20:        #20 for now, should be indefinite waiting time
        print("\n")
        raw_input = input("Enter Values: ")        
        #preprocessed = preprocessing.insert_into_arrays(raw_input, preprocessed)
        preprocessed = preprocessing.insert_into_dict(raw_input, preprocessed)
        for s in preprocessed:
            print(s, ": ", preprocessed[s])

        if count>=const.INITIAL_WAIT-1:      #3 for now; if greater than 3 then run through the rules and models
            result1 = rules.master_rules(preprocessed, count)
            if result1 == True:
                print("Sepsis found with rules!")
                break
            else:
                #continue with model
                model_result = call_model.call(preprocessed, count)
                if model_result>const.ML_THRESHOLD:
                    print("Sepsis!")
                    break
                else:
                    print("not done")

        count+=1
