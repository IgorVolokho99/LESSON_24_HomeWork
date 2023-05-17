import os
import re

from typing import Any, Iterable, List
from flask import Flask, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


class CustomBadRequest(HTTPException):
    status_code = 400
    description = 'Bad request'


def parse_query(file: Iterable[str], query: str) -> List[str]:
    res = map(lambda v: v.strip(), file)
    for q in query.split("|"):
        q_split = q.split(":")
        cmd = q_split[0]
        if cmd == "filter":
            arg = q_split[1]
            res = filter(lambda v, txt=arg: txt in v, res)
        if cmd == "map":
            arg = int(q_split[1])
            res = map(lambda v, idx=arg: v.split(" ")[idx], res)
        if cmd == "unique":
            res = set(res)
        if cmd == "sort":
            arg = q_split[1]
            reverse = arg == "desc"
            res = sorted(res, reverse=reverse)
        if cmd == "limit":
            arg = int(q_split[1])
            res = list(res)[:arg]
        if cmd == "regex":
            arg = q_split[1]
            res = filter(lambda v, pattern=arg: re.search(pattern, v), res)
    return res


@app.route("/perform_query")
def perform_query() -> Any:
    try:
        query = request.args['query']
        file_name = request.args['file_name']
    except KeyError:
        raise CustomBadRequest(description=f"Neded uery was not found")

    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):
        return CustomBadRequest(description=f"{file_name} was not found")

    with open(file_path) as file:
        res = parse_query(file, query)
        data = '\n'.join(res)

    return app.response_class(data, content_type="text/plain")
