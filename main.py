from abc import ABC, abstractmethod
import logging

class FileReaderInterface(ABC):
    @abstractmethod
    def read_file(self, path: str, buffer_size: int):
        pass

class ConfigReaderInterface(ABC):
    @abstractmethod
    def read_config(self, path: str) -> dict:
        pass

class CoderInterface(ABC):
    @abstractmethod
    def run(self, data: bytes, mode: str) -> bytes:
        pass

class ConfigException(Exception):
    pass

class MyFileReader(FileReaderInterface):
    def read_file(self, path: str, buffer_size: int):
        with open(path, 'rb') as file:
            while True:
                data = file.read(buffer_size)
                if not data:
                    break
                yield data

class MyConfigReader(ConfigReaderInterface):
    def __init__(self):
        logging.basicConfig(filename='config_errors.log', level=logging.ERROR)

    def read_config(self, path: str) -> dict:
        config = {}
        try:
            with open(path, 'r') as file:
                for line in file:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        config[key.strip()] = value.strip()
                    else:
                        raise ConfigException(f"Invalid line in config file: {line.strip()}")

            # Проверяем обязательные ключи
            if 'buffer_size' not in config or 'mode' not in config or 'file_path' not in config:
                raise ConfigException("Missing required configuration keys (buffer_size, mode, file_path)")

            # Преобразуем buffer_size в целое число
            try:
                config['buffer_size'] = int(config['buffer_size'])
            except ValueError:
                raise ConfigException("buffer_size must be an integer")

            # Проверяем корректный режим
            if config['mode'] not in ('code', 'decode'):
                raise ConfigException("mode must be 'code' or 'decode'")

        except (FileNotFoundError, ConfigException) as e:
            logging.error(str(e))
            raise ConfigException(str(e))

        return config

class Coder(CoderInterface):

    def run(self, data: bytes, mode: str) -> bytes:
        if mode == 'code':
            return self.encode(data)
        elif mode == 'decode':
            return self.decode(data)
        else:
            raise ValueError("Invalid mode. Use 'code' or 'decode'.")

    def decode(self, data: bytes) -> bytes:
        key = 3
        result = bytes()
        for char in data:
            char = chr(char)
            if char.isalpha():
                ascii_offset = ord('a') if char.islower() else ord('A')
                decrypted_char = chr((ord(char) - ascii_offset - key) % 26 + ascii_offset)
                result += decrypted_char.encode('utf-8')
            else:
                result += char
        return result

    def encode(self, data: bytes) -> bytes:
        key = 3
        result = bytes()
        for char in data:
            char = chr(char)
            if char.isalpha():
                ascii_offset = ord('a') if char.islower() else ord('A')
                decrypted_char = chr((ord(char) - ascii_offset + key) % 26 + ascii_offset)
                result += decrypted_char.encode('utf-8')
            else:
                result += char
        return result

class MainClass:
    def __init__(self, file_reader: FileReaderInterface, config_reader: ConfigReaderInterface, coder: CoderInterface):
        self.file_reader = file_reader
        self.config_reader = config_reader
        self.coder = coder

    def run(self, config_path: str):
        try:
            config = self.config_reader.read_config(config_path)
            buffer_size = config['buffer_size']
            mode = config['mode']
            file_path = config['file_path']

            output_file_path = file_path + ('.encoded' if mode == 'code' else '.decoded')

            with open(output_file_path, 'wb') as output_file:
                for data in self.file_reader.read_file(file_path, buffer_size):
                    processed_data = self.coder.run(data, mode)
                    output_file.write(processed_data)

            print(f"File successfully processed. Output: {output_file_path}")

        except ConfigException as e:
            print(f"Configuration error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    config_path = input("Enter the path to the configuration file: ")

    file_reader = MyFileReader()
    config_reader = MyConfigReader()
    coder = Coder()
    main = MainClass(file_reader, config_reader, coder)

    main.run(config_path)