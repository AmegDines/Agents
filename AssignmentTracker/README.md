Assignment Tracker
--------------------

** My agent has three tools: add_assignment,remove assignment and get_upcoming. It uses add_assignment to save a task and its due date,remove_assignment to remove it and get_upcoming to see all of them.

** The memory works by keeping a global list called chat_memory. Every message, tool call, and answer is added to this list. This way, when the agent runs again, it remembers everything we talked about.

** One honest failure I hit was the agent getting stuck and calling the same tool over and over. I handled this by limiting the agent to a loop of 5 steps maximum, and making sure the tool output was always passed back to the agent so it knew the tool finished.
Second failure if we try to delete an assignment with incorrect date this agent will fail.
