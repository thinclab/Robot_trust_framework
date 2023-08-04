from config_manager import ConfigManger
from utils import *
import pandas as pd
import sys
from statistics import mean


class Predictors:
    def __init__(self, username):
        """
        Reads the configuration based on the username provided
        :param username: username to fetch configuration details
        """
        self.config_manager = ConfigManger(username)
        self.config = self.config_manager.fetch_config()
        self.attitude = self.config[ATTITUDE]
        self.response_time = self.config[RESPONSE_TIME]
        self.predictor_threshold = self.config[PREDICTOR_THRESHOLD]
        self.kinship = self.config[KINSHIP]
        self.predictor_value = 0
        self.total_goals = self.config[MISSIONS_WORKED_TOGETHER]
        # self.goals_achieved = self.config[GOALS_ACHIEVED]

    def fetch_trust_values(self):
        """
        Fetch trust vector from configuration
        @return: trust, distrust, uncertainty
        """
        trust = self.config[TRUST]
        distrust = self.config[DISTRUST]
        uncertainty = self.config[UNCERTAINTY]

        return trust, distrust, uncertainty

    def calculate_competency(self, role: int, goal_status: int):
        """
        Function to calculate human competency
        @param role: role of the human while performing subtask
        @param goal_status: 0 or 1
            0: represents status goal of subtask is not reached
            1: represents status goal of subtask is reached
        @return: float value between 0 and 1
        """
        def assign_knowledge(role_value):
            if role_value not in [1, 2, 3]:
                print("Enter valid role choice")
                sys.exit(1)
            if role_value == 1:
                # If human role is just monitor robot assumes human does not have full information about the area
                return 0.33
            elif role_value == 2:
                # If human also work alongside with robot means human has knowledge on the environment
                return 0.66
            else:
                # If human gives feedback on the work done, human has knowledge on
                # environment and also knows how to validate task
                return 1

        k = assign_knowledge(role)
        s = goal_status
        c = (k + s + self.attitude) / 3
        print("Knowledge is ", k)
        print("Skills is ", s)
        print("Attitude is", self.attitude)

        print("Competency is", c)
        return c, s

    def calculate_conformance(self, actual_time: float, expected_time: float, interaction_list: list):
        """
        Function to calculate conformance
        @param actual_time: float
            actual time to finish the subtask
        @param expected_time: float
            expected time to finish the subtask
        @param interaction_list: list of the actual response times of each interaction
            for each interaction while performing the subtask human has to respond to robot if requires
        @return: float value between 0 and 1
        """
        def dev_time_to_goal(actual, expected):
            print("Actual time taken to finish sub task in minutes", actual)
            if expected_time<=0:
                return 0
            if actual <= expected:
                return 1
            return max(0, 1-(abs(actual - expected) / expected))

        def dev_response_time(response_time_list):
            """
            expected response time is fetched from configuration file
            """
            print("Expected response time in minutes", self.response_time)
            print("Actual response time in minutes", response_time_list)
            response_ratio = []
            for i in response_time_list:
                if i <= self.response_time:
                    response_ratio.append(1)
                else:
                    response_ratio.append(max(0, 1-(abs(i - self.response_time) / self.response_time)))
            if response_ratio: return mean(response_ratio)
            else: return 0

        dt = dev_time_to_goal(actual_time, expected_time)
        dr = dev_response_time(interaction_list)
        print("Deviation between actual and expected time to finish to task", dt)
        print("Deviation between actual and expected response time", dr)
        conformance = (3*dt/4 + dr/4)
        print("Conformance is", conformance)
        return conformance

    def calculate_kinship(self, sub_goal_status: list, predictor_deviation: list):
        """
        Function to calculate kinship once the whole task(mission) is finished
        @param sub_goal_status: list
            status of each subtask whether goal is reached or not
        @param predictor_deviation: list
            predictor value deviation from threshold for each subtask
        @return: float value between 0 and 1
        """
        # kinship = tasks_finished / total_tasks

        sum_d = 0
        sub_tasks_l = len(sub_goal_status)
        for i in range(sub_tasks_l):
            sum_d = sum_d + (sub_goal_status[i] * predictor_deviation[i])

        if self.kinship:
            print(self.total_goals * self.kinship, self.total_goals, self.kinship, sum_d, sub_tasks_l,
                  sum_d / sub_tasks_l)
            self.kinship = ((self.total_goals * self.kinship) / (self.total_goals + 1)) + (
                        (sum_d / sub_tasks_l) / (self.total_goals + 1))
        else:
            self.kinship = (sum_d / sub_tasks_l) / (self.total_goals + 1)
        print("Kinship is", self.kinship)
        updated_dict = {MISSIONS_WORKED_TOGETHER: self.total_goals + 1,
                        KINSHIP: float(round(self.kinship, 2))}
        self.config_manager.update_config(updated_dict)
        return self.kinship

    def get_details(self):
        """
        Function to fetch positive experience count, negative experience count, kinship
        """
        return self.config[POSITIVE_EXP_COUNT], self.config[NEGATIVE_EXP_COUNT], self.config[KINSHIP]

    def update_details_in_config(self, dict_of_values: dict):
        """
        updates values in existing configuration and also in existing config object
        @param dict_of_values: dict
        """
        for key, value in dict_of_values.items():
            self.config[key] = value
        self.config_manager.update_config(dict_of_values)

    def calculate_reliability(self, status):
        """
        @status: list of goal status(0,1) of subtasks handled by human
        If list has only one element and goal status is not reached then reliability is 0 else 1
        If status of all goals is 0 then reliability is 0
        If status of all goals is 1 then reliability is 1
        else reliability is 1-variance
        """
        sr = pd.Series(status)
        if (sr == 0).all():
            reliability = 0
        elif (sr == 1).all():
            reliability = 1
        else:
            reliability = 1 - sr.var(skipna=True)
        print("Reliability is", reliability)
        return reliability

    def calculate_experience_type(self, competency: float, conformance: float, reliability: float):
        """
        Function to calculate predictor value.
        If experience is negative then the deviation from predictor threshold
        else deviation value will be 1

        @return: whether experience is positive(1) or negative(0)
        """
        print("Predictor threshold is ", self.predictor_threshold)
        self.predictor_value = ((competency + reliability) / 6 ) + (2 * conformance / 3)
        predictor_deviation = max(0, self.predictor_value - (
                    abs(self.predictor_value - self.predictor_threshold) / self.predictor_threshold))
        print("Predictor value = Competency+Conformance+Reliability/3", self.predictor_value)
        if self.predictor_threshold <= self.predictor_value:
            print("Interaction is considered as positive experience")
            return 1, 1, self.predictor_value
        print("Interaction is considered as negative experience")

        return 0, predictor_deviation, self.predictor_value

    def update_details(self, positive_count: int, negative_count: int, t: float, d: float, u: float):
        """
        Function to update experience count and trust vector values in configuration
        """
        updated_dict = {POSITIVE_EXP_COUNT: positive_count,
                        NEGATIVE_EXP_COUNT: negative_count,
                        TRUST: t, DISTRUST: d, UNCERTAINTY: u}
        self.config_manager.update_config(updated_dict)
        self.config.update(updated_dict)
