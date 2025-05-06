# Social Media Reply Generator API

This project provides a REST API built with FastAPI to generate authentic, human-like replies to social media posts using Google's Gemini generative AI model. It also integrates with MongoDB to store the original post and the generated reply for tracking and analysis.

## Features

-   **Human-like Replies:** Utilizes Google Gemini (`gemini-2.0-flash` model) with sophisticated prompting to generate context-aware and platform-specific replies.
-   **Platform Awareness:** Prompts are tailored based on the source platform (Twitter, LinkedIn, Instagram) to match typical communication styles.
-   **FastAPI Backend:** Modern, fast (high-performance) web framework for building APIs with Python.
-   **Asynchronous Operations:** Leverages `asyncio`, `motor` (for MongoDB), and FastAPI's async capabilities for efficient handling of requests.
-   **MongoDB Integration:** Stores request-response pairs (`platform`, `post_text`, `generated_reply`, `timestamp`) in a MongoDB database.
-   **Pydantic Validation:** Ensures data integrity for API requests and responses using Pydantic models.
-   **Environment Configuration:** Uses `.env` files for secure management of API keys and database URIs.
-   **Error Handling:** Includes basic error handling for LLM and database operations.
-   **Health Check:** Provides a `/health` endpoint to check the status of core services (LLM, Database).



## Setup and Installation

1.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirement.txt
    ```

3.  **Configure Environment Variables:**
    * Create a file named `.env` in the project root directory.
    * Add your Google API Key and MongoDB Connection String:
        ```text
        # .env
        GOOGLE_API_KEY="YOUR_GOOGLE_GENERATIVE_AI_API_KEY"
        MONGODB_URI="YOUR_MONGODB_CONNECTION_STRING"
        MONGODB_DB_NAME="TechnicalTask" # Optional: Or your preferred DB name (defaults to TechnicalTask in database.py)
        MONGODB_COLLECTION_NAME="replies"   # Optional: Or your preferred collection name (defaults to replies in database.py)
        ```
    * **Get a Google API Key:** Visit the [Google AI Studio](https://aistudio.google.com/app/apikey) to create an API key. Ensure the Generative Language API is enabled for your project in Google Cloud Console if necessary.
    * **Set up MongoDB:** You can use a free tier on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) or run MongoDB locally. Obtain the connection string (URI). Make sure your network allows connections to the database cluster (e.g., whitelist your IP address in Atlas).

4.  **Run the API:**
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    The API will be available at `http://localhost:8000`. The `--reload` flag automatically restarts the server when code changes are detected (useful for development). You can also run `python main.py` if Uvicorn is installed and the `if __name__ == "__main__":` block is uncommented in `main.py`.

## API Usage

The API exposes the following main endpoints:

**`GET /`**
* **Description:** Returns a simple welcome message.

**`GET /health`**
* **Description:** Checks the status of the database connection and LLM configuration. Returns `200 OK` if both are available, `503 Service Unavailable` otherwise.

**`POST /reply`**

* **Description:** Generates a reply to a social media post.
* **Request Body:** JSON object containing:
    * `platform` (string, required): The source platform (e.g., "Twitter", "LinkedIn", "Instagram").
    * `post_text` (string, required): The content of the original post.
* **Success Response (200 OK):** JSON object containing:
    * `platform` (string): The original platform.
    * `post_text` (string): The original post text.
    * `generated_reply` (string): The AI-generated reply.
* **Error Responses:**
    * `400 Bad Request`: Invalid input data (defined in `main.py`, though standard Pydantic validation usually returns `422`).
    * `422 Unprocessable Entity`: Validation error (e.g., missing fields, incorrect JSON format).
    * `500 Internal Server Error`: Failure during LLM generation or database operation.
    * `503 Service Unavailable`: LLM or Database service is not configured or reachable.

**Example Request:**

Using `curl`:

```bash
curl -X POST "http://localhost:8000/reply" \
-H "Content-Type: application/json" \
-d '{
  "platform": "LinkedIn",
  "post_text": "Published a new article on leveraging AI for personalized customer experiences. Check it out and share your thoughts! #AI #CustomerExperience #Marketing"
}'
Example Success Response:{
  "platform": "LinkedIn",
  "post_text": "Published a new article on leveraging AI for personalized customer experiences. Check it out and share your thoughts! #AI #CustomerExperience #Marketing",
  "generated_reply": "Sounds fascinating! Personalized experiences are key. I'll definitely give it a read. Thanks for sharing your insights!"
}
