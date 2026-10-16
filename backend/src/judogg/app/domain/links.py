def contest_url(contest_code: str) -> str:
    return f"https://judobase.ijf.org/#/competition/contest/{contest_code}"


def judotv_url(competition_code: str | None, contest_code: str) -> str | None:
    if competition_code is None:
        return None
    return f"https://judotv.com/competitions/{competition_code}/contests/{contest_code}"


def athlete_url(athlete_id: int) -> str:
    return f"https://judobase.ijf.org/#/competitor/profile/{athlete_id}"
