export interface AttentionAlert {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  title: string;
  sub: string;
  why: string;
  actionText: string;
  actionType?: string;
}

export interface FarmEnvironmentData {
  id: string;
  farmName: string;
  cropName: string;
  stage: string;
  day: number;
  temperature: string;
  humidity: string;
  humidityAlert?: 'High' | 'Critical' | null;
  rainfall: string;
  rainfallAlert?: 'Heavy' | null;
  wind: string;
  status: 'green' | 'amber' | 'red';
}

export interface UpcomingTask {
  id: string;
  name: string;
  farm: string;
  crop: string;
  when: string;
  dotColor: string;
}

export interface OverdueTask {
  id: string;
  title: string;
  sub: string;
}

export interface AIInsight {
  id: string;
  title: string;
  body: string;
  iconType: 'droplets' | 'wind' | 'trending';
}

export interface PerformanceMetric {
  label: string;
  value: string;
  sub: string;
}

export interface ActivityBar {
  height: string;
  type: 'green' | 'accent' | 'warn';
}

export interface DiseaseRisk {
  farm: string;
  crop?: string;
  info: string;
  risk: 'Low' | 'Medium' | 'High';
}
