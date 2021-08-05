import os
from functools import lru_cache

from .endpoint import Ontobee, Graph, Endpoint


class Ontology():

    def __init__(self, path=None, endpoints=None, uri=None):
        if not path and not endpoints:
            raise Exception('A sparql endpoint or a local path to an ontology must be specified')
        self.graph = None
        self.endpoints = None
        self.uri = uri
        if endpoints:
            if not type(endpoints) is list or not all([issubclass(type(e), Endpoint) for e in endpoints]):
                raise TypeError('The endpoints argument requires a list of Endpoints')
            self.endpoints = endpoints
        if path:
            if not type(path) is str:
                raise TypeError('Invalid path specified')
            self.graph = Graph(path)

    def __getattr__(self, name):
        if name in self.__getattribute__('__dict__'):
            return self.__getattribute__(name)
        else:
            return self.__getattribute__('get_uri_by_term')(name)

    def _handler(self, method_name, exception, *args):
        response = None

        # If the ontology graph has already been loaded locally, query that rather
        # than querying over the network
        if self.graph and self.graph.is_loaded():
            method = getattr(self.graph, method_name)
            try:
                response = method(self, *args)
                if response is not None:
                    return response
            except Exception as x:
                print(x)

        # Try endpoints
        if self.endpoints:
            for e in self.endpoints:
                method = getattr(e, method_name)
                response = method(self, *args)
                try:
                    response = method(self, *args)
                    if response is not None:
                        return response
                except Exception as x:
                    print(x)

        # If the connection fails or nothing found, fall back and load the ontology locally
        if self.graph and not self.graph.is_loaded():
            self.graph.load()
            method = getattr(self.graph, method_name)
            try:
                response = method(self, *args)
                if response is not None:
                    return response
            except Exception as x:
                print(x)

        if exception:
            raise exception
        return None

    def get_term_by_uri(self, uri):
        sanitized_uri = self._sanitize_uri(uri)
        exception = LookupError(f'No matching term found for {uri}')
        term = self._handler('get_term_by_uri', exception, sanitized_uri)
        return self._reverse_sanitize_term(term)

    def get_uri_by_term(self, term):
        sanitized_term = self._sanitize_term(term)
        exception = LookupError(f'{term} is not a valid ontology term')
        uri = self._handler('get_uri_by_term', exception, sanitized_term)
        return URI(self._reverse_sanitize_uri(uri), self)

    def _sanitize_uri(self, uri):
        # Some Ontology instances may override this method to translate a URI
        # from purl to identifiers.org namespaces
        return uri

    def _reverse_sanitize_uri(self, uri):
        # Some Ontology instances may override this method to translate a URI
        # from purl to identifiers.org namespaces
        return uri

    def _sanitize_term(self, term):
        # Some Ontology instances may override this method to perform string
        # manipulation of an ontology terms, for example, replacing spaces
        # or changing camel-case to snake-case
        return term

    def _reverse_sanitize_term(self, term):
        # Some Ontology instances may override this method to perform string
        # manipulation of an ontology terms, for example, replacing spaces
        # or changing camel-case to snake-case
        return term


class URI(str):

    def __new__(cls, value: str, ontology: Ontology):
        term = str.__new__(cls, value)
        term.ontology = ontology
        return term

    def is_subclass_of(self, superclass_uri: str):
        subclass_uri = self.ontology._sanitize_uri(self)
        superclass_uri = self.ontology._sanitize_uri(superclass_uri)
        return self.ontology._handler('is_subclass_of', None, subclass_uri, superclass_uri)


# Utility functions
def installation_path(relative_path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        relative_path)


def multi_replace(target_uri, old_namespaces, new_namespace):
    for ns in old_namespaces:
        if ns in target_uri:
            return target_uri.replace(ns, new_namespace)
    return target_uri


def configure_cache_size(maxsize=1000):
    if not '__wrapped__' in Ontology.get_term_by_uri.__dict__:
        # Initialize cache
        Ontology.get_term_by_uri = lru_cache(maxsize=maxsize)(Ontology.get_term_by_uri)
        Ontology.get_uri_by_term = lru_cache(maxsize=maxsize)(Ontology.get_uri_by_term)
    else:
        # Reset cache-size if it was previously set
        Ontology.get_term_by_uri = lru_cache(maxsize=maxsize)(Ontology.get_term_by_uri.__wrapped__)
        Ontology.get_uri_by_term = lru_cache(maxsize=maxsize)(Ontology.get_uri_by_term.__wrapped__)

configure_cache_size()
configure_cache_size(0)
