// Add to existing imports
import ErrorsPage from "./pages/errors";

// Add to route configuration
{
  path: "/errors",
  element: <ErrorsPage />,
},
{
  path: "/errors/:code",
  element: <ErrorDetailPage />, // Implement detail page as needed
},
