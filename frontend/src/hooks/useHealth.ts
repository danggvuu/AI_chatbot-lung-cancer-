import { useEffect, useState } from 'react';

export interface HealthStatus {
  isOnline: boolean;
  isLoading: boolean;
  modelName: string;
  dbRecords: number;
}

interface HealthResponse {
  status: string;
  ollama_connection: string;
  ollama_model: string;
  database_loaded: boolean;
  database_records: number;
}

export function useHealth(): HealthStatus {
  const [status, setStatus] = useState<HealthStatus>({
    isOnline: false,
    isLoading: true,
    modelName: '',
    dbRecords: 0,
  });

  useEffect(() => {
    let cancelled = false;

    async function checkHealth() {
      try {
        const response = await fetch('/api/health');
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = (await response.json()) as HealthResponse;

        if (cancelled) return;

        const isOnline =
          data.status === 'healthy' &&
          data.ollama_connection === 'online';

        setStatus({
          isOnline,
          isLoading: false,
          modelName: data.ollama_model ?? '',
          dbRecords: data.database_records ?? 0,
        });
      } catch {
        if (cancelled) return;
        setStatus({
          isOnline: false,
          isLoading: false,
          modelName: '',
          dbRecords: 0,
        });
      }
    }

    void checkHealth();

    return () => {
      cancelled = true;
    };
  }, []);

  return status;
}
