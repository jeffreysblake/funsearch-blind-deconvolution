// Top navigation bar

import React from 'react';
import { Space, Badge, Button, Tooltip } from 'antd';
import { BellOutlined, QuestionCircleOutlined, GithubOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { healthApi } from '@/api';

const TopBar: React.FC = () => {
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: healthApi.check,
    refetchInterval: 30000, // Check every 30 seconds
  });

  const isHealthy = health?.status === 'healthy';

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '0 24px',
        height: '100%',
      }}
    >
      <div>
        {/* Breadcrumbs or page title can go here */}
      </div>

      <Space size="middle">
        <Tooltip title={isHealthy ? 'System Healthy' : 'System Issues Detected'}>
          <Badge status={isHealthy ? 'success' : 'error'} />
          <span style={{ marginLeft: 4 }}>
            {isHealthy ? 'Connected' : 'Disconnected'}
          </span>
        </Tooltip>

        <Tooltip title="Notifications">
          <Badge count={0}>
            <Button type="text" icon={<BellOutlined />} />
          </Badge>
        </Tooltip>

        <Tooltip title="Documentation">
          <Button
            type="text"
            icon={<QuestionCircleOutlined />}
            href="https://github.com/your-repo/funsearch"
            target="_blank"
          />
        </Tooltip>

        <Tooltip title="GitHub Repository">
          <Button
            type="text"
            icon={<GithubOutlined />}
            href="https://github.com/your-repo/funsearch"
            target="_blank"
          />
        </Tooltip>
      </Space>
    </div>
  );
};

export default TopBar;
