#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "tabulate",
# ]
# ///

import json
from pathlib import Path

from tabulate import tabulate


def extract_movie_title(filename):
    """Extract a readable title from the filename"""
    # Remove extension and convert underscores to spaces
    title = Path(filename).stem.replace("_", " ")
    # Capitalize each word
    return title.title()


def read_json_results(folder_path):
    """Read all JSON files in the specified folder and extract key data"""
    results = []

    # Get all JSON files in the folder
    json_files = sorted(Path(folder_path).glob("*.json"))

    for json_file in json_files:
        try:
            with open(json_file, "r") as f:
                data = json.load(f)

            # Extract the movie title from the video filename
            movie_title = extract_movie_title(data["video_file"]["name"])

            # Extract the required fields
            result = {
                "Movie": movie_title,
                "Intro End": data["intro_end_time"],
                "Outro Start": data["outro_start_time"],
                "Cost ($)": f"{data['total_cost']:.3f}",
            }

            results.append(result)

        except Exception as e:
            print(f"Error reading {json_file}: {e}")

    return results


def generate_markdown_table(results):
    """Generate a markdown table from the results"""
    if not results:
        return "No results found"

    # Create the table
    headers = list(results[0].keys())
    rows = [[r[h] for h in headers] for r in results]

    # Generate markdown table
    markdown_table = tabulate(rows, headers=headers, tablefmt="pipe")

    # Calculate total cost
    total_cost = sum(float(r["Cost ($)"]) for r in results)

    return markdown_table, total_cost


def generate_html_table(results):
    """Generate an HTML table for Medium"""
    if not results:
        return "No results found"

    html = '<table style="width:100%; border-collapse: collapse;">\n'
    html += '<thead>\n<tr style="background-color: #f2f2f2;">\n'

    # Headers
    headers = list(results[0].keys())
    for header in headers:
        html += f'<th style="border: 1px solid #ddd; padding: 12px; text-align: left;">{header}</th>\n'
    html += "</tr>\n</thead>\n<tbody>\n"

    # Rows
    for i, result in enumerate(results):
        bg_color = "#f9f9f9" if i % 2 == 0 else "#ffffff"
        html += f'<tr style="background-color: {bg_color};">\n'
        for header in headers:
            html += f'<td style="border: 1px solid #ddd; padding: 12px;">{result[header]}</td>\n'
        html += "</tr>\n"

    html += "</tbody>\n</table>"

    return html


def main():
    # Specify the folder containing JSON files
    folder_path = input(
        "Enter the path to the folder containing JSON files (or press Enter for current directory): "
    ).strip()
    if not folder_path:
        folder_path = "."

    # Read all JSON results
    results = read_json_results(folder_path)

    if not results:
        print("No JSON files found in the specified folder.")
        return

    # Sort results by movie name
    results.sort(key=lambda x: x["Movie"])

    # Generate markdown table
    markdown_table, total_cost = generate_markdown_table(results)

    print("\n=== RESULTS SUMMARY ===")
    print(f"Total movies analyzed: {len(results)}")
    print(f"Total cost: ${total_cost:.2f}")
    print(f"Average cost per movie: ${total_cost / len(results):.3f}")

    print("\n=== MARKDOWN TABLE (for GitHub/README) ===")
    print(markdown_table)

    # Generate HTML table
    html_table = generate_html_table(results)

    print("\n=== HTML TABLE (for Medium) ===")
    print(html_table)

    # Save to files
    with open("results_summary.md", "w") as f:
        f.write("# Credit Scout Results\n\n")
        f.write(f"**Total movies analyzed:** {len(results)}\n")
        f.write(f"**Total cost:** ${total_cost:.2f}\n")
        f.write(f"**Average cost per movie:** ${total_cost / len(results):.3f}\n\n")
        f.write(markdown_table)

    with open("results_table.html", "w") as f:
        f.write(html_table)

    print("\n✅ Results saved to 'results_summary.md' and 'results_table.html'")


if __name__ == "__main__":
    main()
