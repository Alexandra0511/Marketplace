"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
from logging.handlers import RotatingFileHandler
from threading import Lock
import logging
import unittest

from .product import Tea


class MarketplaceTestCase(unittest.TestCase):
    """
    Class for testing the methods in Marketplace
    """

    def setUp(self):
        """
        Initializari necesare pentru teste
        """
        self.marketplace = Marketplace(15)
        self.prod1 = Tea('tea1', 8, 'Herbal')
        self.prod2 = Tea('tea2', 5, 'Black')

    def test_register(self):
        """
        Test pentru verificarea inregistrarii unui producator
        """
        self.assertEqual(self.marketplace.register_producer(), 0)
        self.assertEqual(self.marketplace.register_producer(), 1)
        self.assertEqual(self.marketplace.register_producer(), 2)

    def test_publish(self):
        """
        Test pentru verificarea publicarii unui produs
        Se testeaza si cazul de depasire a numarului maxim de produse
        """
        self.marketplace.register_producer()
        self.assertTrue(self.marketplace.publish(0, self.prod1))
        for _ in range(14):
            self.assertTrue(self.marketplace.publish(0, self.prod2))
        self.assertFalse(self.marketplace.publish(0, self.prod1))

    def test_new_cart(self):
        """
        Test pentru adaugarea unui nou cos de cumparaturi
        """
        self.assertEqual(self.marketplace.new_cart(), 0)
        self.assertEqual(self.marketplace.new_cart(), 1)

    def test_add_to_cart(self):
        """
        Test pentru verificarea adaugarii unui produs in cos
        Se verifica si cazul de adaugare a unui produs inexistent in magazin
        """
        self.marketplace.new_cart()
        self.marketplace.register_producer()
        self.marketplace.publish(0, self.prod1)
        self.assertTrue(self.marketplace.add_to_cart(0, self.prod1))
        self.assertFalse(self.marketplace.add_to_cart(0, self.prod2))

    def test_remove_from_cart(self):
        """
        Test pentru eliminarea unui produs dintr-un cos
        """
        self.marketplace.new_cart()
        self.marketplace.register_producer()
        self.marketplace.publish(0, self.prod1)
        self.marketplace.publish(0, self.prod2)
        self.marketplace.add_to_cart(0, self.prod1)
        self.marketplace.add_to_cart(0, self.prod2)
        self.marketplace.remove_from_cart(0, self.prod1)
        self.assertEqual(1, len(self.marketplace.carts[0]))

    def test_place_order(self):
        """
        Test pentru plasarea unei comenzi
        """
        self.marketplace.new_cart()
        self.marketplace.register_producer()
        self.marketplace.publish(0, self.prod1)
        self.marketplace.publish(0, self.prod2)
        self.marketplace.publish(0, self.prod2)
        self.marketplace.add_to_cart(0, self.prod1)
        self.marketplace.add_to_cart(0, self.prod2)
        self.marketplace.add_to_cart(0, self.prod2)
        self.marketplace.remove_from_cart(0, self.prod1)
        self.assertEqual(self.marketplace.place_order(0), [self.prod2, self.prod2])


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.producers_size = []  # list with sizes of producers lists of products
        self.carts = {}  # dictionary with cart_id and the products in cart
        self.products = []  # all products available in store
        self.id_prod = -1  # producer id
        self.product_producers = {}  # dictionary with product and its producer
        self.id_cart = -1  # cart id
        self.max = queue_size_per_producer

        self.cart_lock = Lock()
        self.prod_lock = Lock()
        self.new_lock = Lock()

        logging.basicConfig(
            handlers=[RotatingFileHandler('./marketplace.log', maxBytes=100000, backupCount=10)],
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            datefmt='%Y-%m-%dT%H:%M:%S')
        self.logger = logging.getLogger()
        logging.Formatter.converter = time.gmtime  # setting the gmtime

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        For each new producer, a size 0 is added to the list of sizes.
        """
        self.logger.info('Producer %s has been registered', str(self.id_prod + 1))
        with self.prod_lock:
            self.id_prod += 1
        self.producers_size.append(0)
        return self.id_prod

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        self.logger.info('Producer %d tries adding the product %s', producer_id, product)

        # max limit has been reached
        if self.producers_size[int(producer_id)] == self.max:
            return False
        # no lock needed because the actions are on exclusive producer_id
        self.producers_size[int(producer_id)] += 1
        self.products.append(product)
        self.product_producers.update({product: int(producer_id)})
        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        self.logger.info('New cart %s registered', str(self.id_cart + 1))

        # a lock is required because several consumers can request a cart simultaneously
        with self.cart_lock:
            self.id_cart += 1
        self.carts.update({self.id_cart: []})
        return self.id_cart

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        self.logger.info('Try adding product %s to cart %s', product, cart_id)

        # need of lock because of working with the same lists
        with self.new_lock:
            id_prod = self.product_producers.get(product)
            if product not in self.products:
                return False
            self.products.remove(product)
            self.producers_size[id_prod] -= 1
        self.carts[cart_id].append(product)
        return True

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.
        Adds it back to the products list of the store and of the producer
        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        self.logger.info('Try removing product %s from cart %s', product, cart_id)

        self.carts[cart_id].remove(product)
        id_prod = self.product_producers.get(product)
        self.products.append(product)
        self.producers_size[id_prod] += 1

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        self.logger.info('Try to place order %s', cart_id)

        # lock required because of working on the same dictionary
        with self.new_lock:
            cart = self.carts.pop(cart_id)
        return cart
