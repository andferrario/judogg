from app_fakes import WEIGHTS, filters

from judogg.app.domain.categories import most_frequent_weight, selected_weights, sort_orders
from judogg.app.domain.links import athlete_url, contest_url, judotv_url


def test_selected_weights() -> None:
    chosen = selected_weights(filters(weight=("m-81", "m-73", "m-81")), WEIGHTS)
    assert [w.code for w in chosen] == ["m-73", "m-81"]  # category order, no duplicate
    assert selected_weights(filters(gender="f"), WEIGHTS)[0].code == "f-48"
    assert len(selected_weights(filters(), WEIGHTS)) == 14


def test_most_frequent_weight_ties_by_sort_order() -> None:
    order = sort_orders(WEIGHTS)
    assert most_frequent_weight({"m-81": 2, "m-73": 2, "m-60": 1}, order) == "m-73"


def test_links() -> None:
    assert contest_url("gs_x_0001") == "https://judobase.ijf.org/#/competition/contest/gs_x_0001"
    assert judotv_url("gs_x", "gs_x_0001") == "https://judotv.com/competitions/gs_x/contests/gs_x_0001"
    assert judotv_url(None, "gs_x_0001") is None
    assert athlete_url(7) == "https://judobase.ijf.org/#/competitor/profile/7"
