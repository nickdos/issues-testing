import csv
import subprocess
import os

# --- Configuration ---
REPO_OWNER = "AtlasOfLivingAustralia"  # "nickdos"  # Replace with your repository owner (username or organization)
REPO_NAME = "species-lists"  # "issues-testing"  # Replace with your repository name
# CSV_FILE_PATH = "ListToolTest1.csv"  # Path to your CSV file
CSV_FILE_PATH = "ListToolTestScriptSoftwareReview.csv"

# Summary,Category,Size (S/M/L),Details,Link,Priority for integration testing,Status / comment


# --- CSV Header to GitHub Field Mapping ---
# Define mapping of GitHub issue fields to CSV column headers.
# GitHub Field (key) : CSV Column Header (value)  or [List of CSV Column Headers] for concatenation
CSV_TO_GH_FIELD_MAPPING = {
    "title": "Summary",  # GitHub issue title field gets content from CSV column "Issue Title"
    # "body": "Issue Description",  # GitHub issue body field gets content from CSV column "Issue Description"
    "labels": "Category",  # GitHub issue labels field gets content from CSV column "Labels"
    "assignees": "Assignees",  # GitHub issue assignees field gets content from CSV column "Assignees"
    "milestone": "Milestone",  # GitHub issue milestone field gets content from CSV column "Milestone"
    # Example of Concatenation: GitHub issue body field gets content from "Summary" and "Details" CSV columns
    "body": [
        "Details",
        "Size (S/M/L)",
        "Priority for integration testing",
        "Link",
        "Status / comment",
    ],  # **Corrected Concatenation Example:  body field gets combined content**
}

# --- Optional: Label Separator (if labels are comma or pipe separated in CSV) ---
LABEL_SEPARATOR = "|"  # or "," or None if labels are already space-separated or single label per column


def import_issues_from_csv_gh_cli(
    csv_file_path, repo_owner, repo_name, csv_header_mapping, label_separator=None
):
    """
    Imports issues from a CSV file into a GitHub repository using the gh CLI tool.

    Args:
        csv_file_path (str): Path to the CSV file.
        repo_owner (str): GitHub repository owner (username or organization).
        repo_name (str): GitHub repository name.
        csv_header_mapping (dict): Dictionary mapping GitHub issue fields to CSV column headers.
                Keys are GitHub field names (strings), Values are CSV header names (strings) or lists of header names for concatenation.
        label_separator (str, optional): Separator for multiple labels in the CSV column. Defaults to None.
    """

    try:  # **Outer try block - now correctly placed around file opening**
        with open(csv_file_path, mode="r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                gh_command = [
                    "gh",
                    "issue",
                    "create",
                    "--repo",
                    f"{repo_owner}/{repo_name}",
                ]

                for (
                    gh_field_name,
                    csv_header_target,
                ) in (
                    csv_header_mapping.items()
                ):  # Corrected loop order - iterate through GitHub fields as keys
                    if isinstance(csv_header_target, str):  # Single CSV column mapping
                        csv_value = row.get(
                            csv_header_target
                        )  # Get CSV value using CSV header as key

                        if csv_value:  # Only process if CSV column has a value
                            if gh_field_name == "title" or gh_field_name == "body":
                                gh_command.extend([f"--{gh_field_name}", csv_value])
                            elif gh_field_name == "labels":
                                if label_separator and label_separator in csv_value:
                                    labels = csv_value.split(label_separator)
                                    for label in labels:
                                        gh_command.extend(
                                            ["--label", label.strip()]
                                        )  # Trim whitespace
                                elif csv_value:
                                    gh_command.extend(
                                        ["--label", csv_value]
                                    )  # Assume single label or space-separated
                            elif gh_field_name == "assignees":
                                assignees = csv_value.split(
                                    ","
                                )  # Assuming comma-separated assignees
                                for assignee in assignees:
                                    gh_command.extend(
                                        ["--assignee", assignee.strip()]
                                    )  # Trim whitespace
                            elif gh_field_name == "milestone":
                                gh_command.extend(["--milestone", csv_value])

                    elif isinstance(
                        csv_header_target, list
                    ):  # Concatenation of multiple CSV columns
                        combined_value_parts = []
                        for (
                            header_part
                        ) in (
                            csv_header_target
                        ):  # Loop through CSV headers to concatenate
                            part_value = row.get(header_part)
                            if part_value:
                                combined_value_parts.append(part_value)
                        combined_value = "\n".join(
                            combined_value_parts
                        )  # Join with newline for body
                        if (
                            combined_value
                        ):  # Only add body if there's content after concatenation
                            gh_command.extend(["--body", combined_value])

                print(
                    f"Executing: {' '.join(gh_command)}"
                )  # Optional: Print the command being executed

                try:  # **Inner try block - for subprocess execution - correctly placed and handled**
                    result = subprocess.run(
                        gh_command, capture_output=True, text=True, check=True
                    )
                    print(f"Issue created successfully. Output:\n{result.stdout}")
                except subprocess.CalledProcessError as e:
                    print(
                        f"Error creating issue. Command failed with exit code {e.returncode}:"
                    )
                    print(f"Command: {' '.join(gh_command)}")
                    print(f"Error Output:\n{e.stderr}")
                except (
                    FileNotFoundError
                ):  # **Inner try block - FileNotFoundError for gh CLI**
                    print(
                        "Error: gh CLI tool not found. Make sure it's installed and in your PATH."
                    )
                    return
                except (
                    Exception
                ) as e:  # **Inner try block - Catch-all for unexpected errors during subprocess**
                    print(f"An unexpected error occurred during gh CLI execution: {e}")

    except FileNotFoundError:  # **Outer try block - Handle CSV file not found**
        print(f"Error: CSV file not found at path: {csv_file_path}")
        return
    except UnicodeDecodeError as e:  # **Outer try block - Handle CSV encoding issues**
        print(
            f"Error: Problem decoding CSV file. Ensure it's UTF-8 encoded. Error details: {e}"
        )
        return
    except (
        Exception
    ) as e:  # **Outer try block - Catch-all for other file/CSV related errors**
        print(f"An unexpected error occurred during CSV file processing: {e}")
        return


if __name__ == "__main__":
    # Example Usage:
    import_issues_from_csv_gh_cli(
        csv_file_path=CSV_FILE_PATH,
        repo_owner=REPO_OWNER,
        repo_name=REPO_NAME,
        csv_header_mapping=CSV_TO_GH_FIELD_MAPPING,
        label_separator=LABEL_SEPARATOR,  # Pass the label separator if needed
    )
