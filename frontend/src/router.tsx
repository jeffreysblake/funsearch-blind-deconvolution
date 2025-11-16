// Router configuration

import { createBrowserRouter } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import HomePage from './pages/HomePage';
import ProjectDetailPage from './pages/ProjectDetailPage';
import ExperimentMonitorPage from './pages/ExperimentMonitorPage';
import TemplatesPage from './pages/TemplatesPage';
import NotFoundPage from './pages/NotFoundPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: 'projects/:projectId',
        element: <ProjectDetailPage />,
      },
      {
        path: 'projects/:projectId/experiments/:experimentId',
        element: <ExperimentMonitorPage />,
      },
      {
        path: 'templates',
        element: <TemplatesPage />,
      },
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
]);
