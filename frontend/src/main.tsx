// Import the React library, which is necessary for working with JSX and building React components.
import React from 'react'

// Import the createRoot function from react-dom/client, introduced in React 18.
// createRoot enables the new concurrent rendering features and improved performance.
// It is the recommended way to initialize React applications in React 18+ for better scalability.
import { createRoot } from 'react-dom/client'

// Import the root App component which serves as the top-level component of the React application.
// This component typically contains the entire UI and routing logic.
import App from './App'

// Locate the root DOM element where the React app will be mounted.
// The non-null assertion operator (!) is used here to tell TypeScript that the element with id 'root' definitely exists in the DOM.
// This avoids potential null errors during compilation.
// createRoot initializes a React root on this DOM node and enables concurrent features.
// The render method then renders the App component into this root node, bootstrapping the React application.
createRoot(document.getElementById('root')!).render(<App />)