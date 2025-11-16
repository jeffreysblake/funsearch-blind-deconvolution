// Theme configuration for Ant Design and application styles

import type { ThemeConfig } from 'antd';

// Color palette
export const colors = {
  primary: '#1890ff',      // Ant Design blue
  success: '#52c41a',      // Green
  warning: '#faad14',      // Yellow
  error: '#f5222d',        // Red
  info: '#13c2c2',         // Cyan

  // Status colors
  running: '#52c41a',      // Green
  paused: '#faad14',       // Yellow
  completed: '#1890ff',    // Blue
  failed: '#f5222d',       // Red
  pending: '#8c8c8c',      // Gray
  stopped: '#595959',      // Dark gray

  // Chart colors
  chart: [
    '#1890ff',
    '#52c41a',
    '#faad14',
    '#f5222d',
    '#722ed1',
    '#13c2c2',
    '#eb2f96',
    '#fa8c16',
  ],
};

// Typography
export const typography = {
  fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",

  fontSize: {
    xs: '12px',
    sm: '14px',
    base: '16px',
    lg: '18px',
    xl: '20px',
    '2xl': '24px',
    '3xl': '30px',
  },

  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
};

// Spacing
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

// Breakpoints
export const breakpoints = {
  xs: '480px',
  sm: '576px',
  md: '768px',
  lg: '992px',
  xl: '1200px',
  xxl: '1600px',
};

// Ant Design theme configuration
export const antdTheme: ThemeConfig = {
  token: {
    colorPrimary: colors.primary,
    colorSuccess: colors.success,
    colorWarning: colors.warning,
    colorError: colors.error,
    colorInfo: colors.info,
    fontFamily: typography.fontFamily,
    borderRadius: 4,
  },
  components: {
    Layout: {
      headerBg: '#001529',
      siderBg: '#001529',
    },
    Menu: {
      darkItemBg: '#001529',
      darkSubMenuItemBg: '#000c17',
    },
  },
};

// Helper function to get status color
export const getStatusColor = (status: string): string => {
  const statusMap: Record<string, string> = {
    running: colors.running,
    paused: colors.paused,
    completed: colors.completed,
    failed: colors.failed,
    pending: colors.pending,
    stopped: colors.stopped,
    active: colors.success,
    draft: colors.pending,
    archived: colors.pending,
  };

  return statusMap[status.toLowerCase()] || colors.primary;
};
