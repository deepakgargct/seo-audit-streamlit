def page_priority(row):
    score = 0

    # Status
    if row.get("Status") != 200:
        score += 40

    # Title
    if row.get("Title Length", 0) == 0:
        score += 20

    # Meta Description
    if row.get("Meta Desc Length", 0) == 0:
        score += 20

    # H1 issues
    if row.get("H1 Issues"):
        score += 10

    # Images missing ALT
    if row.get("Images Missing Alt", 0) > 5:
        score += 5

    # LCP slow
    if row.get("LCP") and row.get("LCP") > 3000:
        score += 10

    return score
