import yaml
import pandas
import sys
from os.path import join
import os

from common import get_start_row, output, get_pct_change_str, DEFAULT_START_DATE, DEFAULT_END_DATE


class Hodler:

    def __init__(self):
        self.config = yaml.safe_load(open("config_hodler.yaml"))
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
        self.start_date = self.config.get('start_date', DEFAULT_START_DATE)
        self.end_date = self.config.get('end_date', DEFAULT_END_DATE)
        self.cur_row = get_start_row(dataframe=self.df, start_date=self.start_date)
        self.cur_date = self.df.Date[self.cur_row]

        output_filename = f"hodler_{self.start_date}_{self.end_date}"
        self.output_file_path = join(self.config['output_dir'], output_filename)
        # clean up the old file if it exists
        try:
            os.remove(self.output_file_path)
        except FileNotFoundError:
            pass

    def run(self):
        for i in range(self.cur_row, self.df.Date.size):
            self.cur_row = i
            self.cur_date = self.df.Date[self.cur_row]

            output(f"Date: {self.df.Date[self.cur_row]}", self.output_file_path)
            if not self.shares:
                self.buy_shares()
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

    def buy_shares(self):
        self.shares = self.cash / self.df.Open[self.cur_row]
        self.cash = 0
        output(f"Bought {self.shares} shares at {self.df.Open[self.cur_row]}", self.output_file_path)

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
