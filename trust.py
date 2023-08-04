import scipy.integrate as spi
import scipy.special as sc
from sys import exit


class Trust:
    def __init__(self, p_count=0, n_count=0, kinship=None):

        self.p_count = p_count
        self.n_count = n_count
        self.kinship = kinship

    def calculate_certainty(self):
        """
        This functions calculates certainty for various conditions
        if any of experience count is zero beta is 1
        otherwise beta is calculated by using scipy.special module     
        @return: certainty value
        :rtype: float
        """
        if self.p_count != 0 and self.n_count != 0:
            beta = sc.beta(self.p_count, self.n_count)
            print('Single integral computed by SciPy quad', self.p_count, self.n_count, beta)
            if beta != 0:
                integral_equation = lambda p_i: abs(
                    ((p_i ** (self.p_count - 1)) * ((1 - p_i) ** (self.n_count - 1)) / beta) - 1) / 2
            else:
                integral_equation = lambda p_i: abs(
                    ((p_i ** (self.p_count - 1)) * ((1 - p_i) ** (self.n_count - 1))) - 1) / 2

        elif self.p_count == 0 and self.n_count != 0:
            beta = 1
            integral_equation = (lambda p_i: abs((1 * ((1 - p_i) ** (self.n_count - 1))) - 1))
        elif self.n_count == 0 and self.p_count != 0:
            beta = 1
            integral_equation = (lambda p_i: abs(((p_i ** (self.p_count - 1)) * 1) - 1))
        else:
            print("Trust is not calculated as both experience count is zero")
            exit(0)

        a = 0
        b = 1
        result, error = spi.quad(integral_equation, a, b)

        return result

    def update_trust_vector(self):
        """
        This function calculates new trust, distrust and uncertainty values
        @return: updated trust vector
        :rtype: float values of trust, distrust and uncertainty
        """
        c_b = self.calculate_certainty()
        if self.kinship:
            trust = round(self.kinship * self.p_count * c_b / (self.p_count + self.n_count), 2)
            distrust = round((1 - self.kinship) * self.n_count * c_b / (self.p_count + self.n_count), 2)
        else:
            trust = round(self.p_count * c_b / (self.p_count + self.n_count), 2)
            distrust = round(self.n_count * c_b / (self.p_count + self.n_count), 2)
        uncertainty = round(1 - (trust + distrust), 2)
        print("\n Updated trust vector is ", trust, distrust, uncertainty)
        return trust, distrust, uncertainty
