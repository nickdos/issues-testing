#!/bin/bash

# --- Configuration ---
REPO_OWNER="nickdos"
REPO_NAME="issues-testing"
CSV_FILE="issues1.csv"

# --- Check if csvkit is installed ---
if ! command -v csvlook &> /dev/null
then
    echo "Error: csvkit is not installed."
    echo "Please install csvkit to run this script."
    echo "  - Using pip: pip install csvkit"
    echo "    (You might need to use pip3 depending on your Python setup)"
    exit 1
fi

# --- Process CSV using csvkit (csvlook) and import issues ---
csvlook  "$CSV_FILE" | tail -n +3 | while IFS=$'\n' read -r line; do # Use csvlook to process CSV, then pipe and read line by line, skipping header with tail (+3 because csvlook output has extra lines)
    # Parse CSV line using what SHOULD be comma separated output from csvlook -f comma
    IFS=, read -ra fields <<< "$line"

    title="${fields[0]}"
    body="${fields[1]}"
    labels="${fields[2]}"
    assignees="${fields[3]}"
    milestone="${fields[4]}"


    if [[ "$title" != "Title" ]]; then # Basic header row check (though tail -n +3 should handle better)

        GH_COMMAND="gh issue create --repo $REPO_OWNER/$REPO_NAME --title \"$title\" --body \"$body\""

        # Handle multiple labels separated by pipe (|)
        if [[ -n "$labels" ]]; then
            IFS='|' read -ra LABELS_ARRAY <<< "$labels" # Split labels string into an array
            for label in "${LABELS_ARRAY[@]}"; do
            # Trim whitespace from labels if needed (optional)
            label=$(echo "$label" | xargs)
            GH_COMMAND="$GH_COMMAND --label \"$label\""
            done
        fi

        if [[ -n "$assignees" ]]; then
            GH_COMMAND="$GH_COMMAND --assignee \"$assignees\""
        fi
        if [[ -n "$milestone" ]]; then
            GH_COMMAND="$GH_COMMAND --milestone \"$milestone\""
        fi

        echo "Executing: $GH_COMMAND" # Optional: Print the command being executed for debugging
        eval "$GH_COMMAND" # Execute the constructed gh issue create command
    fi
done

echo "Issue import process completed."