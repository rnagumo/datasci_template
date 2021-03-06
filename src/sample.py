
"""Template for ml training"""

import argparse
import json
import logging
import pathlib
import time


# 機械学習モデルの学習
def run(logger, config, args):
    """Runs function for main process.

    Parameters
    ----------
    logger : logging.Logger
        Logger
    config : dict
        Config dict
    args : argparse.Namespace
        Parsed command line args
    """

    logger.info("Start run function")
    logger.info(f"Command line args, {args}")

    # --- some_process ---
    if args.flag:
        logger.info("True process")
    else:
        logger.info("False process")

    logger.info(f"Param1 = {config['param1']}")

    logger.info("End run function")


# ロガーの設定
def init_logger(logdir):
    """Initalizes logger.

    Set stream and file handler with specified format.

    Parameters
    ----------
    logdir : str
        Path to logger directory

    Returns
    -------
    logger : logging.Logger
        Logger
    """

    # Check logdir
    logdir = pathlib.Path(logdir)
    logdir.mkdir(parents=True, exist_ok=True)

    # Log file
    logfn = "training_{}.log".format(time.strftime("%Y%m%d"))
    logpath = logdir / logfn

    # Initialize logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Set stream handler (console)
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh_fmt = logging.Formatter(
        "%(asctime)s - %(module)s.%(funcName)s - %(levelname)s : %(message)s")
    sh.setFormatter(sh_fmt)
    logger.addHandler(sh)

    # Set file handler (log file)
    fh = logging.FileHandler(filename=logpath)
    fh.setLevel(logging.INFO)
    fh_fmt = logging.Formatter(
        "%(asctime)s - %(module)s.%(funcName)s - %(levelname)s : %(message)s")
    fh.setFormatter(fh_fmt)
    logger.addHandler(fh)

    return logger


# jsonファイルを読み込む
def load_config(path):
    """Loads config file.

    Parameters
    ----------
    path : str
        Path to config json file

    Returns
    -------
    config : dict
        Config settings
    """

    with pathlib.Path(path).open() as f:
        config = json.load(f)
    return config


# resultsフォルダにconfigを保存する
def save_config(logdir, config):
    """Saves config file in specified results directory.

    Parameters
    ----------
    logdir : str
        Path to logging directory
    config : dict
        Config settings.
    """

    with pathlib.Path(logdir, "config.json").open("w") as f:
        json.dump(config, f)


# コマンドライン引数
def init_args():
    """Initialize command line parser.

    Returns
    -------
    args : argparse.Namespace
        Parsed command line args
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--logdir", type=str, default="../logs/tmp/",
                        help="Log directory")
    parser.add_argument("--config-path", type=str, default="./config.json",
                        help="Path to config json file")
    parser.add_argument("--data-path", type=str,
                        default="../data/output/tmp.csv",
                        help="Path to dataset for ML")
    parser.add_argument("--flag", action="store_true",
                        help="Some flag (default=False)")
    parser.add_argument("--value", type=int, default=0,
                        help="Some value")
    return parser.parse_args()


# Main関数
def main():
    """Main function.

    1. Load settings (args, logger, config).
    2. Run main process.
    """

    # Settings
    args = init_args()
    logger = init_logger(args.logdir)
    config = load_config(args.config_path)
    save_config(args.logdir, config)

    # Run ml training
    try:
        run(logger, config, args)
    except Exception as e:
        logger.exception(f"Main function error: {e}")

    logger.info("End logger")


if __name__ == "__main__":
    main()
