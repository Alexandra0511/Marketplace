"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread, Lock
from time import sleep


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.name = kwargs["name"]

    def run(self):
        """
        For each product of each cart, the consumers try the actions (add or
        remove. If add nor possible, wait the amount of time required then
        try again.

        Print each purchase.
        """
        for cart in self.carts:
            id_cart = self.marketplace.new_cart()
            for prod in cart:
                if prod["type"] == "add":
                    for i in range(int(prod["quantity"])):
                        res = self.marketplace.add_to_cart(id_cart, prod["product"])
                        while res is False:
                            sleep(self.retry_wait_time)
                            res = self.marketplace.add_to_cart(id_cart, prod["product"])

                if prod["type"] == "remove":
                    for i in range(int(prod["quantity"])):
                        self.marketplace.remove_from_cart(id_cart, prod["product"])
            cart_items = self.marketplace.place_order(id_cart)

            # use the lock because the print was not correct
            lock = Lock()
            with lock:
                for i in cart_items:
                    print(f'{self.name} bought {i}')
