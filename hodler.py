import yaml
import pandas
import sys
from os.path import join
import os

from common import get_start_row, output, get_pct_change_str, DEFAULT_START_DATE, DEFAULT_END_DATE


class Hodler:

    def __init__(self):
        self.config = yaml.safe_load(open("config_hodler.yaml"))
        self.test_cash = self.config['starting_cash']
        self.control_cash = self.config['starting_cash']
        self.test_shares = 0
        self.control_shares = 0
        self.test_portfolio_value = self.test_cash
        self.control_portfolio_value = self.control_cash
        self.test_max_portfolio_value = 0
        self.test_max_portfolio_date = None
        self.test_min_portfolio_value = sys.maxsize
        self.test_min_portfolio_date = None
        self.control_max_portfolio_value = 0
        self.control_max_portfolio_date = None
        self.control_min_portfolio_value = sys.maxsize
        self.control_min_portfolio_date = None
        print(f"Using data file: {self.config['test_data_file_path']}")
        self.test_df = pandas.read_csv(filepath_or_buffer=self.config["test_data_file_path"])
        self.control_df = pandas.read_csv(filepath_or_buffer=self.config["control_data_file_path"])
        test_ticker = self.config["test_data_file_path"].split('/')[1].split('.')[0]
        self.control_ticker = self.config["control_data_file_path"].split('/')[1].split('.')[0]
        self.start_date = self.config.get('start_date', DEFAULT_START_DATE)
        self.end_date = self.config.get('end_date', DEFAULT_END_DATE)
        self.test_cur_row = get_start_row(dataframe=self.test_df, start_date=self.start_date)
        self.control_cur_row = get_start_row(dataframe=self.control_df, start_date=self.start_date)
        self.cur_date = self.test_df.Date[self.test_cur_row]

        output_filename = f"hodler_{test_ticker}_{self.start_date}_{self.end_date}"
        self.output_file_path = join(self.config['output_dir'], output_filename)
        # clean up the old file if it exists
        try:
            os.remove(self.output_file_path)
        except FileNotFoundError:
            pass

    def run(self):
        for i in range(self.test_cur_row, self.test_df.Date.size):
            self.cur_date = self.test_df.Date[i]
            self.test_cur_row = i


            output(f"Date: {self.test_df.Date[self.test_cur_row]}", self.output_file_path)
            if not self.test_shares:
                self.buy_test_shares()
            if not self.control_shares:
                self.buy_control_shares()
            self.update_portfolio_value()

            if self.cur_date == self.end_date:
                break

        output(f"Final portfolio value: {'${:,.2f}'.format(self.portfolio_value)}", self.output_file_path)
        output(f"Highest value: {'${:,.2f}'.format(self.max_portfolio_value)} on {self.max_portfolio_date}",
               self.output_file_path)
        output(f"Lowest value: {'${:,.2f}'.format(self.min_portfolio_value)} on {self.min_portfolio_date}",
               self.output_file_path)
        pct_change = get_pct_change_str(start=self.config['starting_cash'], end=self.portfolio_value)
        os.rename(self.output_file_path, f"{self.output_file_path}_{pct_change}")

    def buy_test_shares(self):
        self.test_shares = self.test_cash / self.test_df.Close[self.test_cur_row]
        self.test_cash = 0
        output(f"Bought {self.test_shares} shares at {self.test_df.Close[self.test_cur_row]}", self.output_file_path)

    def buy_control_shares(self):
        self.control_shares = self.control_cash / self.control_df.Close[self.control_cur_row]

    def update_portfolio_value(self):
        self.portfolio_value = self.shares * self.df.Close[self.cur_row] + self.cash
        if self.portfolio_value >= self.max_portfolio_value:
            self.max_portfolio_value = self.portfolio_value
            self.max_portfolio_date = self.df.Date[self.cur_row]
        if self.portfolio_value <= self.min_portfolio_value:
            self.min_portfolio_value = self.portfolio_value
            self.min_portfolio_date = self.df.Date[self.cur_row]
        output(f"Updated portfolio value to {'${:,.2f}'.format(self.portfolio_value)}", self.output_file_path)


if __name__ == '__main__':
    Hodler().run()
