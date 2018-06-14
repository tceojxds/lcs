from itertools import groupby
from bottle import Bottle, request, run, HTTPResponse

app = Bottle()


@app.post("/lcs")
def post_lcs():
    req_body = request.json
    strings, error = req_body_to_strings(req_body)
    if error is not None:
        return HTTPResponse(status=400, body={"error": error})
    return {
        "lcs": [
            {"value": s}
            for s in lcs(list(strings))
        ]
    }


def req_body_to_strings(req_body):
    set_key = "setOfStrings"
    if type(req_body) is not dict:
        return (None, "Request Body is not a JSON Object")

    values = req_body.get(set_key)
    if type(values) is not list:
        return (None, "key '/{}' is not a JSON Array".format(set_key))

    result = set()
    for i, v in enumerate(values):
        if type(v) is not dict:
            return (None, "key '/{}[{}]' is not a JSON Object".format(set_key, i))
        s = v.get("value")

        if type(s) is not str:
            return (None, "key '/{}[{}]/value' is not a string".format(set_key, i))

        if s in result:
            return (None, "key '/{}' is not a set because {!r} is duplicated".format(set_key, s))

        result.add(s)
    return result, None


def test_req_body_to_strings():
    assert(req_body_to_strings(None) == (
        None, "Request Body is not a JSON Object"))

    assert(req_body_to_strings({}) == (
        None, "key '/setOfStrings' is not a JSON Array"))

    assert(req_body_to_strings({"setOfStrings": None}) == (
        None, "key '/setOfStrings' is not a JSON Array"))

    assert(req_body_to_strings({"setOfStrings": [None]}) == (
        None, "key '/setOfStrings[0]' is not a JSON Object"))

    assert(req_body_to_strings({"setOfStrings": [{"value": None}]}) == (
        None, "key '/setOfStrings[0]/value' is not a string"))

    assert(req_body_to_strings({"setOfStrings": [{"value": "x"}, {"value": "x"}]}) == (
        None, "key '/setOfStrings' is not a set because 'x' is duplicated"))


def lcs(strings):
    # I didn't want to implement a generalized suffix tree to
    # find the lcs, so I brute forced it. This is a MVP right?
    string_count = len(strings)
    if string_count <= 1:
        return []

    s = strings[0]
    for _, xs in groupby(chunks(s), key=len):
        result = set()
        for chunk in xs:
            # Count up all the strings that this chunk is inside
            count = sum(1 for s2 in strings[1:] if chunk in s2)+1
            # This chunk was found in all strings
            if count == string_count:
                result.add(chunk)
        # If we found anything, return early
        if result:
            return result
    return set()


def test_lcs():
    assert(lcs(["abba", "baab"]) == {"ab", "ba"})
    assert(lcs(["chcast", "chromecastic", "broadcaster"]) == {"cast"})


def chunks(s):
    s_len = len(s)
    for i in range(s_len+1, 0, -1):
        for j in range(s_len):
            end = j+i
            if end <= s_len:
                yield s[j:end]


def test_chunks():
    assert(list(chunks("foo")) == ["foo", "fo", "oo", "f", "o", "o"])


if __name__ == '__main__':
    run(app, host='localhost', port=8080)
