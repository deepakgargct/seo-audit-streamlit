def page_priority(row):
    score = 0
    if row["status"] != 200: score += 40
    if row["title_length"] == 0: score += 20
    if row["meta_description_length"] == 0: score += 20
    if row["h1_issues"]: score += 10
    if row["images_missing_alt"] > 5: score += 5
    if row["lcp"] and row["lcp"] > 3000: score += 10
    return score
