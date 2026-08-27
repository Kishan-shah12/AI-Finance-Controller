# ReconAI Frontend

This is the Next.js frontend application for ReconAI, providing the primary user interface for the AI Finance Controller.

## Architecture & Tech Stack

- **Framework**: [Next.js](https://nextjs.org) (App Router)
- **Styling**: Tailwind CSS
- **Components**: Radix UI / shadcn/ui
- **Icons**: Lucide React
- **Data Fetching**: Native Fetch API connecting to the FastAPI backend

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Configure environment:
   Make sure you have an `.env.local` file pointing to the backend API if it's not running on `localhost:8000`. By default, the frontend expects `NEXT_PUBLIC_API_URL` to be configured, falling back to `/api` proxy or `http://localhost:8000` depending on the environment.

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) with your browser.

## Deployment

The application is optimized for deployment on the [Vercel Platform](https://vercel.com/new).

When deploying, ensure you configure the following environment variable:
- `NEXT_PUBLIC_API_URL`: The URL of your deployed FastAPI backend (e.g., `https://reconai-backend.onrender.com`).
