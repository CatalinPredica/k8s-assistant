import { useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css"; // Import the stylesheet for styling the application components

/**
 * Main application component for the Kubernetes Assistant frontend.
 * This component handles user input, communicates with the backend API,
 * and displays the AI-generated responses.
 */
function App() {
  // State to hold the user's input query string
  const [userInput, setUserInput] = useState("");
  // State to store the response object returned from the backend API
  const [response, setResponse] = useState(null);
  // State flag to indicate whether a request is currently being processed
  const [loading, setLoading] = useState(false);
  // State to capture and display any error messages from the API or network
  const [error, setError] = useState(null);

  /**
   * Event handler for form submission.
   * Handles sending the user's query to the backend API asynchronously,
   * manages loading and error states, and updates the response state on success.
   * 
   * @param {React.FormEvent} e - The form submission event
   */
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent default form submission to avoid page reload

    // Reset states to prepare for new request
    setLoading(true);    // Set loading to true to disable inputs and show loader
    setError(null);      // Clear any previous errors
    setResponse(null);   // Clear previous response data

    try {
      // Make a POST request to the backend API endpoint '/api/ask'
      // The backend expects a JSON body with the user's input under 'user_input' key
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json", // Specify JSON content type for proper parsing
        },
        body: JSON.stringify({ user_input: userInput }),
      });

      // Robust error handling: check for HTTP response status
      if (!res.ok) {
        // If status is not OK (200-299), throw an error to be caught below
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      // Parse the JSON response from the backend
      const data = await res.json();

      // Update the response state with the parsed data to trigger UI update
      setResponse(data);
    } catch (e) {
      // Handle network errors or unexpected exceptions gracefully
      setError("Failed to fetch from the backend. Please check your network and backend server.");
      // Log the error to the console for debugging and monitoring purposes
      console.error(e);
    } finally {
      // Always reset loading state regardless of success or failure
      setLoading(false);
    }
  };

  return (
    // Root container div for the entire application UI
    <div className="app-container">
      {/* Header section with title and description */}
      <header className="app-header">
        <h1>Kubernetes Assistant</h1>
        <p>
          Enter your request for the Kubernetes Assistant below. The AI will generate and execute commands to fulfill your request.
        </p>
      </header>

      {/* Form container for user input and submission */}
      <form onSubmit={handleSubmit} className="form-container">
        <input
          type="text"
          value={userInput}
          // Controlled input: update state on every keystroke to keep UI and state in sync
          onChange={(e) => setUserInput(e.target.value)} // <-- THE FIX IS HERE
          placeholder="e.g., show me all pods in the default namespace"
          disabled={loading} // Disable input while loading to prevent multiple submissions
          aria-label="User input for Kubernetes Assistant query"
        />
        <button type="submit" disabled={loading} aria-busy={loading}>
          {/* Show a loader animation during async request, else show 'Ask' */}
          {loading ? <div className="loader" aria-live="polite" aria-label="Loading"></div> : "Ask"}
        </button>
      </form>

      {/* Display error message if any error occurs */}
      {error && <div className="error-message" role="alert">Error: {error}</div>}

      {/* Conditionally render the response container if a response exists */}
      {response && (
        <div className="response-container">
          <h2>Assistant Response:</h2>
          {/* If the response includes a final output, render it as markdown for rich text display */}
          {response.final_output ? (
            <div className="markdown-response">
              <ReactMarkdown>{response.final_output}</ReactMarkdown>
            </div>
          ) : (
            // If no final output, provide a fallback message and display raw steps for transparency/debugging
            <div>
              <p>No final output. Check the steps for details.</p>
              <pre>{JSON.stringify(response.steps, null, 2)}</pre>
            </div>
          )}
        </div>
      )}

      {/* Additional debug section showing the full steps data returned by backend.
          This is useful for developers to trace the AI's step-by-step reasoning.
          This block should be removed or hidden in production. */}
      {response && (
        <div className="response-container debug-container">
          <h2>Full Steps (for debugging):</h2>
          <pre>{JSON.stringify(response.steps, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
