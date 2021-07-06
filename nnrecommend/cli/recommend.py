import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
from nnrecommend.dataset import load_model
import click
import torch
from typing import Container
from nnrecommend.cli.main import Context, main
from nnrecommend.logging import get_logger
from nnrecommend.operation import Finder, Recommender

@main.command()
@click.pass_context
@click.argument('path', type=click.Path(file_okay=True, dir_okay=False))
@click.option('--item', 'item_names', default=[], multiple=True, type=str, help="items that you like")
@click.option('--field', 'fields', default=[], multiple=True, type=str, help="fields in item info to check")
@click.option('--topk', type=int, default=3, help="amount of recommended items to show")
def recommend(ctx, path: str, item_names: Container[str], fields: Container[str], topk: int) -> None:
    """
    load a model and get recommendations
    """
    ctx: Context = ctx.obj
    logger = ctx.logger or get_logger(recommend)
    device = ctx.device

    logger.info("reading model file...")
    try:
        r = load_model(path)
        model: torch.nn.Module = r[0]
        idrange: np.ndarray = r[1]
        items: DataFrame = r[2]
    except:
        logger.error("failed to load model file")
        return False

    if model is None:
        logger.error("could not load model")
        return

    logger.info(f"loaded model of type {type(model)}")
    model = model.eval().to(device)

    items = items.dropna(axis=1, how='all')

    pd.options.display.max_colwidth = 200

    with torch.no_grad():
        finder = Finder(items, fields)
        recommender = Recommender(idrange, items, model, device)

        for item_name in item_names:
            r = finder(item_name)
            logger.info(f"found {r}")
            logger.info("looking for recommendations...")
            for item, rating in recommender(r.id, topk):
                logger.info(f"rating:{rating:.4f}\n{item.to_string()}")