# CauseConnect AI v0.1
Prototype AI-driven recommender app for aspiring activists looking for an
organization to join, based on the Rebert v6 movie recommender prototype by
David McDonald, used with his permission.

## What the prototype does:
The purpose of CauseConnect AI is to recommend community organizing and
political advocacy groups that the user might like to get involved in.
- Like the Rebert prototype, CauseConnect interviews the user using GPT to
  generate two of the interview questions, but they are more structured:
  question 2 always lists ways to get involved with the issue the user named in
  response to the initial hard-coded question, and question 3 always asks about
  skills, resources, and time the user might have to contribute to the cause.
  There is a final hard-coded question about the user's location, and an option
  to only recommend groups based in the user's local area.
- Rather than displaying six randomly selected organizations and trying to match
  them to the user's preferences, CauseConnect uses GPT's internal knowledge
  base to generate a list of up to six recommended groups after going through
  the interview. Therefore, the displayed recommendation flags are always either
  HIGHLY RECOMMENDED or SUGGESTED.
- Like Rebert, CauseConnect displays a description for each card (although it's
  always visible rather than requiring mouse hover), and shows a rationale for
  why the organization was suggested when you hover over the recommendation
  flag. Unlike Rebert, CauseConnect includes a link on each card to go to the
  organization's website.
- While generating the recommendations, CauseConnect runs a hallucination check,
  querying each URL returned by the recommendation prompt to see whether it
  exists and includes the organization name. If either condition is not met, a
  warning is displayed on the organization's card; if the website wasn't found
  at all, the displayed link takes you to an Ecosia web search for the
  organization name.
- Also like Rebert, CauseConnect enables the user to chat with GPT about a given
  organization.

## How to use it:
1. If you don't have an OpenAI API account, create one at
   https://platform.openai.com/login and purchase some tokens
2. Run rebert/classes/data/KeyManager.py, press n, hit enter, and follow the
   instructions to add your API key with the domain api.openai.com
3. Run _causeconnect_1_0_/recommender_0.1.py
4. Maximize your browser window (responsive layout will be implemented soon!)
5. Press the big button in the web interface to start the AI interview
6. Answer as many of the 4 questions as you like and click Recommend when you're
   ready to see recommendations for organizations you might be interested in
7. Hover over the SUGGESTED or HIGHLY RECOMMENDED flags to see an explanation
   for why the AI thinks a given organization is a good match
8. Click "Chat about this group" to learn more about a given organization or
   "Get involved!" to visit its website

## Caveats: 
- There is no validation of the user's responses to the interview questions
  apart from the check for excessively short answers, so the AI may have to deal
  with a lot of nonsense.
- The time it takes to get a response from the recommendation query and do the
  hallucination checks is fairly substantial, and I didn't add any progress UX
  to help the user understand that the processing takes time.
- The hallucination check returns a lot of false positives (real organization,
  wrong URL or weird page title), which is better than false negatives but still
  bothersome to the user.
- I found one false negative, a supposed Washington State chapter of Common
  Cause, and decided not to try to fix it (doing so would have created many more
  false positives).

## Evidence that it works:
- Go to https://vimeo.com/1241008108 for a screen-capture video showing an 
  example use case including the interview, looking at possible hallucinations 
  (which turn out to be false positives), and chatting about two organizations.
- See the test-run folder the server log and session state from the session 
  shown in the video.
  