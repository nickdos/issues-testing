#!/bin/bash

REPO_OWNER="nickdos"
REPO_NAME="issues-testing"
CSV_FILE="issues1.csv"

while IFS=',' read -r title body labels assignees milestone; do
  if [[ "$title" != "title" ]]; then # Skip header row (assuming "Title" is in header)

  GH_COMMAND="gh issue create --repo $REPO_OWNER/$REPO_NAME --title $title --body $body"

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
done < <(tail -n +2 "$CSV_FILE")