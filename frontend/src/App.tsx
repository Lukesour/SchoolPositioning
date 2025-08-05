import React, { useState } from 'react';
import { ConfigProvider, message, Spin } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import UserForm from './components/UserForm';
import AnalysisReport from './components/AnalysisReport';
import { apiService, UserBackground, AnalysisReport as AnalysisReportType } from './services/api';
import './App.css';

function App() {
  const [currentStep, setCurrentStep] = useState<'form' | 'report'>('form');
  const [analysisReport, setAnalysisReport] = useState<AnalysisReportType | null>(null);
  const [loading, setLoading] = useState(false);

  const handleFormSubmit = async (userBackground: UserBackground) => {
    setLoading(true);
    try {
      console.log('Submitting user background:', userBackground);
      
      // 调用后端API进行分析
      const report = await apiService.analyzeUserBackground(userBackground);
      
      console.log('Analysis report received:', report);
      setAnalysisReport(report);
      setCurrentStep('report');
      
      message.success('分析完成！');
    } catch (error: any) {
      console.error('Analysis failed:', error);
      
      let errorMessage = '分析失败，请稍后重试';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleBackToForm = () => {
    setCurrentStep('form');
    setAnalysisReport(null);
  };

  return (
    <ConfigProvider locale={zhCN}>
      <div className="App">
        <Spin spinning={loading} tip="正在进行AI分析，请稍候...">
          {currentStep === 'form' && (
            <UserForm onSubmit={handleFormSubmit} loading={loading} />
          )}
          
          {currentStep === 'report' && analysisReport && (
            <AnalysisReport report={analysisReport} onBack={handleBackToForm} />
          )}
        </Spin>
      </div>
    </ConfigProvider>
  );
}

export default App;
