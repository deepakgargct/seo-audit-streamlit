import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
from crawler import crawl_site
from seo_checks import (
    extract_title, extract_meta_description, extract_canonical,
    extract_robots_meta, extract_headings, extract_word_count,
    extract_images_missing_alt, extract_structured_data,
    get_keywords, readability_score
)
from pagespeed_api import get_pagespeed_data
from utils.sitemap_utils import get_sitemap_urls
from utils.score_utils import page_priority
from data_store import save_run, list_runs, load_run
from export_utils import export_to_sheets

load_dotenv()

PAGESPEED_API_KEY = os.getenv("PAGESPEED_API_KEY")  # Put in .env

st.set_page_config(page_title="SEO Auditor", layout="wide")

st.title("🔎 Advanced SEO Website Crawler")

start_url = st.text_input("Enter Website URL", "https://example.com")
max_pages = st.number_input("Max pages to crawl", 50, 2000, 300)
run_btn = st.button("Start Crawl")

# ============ PAGE FUNCTIONS ===============
def analyze_results(pages, sitemap_urls=None):
    records = []

    for url, data in pages.items():
        soup = data["soup"]
        status = data["status"]
        depth = data["depth"]
        load_time = data["load_time"]

        # SEO
        title, title_len = extract_title(soup)
        meta_desc, meta_desc_len = extract_meta_description(soup)
        canonical = extract_canonical(soup)
        robots_meta = extract_robots_meta(soup)
        headings, h1_issues = extract_headings(soup)
        wc = extract_word_count(soup)
        imgs_no_alt = extract_images_missing_alt(soup)
        schema_count = extract_structured_data(soup)
        readable = readability_score(soup)
        keywords = get_keywords(soup, top_n=10)

        # PageSpeed metrics
        cwv = {}
        if PAGESPEED_API_KEY:
            cwv = get_pagespeed_data(url, PAGESPEED_API_KEY)

        row = {
            "URL": url,
            "Status": status,
            "Depth": depth,
            "Load Time (s)": load_time,
            "Title": title,
            "Title Length": title_len,
            "Meta Description": meta_desc,
            "Meta Desc Length": meta_desc_len,
            "Canonical": canonical,
            "Robots": robots_meta,
            "H1 Issues": ", ".join(h1_issues),
            "Word Count": wc,
            "Images Missing Alt": imgs_no_alt,
            "Structured Data Count": schema_count,
            "Readability": readable,
            "Top Keywords": ", ".join(keywords.keys()),
            "LCP": cwv.get("LCP"),
            "CLS": cwv.get("CLS"),
            "TBT": cwv.get("TBT"),
            "Perf Score": cwv.get("Performance Score")
        }

        records.append(row)

    df = pd.DataFrame(records)

    # Canonical mismatch
    df["Canonical Mismatch"] = df.apply(
        lambda r: r["Canonical"] and r["Canonical"].rstrip("/") != r["URL"].rstrip("/"),
        axis=1
    )

    # Orphan pages
    if sitemap_urls:
        df["In Sitemap"] = df["URL"].isin(sitemap_urls)
        df["Orphan"] = (~df["URL"].isin(sitemap_urls)) & (df["Depth"] > 1)
    else:
        df["In Sitemap"] = False
        df["Orphan"] = False

    # Page Priority
    df["Priority"] = df.apply(page_priority, axis=1)

    return df

# ============ MAIN WORKFLOW ===============
if run_btn:
    if not start_url.startswith("http"):
        st.error("❌ Invalid URL")
        st.stop()

    with st.spinner("🔍 Crawling website…"):
        crawled = crawl_site(start_url, max_pages=max_pages)

    with st.spinner("🔎 Checking sitemap…"):
        sitemap_urls = get_sitemap_urls(start_url)

    with st.spinner("🧠 Running SEO checks…"):
        df = analyze_results(crawled, sitemap_urls)

    st.success("✅ Completed!")
    st.dataframe(df, use_container_width=True)

    # Download
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "results.csv", "text/csv")

    # Export Google Sheets
    if st.button("Export to Google Sheets"):
        export_to_sheets(df, "creds.json", "SEO Audit")
        st.success("✅ Exported to Google Sheets!")

    # Save Run
    run_name = st.text_input("Save current run as:", "latest_audit")
    if st.button("Save Run"):
        f = save_run(df, run_name)
        st.success(f"✅ Saved {run_name}!")

    st.markdown("---")

# ============ HISTORY & COMPARISON ========
st.header("📊 Compare Historical Runs")

runs = list_runs()
if runs:
    c1, c2 = st.columns(2)

    with c1:
        run1 = st.selectbox("Select Run 1", runs)
    with c2:
        run2 = st.selectbox("Select Run 2", runs)

    if st.button("Compare"):
        df1 = load_run(run1)
        df2 = load_run(run2)

        d1 = set(df1["URL"])
        d2 = set(df2["URL"])

        added = d2 - d1
        removed = d1 - d2
        common = d1 & d2

        st.write("🟢 Added Pages:", added)
        st.write("🔴 Removed Pages:", removed)

        # Issues change check
        merged = df1[["URL","Priority"]].merge(
            df2[["URL","Priority"]],
            on="URL", 
            suffixes=("_old", "_new")
        )

        merged["Priority Change"] = merged["Priority_new"] - merged["Priority_old"]
        st.dataframe(merged, use_container_width=True)

else:
    st.info("No history found. Run + Save first!")

