from src.bash import *

def main():
    print("Введите stop для завершения работы")
    while True:
        command = input().split()
        if command == 'stop':
            break

        try:
            res = solving(command)
            print(*res, sep='\n')
        except ValueError as e:
            print(e)
        except FileNotFoundError as e:
            print(e)
        except UnicodeError as e:
            print(e)
        except PermissionError as e:
            print(e)
        except IsADirectoryError as e:
            print(e)

if __name__ == "__main__":
    main()
