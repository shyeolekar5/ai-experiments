# Detailed Setup Guide: Voice Command to Trello Task

This guide walks you through the four steps of setting up your Zapier automation flow, based on the provided configuration images.

## Prerequisites

Before starting, ensure you have active accounts for Zapier, AssemblyAI, and Trello.

### Automation Flow Overview

This is what the completed Zap looks like:
<img src="images/ZapierFlow.JPG" alt="Zapier workflow showing the four steps: Catch Hook, Transcribe, Analyze, and Create Card" style="width: 75%; display: block; margin: 0 auto;">

## Step 1: Trigger - Webhooks by Zapier (Catch Hook)

This step initiates the entire automation when an audio file URL is sent to a unique URL.

1.  **App & Event:** Select **Webhooks by Zapier** as the app and **Catch Hook** as the Event.
<img src="images/Catchhook.JPG" alt="Catch Hook setup showing App: Webhooks by Zapier and Event: Catch Hook" style="width: 75%; display: block; margin: 0 auto;">

2.  **Configure:** Copy the unique **Webhook URL** provided in the configuration screen. This is the URL you will use in your voice recording application to send the audio file link.
<img src="images/WebhookConfigure.JPG" alt="Webhook URL configuration" style="width: 75%; display: block; margin: 0 auto;">

3.  **Test:** Send a test payload to this URL containing a link to a publicly accessible audio file. This will allow Zapier to successfully "catch" the hook and recognize the data structure for the next steps.

-----

## Step 2: Action - AssemblyAI (Transcribe)

This step takes the audio URL from the trigger and converts it into text.

1.  **App & Event:** Select **AssemblyAI** as the app and **Transcribe** as the Event.
<img src="images/AssemblyAISet.JPG" alt="AssemblyAI Transcribe setup" style="width: 75%; display: block; margin: 0 auto;">

2.  **Configure:**

      * **Audio File:** Map the `audio_url` field (or whatever field contains your audio link) from the Webhook trigger in Step 1.

      * **Language Detection:** Set this to `true` to auto-detect the spoken language.

      * **Speech Model:** Select the desired quality; the configuration uses `best`.

      * **Wait until transcript is ready:** Set this to `true` to ensure the next step only runs after transcription is complete.
<img src="images/AssemblyAISetup.JPG" alt="AssemblyAI configuration for transcription" style="width: 75%; display: block; margin: 0 auto;">

-----

## Step 3: Action - AI by Zapier (Analyze and Return Data)

This step uses an AI model to analyze the transcribed text and extract structured data for the Trello card.

1.  **App & Event:** Select **AI by Zapier** as the app and **Analyze and Return Data** as the Event.
<img src="images/AIbyZapierSetup.JPG" alt="AI by Zapier Setup" style="width: 75%; display: block; margin: 0 auto;">

2.  **Configure - Model & Input:**

      * **Provider:** `openai`

      * **Model:** `openai/gpt-4o-mini` (or the preferred model).

      * **Input:** Map the transcribed text output from **Step 2: AssemblyAI**.
<img src="images/AIbyZapierConfigure1.JPG" alt="AI by Zapier Model and Input configuration" style="width: 75%; display: block; margin: 0 auto;">

3.  **Configure - Prompt:** Use a System Prompt to define the AI's role and task. The provided prompt starts with:

    > "You are an expert Trello task organizer. Your job is to analyze the raw voice command provided below and extract the necessary details to create a structured Trello card. 1. \*\*Extraction:\*\* Extract the following five fields: Name..."

4.  **Configure - Output Fields (Schema):** Define the exact structure the AI must return. This ensures consistent data for Trello.

      * **Name:** The title or name of the Trello card.

      * **Due Date:** The date by which the task should be completed, formatted as `YYYY-MM-DD`.

      * **Description:** A detailed description of the task.

      * **Category:** The category (e.g., Work, Personal, Others).

      * **Priority:** The urgency level (Allowed values are High, Medium, and Low).

      * **Return as an array of objects?** Set to `false`.
<img src="images/AIbyZapierConfig2.JPG" alt="AI by Zapier Output fields schema" style="width: 75%; display: block; margin: 0 auto;">

-----

## Step 4: Action - Trello (Create Card)

This final step uses the structured data from the AI to create the task in Trello.

1.  **App & Event:** Select **Trello** as the app and **Create Card** as the Event.
<img src="images/TrelloSetup.JPG" alt="Trello Create Card setup" style="width: 75%; display: block; margin: 0 auto;">

2.  **Configure:** Map the output fields from **Step 3: AI by Zapier** to the Trello card fields:

      * **Board ID:** Select your target board (e.g., "AI tasks").

      * **List ID:** Select the list where new tasks should land (e.g., "Inbox").

      * **Name:** Map the **3. Name** output from the AI step.

      * **Description:** Map the **3. Description** output from the AI step.

      * **Due Date:** Map the **3. Due Date** output from the AI step.

      * **Card Position:** Set as desired (e.g., `bottom`).
<img src="images/TrelloConfig2.JPG" alt="Trello Card Configuration with mapped fields" style="width: 75%; display: block; margin: 0 auto;">

**Congratulations\!** Your Voice Command to Trello automation is complete. You can now test the full flow by sending a voice command URL to your unique webhook.