// Templates page

import React from 'react';
import { Card, Row, Col, Button, Empty, Spin, Typography, Space, Tag } from 'antd';
import { AppstoreOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { templatesApi } from '@/api';
import type { TemplateInfo } from '@/types';

const { Title, Text } = Typography;

const TemplatesPage: React.FC = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['templates'],
    queryFn: () => templatesApi.list(),
  });

  const templates = data?.templates || [];

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="Loading templates..." />
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <Empty
          description="Failed to load templates"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button type="primary" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </Empty>
      </Card>
    );
  }

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        Project Templates
      </Title>

      {templates.length === 0 ? (
        <Card>
          <Empty description="No templates available" />
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {templates.map((template: TemplateInfo) => (
            <Col xs={24} sm={12} lg={8} key={template.id}>
              <Card
                hoverable
                title={
                  <Space>
                    <AppstoreOutlined />
                    {template.name}
                  </Space>
                }
                style={{ height: '100%' }}
              >
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text>{template.description}</Text>

                  <div>
                    <Text strong>Example Problems:</Text>
                    <div style={{ marginTop: 8 }}>
                      {template.example_problems.map((problem) => (
                        <Tag key={problem} style={{ marginBottom: 4 }}>
                          {problem}
                        </Tag>
                      ))}
                    </div>
                  </div>

                  <Button type="primary" block style={{ marginTop: 16 }}>
                    Use Template
                  </Button>
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
};

export default TemplatesPage;
