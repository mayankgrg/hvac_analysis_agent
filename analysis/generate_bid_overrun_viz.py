#!/usr/bin/env python3
import ast
import csv
import html
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path("hvac_construction_dataset")
OUT_HTML = Path("analysis/bid_overrun_visualization.html")
OUT_CSV = Path("analysis/bid_overrun_line_summary.csv")


def load_contract_names(path: Path):
    names = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            names[row["project_id"]] = row["project_name"]
    return names


def load_sov_metadata(path: Path):
    meta = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            meta[(row["project_id"], row["sov_line_id"])] = {
                "line_number": int(row["line_number"]),
                "description": row["description"],
                "scheduled_value": float(row["scheduled_value"] or 0),
            }
    return meta


def load_bid_max(path: Path):
    bid = {}
    cols = [
        "estimated_labor_cost",
        "estimated_material_cost",
        "estimated_equipment_cost",
        "estimated_sub_cost",
    ]
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["project_id"], row["sov_line_id"])
            bid[key] = sum(float(row[c] or 0) for c in cols)
    return bid


def load_actual_labor(path: Path):
    labor = defaultdict(float)
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["project_id"], row["sov_line_id"])
            st = float(row["hours_st"] or 0)
            ot = float(row["hours_ot"] or 0)
            rate = float(row["hourly_rate"] or 0)
            burden = float(row["burden_multiplier"] or 1)
            labor[key] += (st + 1.5 * ot) * rate * burden
    return labor


def load_actual_material(path: Path):
    material = defaultdict(float)
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["project_id"], row["sov_line_id"])
            material[key] += float(row["total_cost"] or 0)
    return material


def load_rejected_co_exposure(path: Path):
    exposure = defaultdict(float)
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["status"].strip().lower() != "rejected":
                continue
            amount = float(row["amount"] or 0)
            if amount <= 0:
                continue

            text = row.get("affected_sov_lines") or "[]"
            try:
                lines = ast.literal_eval(text)
                if not isinstance(lines, list):
                    lines = []
            except (SyntaxError, ValueError):
                lines = []

            if not lines:
                continue

            split_amount = amount / len(lines)
            for sov_line in lines:
                exposure[(row["project_id"], sov_line)] += split_amount

    return exposure


def money(x):
    return f"${x:,.0f}"


def pct(x):
    return f"{x * 100:.1f}%"


def css_class_from_ratio(ratio):
    if ratio <= 0:
        return "safe"
    if ratio <= 0.05:
        return "mild"
    if ratio <= 0.15:
        return "warn"
    return "critical"


