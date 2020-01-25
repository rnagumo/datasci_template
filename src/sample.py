
"""Template for ml training"""

import argparse
import json
import logging
import pathlib
import time


# 機械学習モデルの学習
def run(logger, config, args):
    logger.info("Start run function")

    # --- some_process ---
    if args.flag:
        logger.info("True process")
    else:
        logger.info("False process")

    logger.info(f"Param1 = {config['param1']}")

    logger.info("End run function")


# ロガーの設定
def init_logger(logdir):

    log_dir = pathlib.Path(logdir)
    if not log_dir.exists():
        log_dir.mkdir()

    log_fn = "training_{}.log".format(time.strftime("%Y%m%d"))
    log_path = log_dir.joinpath(log_fn)

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
    fh = logging.FileHandler(filename=log_path)
    fh.setLevel(logging.INFO)
    fh_fmt = logging.Formatter(
        "%(asctime)s - %(module)s.%(funcName)s - %(levelname)s : %(message)s")
    fh.setFormatter(fh_fmt)
    logger.addHandler(fh)

    return logger


# jsonファイルを読み込む
def load_config(path):
    config_path = pathlib.Path(path)
    with config_path.open() as f:
        config = json.load(f)
    return config


# resultsフォルダにconfigを保存する
def save_config(results_dir, config):

    results_path = pathlib.Path(results_dir)
    if not results_path.exists():
        results_path.mkdir()

    with results_path.joinpath("config.json").open("w") as f:
        json.dump(config, f)


# コマンドライン引数
def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--logdir", type=str, default="../logs/",
                        help="Log directory")
    parser.add_argument("--config", type=str, default="./config.json",
                        help="Config json file")
    parser.add_argument("--results-dir", type=str, default="../results/",
                        help="Results directory")
    parser.add_argument("--flag", action="store_true",
                        help="Some flag (default=False)")
    parser.add_argument("--value", type=int, default=0,
                        help="Some value")
    return parser.parse_args()


# Main関数
def main():
    # Settings
    args = init_args()
    logger = init_logger(args.logdir)
    config = load_config(args.config)
    save_config(args.results_dir, config)

    # Log args
    for k, v in vars(args).items():
        logger.info(f"{k} = {v}")

    # Run ml training
    try:
        run(logger, config, args)
    except Exception as e:
        logger.exception(f"Main function error: {e}")

    logger.info("End logger")


if __name__ == "__main__":
    main()
