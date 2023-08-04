from trust import Trust
from predictors import Predictors
from utils import *
import os
import pandas as pd
"""
Flow of steps
1. Get the user details and count of subtask
2. Update mandatory fields
    a. Expected Response time
3. Update Optional fields
    a. experience count
    b. kinship
    c. predictor_threshold
    d. attitude
4. Get subtask details to update trust
5. After all subtask finishes update kinship

"""
DIR_NAME = os.path.dirname(__file__)

class InteractionAPI:

    def __init__(self, user: str):
        """
        @param user: user who is interacting with robot.
        Name has to be unique for each other as we will create a config file with the name
        """
        self.user_predictor = Predictors(user)
        self.predictor_deviation = []
        self.sub_goal_status = []
        
        
        self.csv_file_path =os.path.join(DIR_NAME, "config", user + "api21less.csv")
        self.cols = ["Task", "positive exp Count", "negative exp Count", "Trust", "Distrust", "Uncertainty",  "Kinship",\
                 "Competency", "Conformance", "reliability", "actual time", "expected time", "goalstatus", \
                    "actual response time",  "role", "predictor_value"]
        if not os.path.isfile(self.csv_file_path):

            self.data=pd.DataFrame([],columns=self.cols)
            self.data.to_csv(self.csv_file_path,index=False)
        else:
            self.data = pd.read_csv(self.csv_file_path)

    def update_exp_response_time(self, response_time: float):
        """
        Function to update response time in configuration file
        @param response_time: float value
        """
        self.user_predictor.update_details_in_config({RESPONSE_TIME: response_time})

    def update_experience_count(self, positive: int = None, negative: int = None):
        """
        Function to update positive and negative experience count in configuration file
        User can update only one value also
        @param positive: integer value
        @param negative: integer value
        """
        updated_dict = {}
        if positive is not None:
            updated_dict[POSITIVE_EXP_COUNT] = positive
        if negative is not None:
            updated_dict[NEGATIVE_EXP_COUNT] = negative
        self.user_predictor.update_details_in_config(updated_dict)

    def update_attitude(self, attitude: float):
        """
        Function to update human attitude value in configuration file
        @param attitude: supports only 1 or 0
        """
        # if attitude not in [0, 1]:
        #     raise Exception("Value must be 0 or 1")
        self.user_predictor.update_details_in_config({ATTITUDE: attitude})

    def update_initial_kinship(self, kinship: float):
        """
        Function to update kinship value in configuration file
        @param kinship:float value between 0 or 1
        """
        if kinship < 0 or kinship > 1:
            raise Exception("Value must be in between 0 or 1")
        self.user_predictor.update_details_in_config({KINSHIP: kinship})

    def update_predictor_threshold(self, predictor_threshold: float):
        """
        Function to update predictor_threshold value in configuration file
        @param predictor_threshold: float value between 0 or 1
        """
        if predictor_threshold < 0 or predictor_threshold > 1:
            raise Exception("Value must be in between 0 or 1")
        self.user_predictor.update_details_in_config({PREDICTOR_THRESHOLD: predictor_threshold})

    def calculate_trust(self, role: int, expected_time_for_task: float, actual_response_list: list,
                        sub_task_status: int, actual_time_for_task: float, goal=""):
        """
        Function to calculate trust for a given subtask
        @param role: role of human, must be integer value [1,2,3]
        @param expected_time_for_task: float value
        @param actual_response_list: list of actual response time for interactions
        @param sub_task_status: status of subtask. Value must be 0 or 1
        @param actual_time_for_task: float value actual time in minutes within human finished the subtask
        """
        positive_count, negative_count, kinship = self.user_predictor.get_details()
        c, s = self.user_predictor.calculate_competency(role, sub_task_status)
        co = self.user_predictor.calculate_conformance(actual_time_for_task, expected_time_for_task,
                                                       actual_response_list)
        self.sub_goal_status.append(sub_task_status)
        r = self.user_predictor.calculate_reliability(self.sub_goal_status)
        is_positive, p_deviation, predictor_value = self.user_predictor.calculate_experience_type(c, co, r)
        if is_positive:
            positive_count = positive_count + 1
        else:
            negative_count = negative_count + 1
        self.predictor_deviation.append(p_deviation)
        tr = Trust(positive_count, negative_count, kinship)
        t, d, u = tr.update_trust_vector()
        self.user_predictor.update_details(positive_count, negative_count, t, d, u)
        
        
        
        self.data = pd.concat([self.data, pd.DataFrame([[goal,positive_count, negative_count, t, d, u, kinship, \
                                               c, co, r, actual_time_for_task, expected_time_for_task, \
                                               sub_task_status, actual_response_list,
                                               role, predictor_value]], columns=self.cols)])
        self.data.to_csv(self.csv_file_path, index=False)

    def update_kinship(self):
        """
        This function calculates kinship and updates in the configuration
        """
        self.user_predictor.calculate_kinship(self.sub_goal_status, self.predictor_deviation)

    def get_trust_values(self):
        """
        This function fetches the trust values from configuration
        :return: trust, distrust, uncertainty
        """
        return self.user_predictor.fetch_trust_values()

    def fetch_probability_value(self):
        """
        This function fetches the probability value which robot uses to
        consider human suggestion
        :return:Float probability value 
        """
        trust, distrust, uncertainty = self.get_trust_values()   
        p = 0 
        if not (trust or distrust):
            # print("First interaction") 
            p = 1
        elif uncertainty > (trust + distrust):
            # print("Always work with human as robot is not certain")
            p = 1
        elif trust >= distrust:
            # print("Trust value is more. Robot works with human")
            p = 1
        elif trust < distrust:
            # print("Distrust value is more. So robot works with human with a probability of ",
            #         round((1 - (distrust - trust) / (trust + distrust)), 2))
            # self.message = "Distrust value is more. So robot works with probability of " + \
            p = (1 - ((distrust - trust) / (trust + distrust)))
        return p
        