def main():
    contracts = load_contract_names(DATA_DIR / "contracts.csv")
    sov_meta = load_sov_metadata(DATA_DIR / "sov.csv")
    bid_max = load_bid_max(DATA_DIR / "sov_budget.csv")
    labor = load_actual_labor(DATA_DIR / "labor_logs.csv")
    material = load_actual_material(DATA_DIR / "material_deliveries.csv")
    rejected_exposure = load_rejected_co_exposure(DATA_DIR / "change_orders.csv")

    project_totals = defaultdict(lambda: {
        "bid_max": 0.0,
        "expected_cost": 0.0,
        "variance": 0.0,
        "exceeding_lines": 0,
        "total_lines": 0,
    })

    line_rows = []
    for key, bid in bid_max.items():
        project_id, sov_line_id = key
        actual_labor = labor[key]
        actual_material = material[key]
        rejected = rejected_exposure[key]
        expected_cost = actual_labor + actual_material + rejected
        variance = expected_cost - bid
        exceeds = variance > 0

        meta = sov_meta.get(key, {"line_number": 0, "description": "Unknown", "scheduled_value": 0.0})

        row = {
            "project_id": project_id,
            "project_name": contracts.get(project_id, project_id),
            "sov_line_id": sov_line_id,
            "line_number": meta["line_number"],
            "description": meta["description"],
            "scheduled_value": meta["scheduled_value"],
            "bid_max_cost": bid,
            "actual_labor_cost": actual_labor,
            "actual_material_cost": actual_material,
            "rejected_co_exposure": rejected,
            "expected_unrecovered_cost": expected_cost,
            "variance_to_bid_max": variance,
            "variance_pct": (variance / bid) if bid else 0.0,
            "exceeds_bid_max": exceeds,
        }
        line_rows.append(row)

        p = project_totals[project_id]
        p["bid_max"] += bid
        p["expected_cost"] += expected_cost
        p["variance"] += variance
        p["total_lines"] += 1
        if exceeds:
            p["exceeding_lines"] += 1

    for project_id, vals in project_totals.items():
        vals["project_name"] = contracts.get(project_id, project_id)
        vals["variance_pct"] = vals["variance"] / vals["bid_max"] if vals["bid_max"] else 0.0

    project_list = sorted(project_totals.items(), key=lambda x: x[1]["variance"], reverse=True)

    flagged_projects = [pid for pid, v in project_list if v["variance"] > 0]

    line_rows.sort(key=lambda x: (x["project_id"], x["line_number"]))

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(line_rows[0].keys()))
        writer.writeheader()
        writer.writerows(line_rows)

    all_line_numbers = sorted({r["line_number"] for r in line_rows})

    max_abs = max(abs(r["variance_pct"]) for r in line_rows) if line_rows else 1.0
    max_abs = max(max_abs, 0.01)

    project_rows_html = []
    for project_id, vals in project_list:
        ratio = vals["variance_pct"]
        width = min(100, max(0, abs(ratio) * 100 / 0.75))
        cls = css_class_from_ratio(ratio)
        project_rows_html.append(
            """
            <tr>
              <td>{project_id}</td>
              <td>{project_name}</td>
              <td>{bid}</td>
              <td>{expected}</td>
              <td class=\"{cls}\">{variance}</td>
              <td>{exceeding}/{total}</td>
              <td>
                <div class=\"bar-track\"><div class=\"bar {cls}\" style=\"width:{width:.1f}%\"></div></div>
                <div class=\"bar-label\">{ratio}</div>
              </td>
            </tr>
            """.format(
                project_id=html.escape(project_id),
                project_name=html.escape(vals["project_name"]),
                bid=money(vals["bid_max"]),
                expected=money(vals["expected_cost"]),
                variance=money(vals["variance"]),
                exceeding=vals["exceeding_lines"],
                total=vals["total_lines"],
                width=width,
                cls=cls,
                ratio=pct(ratio),
            )
        )

    matrix_by_project = defaultdict(dict)
    for r in line_rows:
        matrix_by_project[r["project_id"]][r["line_number"]] = r

    heatmap_rows_html = []
    for project_id, vals in project_list:
        tds = []
        for line_number in all_line_numbers:
            r = matrix_by_project[project_id].get(line_number)
            if not r:
                tds.append("<td class='missing'>-</td>")
                continue
            ratio = r["variance_pct"]
            if ratio <= 0:
                cls = "safe"
            elif ratio <= 0.05:
                cls = "mild"
            elif ratio <= 0.15:
                cls = "warn"
            else:
                cls = "critical"
            tds.append(
                f"<td class='{cls}' title='{html.escape(r['description'])}: {money(r['variance_to_bid_max'])} ({pct(ratio)})'>{pct(ratio)}</td>"
            )
        heatmap_rows_html.append(
            f"<tr><td>{html.escape(project_id)}</td><td>{html.escape(vals['project_name'])}</td>{''.join(tds)}</tr>"
        )

    top_exceeded = sorted([r for r in line_rows if r["exceeds_bid_max"]], key=lambda x: x["variance_to_bid_max"], reverse=True)[:15]
    top_rows_html = []
    for r in top_exceeded:
        top_rows_html.append(
            """
            <tr>
              <td>{project_id}</td>
              <td>{line_no}</td>
              <td>{desc}</td>
              <td>{bid}</td>
              <td>{expected}</td>
              <td class=\"critical\">{variance}</td>
              <td>{ratio}</td>
            </tr>
            """.format(
                project_id=html.escape(r["project_id"]),
                line_no=r["line_number"],
                desc=html.escape(r["description"]),
                bid=money(r["bid_max_cost"]),
                expected=money(r["expected_unrecovered_cost"]),
                variance=money(r["variance_to_bid_max"]),
                ratio=pct(r["variance_pct"]),
            )
        )

    html_doc = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>HVAC Bid Max Overrun Analysis</title>
  <style>
    :root {{
      --bg: #f4f6f8;
      --card: #ffffff;
      --ink: #1f2933;
      --muted: #52606d;
      --safe: #2f9e44;
      --mild: #f08c00;
      --warn: #e8590c;
      --critical: #c92a2a;
      --border: #d9e2ec;
    }}
    body {{
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      background: linear-gradient(180deg, #eef3f8, #f8fafc);
      color: var(--ink);
      margin: 0;
      padding: 24px;
    }}
    .container {{ max-width: 1400px; margin: 0 auto; }}
    .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 18px; margin-bottom: 16px; box-shadow: 0 6px 18px rgba(9,30,66,0.05); }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    h2 {{ margin: 0 0 10px; font-size: 21px; }}
    p {{ color: var(--muted); margin-top: 0; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid var(--border); padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f8fbff; position: sticky; top: 0; z-index: 1; }}
    .scroll {{ overflow-x: auto; max-width: 100%; }}
    .bar-track {{ background: #e4ecf4; border-radius: 999px; height: 10px; width: 160px; }}
    .bar {{ height: 100%; border-radius: 999px; }}
    .bar-label {{ font-size: 12px; color: var(--muted); margin-top: 4px; }}
    .safe {{ color: var(--safe); background: #ebfbee; }}
    .mild {{ color: #9c6200; background: #fff4e6; }}
    .warn {{ color: #8a3b12; background: #fff0e6; }}
    .critical {{ color: var(--critical); background: #fff5f5; }}
    .bar.safe {{ background: var(--safe); }}
    .bar.mild {{ background: var(--mild); }}
    .bar.warn {{ background: var(--warn); }}
    .bar.critical {{ background: var(--critical); }}
    .missing {{ color: #9aa5b1; text-align: center; }}
    .kpis {{ display: grid; grid-template-columns: repeat(4, minmax(180px, 1fr)); gap: 10px; margin-top: 10px; }}
    .kpi {{ padding: 12px; border-radius: 10px; border: 1px solid var(--border); background: #f8fbff; }}
    .kpi .label {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }}
    .kpi .value {{ font-size: 22px; font-weight: 700; margin-top: 4px; }}
    @media (max-width: 900px) {{
      .kpis {{ grid-template-columns: 1fr 1fr; }}
    }}
  </style>
</head>
<body>
  <div class=\"container\">
    <div class=\"card\">
      <h1>HVAC Margin Rescue: Bid-Max Exceedance View</h1>
      <p>Method: For each SOV line, compare <strong>bid maximum cost</strong> (`estimated_labor + estimated_material + estimated_equipment + estimated_sub`) against <strong>expected unrecovered cost</strong> (`actual labor cost + actual material cost + rejected positive CO exposure`).</p>
      <div class=\"kpis\">
        <div class=\"kpi\"><div class=\"label\">Projects Flagged</div><div class=\"value\">{len(flagged_projects)} / {len(project_list)}</div></div>
        <div class=\"kpi\"><div class=\"label\">SOV Lines Exceeding</div><div class=\"value\">{sum(1 for r in line_rows if r['exceeds_bid_max'])} / {len(line_rows)}</div></div>
        <div class=\"kpi\"><div class=\"label\">Total Bid Max (All Lines)</div><div class=\"value\">{money(sum(v['bid_max'] for _, v in project_list))}</div></div>
        <div class=\"kpi\"><div class=\"label\">Total Expected Cost</div><div class=\"value\">{money(sum(v['expected_cost'] for _, v in project_list))}</div></div>
      </div>
    </div>

    <div class=\"card\">
      <h2>Step 1: Red-Flag Projects</h2>
      <p>Projects sorted by total variance to bid max. Bar indicates overrun % relative to bid maximum.</p>
      <div class=\"scroll\">
        <table>
          <thead>
            <tr>
              <th>Project</th>
              <th>Name</th>
              <th>Bid Max</th>
              <th>Expected Cost</th>
              <th>Variance</th>
              <th>Exceeded Lines</th>
              <th>Overrun Ratio</th>
            </tr>
          </thead>
          <tbody>
            {''.join(project_rows_html)}
          </tbody>
        </table>
      </div>
    </div>

    <div class=\"card\">
      <h2>Step 2: Deep Dive by SOV Line</h2>
      <p>Cell values show line-level variance % vs bid max. Hover a cell to see line description and absolute dollar variance.</p>
      <div class=\"scroll\">
        <table>
          <thead>
            <tr>
              <th>Project</th>
              <th>Name</th>
              {''.join(f'<th>L{ln:02d}</th>' for ln in all_line_numbers)}
            </tr>
          </thead>
          <tbody>
            {''.join(heatmap_rows_html)}
          </tbody>
        </table>
      </div>
      <p style=\"margin-top:10px\"><strong>Legend:</strong> Safe (<=0%), Mild (0-5%), Warn (5-15%), Critical (>15%).</p>
    </div>

    <div class=\"card\">
      <h2>Top 15 Highest Exceedances</h2>
      <div class=\"scroll\">
        <table>
          <thead>
            <tr>
              <th>Project</th>
              <th>Line</th>
              <th>Description</th>
              <th>Bid Max</th>
              <th>Expected Cost</th>
              <th>Variance</th>
              <th>Variance %</th>
            </tr>
          </thead>
          <tbody>
            {''.join(top_rows_html)}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</body>
</html>
"""

    OUT_HTML.write_text(html_doc, encoding="utf-8")
    print(f"Wrote {OUT_HTML}")
    print(f"Wrote {OUT_CSV}")


if __name__ == "__main__":
    main()
