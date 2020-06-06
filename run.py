import config
import hoshino
import daemon
import argparse

bot = hoshino.init(config)
app = bot.asgi

def main():
    bot.run(use_reloader=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--daemon", help="run as daemon", action="store_true")
    args = parser.parse_args()
    if args.daemon:
        with daemon.DaemonContext():
            main()
    else:
        main()
