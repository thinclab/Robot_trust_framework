from human_interaction import InteractionAPI

import os
import pandas as pd
from predictors import Predictors
csv_file_path = os.path.join(os.getcwd(), "api21less.csv")
cols = ["positive exp Count", "negative exp Count", "Trust", "Distrust", "Uncertainty",  "Kinship"]
if not os.path.isfile(csv_file_path):

    data=pd.DataFrame([],columns=cols)
    data.to_csv(csv_file_path,index=False)
else:
    data = pd.read_csv(csv_file_path)




for i in range(1):
    interaction_object = InteractionAPI(user="user19")

    #CALL WHEN MISSION STARTS BEFORE ANY SUBTASKS, FOR TESTING
    interaction_object.update_exp_response_time(response_time=2)
    """ interaction_object.update_predictor_threshold(predictor_threshold=0.45)
    interaction_object.update_attitude(attitude=1)
    interaction_object.update_initial_kinship(kinship=0.6)
    interaction_object.update_experience_count(positive=10) """


    #prob float  trust value
    interaction_probability = interaction_object.fetch_probability_value()
    print(interaction_probability)


    #AFTER EACH SUBTASK
    interaction_object.calculate_trust(role=1, expected_time_for_task=10.05, 
                                       actual_response_list=[1.2, 0.5, 2.0], 
                                       sub_task_status=0, 
                                       actual_time_for_task=12.03)



    interaction_probability = interaction_object.fetch_probability_value()
    print(interaction_probability)
    interaction_object.calculate_trust(2, 20, [343], 1, 1)
    interaction_probability = interaction_object.fetch_probability_value()
    print(interaction_probability)
    interaction_object.calculate_trust(3, 20, [2, 23, 56], 1, 34)
    interaction_probability = interaction_object.fetch_probability_value()
    print(interaction_probability)

    p_count, n_count, kinship = Predictors("user19").get_details()
    t, d, u = Predictors("user19").fetch_trust_values()
    data = pd.concat([data, pd.DataFrame([[p_count, n_count, t, d, u, kinship]], columns=cols)])
    
    #AFTER aall subtasks
    interaction_object.update_kinship()


    interaction_object.get_trust_values()
data.to_csv(csv_file_path, index=False)
print(data)


