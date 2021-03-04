import yaml
import pandas
import sys

from common import get_starting_row


class TrailAndRebuyer:

    def __init__(self):
        self.config = yaml.safe_load(open("config_trail_and_rebuy.yaml"))
        self.cash = self.config['starting_cash']
        self.shares = 0
        self.portfolio_value = self.cash
        self.max_portfolio_value = 0
        self.max_portfolio_date = None
        self.min_portfolio_value = sys.maxsize
        self.min_portfolio_date = None
        print(f"Using data file: {self.config['data_file_path']}")
        self.df = pandas.read_csv(filepath_or_buffer=self.config["data_file_path"])
        self.cur_row = get_starting_row(dataframe=self.df, starting_date=self.config['starting_date'])
        self.cur_date = self.df.Date[self.cur_row]
        self.trailing_stop_price = 0
        self.trailing_stop_price_basis = 0  # the peak the trailing stop price was last calculated from
        self.buy_stop_price = 0  # rebuy after a small rise in the price
        self.buy_limit_price = 0  # rebuy after a steep fall in the price

    def run(self):
        print("running")
        # make initial buy and set first trailing stop
        self.buy_shares(price=self.df.Open[self.cur_row])
        self.trailing_stop_price = self.df.Open[self.cur_row] * (1 - self.config['trailing_stop_pct'])

        for i in range(self.cur_row + 1, self.df.Date.size):
            self.cur_row = i
            self.cur_date = self.df.Date[self.cur_row]
            print(f"Date: {self.cur_date}")

            if self.shares and self.trailing_stop_loss_hit():
                print(f"hit trailing stop loss price {self.trailing_stop_price}, sell to avoid further loss")
                # we have fallen to the trailing stop loss, sell
                self.sell_shares(price=self.trailing_stop_price)
                # set the buy stop, to rebuy in case of a small rebound
                self.buy_stop_price = self.trailing_stop_price * (1 + self.config['buy_bounce_pct'])
                # set the buy limit, to rebuy in the case of a steep fall
                self.buy_limit_price = self.trailing_stop_price * (1 - self.config['gap_down_pct'])
            elif self.shares:
                # we are holding the shares b/c we haven't hit the trailing stop loss
                # check to see if there is a new high that should reset the trailing stop loss
                self.reset_trailing_stop_price()
            elif self.buy_stop_hit():
                print(f"hit buy stop of {self.buy_stop_price}, buy to avoid missing out on further gains")
                self.buy_shares(price=self.buy_stop_price)
                self.trailing_stop_price = self.buy_stop_price * (1 - self.config['trailing_stop_pct'])
            elif self.buy_limit_hit():
                print(f"hit buy limit of {self.buy_limit_price}, buy because it's likely to go up from here")
                self.buy_shares(price=self.buy_limit_price)
                self.trailing_stop_price = self.buy_limit_price * (1 - self.config['trailing_stop_pct'])

            self.update_portfolio_value()
            if self.cur_date == self.config['ending_date']:
                break

        print(f"Final portfolio value: {'${:,.2f}'.format(self.portfolio_value)}")
        print(f"Highest value: {'${:,.2f}'.format(self.max_portfolio_value)} on {self.max_portfolio_date}")
        print(f"Lowest value: {'${:,.2f}'.format(self.min_portfolio_value)} on {self.min_portfolio_date}")

    def buy_shares(self, price: float):
        print("buying shares")
        self.shares = self.cash / price
        self.cash = 0
        print(f"Bought {self.shares} shares at {price}")

    def sell_shares(self, price: float):
        print("selling shares")
        self.cash = self.shares * price
        print(f"Sold {self.shares} shares at {price}")
        self.shares = 0

    def update_portfolio_value(self):
        self.portfolio_value = self.shares * self.df.Close[self.cur_row] + self.cash
        if self.portfolio_value >= self.max_portfolio_value:
            self.max_portfolio_value = self.portfolio_value
            self.max_portfolio_date = self.df.Date[self.cur_row]
        if self.portfolio_value <= self.min_portfolio_value:
            self.min_portfolio_value = self.portfolio_value
            self.min_portfolio_date = self.df.Date[self.cur_row]
        print(f"Updated portfolio value to {'${:,.2f}'.format(self.portfolio_value)}")

    def trailing_stop_loss_hit(self) -> bool:
        # returns True if the trailing stop loss was hit or surpassed during this day
        # otherwise returns False, indicating the price is still above the trailing stop loss
        # also resets the trailing stop loss price if it was gapped over during after hours
        if self.df.Open[self.cur_row] < self.trailing_stop_price:
            # we gapped down past it during after hours trading, sell immediately to avoid further loss
            self.trailing_stop_price = self.df.Open[self.cur_row]
            return True
        if self.df.Low[self.cur_row] <= self.trailing_stop_price <= self.df.High[self.cur_row]:
            # we hit it during the trading day
            return True
        return False

    def buy_stop_hit(self) -> bool:
        # returns True if the buy stop was hit or surpassed during this day
        # otherwise returns False, indicating the price is still below the buy stop
        # also resets the buy stop price if it was gapped over during after hours
        if self.df.Open[self.cur_row] > self.buy_stop_price:
            # we gapped up past it during after hours trading, buy immediately to avoid missing further gains
            self.buy_stop_price = self.df.Open[self.cur_row]
            return True
        if self.df.Low[self.cur_row] <= self.buy_stop_price <= self.df.High[self.cur_row]:
            # we hit it during the trading day
            return True
        return False

    def buy_limit_hit(self) -> bool:
        # returns True if the buy limit was hit or surpassed during the day
        # otherwise returns False, indicating the price is still above the buy limit
        # also resets the buy limit price if it was gapped over during after hours
        if self.df.Open[self.cur_row] < self.buy_limit_price:
            # we gapped down past it during after hours trading, buy to avoid missing further potential gains
            self.buy_limit_price = self.df.Open[self.cur_row]
            return True
        if self.df.Low[self.cur_row] <= self.buy_stop_price <= self.df.High[self.cur_row]:
            # we hit it during the trading day
            return True
        return False

    def reset_trailing_stop_price(self):
        if self.df.High[self.cur_row] > self.trailing_stop_price_basis:
            self.trailing_stop_price_basis = self.df.High[self.cur_row]
            self.trailing_stop_price = self.trailing_stop_price_basis * (1 - self.config['trailing_stop_pct'])
            print(f"updated trailing stop price to {self.trailing_stop_price}")


if __name__ == '__main__':
    TrailAndRebuyer().run()
