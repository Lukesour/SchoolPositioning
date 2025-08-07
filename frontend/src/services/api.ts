import axios from 'axios';

// API基础配置
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5分钟超时，因为AI分析需要时间
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// 用户背景数据类型
export interface UserBackground {
  undergraduate_university: string;
  undergraduate_major: string;
  gpa: number;
  gpa_scale: string;
  graduation_year: number;
  language_test_type?: string;
  language_total_score?: number;
  language_reading?: number;
  language_listening?: number;
  language_speaking?: number;
  language_writing?: number;
  gre_total?: number;
  gre_verbal?: number;
  gre_quantitative?: number;
  gre_writing?: number;
  gmat_total?: number;
  target_countries: string[];
  target_majors: string[];
  target_degree_type: string;
  research_experiences?: Array<{
    name: string;
    role?: string;
    description: string;
  }>;
  internship_experiences?: Array<{
    company: string;
    position: string;
    description: string;
  }>;
  other_experiences?: Array<{
    name: string;
    description: string;
  }>;
}

// 分析报告数据类型
export interface CompetitivenessAnalysis {
  strengths: string;
  weaknesses: string;
  summary: string;
}

export interface SchoolRecommendation {
  university: string;
  program: string;
  reason: string;
}

export interface SchoolRecommendations {
  reach: SchoolRecommendation[];
  target: SchoolRecommendation[];
  safety: SchoolRecommendation[];
  case_insights: string;
}

export interface CaseComparison {
  gpa: string;
  university: string;
  experience: string;
}

export interface CaseAnalysis {
  case_id: number;
  admitted_university: string;
  admitted_program: string;
  gpa: string;
  language_score: string;
  language_test_type?: string; // 语言考试类型 (TOEFL/IELTS)
  key_experiences?: string; // 主要经历摘要
  undergraduate_info: string;
  comparison: CaseComparison;
  success_factors: string;
  takeaways: string;
}

export interface ActionPlan {
  timeframe: string;
  action: string;
  goal: string;
}

export interface BackgroundImprovement {
  action_plan: ActionPlan[];
  strategy_summary: string;
}

export interface AnalysisReport {
  competitiveness: CompetitivenessAnalysis;
  school_recommendations: SchoolRecommendations;
  similar_cases: CaseAnalysis[];
  background_improvement: BackgroundImprovement | null;
}

// API方法
export const apiService = {
  // 健康检查
  async healthCheck() {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // 获取系统统计信息
  async getStats() {
    const response = await apiClient.get('/api/stats');
    return response.data;
  },

  // 获取院校列表
  async getUniversities() {
    const response = await apiClient.get('/api/universities');
    return response.data;
  },

  // 获取专业列表
  async getMajors() {
    const response = await apiClient.get('/api/majors');
    return response.data;
  },

  // 分析用户背景
  async analyzeUserBackground(userBackground: UserBackground): Promise<AnalysisReport> {
    const response = await apiClient.post('/api/analyze', userBackground);
    return response.data as AnalysisReport;
  },

  // 获取案例详情
  async getCaseDetails(caseId: number) {
    const response = await apiClient.get(`/api/cases/${caseId}`);
    return response.data;
  },

  // 刷新数据
  async refreshData() {
    const response = await apiClient.post('/api/refresh-data');
    return response.data;
  },
};

export default apiService;