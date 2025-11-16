// Main application layout

import React from 'react';
import { Layout } from 'antd';
import { Outlet } from 'react-router-dom';
import MainMenu from './MainMenu';
import TopBar from './TopBar';
import { useUIStore } from '@/store';

const { Header, Sider, Content, Footer } = Layout;

const AppLayout: React.FC = () => {
  const { sidebarCollapsed, setSidebarCollapsed } = useUIStore();

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={sidebarCollapsed}
        onCollapse={setSidebarCollapsed}
        theme="dark"
        width={250}
      >
        <div
          style={{
            height: '64px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '18px',
            fontWeight: 'bold',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          {!sidebarCollapsed ? 'FunSearch' : 'FS'}
        </div>
        <MainMenu />
      </Sider>

      <Layout>
        <Header style={{ padding: 0, background: '#fff', borderBottom: '1px solid #f0f0f0' }}>
          <TopBar />
        </Header>

        <Content style={{ margin: '24px', minHeight: 280 }}>
          <Outlet />
        </Content>

        <Footer style={{ textAlign: 'center', padding: '12px 50px' }}>
          FunSearch Framework ©2025 - AI-Driven Algorithm Discovery
        </Footer>
      </Layout>
    </Layout>
  );
};

export default AppLayout;
