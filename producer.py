"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
from time import sleep


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)

        self.daemon = True
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.id_prod = self.marketplace.register_producer()

    def run(self):
        """
        Producer produce continuously his products, waiting the time
        required for each product and the republish time if the maximum
        quantity has been reached.
        """
        while True:
            for prod in self.products:
                i = 0
                while i < prod[1]:
                    res = self.marketplace.publish(self.id_prod, prod[0])
                    while res is False:
                        sleep(self.republish_wait_time)
                        res = self.marketplace.publish(self.id_prod, prod[0])
                    i += 1
                sleep(prod[2])
