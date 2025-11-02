from src.bash import *
import logging


logging.basicConfig(
    filename='shell.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


def main():
    print("Введите stop для завершения работы")
    while True:
        command = input().split()
        if not(command): continue
        if command[0] == 'stop':
            print('Спасибо за использование bash!')
            break
        log_str = command[0]
        for i in command[1:]: log_str += f' {i}'
        logging.info(log_str)
        try:
            res = solving(command)
            print(*res, sep='\n')
            logging.info('SUCCESS')
        except ValueError as e:
            print(e)
            logging.info(f'ERROR: {e}')
        except FileNotFoundError as e:
            print(e)
            logging.info(f'ERROR: {e}')
        except UnicodeError as e:
            print(e)
            logging.info(f'ERROR: {e}')
        except PermissionError as e:
            print(e)
            logging.info(f'ERROR: {e}')
        except IsADirectoryError as e:
            print(e)
            logging.info(f'ERROR: {e}')


if __name__ == "__main__":
    main()
