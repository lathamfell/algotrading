import yaml
import pandas
import sys


class Hodler:

    def __init__(self):
        self.config = yaml.safe_load(open("config.yaml"))
        self.cash = self.config['starting_cash']
        self.shares = 0
        self.last_sold_price = 0
        self.portfolio_value = self.cash
        self.max_portfolio_value = 0
        self.max_portfolio_date = None
        self.min_portfolio_value = sys.maxsize
        self.min_portfolio_date = None
        print(f"Using data file: {self.config['data_file_path']}")
        self.df = pandas.read_csv(filepath_or_buffer=self.config["data_file_path"])
        self.cur_row = self.get_starting_row()

    def run(self):
        # spend available cash on shares
        print("running")

        for i in range(self.cur_row, self.df.Date.size):
            self.cur_row = i
            print(f"Date: {self.df.Date[self.cur_row]}")
            if not self.shares:
                self.buy_shares()
            self.update_portfolio_value()

        print(f"Final portfolio value: {'${:,.2f}'.format(self.portfolio_value)}")
        print(f"Highest value: {'${:,.2f}'.format(self.max_portfolio_value)} on {self.max_portfolio_date}")
        print(f"Lowest value: {'${:,.2f}'.format(self.min_portfolio_value)} on {self.min_portfolio_date}")

    def buy_shares(self):
        print("buying shares")
        self.shares = self.cash / self.df.Open[self.cur_row]
        self.cash = 0
        print(f"Bought {self.shares} shares at {self.df.Open[self.cur_row]}")

    def update_portfolio_value(self):
        self.portfolio_value = self.shares * self.df.Close[self.cur_row] + self.cash
        if self.portfolio_value >= self.max_portfolio_value:
            self.max_portfolio_value = self.portfolio_value
            self.max_portfolio_date = self.df.Date[self.cur_row]
        if self.portfolio_value <= self.min_portfolio_value:
            self.min_portfolio_value = self.portfolio_value
            self.min_portfolio_date = self.df.Date[self.cur_row]
        print(f"Updated portfolio value to {'${:,.2f}'.format(self.portfolio_value)}")

    def get_starting_row(self):
        for i in range(self.df.Date.size):
            if self.df.Date[i] == self.config["starting_date"]:
                return i
            else:
                raise Exception(f"Configured starting date {self.config['starting_date']} not found in data.")


if __name__ == '__main__':
    Hodler().run()
