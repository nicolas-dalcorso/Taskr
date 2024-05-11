"""Implements hashing classes and functions.
"""

import hashlib;

class Hashr:
    """Hashr class for hashing data.
    """

    def __init__(self):
        """Initializes the Hashr class.
        """

        self.hasher = hashlib.sha256()

    def hash_data(self, data):
        """Hashes data.

        Args:
            data: The data to hash.

        Returns:
            The hashed data.
        """
        try:
            self.hasher.update(data.encode());
        except:
            self.hasher.update(str(data).encode());
        return self.hasher.hexdigest()

    def hash_file(self, file_path):
        """Hashes a file.

        Args:
            file_path: The path to the file to hash.

        Returns:
            The hashed file.
        """

        with open(file_path, 'rb') as file:
            while True:
                data = file.read(65536)
                if not data:
                    break
                self.hasher.update(data)
        return self.hasher.hexdigest();