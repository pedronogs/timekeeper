# from loguru import logger
import argparse


def log_wrapper(fnct):

    def wrapper(*args):
        # logger.add(f"/opt/{args['file_path'].split('/')[-1].split('.')[0]}.log", rotation="1 MB")
        fnct(*args)

    return wrapper


@log_wrapper
def exec_script(file_path):
    script_content = open(file_path, "rb").read()
    exec(script_content)


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-f', type=str, help='Client Python script file path.')
    args = parser.parse_args()

    print(args.f)

    exec_script(args.f)


if __name__ == "__main__":
    main()